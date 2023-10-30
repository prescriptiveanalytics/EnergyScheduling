using Fluxor;
using UserInterface.Data;

namespace UserInterface.Store
{
    public record ScenarioDataState
    {
        public bool Initialized { get; init; }
        public bool Loading { get; init; }
        public ScenarioData? ScenarioData { get; init; }
        public ScenarioModelJson? SelectedScenario { get; init; }
    }

    public class ScenarioDataFeature : Feature<ScenarioDataState>
    {
        public override string GetName()
        {
            return "ScenarioData";
        }

        protected override ScenarioDataState GetInitialState()
        {
            return new ScenarioDataState
            {
                Initialized = false,
                Loading = false,
                ScenarioData = null
            };
        }
    }

    public class ScenarioDataLoadDataAction { }

    public class ScenarioDataSetDataAction
    {
        public ScenarioData ScenarioData { get; }

        public ScenarioDataSetDataAction(ScenarioData scenarioData)
        {
            ScenarioData = scenarioData;
        }
    }

    public class ScenarioDataSetSelectedScenario
    {
        public ScenarioModelJson ScenarioModelJson { get; set; }

        public ScenarioDataSetSelectedScenario(ScenarioModelJson scenarioModelJson)
        {
            ScenarioModelJson = scenarioModelJson;
        }
    }

    public static class ScenarioDataReducers
    {
        [ReducerMethod]
        public static ScenarioDataState OnSetData(ScenarioDataState state, ScenarioDataSetDataAction action)
        {
            return state with
            {
                ScenarioData = action.ScenarioData,
                Loading = false,
                Initialized = true
            };
        }

        [ReducerMethod(typeof(ScenarioDataLoadDataAction))]
        public static ScenarioDataState OnSetLoading(ScenarioDataState state)
        {
            return state with
            {
                Loading = true
            };
        }

        [ReducerMethod]
        public static ScenarioDataState OnSetSelectedScenario(ScenarioDataState state, ScenarioDataSetSelectedScenario action)
        {
            return state with
            {
                SelectedScenario = action.ScenarioModelJson
            };
        }
    }
}
