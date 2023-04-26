using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using NetworkDataGenerator.App.Domain.Data;

namespace NetworkDataGenerator.App.Domain
{
    public class MatpowerOpfDecoder /*: ISolutionDecoder*/
    {
        private readonly MatpowerDecoderConfigurationContext _configurationContext;

        public MatpowerOpfDecoder(MatpowerDecoderConfigurationContext configurationContext)
        {
            _configurationContext = configurationContext;
        }

        public NetPowerFlow Decode(EnergyNetEncoding encodedSolution, NetPowerFlow solution)
        {
            NetPowerFlow powerFlow = solution as NetPowerFlow;
            EnergyNetEncoding ene = encodedSolution as EnergyNetEncoding;

            powerFlow.Reset();

            return _configurationContext.RunParallel ? DecodeParallel(ene, powerFlow) : DecodeSync(ene, powerFlow);
        }

        public NetPowerFlow InitSolution(EnergyNetEncoding encodedSolution)
        {
            EnergyNetEncoding ene = encodedSolution as EnergyNetEncoding;
            if (ene == null)
            {
                //string error = $"Could not initialize solution. {LogMessageUtil.ParamNotOfTypeString(nameof(encodedSolution), typeof(EnergyNetEncoding))}";
                //Logger.Error(error);
                //throw new DecoderException(error);
                throw new ArgumentNullException("encodedSolution");
            }

            // TODO: do some initializing work, e.g. in Schedule we would initialize machine allocations
            IDictionary<int, TimeStepOpf> opfPerTimeStep = new Dictionary<int, TimeStepOpf>();
            foreach (var state in ene.StatesPerTimeStep)
            {
                TimeStepOpf opf = new TimeStepOpf(state.Period, state.StateList);
                opfPerTimeStep.Add(state.Period, opf);
            }

            //ISolutionDecoderStateInformation stateInfo = _configurationContext.DecodingStateInfo.Copy();
            return new NetPowerFlow(ene, opfPerTimeStep); //, stateInfo);
        }

        //public string ExportSolution(EnergyNetEncoding encodedSolution, NetPowerFlow decodedSolution)
        //{
        //    Decode(encodedSolution, decodedSolution);
        //    return _configurationContext.ExportSolutionCallback(decodedSolution);
        //}

        private NetPowerFlow DecodeSync(EnergyNetEncoding energyNet, NetPowerFlow powerFlow)
        {
            foreach (var timeStep in energyNet.StatesPerTimeStep)
            {
                string caseFileName = _configurationContext.CaseFileName;
                string solvedCaseFileName = _configurationContext.SolvedCaseFileName;

                RunTimeStepOpf(timeStep, caseFileName, solvedCaseFileName, powerFlow);

                if (!powerFlow.IsFeasible)  // runopf() wrote an error
                {
                    //Logger.Info("Cancelling decoding.");
                    break;
                }

                ReadOpfResult(timeStep, solvedCaseFileName, powerFlow);
                if (!powerFlow.IsFeasible)  // runopf() did not converge
                {
                    //Logger.Info("Cancelling decoding.");
                    break;
                }
            }

            return powerFlow;
        }

        private NetPowerFlow DecodeParallel(EnergyNetEncoding energyNet, NetPowerFlow powerFlow)
        {
            Parallel.ForEach(energyNet.StatesPerTimeStep, new ParallelOptions { MaxDegreeOfParallelism = _configurationContext.MaxConcurrency },
                timeStep =>
                {
                    string caseFileName = GetTimeStepCaseFileName(_configurationContext.CaseFileName, timeStep);
                    string solvedCaseFileName = GetTimeStepCaseFileName(_configurationContext.SolvedCaseFileName, timeStep);

                    RunTimeStepOpf(timeStep, caseFileName, solvedCaseFileName, powerFlow);
                });

            foreach (var timeStep in energyNet.StatesPerTimeStep)
            {
                string solvedCaseFileName = GetTimeStepCaseFileName(_configurationContext.SolvedCaseFileName, timeStep);
                ReadOpfResult(timeStep, solvedCaseFileName, powerFlow);
            }

            // write the summary of the OPF run to .csv file (timeslot, real power output of first generator, real power output of second generator,...)
            //powerFlow.WriteSolutionSummary();

            return powerFlow;
        }

