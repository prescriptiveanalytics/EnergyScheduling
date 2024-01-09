using System;
using DAT.Communication;
using DAT.Configuration;

namespace UserInterface.Data
{
    public class MqttService
    {
        MqttServiceConfigurationContext _configurationContext;
        HostAddress _hostAddress;
        IPayloadConverter _payloadConverter;
        ISocket _server;

        PublicationOptions _publicationOptions;


        public MqttService(MqttServiceConfigurationContext configurationContext)
        {
            _configurationContext = configurationContext;
            _hostAddress = new HostAddress(_configurationContext.Host, _configurationContext.Port);
            _payloadConverter = new JsonPayloadConverter();
            _publicationOptions = new PublicationOptions("frontend", "frontend/response", QualityOfServiceLevel.ExactlyOnce);
            Server = new MqttSocket(Guid.NewGuid().ToString(), "frontend", _hostAddress, _payloadConverter, defPubOptions: _publicationOptions);
            Server.Connect();
        }

        public ISocket Server { get => _server; set => _server = value; }
    }
}
