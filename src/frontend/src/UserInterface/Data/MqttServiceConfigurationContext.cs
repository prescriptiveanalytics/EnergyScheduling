namespace UserInterface.Data
{
    public class MqttServiceConfigurationContext
    {
        public string MQTT_HOST { get; set; }
        public int MQTT_PORT { get; set; }

        public MqttServiceConfigurationContext(string mqtt_host = "localhost", int mqtt_port = 1883)
        {
            MQTT_HOST = mqtt_host;
            MQTT_PORT = mqtt_port;
        }
    }
}
