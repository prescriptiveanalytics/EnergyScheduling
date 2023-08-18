using System.Collections.Generic;

namespace NetworkDataGenerator.App.Domain
{
    public class CaseProblemData
    {
        public CaseProblemData()
        {
            Bus = new List<IList<double>>();
            Gen = new List<IList<double>>();
            Branch = new List<IList<double>>();
            GenCost = new List<IList<double>>();
            GenAuxiliaryData = new List<IList<double>>();
            EnergyStorageSystem = new List<IList<double>>();
            MarketPrice = new List<IList<double>>();
            NonProgrammableGenerator = new List<IList<double>>();
        }

        public double BaseMVA { get; set; }
        public IList<IList<double>> Bus { get; set; }
        public IList<IList<double>> Gen { get; set; }
        public IList<IList<double>> Branch { get; set; }
        public IList<IList<double>> GenCost { get; set; }
        public IList<IList<double>> GenAuxiliaryData { get; set; }
        public IList<IList<double>> EnergyStorageSystem { get; set; }
        public IList<IList<double>> MarketPrice { get; set; }
        public IList<IList<double>> NonProgrammableGenerator { get; set; }
        public double ObjVal { get; set; }
        public bool Converged { get; set; }
    }
}
