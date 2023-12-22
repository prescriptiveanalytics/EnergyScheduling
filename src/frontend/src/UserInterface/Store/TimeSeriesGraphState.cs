using System.Timers;
using Fluxor;
using MudBlazor;
using Plotly.Blazor;
using UserInterface.Data;

namespace UserInterface.Store
{
    public record TimeSeriesGraphState
    {
        public IList<ITrace> Data { get; init; }
        public PlotlyChart Chart { get; init; }
        
        public TimeSeriesGraphState()
        {
        }
    }

    public class TimeSeriesGraphFeature : Feature<TimeSeriesGraphState>
    {
        public override string GetName()
        {
            return "TimeSeriesGraphState";
        }

        protected override TimeSeriesGraphState GetInitialState()
        {
            return new TimeSeriesGraphState();
        }
    }

    public class UpdateChartDataAction
    {
        public IDictionary<DateTime, OptimalPowerFlow> PowerFlowData;

        public UpdateChartDataAction(IDictionary<DateTime, OptimalPowerFlow> powerFlowData)
        {
            PowerFlowData = powerFlowData;
        }
    }

    public static class TimeSeriesGraphReducers
    {
        [ReducerMethod]
        public static TimeSeriesGraphState OnUpdateChartDataAction(TimeSeriesGraphState state, UpdateChartDataAction action)
        {
            var overviewChartSeries = new List<ChartSeries>();
            List<double> gen = new List<double>();
            List<double> load = new List<double>();
            List<double> grid = new List<double>();

            // sgen, ext_grid, load
            foreach (var pf in action.PowerFlowData.Values)
            {
                // TODO
                gen.Add(pf.ResSgen.PMw.Values.Sum());
                load.Add(pf.ResLoad.PMw.Values.Sum());
                grid.Add(pf.ResExtGrid.PMw.Values.Sum());
            }

            overviewChartSeries.Add(new ChartSeries { Name = "Generation", Data = gen.ToArray() });
            overviewChartSeries.Add(new ChartSeries { Name = "Consumption", Data = load.ToArray() });
            overviewChartSeries.Add(new ChartSeries { Name = "External grid", Data = grid.ToArray() });

            var overviewChartSeriesXAxisLabels = action.PowerFlowData.Keys.Select(x => x.ToString()).ToArray();

            // TODO
            return state with
            {
                //OverviewChartSeries = overviewChartSeries,
                //OverviewChartSeriesXAxisLabels = overviewChartSeriesXAxisLabels,
            };
        }
    }
}
