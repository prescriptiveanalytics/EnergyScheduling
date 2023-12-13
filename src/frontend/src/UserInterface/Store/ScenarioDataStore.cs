using System.Formats.Asn1;
using System.Text.Json.Serialization;
using System.Text.Json;
using Fluxor;
using UserInterface.Data;
using YamlDotNet.Core.Tokens;
using System.Buffers.Text;
using static MudBlazor.CategoryTypes;
using static Confluent.Kafka.ConfigPropertyNames;

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
        public SortedList<DateTime, OptimalPowerFlow> PowerFlows { get; init; }

        public ScenarioDataState()
        {
            PowerFlows = new SortedList<DateTime, OptimalPowerFlow>();
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
        public OptimalPowerFlow PowerFlow { get; set; }
        public AddSingleStepResultAction(DateTime dateTime, OptimalPowerFlow powerFlow)
        {
            DateTime = dateTime;
            PowerFlow = powerFlow;
        }
    }

    public class DeploySelectedScenarioAction
    {

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
                PowerFlows = new SortedList<DateTime, OptimalPowerFlow>()
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
                PowerFlows = new SortedList<DateTime, OptimalPowerFlow>()
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
                PowerFlows = new SortedList<DateTime, OptimalPowerFlow>()
            };
        }

        [ReducerMethod]
        public static ScenarioDataState OnAddSingleStepResultAction(ScenarioDataState state, AddSingleStepResultAction action)
        {
            SortedList<DateTime, OptimalPowerFlow> powerflows = state.PowerFlows ?? new SortedList<DateTime, OptimalPowerFlow>();
            powerflows.Add(action.DateTime, action.PowerFlow);
            return state with
            {
                PowerFlows = powerflows,
                CurrentDateTimeOffset = state.CurrentDateTimeOffset.AddMinutes(15)
            };
        }

        [ReducerMethod(typeof(DeploySelectedScenarioAction))]
        public static ScenarioDataState OnDeploySelectedScenario(ScenarioDataState state)
        {
            return state with
            {
                Loading = true
            };
        }

    }

    public class ScenarioEffects
    {
        private IState<ScenarioDataState> ScenarioDataState;
        private MqttService MqttService;

        public ScenarioEffects(IState<ScenarioDataState> scenarioDataState, MqttService mqttService) 
        {
            ScenarioDataState = scenarioDataState;
            MqttService = mqttService;
        }

        [EffectMethod]
        public async Task SimulationSingleStep(SimulationSingleStepAction action, IDispatcher dispatcher)
        {
            NetworkRequest gr = new NetworkRequest()
            {
                UnixTimestampSeconds = (int)action.DateTimeOffset.ToUnixTimeSeconds()
            };
            var powerFlow = await MqttService.Server.RequestAsync<OptimalPowerFlow, NetworkRequest>(new DAT.Configuration.RequestOptions()
            {
                GenerateResponseTopicPostfix = true,
                Topic = $"network/opf"
            }, gr);
            dispatcher.Dispatch(new AddSingleStepResultAction(action.DateTimeOffset.DateTime, powerFlow));
            dispatcher.Dispatch(new UpdateChartDataAction(ScenarioDataState.Value.PowerFlows));
        }

        [EffectMethod]
        public async Task DeployScenario(DeploySelectedScenarioAction action, IDispatcher dispatcher)
        {
            var scenario = ScenarioDataState.Value.SelectedScenario.Scenario;
            string uuid = Guid.NewGuid().ToString();
            // deploy consumers
            ConsumersMessage cm = new ConsumersMessage()
            {
                ScenarioIdentifier = uuid,
                Consumers = scenario.Consumers
            };

            MqttService.Server.Publish<ConsumersMessage>(new DAT.Configuration.PublicationOptions()
            {
               Topic = "consumer/scenario",
            }, cm);

            // deploy consumer models
            foreach (var consumer in scenario.Consumers)
            {
                var model = ScenarioDataState.Value.ScenarioData.Models.Where(x => x.Key.Contains(consumer.ProfileIdentifier)).FirstOrDefault();
                if (!model.Key.Contains(consumer.ProfileIdentifier))
                {
                    continue;
                }
                string base64 = Convert.ToBase64String(model.Value);
                FileMessage fm = new FileMessage()
                {
                    File = base64
                };
                string topic = $"consumer/{consumer.Identifier}/model";
                MqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
                {
                    Topic = topic
                }, fm);
            }
            // deploy generators
            GeneratorsMessage gm = new GeneratorsMessage()
            {
                ScenarioIdentifier = uuid,
                Generators = scenario.Generators
            };

            MqttService.Server.Publish<GeneratorsMessage>(new DAT.Configuration.PublicationOptions()
            {
                Topic = "generator/scenario",
                QosLevel = DAT.Configuration.QualityOfServiceLevel.ExactlyOnce
            }, gm);


            foreach (var generator in scenario.Generators)
            {                
                var model = ScenarioDataState.Value.ScenarioData.Models.Where(x => x.Key.Contains(generator.ProfileIdentifier)).FirstOrDefault();
                string base64 = Convert.ToBase64String(model.Value);
                FileMessage fm = new FileMessage()
                {
                    File = base64
                };
                string topic = $"generator/{generator.Identifier}/model";
                MqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
                {
                    Topic = topic,
                    QosLevel = DAT.Configuration.QualityOfServiceLevel.ExactlyOnce
                }, fm);
                GenerationRequest gr = new GenerationRequest()
                {
                    UnixTimestampSeconds = 1699975259
                };
            }

            // deploy network
            NetworkMessage nm = new NetworkMessage()
            {
                ScenarioIdentifier = uuid,
                Network = scenario.Network
            };

            MqttService.Server.Publish<NetworkMessage>(new DAT.Configuration.PublicationOptions()
            {
                Topic = "network/scenario",
            }, nm);
        }

    }

    public class ConsumptionRequest
    {
        public int UnixTimestampSeconds { get; set; }
    }

    public class ConsumptionResponse
    {
        public long UnixTimestampSeconds { get; set; }
        public string Identifier { get; set; }
        public double Usage { get; set; }
        public string Category { get; set; } = "load";
        public string CategoryUnit { get; set; } = "Wh";
        public int Interval { get; set; } = 15;
        public string IntervalUnit { get; set; } = "minutes";
    }
    public class ConsumersMessage
    {
        public string ScenarioIdentifier { get; set; }
        public Data.Consumer[] Consumers { get; set; } 
    }

    public class GeneratorsMessage
    {
        public string ScenarioIdentifier { get; set; }
        public Generator[] Generators { get; set; }
    }

    public class GenerationRequest
    {
        public int UnixTimestampSeconds { get; set; } 
    }

    public class GenerationResponse
    {
        public long UnixTimestampSeconds { get; set; }
        public string Identifier { get; set; }
        public double Generation { get; set; }
        public string Category { get; set; }
        public string CategoryUnit { get; set; }
        public int Interval { get; set; }
        public string IntervalUnit { get; set; }
    }

    public class NetworkMessage
    {
        public string ScenarioIdentifier { get; set; }
        public Network Network { get; set; }
    }

    public class NetworkRequest
    {
        public int UnixTimestampSeconds { get; set;}
    }

    public class NetworkResponse
    {
        public OptimalPowerFlow PowerFlow{ get; set; }
    }

    public class FileMessage
    {
        public string File { get; set; }
    }
}
 