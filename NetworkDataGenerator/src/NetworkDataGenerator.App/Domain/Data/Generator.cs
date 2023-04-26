namespace NetworkDataGenerator.App.Domain.Data
{
    public class Generator : INetComponent
    {
        public Bus Bus { get; }

        public int Id { get; }

        public bool IsProgrammable { get; }

        public GeneratorCost Cost { get; }

        public double RealPowerOutput { get; set; }             // generator data: Pg
        public double MaxRealPowerOutput { get; set; }          // generator data: Pmax
        public double MinRealPowerOutput { get; set; }          // generator data: Pmin
        public double BaseMVA { get; set; }                     // generator data: mBase

        public int MinUpTime { get; set; }       // multiple of time unit (e.g. MinUpTime = 3h when the time unit is 1h) 
        public int MinDownTime { get; set; }     // multiple of time unit (e.g. MinUpTime = 3h when the time unit is 1h) 
        public double RampUpRate { get; set; }   // same unit as for MaxRealPowerOutput
        public double RampDownRate { get; set; } // same unit as for MaxRealPowerOutput

        public double ReserveMaxLimit { get; set; }
        public double ReserveCost { get; set; }

        public Generator(Bus bus, int id, bool isProgrammable, GeneratorCost cost)
        {
            Bus = bus;
            Id = id;
            IsProgrammable = isProgrammable;
            Cost = cost;
        }

        public bool Equals(Generator nc)
        {
            var other = nc as Generator;
            if (other != null && Id == other.Id )
            {
                return true;
            }
            return false;
        }
    }

}
