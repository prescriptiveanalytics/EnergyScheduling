using System;
using System.Collections.Generic;
using NetworkDataGenerator.App.Domain.Data;

namespace NetworkDataGenerator.App.Domain
{
    public class TimeStepOpf
    {
        public int Period { get; }
        public TimeStepStates StateList { get; set; }
        public double OpfObjectiveFunctionValue { get; set; }
        public bool IsFeasible { get; set; }
        // some structure to hold generation values etc
        // real power output for each generator 
        public IList<Tuple<Generator, double>> RealPowerGeneration { get; set; }
        public IList<Tuple<Generator, double>> RealPowerReserve { get; set; }
        public IList<Tuple<EnergyStorageSystem, double>> RealPowerDispatch { get; set; } // for energy storage systems
        public double ExtGridImportExport { get; set; }

        public TimeStepOpf(int period, IList<NetComponentState> stateList)
        {
            Period = period;
            StateList = StateList;
        }

        public TimeStepOpf(TimeStepOpf other)
        {
            Period = other.Period;
            StateList = new TimeStepStates(other.StateList);
        }

        public double GetPower(Generator g)
        {
            double power = 0;

            if (RealPowerGeneration != null)
            {
                foreach (Tuple<Generator, double> t in RealPowerGeneration)
                {
                    if (g.Id == t.Item1.Id)
                    {
                        power = t.Item2;
                        break;
                    }
                }
            }

            return power;
        }


        public double GetPowerReserve(Generator g)
        {
            double power = 0;

            if (RealPowerReserve != null)
            {
                foreach (Tuple<Generator, double> t in RealPowerReserve)
                {
                    if (g.Id == t.Item1.Id)
                    {
                        power = t.Item2;
                        break;
                    }
                }
            }

            return power;
        }


        public int GetState(Generator g)
        {
            int state = 0;

            if( StateList != null )
            {
                NetComponentState ncs = StateList.Get(g);
                state = (int)ncs.State;
            }

            return state;
        }
    }
}
