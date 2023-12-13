using UserInterface.Data;
using UserInterface.Store;
using System.Text.Json;

namespace Unittest
{
    public class IntegrationTestMqttMessages
    {
        [Fact]
        public void TestConsumerModelDeployment()
        {
            /*
             * Test case needs a running mqtt service and a consumer service
             */
            string text = File.ReadAllText("./Resources/ExampleConfigOneConsumer.json");
            // read scenario
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,

            };
            ScenarioModelJson? scenario = JsonSerializer.Deserialize<ScenarioModelJson>(text, options);

            // read model
            //FileStream inputFile = File.OpenRead("./Resources/london2011-2014_cluster0");
            var model = File.ReadAllBytes("./Resources/london2011-2014_cluster0");
            MqttService mqttService = new MqttService(new MqttServiceConfigurationContext()
            {
                MQTT_HOST = "localhost",
                MQTT_PORT = 1883
            });

            string uuid = System.Guid.NewGuid().ToString();
            ConsumersMessage cm = new ConsumersMessage()
            {
                ScenarioIdentifier = uuid,
                Consumers = scenario?.Scenario?.Consumers
            };

            mqttService.Server.Publish<ConsumersMessage>(new DAT.Configuration.PublicationOptions()
            {
                Topic = "consumer/scenario",
            }, cm);


