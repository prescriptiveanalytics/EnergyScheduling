using System.Text.Json;
using UserInterface.Data;

namespace Unittest
{
    public class UnitTest
    {
        [Fact]
        public void TestJsonConfigParsing()
        {
            string text = File.ReadAllText("./Resources/ExampleConfig.json");
            try {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true,
                    
                };
                ScenarioModelJson? model = JsonSerializer.Deserialize<ScenarioModelJson>(text, options);
            } catch (Exception ex) 
            {
                Console.WriteLine(ex.ToString());
            }
        }
    }
}