using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using NetworkDataGenerator.App.Domain;
using NetworkDataGenerator.App.Domain.Data;

namespace NetworkDataGenerator.App
{
    public class PowerGridProblem
    {
        private CaseProblemData _problemData;
        private NetworkData _networkData;

        public CaseProblemData ProblemData { get => _problemData; set => _problemData = value; }
        public NetworkData NetworkData { get => _networkData; set => _networkData = value; }

        public PowerGridProblem(StreamReader reader)
        {
            MatCaseDataReader caseImport = new MatCaseDataReader(reader, null, null, null, null);
            ProblemData = caseImport.ProblemData;
            CalculateProblemData();
        }

        private NetworkData CalculateProblemData()
        {
            IList<Bus> buses = InitBuses();
            IList<Generator> generators = InitGenerators(buses);
            IList<Load> loads = InitLoads(buses);
            IList<Branch> branches = InitBranches(buses);

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
                BaseMVA = ProblemData.BaseMVA,
                Buses = buses,
                Generators = generators,
                Loads = loads,
                Branches = branches,
                PairsBusesInBranches = pairsBusesInBranches,
                PairBusesInBranchesToBranch = pairsBusesInBranchesToBranch,
            };

            // powerDemandsInit contains the values for real power demand as they are defined in the original case file
            IList<double> powerDemandsInit = new List<double>();
            foreach (var load in netData.Loads)
            {
                powerDemandsInit.Add(load.RealPowerDemand);
            }

            NetworkData = netData;
            return NetworkData;
        }

        private IList<Bus> InitBuses()
        {
            IList<Bus> buses = new List<Bus>();
            int internalId = 1;
            foreach (var busEntry in ProblemData.Bus)
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

            foreach (var genEntry in ProblemData.GenCost)
            {
                GeneratorCost gencost = new GeneratorCost()
                {
                    // CostModelType = genEntry[0],
                    StartupCost = genEntry[1],
                    ShutdownCost = genEntry[2],
                    // NumberCoefficients = genEntry[3],
                    C1 = genEntry[4], // * _deltaTime,
                    C0 = genEntry[5], // * _deltaTime
                };
                generatorCosts.Add(gencost);
            }

            return generatorCosts;
        }

        private IList<Tuple<int, int>> InitGeneratorMinUpDownTimes()
        {
            IList<Tuple<int, int>> generatorMinUpDownTime = new List<Tuple<int, int>>();

            foreach (var genEntry in ProblemData.GenAuxiliaryData)
            {
                int genMinUpTime = (int)(genEntry[0]/* / _deltaTime*/);
                int genMinDownTime = (int)(genEntry[1]/* / _deltaTime*/);
                generatorMinUpDownTime.Add(new Tuple<int, int>(genMinUpTime, genMinDownTime));
            }

            return generatorMinUpDownTime;
        }

        private IList<Tuple<double, double>> InitGeneratorReserveCostAndMaxLimits()
        {
            IList<Tuple<double, double>> generatorReserveCostAndMaxLimit = new List<Tuple<double, double>>();

            foreach (var genEntry in ProblemData.GenAuxiliaryData)
            {
                double genReserveCost = genEntry[2]/* * _deltaTime*/;
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
            foreach (var genEntry in ProblemData.Gen)
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
                        RampUpRate = genEntry[18] != 0 ? (genEntry[18]/* * _deltaTime*/) : genEntry[8], // https://www.mail-archive.com/matpower-l@cornell.edu/msg05398.html
                        RampDownRate = genEntry[18] != 0 ? (genEntry[18]/* * _deltaTime*/) : genEntry[8], // not necessarily equal to RampUpRate
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
            foreach (var busEntry in ProblemData.Bus)
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
            foreach (var branchEntry in ProblemData.Branch)
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
    }
}
