using System;
using System.Collections.Generic;

namespace NetworkDataGenerator.App.Domain.Data
{
    public class NetworkData
    {
        public double BaseMVA { get; set; }
        public IList<Bus> Buses { get; set; }
        public IList<Generator> Generators { get; set; }
        public IList<Load> Loads { get; set; }
        public IList<Branch> Branches { get; set; }
        public IList<EnergyStorageSystem> EnergyStorageSystems { get; set; }
        public IDictionary<int, double> MarketPrice { get; set; }
        public IList<NonProgrammableGenerator> NonProgrammableGenerators { get; set; }
        public IList<Tuple<int, int>> PairsBusesInBranches { get; set; }
        public IDictionary<Tuple<int, int>, Branch> PairBusesInBranchesToBranch { get; set; }
        public double SeamlessIndex { get; set; }
        public double ReserveFactor { get; set; }
    }
}
