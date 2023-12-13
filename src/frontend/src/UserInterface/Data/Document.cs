namespace UserInterface.Data
{
    public class Document
    {
        public string Id { get; set; }
        public string Payload { get; set; }

        public Document(string id, string payload)
        {
            Id = id;
            Payload = payload ?? "";
        }

        public override string ToString()
        {
            return $"Id={Id}, Payload={Payload}";
        }
    }

    public class ConsumerRequest
    {
        public string Payload { get; set; }

        public ConsumerRequest()
        {
            Payload = "test";
        }

        public override string ToString()
        {
            return Payload;
        }
    }

    public class ConsumerResponse
    {
        public string Payload { get; set; }

    }
}
