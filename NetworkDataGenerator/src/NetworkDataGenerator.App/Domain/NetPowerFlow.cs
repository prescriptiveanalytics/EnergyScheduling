using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

namespace NetworkDataGenerator.App.Domain
{
    public class NetPowerFlow /*: ISolution*/
    {
        public EnergyNetEncoding EnergyNet { get; set; }
        public IDictionary<int, TimeStepOpf> OpfPerTimeStep { get; }
        public bool IsFeasible { get; set; }
    
        public NetPowerFlow(EnergyNetEncoding energyNet, IDictionary<int, TimeStepOpf> opfPerTimeStep) //, ISolutionDecoderStateInformation stateInformation)
        {
            EnergyNet = energyNet;
            OpfPerTimeStep = opfPerTimeStep;
            //DecodingStateInfo = stateInformation;
            IsInitialized = true;
        }

        //public NetPowerFlow(NetPowerFlow other)
        //{
        //    EnergyNet = new EnergyNetEncoding(other.EnergyNet);
        //    foreach (var opf in other.OpfPerTimeStep.Keys)
        //    {
        //        OpfPerTimeStep[opf] = new TimeStepOpf(other.OpfPerTimeStep[opf]);
        //    }
        //    DecodingStateInfo = other.DecodingStateInfo.Copy();
        //    DecodingStateInfo.Reset();
        //    IsInitialized = true;
        //}

        //public ISolution ShallowCopy()
        //{
        //    return new NetPowerFlow(this);
        //}

        public bool IsInitialized { get; }
        //public bool IsPruned { get; set; }
        //public ISolutionDecoderStateInformation DecodingStateInfo { get; set; }

        public void Reset()
        {
            IsFeasible = true;
        }

        //public void WriteExtendedSolutionSummaryTS()
        //{
        //    StringBuilder sb = new StringBuilder();
        //    string separator = ",";
        //    CultureInfo culture = CultureInfo.InvariantCulture;

        //    // commitment status
        //    string firstLine = "";
        //    firstLine += "t";
        //    firstLine += separator;
        //    for (int i = 0; i < EnergyNet.StatesPerTimeStep.Count(); i++)
        //    {
        //        firstLine += i;
        //        firstLine += separator;
        //    }
        //    sb.Append(firstLine);
        //    sb.Append(Environment.NewLine);
        //    firstLine = "";

        //    string nextLine = "";
        //    foreach (Generator g in EnergyNet.NetworkData.Generators)
        //    {
        //        nextLine += "G" + g.Id + " (Bus " + g.Bus.ExtId + ")";
        //        nextLine += separator;

        //        foreach (TimeStepOpf timeStepOpf in OpfPerTimeStep.Values)
        //        {
        //            TimeStepStates stateListPerTimeStep = timeStepOpf.StateList;

        //            foreach (NetComponentState ncState in stateListPerTimeStep.StateList)
        //            {
        //                if (ncState.NetComponent is Generator && ncState.NetComponent.Id == g.Id)
        //                {
        //                    nextLine += ncState.State;
        //                    nextLine += separator;
        //                }
        //            }
        //        }

        //        sb.Append(nextLine);
        //        sb.Append(Environment.NewLine);
        //        nextLine = "";
        //    }
        //    foreach (EnergyStorageSystem s in EnergyNet.NetworkData.EnergyStorageSystems)
        //    {
        //        nextLine += "ESS" + s.Id + " (Bus " + s.Bus.ExtId + ")";
        //        nextLine += separator;

        //        foreach (TimeStepOpf timeStepOpf in OpfPerTimeStep.Values)
        //        {
        //            TimeStepStates stateListPerTimeStep = timeStepOpf.StateList;

        //            foreach (NetComponentState ncState in stateListPerTimeStep.StateList)
        //            {
        //                if (ncState.NetComponent is EnergyStorageSystem && ncState.NetComponent.Id == s.Id)
        //                {
        //                    nextLine += ncState.State;
        //                    nextLine += separator;
        //                }
        //            }
        //        }

        //        sb.Append(nextLine);
        //        sb.Append(Environment.NewLine);
        //        nextLine = "";
        //    }
        //    sb.Append(nextLine);
        //    sb.Append(Environment.NewLine);