            foreach (var consumer in scenario?.Scenario?.Consumers)
            {
                string base64 = Convert.ToBase64String(model);
                FileMessage fm = new FileMessage()
                {
                    File = base64
                };
                string topic = $"consumer/{consumer.Identifier}/model";
                mqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
                {
                    Topic = topic
                }, fm);
                Thread.Sleep(1000);
                ConsumptionRequest cr = new ConsumptionRequest()
                {
                    UnixTimestampSeconds = 1699975259
                };
                var response = mqttService.Server.Request<ConsumptionResponse, ConsumptionRequest>(new DAT.Configuration.RequestOptions()
                {
                    GenerateResponseTopicPostfix = true,
                    Topic = $"consumer/{consumer.Identifier}/consumption"
                }, cr);
                Assert.Equal(cr.UnixTimestampSeconds, response.UnixTimestampSeconds);
                Assert.Equal(96, response.Usage);
            }
        }
                
        [Fact]
        public void TestGeneratorModelDeployment()
        {
            /*
             * Test case needs a running mqtt service and a consumer service
             */
            string text = File.ReadAllText("./Resources/ExampleConfigOneConsumer.json");
            // read scenario
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,

            };
            ScenarioModelJson? scenario = JsonSerializer.Deserialize<ScenarioModelJson>(text, options);

            // read model
            var model = File.ReadAllBytes("./Resources/hgb_south_10kwp");
            MqttService mqttService = new MqttService(new MqttServiceConfigurationContext()
            {
                MQTT_HOST = "localhost",
                MQTT_PORT = 1883
            });

            string uuid = System.Guid.NewGuid().ToString();
            GeneratorsMessage gm = new GeneratorsMessage()
            {
                ScenarioIdentifier = uuid,
                Generators = scenario?.Scenario?.Generators
            };

            mqttService.Server.Publish<GeneratorsMessage>(new DAT.Configuration.PublicationOptions()
            {
                Topic = "generator/scenario",
                QosLevel = DAT.Configuration.QualityOfServiceLevel.ExactlyOnce
            }, gm);


            foreach (var generator in scenario?.Scenario?.Generators)
            {
                string base64 = Convert.ToBase64String(model);
                FileMessage fm = new FileMessage()
                {
                    File = base64
                };
                string topic = $"generator/{generator.Identifier}/model";
                mqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
                {
                    Topic = topic,
                    QosLevel = DAT.Configuration.QualityOfServiceLevel.ExactlyOnce
                }, fm);
                GenerationRequest gr = new GenerationRequest()
                {
                    UnixTimestampSeconds = 1699975259
                };
                Thread.Sleep(500);
                var response = mqttService.Server.Request<GenerationResponse, GenerationRequest>(new DAT.Configuration.RequestOptions()
                {
                    GenerateResponseTopicPostfix = true,
                    Topic = $"generator/{generator.Identifier}/generation"
                }, gr);
                Assert.Equal(gr.UnixTimestampSeconds, response.UnixTimestampSeconds);
                Assert.Equal(0, response.Generation);
            }
        }

        [Fact]
        public void TestNetworkModelDeployment()
        {
            /*
             * Test case needs a running mqtt service and a consumer service
             */
            string text = File.ReadAllText("./Resources/ExampleConfigOneConsumer.json");
            // read scenario
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,

            };
            ScenarioModelJson? scenario = JsonSerializer.Deserialize<ScenarioModelJson>(text, options);
            Network network = scenario?.Scenario?.Network;
            MqttService mqttService = new MqttService(new MqttServiceConfigurationContext()
            {
                MQTT_HOST = "localhost",
                MQTT_PORT = 1883
            });

            string uuid = System.Guid.NewGuid().ToString();
            NetworkMessage nm = new NetworkMessage()
            {
                ScenarioIdentifier = uuid,
                Network = scenario?.Scenario?.Network
            };

            mqttService.Server.Publish<NetworkMessage>(new DAT.Configuration.PublicationOptions()
            {
                Topic = "network/scenario",
            }, nm);
            NetworkRequest gr = new NetworkRequest()
            {
                UnixTimestampSeconds = 1699975259
            };
            var response = mqttService.Server.Request<OptimalPowerFlow, NetworkRequest>(new DAT.Configuration.RequestOptions()
            {
                GenerateResponseTopicPostfix = true,
                Topic = $"network/opf"
            }, gr);
            Assert.NotNull(response);
        }

        [Fact]
        public void TestModelDeploymentAndOpfQuery()
        {
            /*
             * Test case needs a running mqtt service and a consumer service
             */
            string text = File.ReadAllText("./Resources/ExampleConfigOneConsumer.json");
            // read scenario
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,

            };
            ScenarioModelJson? scenario = JsonSerializer.Deserialize<ScenarioModelJson>(text, options);

            // read model
            //FileStream inputFile = File.OpenRead("./Resources/london2011-2014_cluster0");
            var model_consumer = File.ReadAllBytes("./Resources/london2011-2014_cluster0");
            MqttService mqttService = new MqttService(new MqttServiceConfigurationContext()
            {
                MQTT_HOST = "localhost",
                MQTT_PORT = 1883
            });

            string uuid = System.Guid.NewGuid().ToString();
            ConsumersMessage cm = new ConsumersMessage()
            {
                ScenarioIdentifier = uuid,
                Consumers = scenario?.Scenario?.Consumers
            };

            mqttService.Server.Publish<ConsumersMessage>(new DAT.Configuration.PublicationOptions()
            {
                Topic = "consumer/scenario",
            }, cm);

            foreach (var consumer in scenario?.Scenario?.Consumers)
            {
                string base64 = Convert.ToBase64String(model_consumer);
                FileMessage fm = new FileMessage()
                {
                    File = base64
                };
                string topic = $"consumer/{consumer.Identifier}/model";
                mqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
                {
                    Topic = topic
                }, fm);
                Thread.Sleep(1000);
                ConsumptionRequest cr = new ConsumptionRequest()
                {
                    UnixTimestampSeconds = 1699975259
                };
                var response = mqttService.Server.Request<ConsumptionResponse, ConsumptionRequest>(new DAT.Configuration.RequestOptions()
                {
                    GenerateResponseTopicPostfix = true,
                    Topic = $"consumer/{consumer.Identifier}/consumption"
                }, cr);
                Assert.Equal(cr.UnixTimestampSeconds, response.UnixTimestampSeconds);
                Assert.Equal(96, response.Usage);
            }
            GeneratorsMessage gm = new GeneratorsMessage()
            {
                ScenarioIdentifier = uuid,
                Generators = scenario?.Scenario?.Generators
            };

            mqttService.Server.Publish<GeneratorsMessage>(new DAT.Configuration.PublicationOptions()
            {
                Topic = "generator/scenario",
                QosLevel = DAT.Configuration.QualityOfServiceLevel.ExactlyOnce
            }, gm);

            var model_generator = File.ReadAllBytes("./Resources/hgb_south_10kwp");
            foreach (var generator in scenario?.Scenario?.Generators)
            {
                string base64 = Convert.ToBase64String(model_generator);
                FileMessage fm = new FileMessage()
                {
                    File = base64
                };
                string topic = $"generator/{generator.Identifier}/model";
                mqttService.Server.Publish<FileMessage>(new DAT.Configuration.PublicationOptions()
                {
                    Topic = topic,
                    QosLevel = DAT.Configuration.QualityOfServiceLevel.ExactlyOnce
                }, fm);
                GenerationRequest gr = new GenerationRequest()
                {
                    UnixTimestampSeconds = 1699975259
                };
                Thread.Sleep(500);
                var response1 = mqttService.Server.Request<GenerationResponse, GenerationRequest>(new DAT.Configuration.RequestOptions()
                {
                    GenerateResponseTopicPostfix = true,
                    Topic = $"generator/{generator.Identifier}/generation"
                }, gr);
                Assert.Equal(gr.UnixTimestampSeconds, response1.UnixTimestampSeconds);
                Assert.Equal(0, response1.Generation);
            }

            NetworkMessage nm = new NetworkMessage()
            {
                ScenarioIdentifier = uuid,
                Network = scenario?.Scenario?.Network
            };

            mqttService.Server.Publish<NetworkMessage>(new DAT.Configuration.PublicationOptions()
            {
                Topic = "network/scenario",
            }, nm);
            NetworkRequest nr = new NetworkRequest()
            {
                UnixTimestampSeconds = 1699975259
            };
            Thread.Sleep(500);
            var response2 = mqttService.Server.Request<OptimalPowerFlow, NetworkRequest>(new DAT.Configuration.RequestOptions()
            {
                GenerateResponseTopicPostfix = true,
                Topic = $"network/opf"
            }, nr);
            Assert.NotNull(response2);

        }

    }
}
