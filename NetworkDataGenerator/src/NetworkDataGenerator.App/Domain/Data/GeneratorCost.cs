namespace NetworkDataGenerator.App.Domain.Data
{
    /// <summary>
    /// A class to summarize generation cost coefficients for a generator.
    /// Note: currently, only a linear model can be assumed. Polynomial is currently not possible.
    /// </summary>
    public class GeneratorCost
    {
        public double StartupCost { get; set; }
        public double ShutdownCost { get; set; }
        public double C1 { get; set; }
        public double C0 { get; set; }
    }
}
