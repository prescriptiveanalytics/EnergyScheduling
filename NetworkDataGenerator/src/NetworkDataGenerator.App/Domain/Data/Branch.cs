namespace NetworkDataGenerator.App.Domain.Data
{
    public class Branch
    {
        // %	fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax
        public int Id { get; }

        public int FromBusNumber { get; set; }      // branch data: fbus
        public int ToBusNumber { get; set; }        // branch data: tbus
        public double Susceptance { get; set; }     // calculated: 1 / (branch data: x)
        public double RateA { get; set; }           // branch data: rateA
        public double Ratio { get; set; }           // ratio, transformer off nominal turns ratio ( = 0 for lines, > 0 for transformer)

        public Branch(int id)
        {
            Id = id;
        }
    }
}
