using YamlDotNet.Serialization;

namespace Build.Extensions;

public static class Yaml
{
  public static readonly ISerializer Serializer = new SerializerBuilder()
    .ConfigureDefaultValuesHandling(DefaultValuesHandling.OmitNull)
    .Build();

  public static void Save<T>(T value, FilePath file) where T : class
  {
    var str = Serializer.Serialize(value);

    File.WriteAllText(file.FullPath, str);
  }
}