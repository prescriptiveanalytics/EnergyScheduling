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
        public DateTimeOffset StartDateTimeOffset { get; init; }
        public DateTimeOffset CurrentDateTimeOffset { get; init; }
        public DateTimeOffset EndDateTimeOffset { get; init; }
        public bool StartEndDateValid { get; init; }
        public bool SimulationStarted { get; init; }
        public SortedList<DateTime, PowerFlow> PowerFlows { get; init; }

        public ScenarioDataState()
        {
            PowerFlows = new SortedList<DateTime, PowerFlow>();
        }
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

    public class ScenarioDataSetSelectedScenarioAction
    {
        public ScenarioModelJson ScenarioModelJson { get; set; }

        public ScenarioDataSetSelectedScenarioAction(ScenarioModelJson scenarioModelJson)
        {
            ScenarioModelJson = scenarioModelJson;
        }
    }

    public class SimulationSetStartDateTimeOffsetAction
    {
        public DateTimeOffset StartDateTimeOffset { get; set; }
        public SimulationSetStartDateTimeOffsetAction(DateTimeOffset startDateTimeOffset)
        {
            StartDateTimeOffset = startDateTimeOffset;
        }
    }

    public class SimulationSetEndDateTimeOffsetAction
    {
        public DateTimeOffset EndDateTimeOffset { get; set; }
        public SimulationSetEndDateTimeOffsetAction(DateTimeOffset endDateTimeOffset)
        {
            EndDateTimeOffset = endDateTimeOffset;
        }
    }

    public class SimulationSingleStepAction
    {
        public DateTimeOffset DateTimeOffset { get; set; }
        public SimulationSingleStepAction(DateTimeOffset dateTimeOffset)
        {
            DateTimeOffset = dateTimeOffset;
        }
    }

    public class AddSingleStepResultAction
    {
        public DateTime DateTime { get; set; }
        public PowerFlow PowerFlow { get; set; }
        public AddSingleStepResultAction(DateTime dateTime, PowerFlow powerFlow)
        {
            DateTime = dateTime;
            PowerFlow = powerFlow;
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
        public static ScenarioDataState OnSetSelectedScenario(ScenarioDataState state, ScenarioDataSetSelectedScenarioAction action)
        {
            return state with
            {
                SelectedScenario = action.ScenarioModelJson,
                PowerFlows = new SortedList<DateTime, PowerFlow>()
            };
        }

        [ReducerMethod]
        public static ScenarioDataState OnSetStartDateTimeOffset(ScenarioDataState state, SimulationSetStartDateTimeOffsetAction action)
        {
            bool dateValid = action.StartDateTimeOffset <= state.EndDateTimeOffset && action.StartDateTimeOffset != DateTimeOffset.MinValue;
            return state with
            {
                StartDateTimeOffset = action.StartDateTimeOffset,
                CurrentDateTimeOffset = action.StartDateTimeOffset,
                SimulationStarted = false,
                StartEndDateValid = dateValid,
                PowerFlows = new SortedList<DateTime, PowerFlow>()
            };
        }

        [ReducerMethod]
        public static ScenarioDataState OnSetEndDateTimeOffset(ScenarioDataState state, SimulationSetEndDateTimeOffsetAction action)
        {
            bool dateValid = state.StartDateTimeOffset <= action.EndDateTimeOffset && state.StartDateTimeOffset != DateTimeOffset.MinValue;

            return state with
            {
                EndDateTimeOffset = action.EndDateTimeOffset,
                CurrentDateTimeOffset = state.StartDateTimeOffset,
                SimulationStarted = false,
                StartEndDateValid = dateValid,
                PowerFlows = new SortedList<DateTime, PowerFlow>()
            };
        }

        [ReducerMethod]
        public static ScenarioDataState OnAddSingleStepResultAction(ScenarioDataState state, AddSingleStepResultAction action)
        {
            SortedList<DateTime, PowerFlow> powerflows = state.PowerFlows ?? new SortedList<DateTime, PowerFlow>();
            powerflows.Add(action.DateTime, action.PowerFlow);
            return state with
            {
                PowerFlows = powerflows,
                CurrentDateTimeOffset = state.CurrentDateTimeOffset.AddMinutes(15)
            };
        }
    }

    public class ScenarioEffects
    {
        private IState<ScenarioDataState> ScenarioDataState;
        private MqttService MqttService;
        // TODO: Remove the hardcoded powerflow result and use the actual result from the call; this is currently not possible, because .net and python do not talk
        private PowerFlow PowerFlow;

        public ScenarioEffects(IState<ScenarioDataState> scenarioDataState, MqttService mqttService, PowerFlow pf) 
        {
            ScenarioDataState = scenarioDataState;
            MqttService = mqttService;
            PowerFlow = pf;
        }

        [EffectMethod]
        public async Task SimulationSingleStep(SimulationSingleStepAction action, IDispatcher dispatcher)
        {
            // TODO: Call to opf and parse result
            // TODO: Remove the hardcoded powerflow result
            dispatcher.Dispatch(new AddSingleStepResultAction(action.DateTimeOffset.DateTime, PowerFlow));
        }
    }
}
