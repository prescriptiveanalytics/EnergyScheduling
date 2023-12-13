using System.Formats.Asn1;
using System.Text.Json.Serialization;
using System.Text.Json;
using YamlDotNet.Core.Tokens;

namespace UserInterface.Data
{
    public class EneryMessage<T>
    {
        public string ScenarioIdentifier { get; set; }
        public T Payload { get; set; }
    }

    // https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/converters-how-to?pivots=dotnet-7-0
    //class EnergyMessageConverter<V> : JsonConverterFactory
    //{
    //    public EnergyMessageConverter(string keyPropertyName, string valuePropertyName)
    //    {
    //        KeyPropertyName = keyPropertyName;
    //        ValuePropertyName = valuePropertyName;
    //    }

    //    public override bool CanConvert(Type objectType)
    //        {
    //        return typeof(EnergyMessage<K, V>).IsAssignableFrom(objectType);
    //    }

    //    public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
    //    {
    //        IDictionary<K, V> dict = (IDictionary<K, V>)value;
    //            JArray array = new JArray();
    //        foreach (var kvp in dict)
    //        {
    //                JObject obj = new JObject();
    //            obj.Add(KeyPropertyName, JToken.FromObject(kvp.Key, serializer));
    //            obj.Add(ValuePropertyName, JToken.FromObject(kvp.Value, serializer));
    //            array.Add(obj);
    //            }
    //            array.WriteTo(writer);
    //    }
    //    public override bool CanRead
    //    {
    //        get { return false; }
    //    }

    //    public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
    //    {
    //        throw new NotImplementedException();
    //    }

    //    public override JsonConverter? CreateConverter(Type typeToConvert, JsonSerializerOptions options)
    //    {
    //        throw new NotImplementedException();
    //    }
    //}
}
