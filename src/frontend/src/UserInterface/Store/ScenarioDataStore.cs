using System.Formats.Asn1;
using System.Text.Json.Serialization;
using System.Text.Json;
using Fluxor;
using UserInterface.Data;
using YamlDotNet.Core.Tokens;
using System.Buffers.Text;
using static MudBlazor.CategoryTypes;
using static Confluent.Kafka.ConfigPropertyNames;
using Plotly.Blazor;
using Plotly.Blazor.Traces;
using UserInterface.Dataprocessor;

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
        public IList<ITrace> PowerflowTimeSeries { get; init; }
        public ScenarioDataState()
        {
            PowerFlows = new SortedList<DateTime, OptimalPowerFlow>();
            PowerflowTimeSeries = new List<ITrace>();
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

    public class SimulationSingleStepAction2
    {
        public DateTimeOffset DateTimeOffset { get; set; }
        public PlotlyChart Chart { get; set; }
        public SimulationSingleStepAction2(DateTimeOffset dateTimeOffset, PlotlyChart chart)
        {
            DateTimeOffset = dateTimeOffset;
            Chart = chart;
        }
    }

    public class AddSingleStepResultAction
    {
        public DateTime DateTime { get; set; }
        public OptimalPowerFlow PowerFlow { get; set; }
        public PlotlyChart Chart { get; set; }
        public AddSingleStepResultAction(DateTime dateTime, OptimalPowerFlow powerFlow, PlotlyChart chart)
        {
            DateTime = dateTime;
            PowerFlow = powerFlow;
            Chart = chart;
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

            PowerflowDataProcessor pdp = new PowerflowDataProcessor(state?.SelectedScenario);
            var data = pdp.GetPowerflowSummaryGraphInfo(action.PowerFlow);

            IList<ITrace> timeSeriesData = state.PowerflowTimeSeries ?? new List<ITrace>();
            string[] name = { "Load", "Generation", "Grid", "Storage" };

            if (timeSeriesData.Count == 0)
            {
                foreach (var entry in name) 
                {
                    timeSeriesData.Add(new Scatter
                    {
                        Name = entry,
                        X = new List<object>(),
                        Y = new List<object>()
                    });
                }
            }
            for (int i = 0; i < data.Length; i++)
            {
                if (timeSeriesData[i] is Scatter scatter)
                {
                    scatter.X.Add(scatter.X.Count);
                    scatter.Y.Add(data[i]);
                }
            }
            action.Chart.Data = timeSeriesData;
            action.Chart.Update();

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
        public async Task SimulationSingleStep(SimulationSingleStepAction2 action, IDispatcher dispatcher)
        {
            // TODO: Check is this is null or empty
            StorageModelState[] states = new StorageModelState[ScenarioDataState.Value.SelectedScenario.Scenario.Storages.Length];

            if (ScenarioDataState != null && ScenarioDataState.Value != null && ScenarioDataState.Value.PowerFlows != null && ScenarioDataState.Value.PowerFlows.Count() > 0) {
                var lastPf = ScenarioDataState.Value.PowerFlows.Last().Value;
                string[] identifier = lastPf.Storage.Name.Values.ToArray<string>();

                for (int i = 0; i < states.Length; i++)
                {
                    string busIndex = lastPf.Storage.Name.FirstOrDefault(x => x.Value == identifier[i]).Key;
                    StorageModelState sms = new StorageModelState()
                    {
                        Identifier = identifier[i],
                        StateOfCharge = lastPf.Storage.SocPercent.FirstOrDefault(x => x.Key == busIndex).Value
                    };
                    states[i] = sms;
                }
            }else
            {
                for (int i = 0; i < states.Length; i++)
                {
                    var st = ScenarioDataState.Value.SelectedScenario.Scenario.Storages[i];
                    states[i] = new StorageModelState()
                    {
                        Identifier = st.Identifier,
                        StateOfCharge = st.StateOfCharge
                    };
                }
            }
            StorageModelStateCollection smsc = new StorageModelStateCollection()
            {
                Storages = states
            };

            NetworkRequestWithModelState gr = new NetworkRequestWithModelState()
            {
                UnixTimestampSeconds = (int)action.DateTimeOffset.ToUnixTimeSeconds(),
                StorageModelStates = smsc
                
            };
            var powerFlow = await MqttService.Server.RequestAsync<OptimalPowerFlow, NetworkRequestWithModelState>(new DAT.Configuration.RequestOptions()
            {
                GenerateResponseTopicPostfix = true,
                Topic = $"network/opf_with_state"
            }, gr);
            dispatcher.Dispatch(new AddSingleStepResultAction(action.DateTimeOffset.DateTime, powerFlow, action.Chart));
        }

        [EffectMethod]
        public async Task DeployScenario(DeploySelectedScenarioAction action, IDispatcher dispatcher)
        {
            var scenario = ScenarioDataState.Value.SelectedScenario.Scenario;
            string uuid = Guid.NewGuid().ToString();

            foreach (var c in scenario.Consumers)
            {
                MqttService.Server.Publish<UserInterface.Data.Consumer>(new DAT.Configuration.PublicationOptions() 
                {
                    Topic = $"consumer/{c.Identifier}/add"
                }, c);

                var model = ScenarioDataState.Value.ScenarioData.Models.Where(x => x.Key.Contains(c.ProfileIdentifier)).FirstOrDefault();
                string base64 = Convert.ToBase64String(model.Value);
                FileMessage fm = new FileMessage()
                {
                    File = base64
                };
                string topic = $"consumer/{c.Identifier}/model";
                MqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
                {
                    Topic = topic
                }, fm);
            }

            foreach (var g in scenario.Generators)
            {
                MqttService.Server.Publish<UserInterface.Data.Generator>(new DAT.Configuration.PublicationOptions() 
                {
                    Topic = $"generator/{g.Identifier}/add"
                }, g);

                var model = ScenarioDataState.Value.ScenarioData.Models.Where(x => x.Key.Contains(g.ProfileIdentifier)).FirstOrDefault();
                string base64 = Convert.ToBase64String(model.Value);
                FileMessage fm = new FileMessage()
                {
                    File = base64
                };
                string topic = $"generator/{g.Identifier}/model";
                MqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
                {
                    Topic = topic
                }, fm);
            }

            foreach (var s in scenario.Storages) {
                MqttService.Server.Publish<UserInterface.Data.Storage>(new DAT.Configuration.PublicationOptions()
                {
                    Topic = $"storage/{s.Identifier}/add"
                }, s);
            }

            NetworkMessage nm = new NetworkMessage()
            {
                ScenarioIdentifier = uuid,
                Network = scenario.Network
            };

            MqttService.Server.Publish<NetworkMessage>(new DAT.Configuration.PublicationOptions()
            {
                Topic = "network/scenario",
            }, nm);

            //var scenario = ScenarioDataState.Value.SelectedScenario.Scenario;
            //string uuid = Guid.NewGuid().ToString();
            //// deploy consumers
            //ConsumersMessage cm = new ConsumersMessage()
            //{
            //    ScenarioIdentifier = uuid,
            //    Consumers = scenario.Consumers
            //};

            //MqttService.Server.Publish<ConsumersMessage>(new DAT.Configuration.PublicationOptions()
            //{
            //   Topic = "consumer/scenario",
            //}, cm);

            //// deploy consumer models
            //foreach (var consumer in scenario.Consumers)
            //{
            //    var model = ScenarioDataState.Value.ScenarioData.Models.Where(x => x.Key.Contains(consumer.ProfileIdentifier)).FirstOrDefault();
            //    if (!model.Key.Contains(consumer.ProfileIdentifier))
            //    {
            //        continue;
            //    }
            //    string base64 = Convert.ToBase64String(model.Value);
            //    FileMessage fm = new FileMessage()
            //    {
            //        File = base64
            //    };
            //    string topic = $"consumer/{consumer.Identifier}/model";
            //    MqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
            //    {
            //        Topic = topic
            //    }, fm);
            //}
            //// deploy generators
            //GeneratorsMessage gm = new GeneratorsMessage()
            //{
            //    ScenarioIdentifier = uuid,
            //    Generators = scenario.Generators
            //};

            //MqttService.Server.Publish<GeneratorsMessage>(new DAT.Configuration.PublicationOptions()
            //{
            //    Topic = "generator/scenario",
            //    QosLevel = DAT.Configuration.QualityOfServiceLevel.ExactlyOnce
            //}, gm);


            //foreach (var generator in scenario.Generators)
            //{                
            //    var model = ScenarioDataState.Value.ScenarioData.Models.Where(x => x.Key.Contains(generator.ProfileIdentifier)).FirstOrDefault();
            //    string base64 = Convert.ToBase64String(model.Value);
            //    FileMessage fm = new FileMessage()
            //    {
            //        File = base64
            //    };
            //    string topic = $"generator/{generator.Identifier}/model";
            //    MqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
            //    {
            //        Topic = topic,
            //        QosLevel = DAT.Configuration.QualityOfServiceLevel.ExactlyOnce
            //    }, fm);
            //    GenerationRequest gr = new GenerationRequest()
            //    {
            //        UnixTimestampSeconds = 1699975259
            //    };
            //}

            //// deploy network
            //NetworkMessage nm = new NetworkMessage()
            //{
            //    ScenarioIdentifier = uuid,
            //    Network = scenario.Network
            //};

            //MqttService.Server.Publish<NetworkMessage>(new DAT.Configuration.PublicationOptions()
            //{
            //    Topic = "network/scenario",
            //}, nm);
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

    public class ConsumerMessage
    {
        public string ScenarioIdentifier { get; set;}
        public Data.Consumer Consumer { get; set; }
    }

    public class GeneratorsMessage
    {
        public string ScenarioIdentifier { get; set; }
        public Generator[] Generators { get; set; }
    }

    public class GeneratorMessage
    {
        public string ScenarioIdentifier { get; set; }
        public Data.Generator Generator { get; set; }
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

    public class NetworkRequestWithModelState
    {
        public int UnixTimestampSeconds { get; set; }
        public StorageModelStateCollection StorageModelStates { get; set; }
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
 