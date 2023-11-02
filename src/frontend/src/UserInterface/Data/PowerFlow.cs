using System.Text.Json.Serialization;

namespace UserInterface.Data
{
    public class PowerFlow
    {
        [JsonPropertyName("res_bus")]
        public ResBus ResBus { get; set; }
        [JsonPropertyName("res_line")]
        public ResLine ResLine { get; set; }
        [JsonPropertyName("res_load")]
        public ResLoad ResLoad { get; set; }
        [JsonPropertyName("res_ext_grid")]
        public ResExtGrid ResExtGrid { get; set; }
        [JsonPropertyName("res_sgen")]
        public ResSgen ResSgen { get; set; }
    }

    public class ResBus
    {
        [JsonPropertyName("p_mw")]
        public IDictionary<string, double> PMw { get;set; }
        [JsonPropertyName("q_mvar")]
        public IDictionary<string, double> QMvar { get;set; }
        [JsonPropertyName("va_degree")]
        public IDictionary<string, double> VaDegree { get;set; }
        [JsonPropertyName("vm_pu")]
        public IDictionary<string, double> VmPu { get;set; }
    }

    public class ResLine 
    {
        [JsonPropertyName("i_from_ka")]
        public IDictionary<string, double> IFromKa { get;set; }
        [JsonPropertyName("i_ka")]
        public IDictionary<string, double> IKa { get;set; }
        [JsonPropertyName("i_to_ka")]
        public IDictionary<string, double> IToKa { get;set; }
        [JsonPropertyName("loading_percent")]
        public IDictionary<string, double> LoadingPercent { get;set; }
        [JsonPropertyName("p_from_mw")]
        public IDictionary<string, double> PFromMw { get;set; }
        [JsonPropertyName("p_to_mw")]
        public IDictionary<string, double> PToMw { get;set; }
        [JsonPropertyName("pl_mw")]
        public IDictionary<string, double> PlMw { get;set; }
        [JsonPropertyName("q_from_mvar")]
        public IDictionary<string, double> QFromMvar { get;set; }
        [JsonPropertyName("q_to_mvar")]
        public IDictionary<string, double> QToMvar { get;set; }
        [JsonPropertyName("ql_mvar")]
        public IDictionary<string, double> QlMvar { get;set; }
        [JsonPropertyName("var_from_degree")]
        public IDictionary<string, double> VaFromDegree { get;set; }
        [JsonPropertyName("va_to_degree")]
        public IDictionary<string, double> VaToDegree { get;set; }
        [JsonPropertyName("vm_from_pu")]
        public IDictionary<string, double> VmFromPu { get;set; }
        [JsonPropertyName("vm_to_pu")]
        public IDictionary<string, double> VmToPu { get;set; }
    }

    public class ResLoad
    {
        [JsonPropertyName("p_mw")]
        public IDictionary<string, double> PMw { get;set; }        
        [JsonPropertyName("q_mvar")]
        public IDictionary<string, double> QMvar { get;set; }  
    }

    public class ResExtGrid
    {
        [JsonPropertyName("p_mw")]
        public IDictionary<string, double> PMw { get;set; }
        [JsonPropertyName("q_mvar")]
        public IDictionary<string, double> QMvar { get;set; }
    }

    public class ResSgen
    {
        [JsonPropertyName("p_mw")]
        public IDictionary<string, double> PMw { get;set; }
        [JsonPropertyName("q_mvar")]
        public IDictionary<string, double> QMvar { get;set; }
    }
}
