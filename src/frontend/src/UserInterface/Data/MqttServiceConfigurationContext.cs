namespace UserInterface.Data
{
    public class MqttServiceConfigurationContext
    {
        public const string Mqtt = "MQTT";

        public string Host { get; set; }
        public int Port { get; set; }

        public MqttServiceConfigurationContext(IConfiguration configuration)
        {
            configuration.GetSection(Mqtt).Bind(this);
        }
    }
}
