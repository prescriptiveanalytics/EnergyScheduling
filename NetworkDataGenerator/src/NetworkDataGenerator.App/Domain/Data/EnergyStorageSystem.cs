using System;
using System.Collections.Generic;
using System.Text;

namespace NetworkDataGenerator.App.Domain.Data
{
    public enum EnergyStorageSystemState
    {
        Idle = 0,
        Charging = -1,
        Discharging = 1
    }

    public class EnergyStorageSystem : INetComponent
    {
        public Bus Bus { get; }
        public int Id { get; }
        public double Capacity { get; set; } // MW h or MW t, t = time interval (15 min, 1h, ...)
        public double MinChargingPower { get; set; } // MW
        public double MaxChargingPower { get; set; } // MW
        public double MinDischargingPower { get; set; } // MW
        public double MaxDischargingPower { get; set; } // MW

        public int
            MinChargingTime
        {
            get;
            set;
        } // integer multiple of time units (e.g. if t = 1h, then min charging time = 3h)

        public int MinDischargingTime { get; set; } // integer multiple of time units
        public double ChargingEfficiencyFactor { get; set; } // in [0,1]
        public double DischargingEfficiencyFactor { get; set; } // in [0,1]
        public double InitialSOC { get; set; } // initial SOC (State of Charge) TODO: or defined somewhere else?

        public Dictionary<int, double> PowerOutput { get; set; }


        public EnergyStorageSystem(Bus bus, int id)
        {
            Bus = bus;
            Id = id;
        }

        public bool Equals(EnergyStorageSystem nc)
        {
            var other = nc as EnergyStorageSystem;
            if (other != null && Id == other.Id)
            {
                return true;
            }
            return false;
        }
    }
}
