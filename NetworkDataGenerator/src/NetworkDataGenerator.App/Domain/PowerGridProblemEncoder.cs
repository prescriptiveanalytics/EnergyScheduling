using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using NetworkDataGenerator.App.Domain.Data;

namespace NetworkDataGenerator.App.Domain
{
    public class PowerGridProblemEncoder /*: IEncoder*/
    {
        //private static readonly Logger Logger = LogManager.GetCurrentClassLogger();

        private CaseProblemData _problemData;
        private int _numberOfTimeSteps;
        private DecoderType _decoderType;
        private string _loadProfile;
        private string _pvProfile;
        private string _caseFileESS;
        private string _caseFilePV;
        private string _caseFileAux;
        private string _caseFileMarketPrice;
        private double _deltaTime;
        private double _seamlessIndex;
        private double _reserveFactor;
        private string _caseFile;

        /// <summary>
        /// Constructor for PowerProblemEncoder.
        /// </summary>
        /// <param name="reader">Stream containing the problem data.</param>
        /// <param name="args">Dictionary of string, string arguments necessary to initialize encoder with the following keys:
        ///     NumberOfTimeSteps
        ///     LengthOfTimeStepsInHours, e.g. 0.25 (for 15 minute time step length), 1 (for 1h time step length)
        ///     DecoderType:  "OrTools" or "Matpower" TODO
        ///     CaseFileAuxiliaryData -> min up time (h) & min down down (h) & reserve cost ($/MW h) & reserve max limit (MW)
        ///     LoadProfile TODO
        ///     CaseFileESS TODO
        ///     CaseFilePV  TODO
        ///     PVProfile   TODO
        /// </param>
        /// List of unit measures for the input data:
        /// Generator
        /// - Min/Max real power output (MW)
        /// - Startup Cost ($)
        /// - Shutdown Cost ($)
        /// - Generating cost ($/MW h)
        /// - Min up/down time (h)
        /// - Ramp up/down rate (MW/h)
        /// - Reserve cost ($/MW h)
        /// - Max reserve limit (MW)
        /// Load
        /// - Real power demand (MW)
        /// Energy Storage Systems
        /// - Capacity (MW h)
        /// - Min/Max charging/discharging power (MW)
        /// - Min charging/discharging time (h)
        /// PV
        /// - Installed capacity (MW)
        public PowerGridProblemEncoder(StreamReader reader, IDictionary<string, string> args)
        {
            if (args.Count != 11)
                throw new EncoderException($"Could not instantiate {GetType().Name}: Wrong number of arguments.");

            _caseFile = (reader.BaseStream as FileStream)?.Name;

            string numberOfTimeStepsString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "NumberOfTimeSteps");
            if (string.IsNullOrEmpty(numberOfTimeStepsString))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not find encoder parameter NumberOfTimeSteps.");
            }
            if (!int.TryParse(numberOfTimeStepsString, out _numberOfTimeSteps))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not parse encoder parameter NumberOfTimeSteps.");
            }

            string timeResolutionInHoursString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "TimeResolutionInHours");
            if (string.IsNullOrEmpty(timeResolutionInHoursString))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not find encoder parameter TimeResolutionInHours.");
            }
            if (!double.TryParse(timeResolutionInHoursString, NumberStyles.Number, CultureInfo.InvariantCulture, out _deltaTime))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not parse encoder parameter TimeResolutionInHours.");
            }

            string decoderTypeString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "DecoderType");
            if (string.IsNullOrEmpty(decoderTypeString))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not find encoder parameter DecoderType.");
            }
            if (!Enum.TryParse(decoderTypeString, out _decoderType))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not parse encoder parameter DecoderType.");
            }

            string loadProfileString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "LoadProfile");
            if (string.IsNullOrEmpty(loadProfileString))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not find encoder parameter LoadProfile.");
            }
            _loadProfile = loadProfileString;

            string caseFileAuxString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "CaseFileAuxiliaryData");
            _caseFileAux = caseFileAuxString;

            string caseFileEssString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "CaseFileESS");
            _caseFileESS = caseFileEssString;

            string caseFileMarketPriceString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "CaseFileMarketPrice");
            _caseFileMarketPrice = caseFileMarketPriceString;

            string caseFilePvString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "CaseFilePV");
            _caseFilePV = caseFilePvString;

            string pvProfileString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "PVProfile");
            if (!string.IsNullOrEmpty(_caseFilePV) && string.IsNullOrEmpty(pvProfileString))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not find encoder parameter PVProfile, while encoder parameter CaseFilePV is defined.");
            }
            _pvProfile = pvProfileString;

            string seamlessIndexString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "SeamlessIndex");
            if (string.IsNullOrEmpty(seamlessIndexString))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not find encoder parameter SeamlessIndex.");
            }
            if (!double.TryParse(seamlessIndexString, NumberStyles.Number, CultureInfo.InvariantCulture, out _seamlessIndex))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not parse encoder parameter SeamlessIndex.");
            }

            string reserveFactorString = ReflectionUtil.GetDictionaryValueCaseInsensitive(args, "ReserveFactor");
            if (string.IsNullOrEmpty(reserveFactorString))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not find encoder parameter ReserveFactor.");
            }
            if (!double.TryParse(reserveFactorString, NumberStyles.Number, CultureInfo.InvariantCulture, out _reserveFactor))
            {
                throw new EncoderException($"Could not instantiate {GetType().Name}: Could not parse encoder parameter ReserveFactor.");
            }


            StreamReader readerAux1 = (!string.IsNullOrEmpty(_caseFileAux)) ? new StreamReader(_caseFileAux) : null;
            StreamReader readerAux2 = (!string.IsNullOrEmpty(_caseFileESS)) ? new StreamReader(_caseFileESS) : null;
            StreamReader readerAux3 = (!string.IsNullOrEmpty(_caseFileMarketPrice)) ? new StreamReader(_caseFileMarketPrice) : null;
            StreamReader readerAux4 = (!string.IsNullOrEmpty(_caseFilePV)) ? new StreamReader(_caseFilePV) : null;
            MatCaseDataReader caseImport = new MatCaseDataReader(reader, readerAux1, readerAux2, readerAux3, readerAux4);
            _problemData = caseImport.ProblemData;
            reader.Close();
        }

        public EnergyNetEncoding GenerateEncodedSolution()
        {
            return CalculateProblemData();
        }

        public MatpowerOpfDecoder GetSolutionDecoder(MatpowerDecoderConfigurationContext configContext)
        {
            if (_decoderType == DecoderType.Matpower)
            {
                if (configContext is MatpowerDecoderConfigurationContext opfConfigContext)
                {
                    MatCaseDataWriter writer = new MatCaseDataWriter(_problemData);
                    opfConfigContext.ImportCaseFile = (reader, readerAux1, readerAux2, readerAux3, readerAux4) =>
                    {
                        MatCaseDataReader caseImport = new MatCaseDataReader(reader, readerAux1, readerAux2, readerAux3, readerAux4);
                        CaseProblemData problemData = caseImport.ProblemData;
                        reader.Close();
                        return problemData;
                    };
                    opfConfigContext.ExportCaseFile = (encodedItem, filepath) =>
                    {
                        writer.WriteSolution(encodedItem, filepath);
                    };

                    MatpowerOpfDecoder decoder = new MatpowerOpfDecoder(opfConfigContext);
                    return decoder;
                }
            }
            //else if (_decoderType == DecoderType.OrTools)
            //{
            //    if (configContext is IOrToolsDecoderConfigurationContext opfConfigContext)
            //    {
            //        ISolutionDecoder decoder = new OrToolsOpfDecoder(opfConfigContext);
            //        return decoder;
            //    }
            //}

            throw new EncoderException("Attempt to initialize SolutionDecoder with configuration context failed.");
        }

        public MatCaseDataWriter GetDataWriter()
        {
            return new MatCaseDataWriter(_problemData);
        }

        public DecoderType DecoderType => _decoderType;

        //private bool CheckValidity(NetworkData netData)
        //{
        //    double reserveDataSum = 0.0;
        //    foreach (Generator genEl in netData.Generators)
        //    {
        //        reserveDataSum += genEl.ReserveMaxLimit;
        //        reserveDataSum += genEl.ReserveCost;
        //    }
        //    if (netData.ReserveFactor > 0 && reserveDataSum == 0)
        //    {
        //        Logger.Error("Inconsistencies in the input data: the reserve factor RF > 0 and no reserve data defined for the generators!");
        //        return false;
        //    }

        //    return true;
        //}

        private EnergyNetEncoding CalculateProblemData()
        {
            IList<Bus> buses = InitBuses();
            IList<Generator> generators = InitGenerators(buses);
            IList<Load> loads = InitLoads(buses);
            IList<Branch> branches = InitBranches(buses);
            IList<EnergyStorageSystem> energyStorageSystems = InitEnergyStorageSystems(buses);
            IDictionary<int, double> marketPrice = InitMarketPrice();
            IList<NonProgrammableGenerator> nonProgrammableGenerators = InitNonProgrammableGenerators(buses);

            IList<Tuple<int, int>> pairsBusesInBranches = new List<Tuple<int, int>>();
            IDictionary<Tuple<int, int>, Branch> pairsBusesInBranchesToBranch = new Dictionary<Tuple<int, int>, Branch>();
            foreach (Branch b in branches)
            {
                Tuple<int, int> pair1 = new Tuple<int, int>(b.FromBusNumber - 1, b.ToBusNumber - 1);
                Tuple<int, int> pair2 = new Tuple<int, int>(b.ToBusNumber - 1, b.FromBusNumber - 1);
                pairsBusesInBranches.Add(pair1);
                pairsBusesInBranches.Add(pair2);
                pairsBusesInBranchesToBranch[pair1] = b;
                pairsBusesInBranchesToBranch[pair2] = b;
            }

            NetworkData netData = new NetworkData()
            {
                BaseMVA = _problemData.BaseMVA,
                Buses = buses,
                Generators = generators,
                Loads = loads,
                Branches = branches,
                EnergyStorageSystems = energyStorageSystems,
                MarketPrice = marketPrice,
                NonProgrammableGenerators = nonProgrammableGenerators,
                PairsBusesInBranches = pairsBusesInBranches,
                PairBusesInBranchesToBranch = pairsBusesInBranchesToBranch,
                SeamlessIndex = _seamlessIndex,
                ReserveFactor = _reserveFactor
            };

            //bool isNetDataValid = CheckValidity(netData);
            //if (!isNetDataValid)
            //    return null;

            IList<TimeStepStates> statesPerTimeStep = new List<TimeStepStates>();
            //Random rnd = new Random(0);

            // powerDemandsInit contains the values for real power demand as they are defined in the original case file
            IList<double> powerDemandsInit = new List<double>();
            foreach (var load in netData.Loads)
            {
                powerDemandsInit.Add(load.RealPowerDemand);
            }


            // factors are from a load profile 
            List<double> factors = new List<double>();
            using (var reader = new StreamReader(_loadProfile))
            {
                var firstLine = reader.ReadLine();
                var secondLine = reader.ReadLine();
                while (!reader.EndOfStream)
                {
                    var line = reader.ReadLine();
                    string[] values = line.Split(',');
                    string valueFactor = values[values.Count() - 1];
                    bool success = double.TryParse(valueFactor, NumberStyles.Any, CultureInfo.InvariantCulture, out double val);
                    if (success) factors.Add(val);
                }
            }
            IList<double> powerDemands = new List<double>();
            for (int i = 0; i < factors.Count; i++)
            {
                for (int j = 0; j < powerDemandsInit.Count; j++)
                {
                    powerDemands.Add(factors[i] * powerDemandsInit[j]);
                }
            }

            IList<double> pvGeneration = new List<double>();
            if (nonProgrammableGenerators != null && nonProgrammableGenerators.Count > 0)
            {
                // pv generation => installed capacity with pv generation factors
                IList<double> pvCapacities = new List<double>();
                foreach (var pv in nonProgrammableGenerators)
                {
                    pvCapacities.Add(pv.Capacity);
                }

                IList<double> pvFactors = new List<double>();
                using (var reader = new StreamReader(_pvProfile))
                {
                    var firstLine = reader.ReadLine();
                    var secondLine = reader.ReadLine();
                    while (!reader.EndOfStream)
                    {
                        var line = reader.ReadLine();
                        string[] values = line.Split(',');
                        string valueFactor = values[values.Count() - 1];
                        bool success = double.TryParse(valueFactor, NumberStyles.Any, CultureInfo.InvariantCulture,
                            out double val);
                        if (success) pvFactors.Add(val);
                    }
                }

                for (int i = 0; i < pvFactors.Count; i++)
                {
                    for (int j = 0; j < pvCapacities.Count; j++)
                    {
                        //pvGeneration.Add(pvFactors[i] * pvCapacities[j]);
                        decimal d = (decimal)pvFactors[i] * (decimal)pvCapacities[j];
                        pvGeneration.Add((double)d);
                    }
                }
            }


            int p = 0;
            int q = 0;
            for (int i = 0; i < _numberOfTimeSteps; ++i)
            {
                // add state for each schedulable network component
                IList<NetComponentState> stateList = new List<NetComponentState>();
                foreach (var gen in generators)
                {
                    // initialize each programmable generator as active at each time step, with valid states being 0 and 1
                    if (gen.IsProgrammable)
                    {
                        stateList.Add(new NetComponentState(gen, i, Tuple.Create(0.0, 1.0)) { State = 1 });
                    }
                }

                foreach (var load in loads)
                {
                    //int realPowerDemand = rnd.Next(50, 300);
                    double realPowerDemand = powerDemands[p++];
                    stateList.Add(new NetComponentState(load, i, Tuple.Create(realPowerDemand, realPowerDemand)) { State = realPowerDemand });
                }

                foreach (var ess in energyStorageSystems)
                {
                    stateList.Add(new NetComponentState(ess, i, Tuple.Create(-1.0, 1.0)) { State = (double)EnergyStorageSystemState.Idle });

                }

                foreach (var npg in nonProgrammableGenerators)
                {
                    double pvPowerGeneration = pvGeneration[q++];
                    stateList.Add(new NetComponentState(npg, i, Tuple.Create(pvPowerGeneration, pvPowerGeneration)) { State = pvPowerGeneration });
                }


                // add time step with component state information to list
                TimeStepStates timeStep = new TimeStepStates(i, stateList);
                statesPerTimeStep.Add(timeStep);
            }

            EnergyNetEncoding ene = new EnergyNetEncoding(statesPerTimeStep, netData);
            return ene;
        }

        private IList<Bus> InitBuses()
        {
            IList<Bus> buses = new List<Bus>();
            int internalId = 1;
            foreach (var busEntry in _problemData.Bus)
            {
                Bus bus = new Bus(internalId, (int)busEntry[0], (int)busEntry[1]);
                buses.Add(bus);
                internalId++;
            }

            return buses;
        }

        private IList<GeneratorCost> InitGeneratorCosts()
        {
            IList<GeneratorCost> generatorCosts = new List<GeneratorCost>();

            foreach (var genEntry in _problemData.GenCost)
            {
                GeneratorCost gencost = new GeneratorCost()
                {
                    // CostModelType = genEntry[0],
                    StartupCost = genEntry[1],
                    ShutdownCost = genEntry[2],
                    // NumberCoefficients = genEntry[3],
                    C1 = genEntry[4] * _deltaTime,
                    C0 = genEntry[5] * _deltaTime
                };
                generatorCosts.Add(gencost);
            }

            return generatorCosts;
        }

        private IList<Tuple<int, int>> InitGeneratorMinUpDownTimes()
        {
            IList<Tuple<int, int>> generatorMinUpDownTime = new List<Tuple<int, int>>();

            foreach (var genEntry in _problemData.GenAuxiliaryData)
            {
                int genMinUpTime = (int)(genEntry[0] / _deltaTime);
                int genMinDownTime = (int)(genEntry[1] / _deltaTime);
                generatorMinUpDownTime.Add(new Tuple<int, int>(genMinUpTime, genMinDownTime));
            }

            return generatorMinUpDownTime;
        }

        private IList<Tuple<double, double>> InitGeneratorReserveCostAndMaxLimits()
        {
            IList<Tuple<double, double>> generatorReserveCostAndMaxLimit = new List<Tuple<double, double>>();

            foreach (var genEntry in _problemData.GenAuxiliaryData)
            {
                double genReserveCost = genEntry[2] * _deltaTime;
                double genReserveMaxLimit = genEntry[3];
                generatorReserveCostAndMaxLimit.Add(new Tuple<double, double>(genReserveCost, genReserveMaxLimit));
            }

            return generatorReserveCostAndMaxLimit;
        }

        private IList<Generator> InitGenerators(IList<Bus> buses)
        {
            IList<Generator> generators = new List<Generator>();
            IDictionary<int, Bus> idToBus = buses.ToDictionary(x => x.Id, x => x);
            IList<GeneratorCost> generatorCosts = InitGeneratorCosts();
            IList<Tuple<int, int>> generatorMinUpDownTimes = InitGeneratorMinUpDownTimes();
            IList<Tuple<double, double>> generatorReserveCostAndMaxLimits = InitGeneratorReserveCostAndMaxLimits();

            int genUnitId = 0;
            foreach (var genEntry in _problemData.Gen)
            {
                int busId = buses.First(x => x.ExtId == (int)genEntry[0]).Id;
                if (idToBus.ContainsKey(busId))
                {
                    Bus bus = idToBus[busId];
                    GeneratorCost genCost = generatorCosts[genUnitId];
                    Tuple<int, int> genMinUpDownTime = (generatorMinUpDownTimes.Count > 0) ? generatorMinUpDownTimes.ElementAt(genUnitId) : new Tuple<int, int>(1, 1);
                    Tuple<double, double> genReserveCostAndMaxLimit = (generatorReserveCostAndMaxLimits.Count > 0) ? generatorReserveCostAndMaxLimits.ElementAt(genUnitId) : new Tuple<double, double>(0.0, 0.0);
                    Generator generator = new Generator(bus, ++genUnitId, true, genCost)
                    {
                        RealPowerOutput = genEntry[1],
                        MaxRealPowerOutput = genEntry[8],
                        MinRealPowerOutput = genEntry[9],
                        BaseMVA = genEntry[6],
                        MinUpTime = genMinUpDownTime.Item1,
                        MinDownTime = genMinUpDownTime.Item2, // not necessarily equal to MinUpTime
                        RampUpRate = genEntry[18] != 0 ? (genEntry[18] * _deltaTime) : genEntry[8], // https://www.mail-archive.com/matpower-l@cornell.edu/msg05398.html
                        RampDownRate = genEntry[18] != 0 ? (genEntry[18] * _deltaTime) : genEntry[8], // not necessarily equal to RampUpRate
                        ReserveCost = genReserveCostAndMaxLimit.Item1,
                        ReserveMaxLimit = genReserveCostAndMaxLimit.Item2
                    };
                    generators.Add(generator);
                    bus.Generators.Add(generator);
                }
            }

            return generators;
        }

        private IList<Load> InitLoads(IList<Bus> buses)
        {
            IList<Load> loads = new List<Load>();
            IDictionary<int, Bus> idToBus = buses.ToDictionary(x => x.Id, x => x);

            int loadId = 1;
            foreach (var busEntry in _problemData.Bus)
            {
                int busId = buses.First(x => x.ExtId == (int)busEntry[0]).Id;
                if (idToBus.ContainsKey(busId))
                {
                    // according to Matpower, a bus entry is interpreted as a load if Pd != 0 or Qd != 0
                    if (busEntry[2] != 0 || busEntry[3] != 0)
                    {
                        Bus bus = idToBus[busId];
                        Load load = new Load(bus, loadId++)
                        {
                            RealPowerDemand = busEntry[2]
                        };
                        loads.Add(load);
                        bus.Loads.Add(load);
                    }
                }
            }

            return loads;
        }

        private IList<Branch> InitBranches(IList<Bus> buses)
        {
            IList<Branch> branches = new List<Branch>();

            int branchId = 1;
            foreach (var branchEntry in _problemData.Branch)
            {
                Branch branch = new Branch(branchId++)
                {
                    FromBusNumber = buses.First(x => x.ExtId == (int)branchEntry[0]).Id,
                    ToBusNumber = buses.First(x => x.ExtId == (int)branchEntry[1]).Id,
                    Susceptance = 1 / branchEntry[3],
                    RateA = (branchEntry[5] != 0) ? branchEntry[5] : 9900,
                    Ratio = branchEntry[8]
                };
                branches.Add(branch);
            }

            return branches;
        }

        private IList<EnergyStorageSystem> InitEnergyStorageSystems(IList<Bus> buses)
        {
            IDictionary<int, Bus> idToBus = buses.ToDictionary(x => x.Id, x => x);

            IList<EnergyStorageSystem> energyStorageSystems = new List<EnergyStorageSystem>();
            int id = 1;
            foreach (var essEntry in _problemData.EnergyStorageSystem)
            {
                int busId = (int)buses.First(x => x.ExtId == (int)essEntry[0]).Id;
                if (idToBus.ContainsKey(busId))
                {
                    Bus bus = idToBus[busId];
                    EnergyStorageSystem ess = new EnergyStorageSystem(bus, id++)
                    {
                        Capacity = (double)(essEntry[1] / _deltaTime),
                        MinChargingPower = (double)essEntry[2],
                        MaxChargingPower = (double)essEntry[3],
                        MinDischargingPower = (double)essEntry[4],
                        MaxDischargingPower = (double)essEntry[5],
                        MinChargingTime = (int)(essEntry[6] / _deltaTime),
                        MinDischargingTime = (int)(essEntry[7] / _deltaTime),
                        ChargingEfficiencyFactor = (double)essEntry[8],
                        DischargingEfficiencyFactor = (double)essEntry[9],
                        InitialSOC = (double)essEntry[10]
                    };

                    energyStorageSystems.Add(ess);
                }
            }
            return energyStorageSystems;
        }

        private IDictionary<int, double> InitMarketPrice()
        {
            IDictionary<int, double> marketPrice = new Dictionary<int, double>();
            foreach (var priceEntry in _problemData.MarketPrice)
            {
                int timeUnitEntry = (int)priceEntry[0];
                int timeUnit = (int)(timeUnitEntry / _deltaTime);
                double price = (double)(priceEntry[1] * _deltaTime);
                marketPrice.Add(timeUnit, price);

                int nb = (int)(1 / _deltaTime);
                if (nb > 1)
                {
                    for (int i = 1; i <= nb - 1; i++)
                    {
                        marketPrice.Add(timeUnit + i, price);
                    }
                }
            }
            return marketPrice;
        }

        private IList<NonProgrammableGenerator> InitNonProgrammableGenerators(IList<Bus> buses)
        {
            IDictionary<int, Bus> idToBus = buses.ToDictionary(x => x.Id, x => x);

            IList<NonProgrammableGenerator> nonProgrammableGenerators = new List<NonProgrammableGenerator>();
            int id = 1;
            foreach (var npgEntry in _problemData.NonProgrammableGenerator)
            {
                int busId = buses.First(x => x.ExtId == (int)npgEntry[0]).Id;
                if (idToBus.ContainsKey(busId))
                {
                    Bus bus = idToBus[busId];
                    NonProgrammableGenerator npg = new NonProgrammableGenerator(bus, id++)
                    {
                        Capacity = (double)npgEntry[1],
                        Type = NonProgrammableGeneratorType.Photovoltaic
                    };

                    nonProgrammableGenerators.Add(npg);
                }
            }
            return nonProgrammableGenerators;
        }

        public string GetOverviewInputData()
        {
            string s = "Overview input: ";
            s += Environment.NewLine;

            s += "NumberOfTimeSteps: ";
            s += _numberOfTimeSteps;
            s += Environment.NewLine;

            s += "TimeResolutionInHours: ";
            s += _deltaTime;
            s += Environment.NewLine;

            s += "CaseFile: ";
            s += _caseFile;
            s += Environment.NewLine;

            s += "LoadProfile: ";
            s += _loadProfile;
            s += Environment.NewLine;

            s += "CaseFileAuxiliaryData: ";
            s += _caseFileAux;
            s += Environment.NewLine;

            s += "CaseFileESS: ";
            s += _caseFileESS;
            s += Environment.NewLine;

            s += "CaseFileMarketPrice: ";
            s += _caseFileMarketPrice;
            s += Environment.NewLine;

            s += "CaseFilePV: ";
            s += _caseFilePV;
            s += Environment.NewLine;

            s += "PVProfile: ";
            s += _pvProfile;
            s += Environment.NewLine;

            s += "SeamlessIndex: ";
            s += _seamlessIndex;
            s += Environment.NewLine;

            s += "ReserveFactor: ";
            s += _reserveFactor;
            s += Environment.NewLine;

            return s;
        }
    }
}