        //    TimeStepOpf opfPerTimeStep0 = OpfPerTimeStep[0];
        //    firstLine += "t";
        //    firstLine += separator;
        //    for (int t = 0; t < EnergyNet.StatesPerTimeStep.Count; t++)
        //    {
        //        firstLine += t.ToString(CultureInfo.InvariantCulture);
        //        firstLine += separator;
        //    }
        //    sb.Append(firstLine);
        //    sb.Append(Environment.NewLine);

        //    double zero = 0.0;
        //    foreach (Generator g in EnergyNet.NetworkData.Generators)
        //    {
        //        nextLine += "G" + g.Id + " (Bus " + g.Bus.ExtId + ")";
        //        nextLine += separator;

        //        foreach (int timeStep in OpfPerTimeStep.Keys)
        //        {
        //            TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];
        //            for (int i = 0; i < opfPerTimeStep.RealPowerGeneration.Count; i++)
        //            {
        //                Tuple<Generator, double> realPowerGenPerTimeStep = opfPerTimeStep.RealPowerGeneration.ElementAt(i);
        //                if (realPowerGenPerTimeStep.Item1.Id == g.Id)
        //                {
        //                    if ((realPowerGenPerTimeStep.Item2 > 0 && realPowerGenPerTimeStep.Item2 < 0.000001)
        //                       || (realPowerGenPerTimeStep.Item2 < 0 && realPowerGenPerTimeStep.Item2 > -0.000001))
        //                        nextLine += zero.ToString(CultureInfo.InvariantCulture);
        //                    else
        //                        nextLine += realPowerGenPerTimeStep.Item2.ToString(CultureInfo.InvariantCulture);
        //                    nextLine += separator;
        //                }
        //            }
        //        }

        //        sb.Append(nextLine);
        //        sb.Append(Environment.NewLine);
        //        nextLine = "";
        //    }

        //    double reserveSum = 0.0;
        //    foreach (Generator genEl in EnergyNet.NetworkData.Generators)
        //    {
        //        reserveSum += genEl.ReserveMaxLimit;
        //        reserveSum += genEl.ReserveCost;
        //    }
        //    int areGenReservesDefined = (reserveSum > 0) ? 1 : 0;
        //    if (areGenReservesDefined > 0)
        //    {
        //        foreach (Generator g in EnergyNet.NetworkData.Generators)
        //        {
        //            nextLine += "ReserveG" + g.Id;
        //            nextLine += separator;

        //            foreach (int timeStep in OpfPerTimeStep.Keys)
        //            {
        //                TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];
        //                for (int i = 0; i < opfPerTimeStep.RealPowerReserve.Count; i++)
        //                {
        //                    Tuple<Generator, double> realPowerResPerTimeStep =
        //                        opfPerTimeStep.RealPowerReserve.ElementAt(i);
        //                    if (realPowerResPerTimeStep.Item1.Id == g.Id)
        //                    {
        //                        if ((realPowerResPerTimeStep.Item2 > 0 && realPowerResPerTimeStep.Item2 < 0.000001)
        //                            || (realPowerResPerTimeStep.Item2 < 0 && realPowerResPerTimeStep.Item2 > -0.000001))
        //                            nextLine += zero.ToString(CultureInfo.InvariantCulture);
        //                        else
        //                            nextLine += realPowerResPerTimeStep.Item2.ToString(CultureInfo.InvariantCulture);
        //                        nextLine += separator;
        //                    }
        //                }
        //            }

        //            sb.Append(nextLine);
        //            sb.Append(Environment.NewLine);
        //            nextLine = "";
        //        }
        //    }


        //    foreach (EnergyStorageSystem s in EnergyNet.NetworkData.EnergyStorageSystems)
        //    {
        //        nextLine += "ESS" + s.Id + " (Bus " + s.Bus.ExtId + ")";
        //        nextLine += separator;

        //        foreach (int timeStep in OpfPerTimeStep.Keys)
        //        {
        //            TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];

