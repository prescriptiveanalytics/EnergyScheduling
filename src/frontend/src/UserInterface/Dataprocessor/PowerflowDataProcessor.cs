using Plotly.Blazor;
using UserInterface.Data;

namespace UserInterface.Dataprocessor
{
    public class PowerflowDataProcessor
    {
        // Scenario data, necessary to reconstruct all information
        private ScenarioModelJson _scenario;
        // Mapping of uuid to readable names
        private IDictionary<string, string> _uuidToName;


        public PowerflowDataProcessor(ScenarioModelJson scenario)
        {
            _scenario = scenario;
            _uuidToName = new Dictionary<string, string>();
            // map consumers
            foreach (var consumer in scenario.Scenario.Consumers)
            {
                _uuidToName.Add(consumer.Identifier, consumer.Name);
            }
            // map generators
            foreach (var generator in scenario.Scenario.Generators)
            {
                _uuidToName.Add(generator.Identifier, generator.Name);
            }
            // map network lines
            foreach (var networkEntity in scenario.Scenario.Network.Lines)
            {
                // what do we map?
            }
            // map external grid
            foreach (var externalGrid in scenario.Scenario.Network.Buses)
            {
                if (!_uuidToName.ContainsKey(externalGrid.Identifier))
                {
                    _uuidToName.Add(externalGrid.Identifier, externalGrid.Category);
                }
            }
        }

        /// <summary>
        /// Extracts solution information and returns it in table form.
        /// </summary>
        /// <param name="optimalPowerFlow"></param>
        /// <returns></returns>
        public PowerflowTableView GetPowerflowTableInfo(OptimalPowerFlow optimalPowerFlow)
        {
            PowerflowTableView powerflowTableView = new();
            IDictionary<string, string> idToUUid = new Dictionary<string, string>();
            powerflowTableView.Headings = new List<string>();
            powerflowTableView.Values = new List<IList<string>>();

            foreach (var entry in optimalPowerFlow.Bus.Name)
            {
                idToUUid.Add(entry.Key, entry.Value);
            }

            powerflowTableView.Headings.AddRange(new List<string>(){"Name", "Category", "Value"});
            
            foreach (var entry in optimalPowerFlow.ResBus.PMw)
            {
                powerflowTableView.Values.Add(new List<string>(){IdToName(entry.Key, idToUUid), "-", entry.Value.ToString()});
            }

            return powerflowTableView;
        }

        /// <summary>
        /// Extracts summary information: consumption, generation, grid import
        /// </summary>
        /// <param name="optimalPowerFlow"></param>
        /// <returns></returns>
        public PowerflowTableView GetPowerflowSummaryTableInfo(OptimalPowerFlow optimalPowerFlow)
        {
            PowerflowTableView powerflowTableView = new();
            IDictionary<string, string> idToUUid = new Dictionary<string, string>();
            powerflowTableView.Headings = new List<string>();
            powerflowTableView.Values = new List<IList<string>>();

            foreach (var entry in optimalPowerFlow.Bus.Name)
            {
                idToUUid.Add(entry.Key, entry.Value);
            }

            powerflowTableView.Headings.AddRange(new List<string>() {"Name", "Value"});

            // load
            double load = optimalPowerFlow.ResLoad.PMw.Sum(x => x.Value);
            powerflowTableView.Values.Add(new List<string>() {"Load", load.ToString()});
            // generation
            double generation = optimalPowerFlow.ResSgen.PMw.Sum(x => x.Value);
            powerflowTableView.Values.Add(new List<string>() {"Generation", generation.ToString()});
            // import/export
            double import = optimalPowerFlow.ResExtGrid.PMw.Sum(x => x.Value);
            powerflowTableView.Values.Add(new List<string>() {"Import", import.ToString()});

            double storage = optimalPowerFlow.ResStorage.PMw.Sum(x => x.Value);
            powerflowTableView.Values.Add(new List<string>() {"Storage", storage.ToString()});

            return powerflowTableView;
        }

        /// <summary>
        /// Extracts graph data
        /// </summary>
        /// <param name="optimalPowerFlow"></param>
        /// <returns></returns>
        public double[] GetPowerflowSummaryGraphInfo(OptimalPowerFlow optimalPowerFlow)
        {
            IList<double> values = new List<double>();
            IDictionary<string, string> idToUUid = new Dictionary<string, string>();

            foreach (var entry in optimalPowerFlow.Bus.Name)
            {
                idToUUid.Add(entry.Key, entry.Value);
            }

            // load
            double load = optimalPowerFlow.ResLoad.PMw.Sum(x => x.Value);
            values.Add(load);
            // generation
            double generation = optimalPowerFlow.ResSgen.PMw.Sum(x => x.Value);
            values.Add(generation);
            // import/export
            double import = optimalPowerFlow.ResExtGrid.PMw.Sum(x => x.Value);
            values.Add(import);
            //double import = optimalPowerFlow.ResExtGrid.PMw.Sum(x => x.Value >= 0 ? x.Value : 0.0);
            //values.Add(import);
            //double export = optimalPowerFlow.ResExtGrid.PMw.Sum(x => x.Value <= 0 ? x.Value : 0.0);
            //values.Add(export);
            double storage = optimalPowerFlow.ResStorage.PMw.Sum(x => x.Value);
            values.Add(storage);
            return values.ToArray<double>();
        }
        private string IdToName(string id, IDictionary<string, string> idToUuid)
        {
            return _uuidToName[idToUuid[id]];
        }
    }
}
