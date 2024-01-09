using System.Text.Json.Serialization;

namespace UserInterface.Data
{
    public class ScenarioModelJson
    {
        public Scenario Scenario { get; set; }
    }

    public class Scenario
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public string Version { get; set; }
        public Consumer[] Consumers { get; set; }
        public Generator[] Generators { get; set; }
        public Storage[] Storages { get; set; }
        public Network Network { get; set; }
    }

    public class Consumer
    {
        public string Name { get; set; }
        public string Identifier { get; set; }
        public float Latitude { get; set; }
        public float Longitude { get; set; }
        public string Address { get; set; }
        public int Level { get; set; }
        public string Category { get; set; }
        public string Type { get; set; }
        public string ProfileIdentifier { get; set; }
        public bool InService { get; set; }
    }

    public class Generator
    {
        public string Name { get; set; }
        public string Identifier { get; set; }
        public float Latitude { get; set; }
        public float Longitude { get; set; }
        public string Address { get; set; }
        public int Level { get; set; }
        public string Category { get; set; }
        public string Type { get; set; }
        public string ProfileIdentifier { get; set; }
        public bool InService { get; set; }
    }

    public class Storage
    {
        public string Name { get; set; }
        public string Identifier { get; set; }
        public float Latitude { get; set; }
        public float Longitude { get; set; }
        public string Address { get; set; }
        public int Level { get; set; }
        public string Category { get; set; }
        public string Type { get; set; }
        public double MinimumCapacity { get; set; }
        public double MaximumCapacity { get; set; }
        public string CapacityUnit { get; set; }
        public double MinimumActivePower { get; set; }
        public double MaximumActivePower { get; set; }
        public double MinimumReactivePower { get; set; }
        public double MaximumReactivePower { get; set; }
        public double CurrentActivePower { get; set; }
        public double StateOfCharge { get; set; }
        public bool InService { get; set; }
    }

    public class Network
    {
        public Entity[] Entities { get; set; }
        public Bus[] Buses { get; set; }
        public Line[] Lines { get; set; }
    }

    public class Entity
    {
        public string Name { get; set; }
        public string Identifier { get; set; }
        public float Latitude { get; set; }
        public float Longitude { get; set; }
        public string Address { get; set; }
        public string Category { get; set; }
        public string Type { get; set; }
        public string NetworkEntity { get; set; }
    }

    public class Bus
    {
        public string Identifier { get; set; }
        public float Voltage { get; set; }
        public string Category { get; set; }
        public string Type { get; set; }

    }

    public class Line
    {
        public string FromBus { get; set; }
        public string ToBus { get; set; }
        public string StdType { get; set; }
        public double LengthKm { get; set; }
    }

    public class StorageModelState
    {
        public string Identifier { get; set; }
        public double StateOfCharge { get; set; }
    }

    public class StorageModelStateCollection
    {
        public StorageModelState[] Storages { get; set; }
    }
}