        //            for (int i = 0; i < opfPerTimeStep.RealPowerDispatch.Count; i++)
        //            {
        //                Tuple<EnergyStorageSystem, double> realPowerDispatchPerTimeStep = opfPerTimeStep.RealPowerDispatch.ElementAt(i);
        //                if (s.Id == realPowerDispatchPerTimeStep.Item1.Id)
        //                {
        //                    if (realPowerDispatchPerTimeStep.Item2 > 0 && realPowerDispatchPerTimeStep.Item2 < 0.000001)
        //                        nextLine += zero.ToString(CultureInfo.InvariantCulture);
        //                    else
        //                        nextLine += realPowerDispatchPerTimeStep.Item2.ToString(CultureInfo.InvariantCulture);
        //                    nextLine += separator;
        //                }
        //            }
        //        }

        //        sb.Append(nextLine);
        //        sb.Append(Environment.NewLine);
        //        nextLine = "";
        //    }

        //    nextLine += "ExtGrid";
        //    nextLine += separator;
        //    foreach (int timeStep in OpfPerTimeStep.Keys)
        //    {
        //        TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];

        //        nextLine += opfPerTimeStep.ExtGridImportExport.ToString(CultureInfo.InvariantCulture);
        //        nextLine += separator;
        //    }
        //    sb.Append(nextLine);
        //    sb.Append(Environment.NewLine);
        //    nextLine = "";

        //    nextLine += "TotalLoad";
        //    nextLine += separator;
        //    foreach (int timeStep in OpfPerTimeStep.Keys)
        //    {
        //        TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];

        //        double totalLoad = 0.0;
        //        IList<NetComponentState> list1 = EnergyNet.StatesPerTimeStep.First(x => x.Period == timeStep).StateList;
        //        foreach (NetComponentState ncState in list1)
        //        {
        //            if (ncState.NetComponent is Load)
        //                totalLoad += ncState.State;
        //        }
        //        nextLine += (-totalLoad).ToString(CultureInfo.InvariantCulture);
        //        nextLine += separator;
        //    }
        //    sb.Append(nextLine);
        //    sb.Append(Environment.NewLine);
        //    nextLine = "";

        //    nextLine += "TotalPVGen";
        //    nextLine += separator;
        //    foreach (int timeStep in OpfPerTimeStep.Keys)
        //    {
        //        TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];

        //        double totalPVGen = 0.0;
        //        IList<NetComponentState> list1 = EnergyNet.StatesPerTimeStep.First(x => x.Period == timeStep).StateList;
        //        foreach (NetComponentState ncState in list1)
        //        {
        //            if ((ncState.NetComponent is NonProgrammableGenerator) && (ncState.NetComponent as NonProgrammableGenerator).Type == NonProgrammableGeneratorType.Photovoltaic)
        //                totalPVGen += ncState.State;
        //        }
        //        nextLine += totalPVGen.ToString(CultureInfo.InvariantCulture);
        //        nextLine += separator;
        //    }
        //    sb.Append(nextLine);
        //    sb.Append(Environment.NewLine);

        //    string directoryName = "..\\..\\..\\..\\Resources\\Data\\";
        //    if (!string.IsNullOrEmpty(directoryName) && !Directory.Exists(directoryName))
        //        Directory.CreateDirectory(directoryName);

        //    using var sw = new StreamWriter(directoryName + "SolutionSummaryTS.csv");
        //    sw.Write(sb.ToString());
        //}

        //public void WriteExtendedSolutionSummaryUCP()
        //{
        //    StringBuilder sb = new StringBuilder();
        //    string separator = ",";
        //    CultureInfo culture = CultureInfo.InvariantCulture;

        //    // commitment status
        //    string firstLine = "";
        //    firstLine += "t";
        //    firstLine += separator;
        //    for (int i = 0; i < EnergyNet.StatesPerTimeStep.Count(); i++)
        //    {
        //        firstLine += i;
        //        firstLine += separator;
        //    }
        //    sb.Append(firstLine);
        //    sb.Append(Environment.NewLine);
        //    firstLine = "";

        //    string nextLine = "";
        //    // commitment status
        //    foreach (Generator g in EnergyNet.NetworkData.Generators)
        //    {
        //        nextLine += "G" + g.Id + " (Bus " + g.Bus.ExtId + ")";
        //        nextLine += separator;