        private string GetTimeStepCaseFileName(string fileName, TimeStepStates timeStep)
        {
            return Path.GetFileNameWithoutExtension(fileName) + "t" + timeStep.Period + Path.GetExtension(fileName);
        }

        private void RunTimeStepOpf(TimeStepStates timeStep, string caseFileName, string solvedCaseFileName, NetPowerFlow powerFlow)
        {
            // write case file according to net component states at time step
            if (timeStep != null)
                _configurationContext.ExportCaseFile(timeStep, Path.Combine(_configurationContext.CaseFileDirectory, caseFileName));

            //Logger.Info(timeStep.ToString());

            // instantiate GNU Octave process with a Matlab script running Matpower's runopf() function
            ProcessStartInfo psi = new ProcessStartInfo
            {
                Arguments = "",
                UseShellExecute = false,
                FileName = _configurationContext.PathToOpfToolExe,
                RedirectStandardError = true,
                RedirectStandardOutput = true
            };
            psi.ArgumentList.Add(_configurationContext.OpfScriptFilePath);
            psi.ArgumentList.Add(_configurationContext.CaseFileDirectory);
            psi.ArgumentList.Add(caseFileName);
            psi.ArgumentList.Add(solvedCaseFileName);
            Process p = Process.Start(psi);

            string stdErr = p.StandardError.ReadToEnd();
            //string stdOut = p.StandardOutput.ReadToEnd();
            p.WaitForExit();
            //if (!string.IsNullOrEmpty(stdErr)) Logger.Warn(stdErr);
            //if (!string.IsNullOrEmpty(stdOut)) Logger.Info(stdOut);
            if (stdErr.ToLower().Contains("error"))
            {
                powerFlow.IsFeasible = false;
                //Logger.Info("OPF returned an error. Solution is not feasible.");
            }
        }

        private void ReadOpfResult(TimeStepStates timeStep, string solvedCaseFileName, NetPowerFlow powerFlow)
        {
            // read resulting case file and adapt solution object
            StreamReader reader = new StreamReader(Path.Combine(_configurationContext.CaseFileDirectory, solvedCaseFileName));
            CaseProblemData problemData = _configurationContext.ImportCaseFile(reader, null, null, null, null);
            powerFlow.OpfPerTimeStep[timeStep.Period].OpfObjectiveFunctionValue = problemData.ObjVal;
            powerFlow.OpfPerTimeStep[timeStep.Period].RealPowerGeneration = new List<Tuple<Generator, double>>();
            IDictionary<int, Bus> idToBus = powerFlow.EnergyNet.NetworkData.Buses.ToDictionary(x => x.Id, x => x);
            int genUnitId = 0;
            foreach (var genEntry in problemData.Gen)
            {
                int busId = (int)genEntry[0];
                if (idToBus.ContainsKey(busId))
                {
                    Bus bus = idToBus[busId];
                    ++genUnitId;
                    Generator g = bus.Generators.First(x => x.Id == genUnitId);
                    powerFlow.OpfPerTimeStep[timeStep.Period].RealPowerGeneration.Add(new Tuple<Generator, double>(g, problemData.Gen[genUnitId - 1][1]));
                }
            }
            powerFlow.OpfPerTimeStep[timeStep.Period].IsFeasible = powerFlow.IsFeasible && problemData.Converged;
            if (!problemData.Converged)
            {
                powerFlow.IsFeasible = false;
                //Logger.Info("OPF did not converge. Solution is not feasible.");
            }
        }
    }
}
