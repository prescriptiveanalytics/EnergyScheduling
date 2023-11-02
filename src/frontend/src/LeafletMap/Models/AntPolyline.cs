using System.Drawing;

namespace BlazorLeaflet.Models
{
    public class AntPolyline<TShape> : Path
    {

        public TShape Shape { get; set; }

        ///// <summary>
        ///// How much to simplify the polyline on each zoom level. More means better performance and smoother look, and less means more accurate representation.
        ///// </summary>
        //public double SmoothFactory { get; set; } = 1.0;

        ///// <summary>
        ///// Disable polyline clipping.
        ///// </summary>
        //public bool NoClipEnabled { get; set; }

        public int Delay { get;set; } = 5000;
        public int[] DashArray { get; set; } = new int[] { 10, 20 };
        public int Weight { get; set; } = 5;
        public string Color { get; set; } = "#0000FF";
        public string PulseColor { get; set; } = "#DDDDDD";
        public bool Reverse { get; set; } = false;
        public bool Paused { get; set; } = false;
    }

    public class AntPolyline : AntPolyline<PointF[][]>
    { }


}