        //        foreach (TimeStepStates timeStepStates in EnergyNet.StatesPerTimeStep)
        //        {
        //            IList<NetComponentState> stateListPerTimeStep = timeStepStates.StateList;

        //            foreach (NetComponentState ncState in stateListPerTimeStep)
        //            {
        //                if (ncState.NetComponent is Generator && ncState.NetComponent.Id == g.Id)
        //                {
        //                    nextLine += ncState.State;
        //                    nextLine += separator;
        //                }
        //            }
        //        }

        //        sb.Append(nextLine);
        //        sb.Append(Environment.NewLine);
        //        nextLine = "";
        //    }
        //    foreach (EnergyStorageSystem s in EnergyNet.NetworkData.EnergyStorageSystems)
        //    {
        //        nextLine += "ESS" + s.Id + " (Bus " + s.Bus.ExtId + ")";
        //        nextLine += separator;

        //        foreach (TimeStepStates timeStepStates in EnergyNet.StatesPerTimeStep)
        //        {
        //            IList<NetComponentState> stateListPerTimeStep = timeStepStates.StateList;

        //            foreach (NetComponentState ncState in stateListPerTimeStep)
        //            {
        //                if (ncState.NetComponent is EnergyStorageSystem && ncState.NetComponent.Id == s.Id)
        //                {
        //                    nextLine += ncState.State;
        //                    nextLine += separator;
        //                }
        //            }
        //        }

        //        sb.Append(nextLine);
        //        sb.Append(Environment.NewLine);
        //        nextLine = "";
        //    }

        //    sb.Append(nextLine);
        //    sb.Append(Environment.NewLine);

        //    TimeStepOpf opfPerTimeStep0 = OpfPerTimeStep[0];
        //    firstLine += "t";
        //    firstLine += separator;
        //    for (int t = 0; t < EnergyNet.StatesPerTimeStep.Count; t++)
        //    {
        //        firstLine += t.ToString(CultureInfo.InvariantCulture);
        //        firstLine += separator;
        //    }
        //    sb.Append(firstLine);
        //    sb.Append(Environment.NewLine);

        //    double zero = 0.0;
        //    foreach (Generator g in EnergyNet.NetworkData.Generators)
        //    {
        //        nextLine += "G" + g.Id + " (Bus " + g.Bus.ExtId + ")";
        //        nextLine += separator;

        //        foreach (int timeStep in OpfPerTimeStep.Keys)
        //        {
        //            TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];
        //            for (int i = 0; i < opfPerTimeStep.RealPowerGeneration.Count; i++)
        //            {
        //                Tuple<Generator, double> realPowerGenPerTimeStep = opfPerTimeStep.RealPowerGeneration.ElementAt(i);
        //                if (realPowerGenPerTimeStep.Item1.Id == g.Id)
        //                {
        //                    if ((realPowerGenPerTimeStep.Item2 > 0 && realPowerGenPerTimeStep.Item2 < 0.000001)
        //                       || (realPowerGenPerTimeStep.Item2 < 0 && realPowerGenPerTimeStep.Item2 > -0.000001))
        //                        nextLine += zero.ToString(CultureInfo.InvariantCulture);
        //                    else
        //                        nextLine += realPowerGenPerTimeStep.Item2.ToString(CultureInfo.InvariantCulture);
        //                    nextLine += separator;
        //                }
        //            }
        //        }

        //        sb.Append(nextLine);
        //        sb.Append(Environment.NewLine);
        //        nextLine = "";
        //    }

        //    double reserveSum = 0.0;
        //    foreach (Generator genEl in EnergyNet.NetworkData.Generators)
        //    {
        //        reserveSum += genEl.ReserveMaxLimit;
        //        reserveSum += genEl.ReserveCost;
        //    }
        //    int areGenReservesDefined = (reserveSum > 0) ? 1 : 0;
        //    if (areGenReservesDefined > 0)
        //    {
        //        foreach (Generator g in EnergyNet.NetworkData.Generators)
        //        {
        //            nextLine += "ReserveG" + g.Id;
        //            nextLine += separator;

