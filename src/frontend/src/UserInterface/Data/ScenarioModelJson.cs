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
        [JsonPropertyName("profile_identifier")]
        public string ProfileIdentifier { get; set; }
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
        [JsonPropertyName("profile_identifier")]
        public string ProfileIdentifier { get; set; }
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
        [JsonPropertyName("network_entity")]
        public string NetworkEntity { get; set; }
    }

    public class Bus
    {
        public string Identifier { get; set; }
        public float Voltage { get; set; }
        public string Category  { get; set; }
        public string Type { get;set; }

    }

    public class Line
    {
        [JsonPropertyName("from_bus")]
        public string FromBus { get; set; }
        [JsonPropertyName("to_bus")]
        public string ToBus { get; set; }
        [JsonPropertyName("std_type")]
        public string StdType { get; set; }
        [JsonPropertyName("length_km")]
        public float LengthKm { get; set; }
    }
}
