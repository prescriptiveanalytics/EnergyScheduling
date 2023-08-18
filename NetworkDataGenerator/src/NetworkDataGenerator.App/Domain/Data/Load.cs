namespace NetworkDataGenerator.App.Domain.Data
{
    public class Load : INetComponent
    {
        public Bus Bus { get; }

        public double RealPowerDemand { get; set; }         // bus data: Pd

        public Load(Bus bus, int id)
        {
            Bus = bus;
            Id = id;
        }

        public int Id { get; }
    }
}