        //            foreach (int timeStep in OpfPerTimeStep.Keys)
        //            {
        //                TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];
        //                for (int i = 0; i < opfPerTimeStep.RealPowerReserve.Count; i++)
        //                {
        //                    Tuple<Generator, double> realPowerResPerTimeStep =
        //                        opfPerTimeStep.RealPowerReserve.ElementAt(i);
        //                    if (realPowerResPerTimeStep.Item1.Id == g.Id)
        //                    {
        //                        if ((realPowerResPerTimeStep.Item2 > 0 && realPowerResPerTimeStep.Item2 < 0.000001)
        //                            || (realPowerResPerTimeStep.Item2 < 0 && realPowerResPerTimeStep.Item2 > -0.000001))
        //                            nextLine += zero.ToString(CultureInfo.InvariantCulture);
        //                        else
        //                            nextLine += realPowerResPerTimeStep.Item2.ToString(CultureInfo.InvariantCulture);
        //                        nextLine += separator;
        //                    }
        //                }
        //            }

        //            sb.Append(nextLine);
        //            sb.Append(Environment.NewLine);
        //            nextLine = "";
        //        }
        //    }

        //    foreach (EnergyStorageSystem s in EnergyNet.NetworkData.EnergyStorageSystems)
        //    {
        //        nextLine += "ESS" + s.Id + " (Bus " + s.Bus.ExtId + ")";
        //        nextLine += separator;

        //        foreach (int timeStep in OpfPerTimeStep.Keys)
        //        {
        //            TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];

        //            for (int i = 0; i < opfPerTimeStep.RealPowerDispatch.Count; i++)
        //            {
        //                Tuple<EnergyStorageSystem, double> realPowerDispatchPerTimeStep = opfPerTimeStep.RealPowerDispatch.ElementAt(i);
        //                if (s.Id == realPowerDispatchPerTimeStep.Item1.Id)
        //                {
        //                    if ((realPowerDispatchPerTimeStep.Item2 > 0 && realPowerDispatchPerTimeStep.Item2 < 0.000001)
        //                        || (realPowerDispatchPerTimeStep.Item2 < 0 && realPowerDispatchPerTimeStep.Item2 > -0.000001))
        //                        nextLine += zero.ToString(CultureInfo.InvariantCulture);
        //                    else
        //                        nextLine += realPowerDispatchPerTimeStep.Item2.ToString(CultureInfo.InvariantCulture);
        //                    nextLine += separator;
        //                }
        //            }
        //        }

        //        sb.Append(nextLine);
        //        sb.Append(Environment.NewLine);
        //        nextLine = "";
        //    }

        //    nextLine += "ExtGrid";
        //    nextLine += separator;
        //    foreach (int timeStep in OpfPerTimeStep.Keys)
        //    {
        //        TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];

        //        nextLine += opfPerTimeStep.ExtGridImportExport.ToString(CultureInfo.InvariantCulture);
        //        nextLine += separator;
        //    }
        //    sb.Append(nextLine);
        //    sb.Append(Environment.NewLine);
        //    nextLine = "";
        //    sb.Append(Environment.NewLine);
        //    nextLine = "";

        //    nextLine += "TotalLoad";
        //    nextLine += separator;
        //    foreach (int timeStep in OpfPerTimeStep.Keys)
        //    {
        //        TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];

        //        double totalLoad = 0.0;
        //        IList<NetComponentState> list1 = EnergyNet.StatesPerTimeStep.First(x => x.Period == timeStep).StateList;
        //        foreach (NetComponentState ncState in list1)
        //        {
        //            if (ncState.NetComponent is Load)
        //                totalLoad += ncState.State;
        //        }
        //        nextLine += (- totalLoad).ToString(CultureInfo.InvariantCulture);
        //        nextLine += separator;
        //    }
        //    sb.Append(nextLine);
        //    sb.Append(Environment.NewLine);
        //    nextLine = "";

        //    nextLine += "TotalPVGen";
        //    nextLine += separator;
        //    foreach (int timeStep in OpfPerTimeStep.Keys)
        //    {
        //        TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];

