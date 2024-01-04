using System.Text.Json.Serialization;

namespace UserInterface.Data
{
    public class OptimalPowerFlow
    {
        [JsonPropertyName("Bus")]
        public BusPowerFlow Bus { get; set; }
        [JsonPropertyName("Line")]
        public LinePowerFlow Line { get; set; }
        [JsonPropertyName("Load")]
        public LoadPowerFlow Load { get; set; }
        [JsonPropertyName("ResBus")]
        public ResBusPowerFlow ResBus { get; set; }
        [JsonPropertyName("ResLine")]
        public ResLinePowerFlow ResLine { get; set; }
        [JsonPropertyName("ResLoad")]
        public ResLoadPowerFlow ResLoad { get; set; }
        [JsonPropertyName("ResExtGrid")]
        public ResExtGridPowerFlow ResExtGrid { get; set; }
        [JsonPropertyName("Sgen")]
        public SgenPowerFlow Sgen { get; set; }
        [JsonPropertyName("ResSgen")]
        public ResSgenPowerFlow ResSgen { get; set; }
        [JsonPropertyName("Storage")]
        public StoragePowerFlow Storage { get; set; }
        [JsonPropertyName("ResStorage")]
        public ResStoragePowerFlow ResStorage { get; set; }
    }

    public class BusPowerFlow
    {
        public IDictionary<string, string> Name { get; set; }
        public IDictionary<string, double> VnKv { get; set; }
        public IDictionary<string, string> Type { get; set; }
        public IDictionary<string, string> Zone { get; set; }
        public IDictionary<string, bool> InService { get; set; }
    }

    public class LinePowerFlow
    {

    }

    public class LoadPowerFlow
    {

    }

    public class SgenPowerFlow
    {

    }
    public class ResBusPowerFlow
    {
        public IDictionary<string, double> PMw { get;set; }
        public IDictionary<string, double> QMvar { get;set; }
        public IDictionary<string, double> VaDegree { get;set; }
        public IDictionary<string, double> VmPu { get;set; }
    }

    public class ResLinePowerFlow 
    {
        public IDictionary<string, double> IFromKa { get;set; }
        public IDictionary<string, double> IKa { get;set; }
        public IDictionary<string, double> IToKa { get;set; }
        public IDictionary<string, double> LoadingPercent { get;set; }
        public IDictionary<string, double> PFromMw { get;set; }
        public IDictionary<string, double> PToMw { get;set; }
        public IDictionary<string, double> PlMw { get;set; }
        public IDictionary<string, double> QFromMvar { get;set; }
        public IDictionary<string, double> QToMvar { get;set; }
        public IDictionary<string, double> QlMvar { get;set; }
        public IDictionary<string, double> VaFromDegree { get;set; }
        public IDictionary<string, double> VaToDegree { get;set; }
        public IDictionary<string, double> VmFromPu { get;set; }
        public IDictionary<string, double> VmToPu { get;set; }
    }

    public class ResLoadPowerFlow
    {
        public IDictionary<string, double> PMw { get;set; }        
        public IDictionary<string, double> QMvar { get;set; }  
    }

    public class ResExtGridPowerFlow
    {
        public IDictionary<string, double> PMw { get;set; }
        public IDictionary<string, double> QMvar { get;set; }
    }

    public class ResSgenPowerFlow
    {
        public IDictionary<string, double> PMw { get;set; }
        public IDictionary<string, double> QMvar { get;set; }
    }

    public class StoragePowerFlow
    {
        public IDictionary<string, string> Name { get; set; }
        public IDictionary<string, int> Bus{ get; set; }
        public IDictionary<string, double> MaxEMwh { get; set; }
        public IDictionary<string, double> MinEMwh { get; set; }
        public IDictionary<string, double> PMw { get; set; }
        public IDictionary<string, double> QMvar { get; set; }
        public IDictionary<string, double> Scaling { get; set; }
        public IDictionary<string, double> SnMva { get; set; }
        public IDictionary<string, double> SocPercent { get; set; }
        public IDictionary<string, bool> InService { get; set; }
    }

    public class ResStoragePowerFlow
    {
        public IDictionary<string, double> PMw { get;set; }
        public IDictionary<string, double> QMvar { get;set; }
    }

}
