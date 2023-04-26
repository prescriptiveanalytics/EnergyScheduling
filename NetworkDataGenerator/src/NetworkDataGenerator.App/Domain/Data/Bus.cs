using System.Collections.Generic;

namespace NetworkDataGenerator.App.Domain.Data
{
    public enum BusType
    {
        LoadBus = 1,        // A bus without any generators connected to it is called a Load Bus.
        GeneratorBus = 2,   // A bus with at least one generator connected to it is called a Generator Bus (with one exception).
        SlackBus = 3        // The exception is the Slack Bus: one arbitrarily-selected bus that has a generator and is used to provide for system losses by emitting or absorbing active and/or reactive power to and from the system.
    }

    public class Bus
    {
        public int Id { get; }                       // internal indexing so that the buses are numbered consecutively
        public int ExtId { get; }                    // bus data: the index of the bus in the case file; this external indexing is not always numbered consecutively  
        public BusType Type { get; }                 // bus data: type

        public IList<Generator> Generators { get; }
        public IList<Load> Loads { get; }

        public Bus(int id, int externalId, int type)
        {
            Id = id;
            ExtId = externalId;
            Type = (BusType)type;

            Generators = new List<Generator>();
            Loads = new List<Load>();
        }

    }
}