        //        double totalPVGen = 0.0;
        //        IList<NetComponentState> list1 = EnergyNet.StatesPerTimeStep.First(x => x.Period == timeStep).StateList;
        //        foreach (NetComponentState ncState in list1)
        //        {
        //            if ((ncState.NetComponent is NonProgrammableGenerator) && (ncState.NetComponent as NonProgrammableGenerator).Type == NonProgrammableGeneratorType.Photovoltaic)
        //                totalPVGen += ncState.State;
        //        }
        //        nextLine += totalPVGen.ToString(CultureInfo.InvariantCulture);
        //        nextLine += separator;
        //    }
        //    sb.Append(nextLine);
        //    sb.Append(Environment.NewLine);

        //    string directoryName = "..\\..\\..\\..\\Resources\\Data\\";
        //    if (!string.IsNullOrEmpty(directoryName) && !Directory.Exists(directoryName))
        //        Directory.CreateDirectory(directoryName);

        //    using var sw = new StreamWriter(directoryName + "SolutionSummaryUCP.csv");
        //    sw.Write(sb.ToString());
        //}


        //public void WriteSolutionSummary()
        //{
        //    StringBuilder sb = new StringBuilder();
        //    string separator = ",";
        //    CultureInfo culture = CultureInfo.InvariantCulture;

        //    TimeStepOpf opfPerTimeStep0 = OpfPerTimeStep[0];
        //    string firstLine = "";
        //    firstLine += "t";
        //    firstLine += separator;
        //    int nbGen = opfPerTimeStep0.RealPowerGeneration.Count();
        //    for (int i = 0; i < nbGen-1; i++)
        //    {
        //        Tuple<Generator, double> gen = opfPerTimeStep0.RealPowerGeneration.ElementAt(i);
        //        firstLine += "G" + gen.Item1.Id.ToString(CultureInfo.InvariantCulture) + "(Bus" + gen.Item1.Bus.Id + ")";
        //        firstLine += separator;
        //    }
        //    Tuple<Generator, double> lastGen = opfPerTimeStep0.RealPowerGeneration.ElementAt(nbGen-1);
        //    firstLine += "G" + lastGen.Item1.Id.ToString(CultureInfo.InvariantCulture) + "(Bus" + lastGen.Item1.Bus.Id + ")";

        //    /*foreach (Tuple<Generator, double> gen in opfPerTimeStep0.RealPowerGeneration)
        //    {
        //        firstLine += "G" + gen.Item1.Id.ToString(CultureInfo.InvariantCulture) + "(Bus" + gen.Item1.Bus.Id + ")";
        //        firstLine += separator;
        //    }*/
        //    sb.Append(firstLine);
        //    sb.Append(Environment.NewLine);

        //    foreach (int timeStep in OpfPerTimeStep.Keys)
        //    {
        //        string line = "";
        //        line += timeStep.ToString();
        //        line += separator;
        //        TimeStepOpf opfPerTimeStep = OpfPerTimeStep[timeStep];
        //        for (int i = 0; i < opfPerTimeStep.RealPowerGeneration.Count - 1; i++)
        //        {
        //            Tuple<Generator, double> realPowerGenPerTimeStep = opfPerTimeStep.RealPowerGeneration.ElementAt(i);
        //            line += realPowerGenPerTimeStep.Item2.ToString(CultureInfo.InvariantCulture);
        //            line += separator;
        //        }
        //        Tuple<Generator, double> gen = opfPerTimeStep.RealPowerGeneration.ElementAt(opfPerTimeStep.RealPowerGeneration.Count - 1);
        //        line += gen.Item2.ToString(CultureInfo.InvariantCulture);
        //        sb.Append(line);
        //        sb.Append(Environment.NewLine);
        //    }


        //    string directoryName = "..\\..\\..\\..\\Resources\\Data\\";
        //    if (!string.IsNullOrEmpty(directoryName) && !Directory.Exists(directoryName))
        //        Directory.CreateDirectory(directoryName);

        //    using var sw = new StreamWriter(directoryName + "SolutionSummary.csv");
        //    sw.Write(sb.ToString());
        //}
    }
}
