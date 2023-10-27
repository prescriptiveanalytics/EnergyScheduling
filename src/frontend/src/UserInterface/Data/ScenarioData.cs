namespace UserInterface.Data
{
    public class ScenarioData
    {
        public IDictionary<string, ScenarioModelJson> ConfigJsonData { get; set; }
      
        public IDictionary<string, byte[]> Models { get; set; }
    }
}
