using System;

namespace NetworkDataGenerator.App.Domain
{
    public class NetComponentState
    {
        public int TimeStep { get; }

        public INetComponent NetComponent { get; }

        public Tuple<double, double> StateBounds { get; }

        public double State { get; set; }

        public double Dispatch { get; set; } // just for ESS; how much is charging, if state = charging; resp. how much is discharging, if state = discharging TODO: maybe save this in state?

        public NetComponentState(INetComponent component, int timeStep, Tuple<double, double> bounds)
        {
            TimeStep = timeStep;
            NetComponent = component;
            StateBounds = bounds;
        }

        public NetComponentState(NetComponentState other)
        {
            TimeStep = other.TimeStep;
            NetComponent = other.NetComponent;
            StateBounds = other.StateBounds;
            State = other.State;
        }
    }
}
