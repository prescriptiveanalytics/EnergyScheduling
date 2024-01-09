namespace UserInterface.Data
{
    public class PowerflowTableView
    {
        public IList<string> Headings { get; set; }
        public IList<IList<string>> Values { get; set; }
    }

    public class TimeSeriesDataPoint
    {
        public long UnixTimestampSeconds { get; set; }
        public IList<string> Keys { get; set; }
        public List<double> Values { get; set; }
    }
}
