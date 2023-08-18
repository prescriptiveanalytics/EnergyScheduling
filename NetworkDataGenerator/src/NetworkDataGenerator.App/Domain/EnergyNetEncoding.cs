using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Text;
using NetworkDataGenerator.App.Domain.Data;

namespace NetworkDataGenerator.App.Domain
{
    public class EnergyNetEncoding /*: IEncodedSolution*/
    {
        public NetworkData NetworkData { get; }
        public IList<TimeStepStates> StatesPerTimeStep { get; set; }

        public int NTimeSteps { get { return StatesPerTimeStep.Count; } }


        /// <summary>
        /// This is the place to store custom properties, which are for example needed in the decoding.
        /// </summary>
        public IDictionary<Type, object> SolutionProperties { get; set; }



        private IDictionary<int, IDictionary<Generator, NetComponentState>> _lookupTableTime2Generators;
        private IDictionary<Generator, IDictionary<int, NetComponentState>> _lookupTableGenerators2Time;
        private IDictionary<EnergyStorageSystem, IDictionary<int, NetComponentState>> _lookupTableESS2Time;
        private IDictionary<int, IDictionary<EnergyStorageSystem, NetComponentState>> _lookupTableTime2ESSs;


        public EnergyNetEncoding(IList<TimeStepStates> statesPerTimeStep, NetworkData networkData)
        {
            StatesPerTimeStep = statesPerTimeStep;
            NetworkData = networkData;

            FillLookupTable(statesPerTimeStep);

            SolutionProperties = new ConcurrentDictionary<Type, object>();
        }

        public EnergyNetEncoding(EnergyNetEncoding other)
        {
            StatesPerTimeStep = new List<TimeStepStates>();
            foreach (var timeStep in other.StatesPerTimeStep)
            {
                StatesPerTimeStep.Add(new TimeStepStates(timeStep));
            }
            NetworkData = other.NetworkData;

            FillLookupTable(StatesPerTimeStep);

            SolutionProperties = new ConcurrentDictionary<Type, object>(other.SolutionProperties);
        }


        private void FillLookupTable(IList<TimeStepStates> statesPerTimeStep)
        {
            Dictionary<int, IDictionary<Generator, NetComponentState>> time2Generators = new Dictionary<int, IDictionary<Generator, NetComponentState>>();
            Dictionary<int, IDictionary<EnergyStorageSystem, NetComponentState>> time2ESSs = new Dictionary<int, IDictionary<EnergyStorageSystem, NetComponentState>>();
            IDictionary<EnergyStorageSystem, IDictionary<int, NetComponentState>> ESS2Time = new Dictionary<EnergyStorageSystem, IDictionary<int, NetComponentState>>();
            Dictionary<Generator, IDictionary<int, NetComponentState>> generators2Time = new Dictionary<Generator, IDictionary<int, NetComponentState>>();

            foreach (TimeStepStates tss in statesPerTimeStep)
            {
                Dictionary<Generator, NetComponentState> auxTableGen = new Dictionary<Generator, NetComponentState>();
                foreach (Generator g in NetworkData.Generators)
                {
                    NetComponentState foundNCS = null;

                    foreach (NetComponentState ncs in tss.StateList)
                    {
                        if (ncs.NetComponent == g)
                        {
                            foundNCS = ncs;
                            break;
                        }
                    }

                    if (foundNCS != null)
                    {
                        auxTableGen[g] = foundNCS;
                    }
                    else
                    {
                        throw new Exception();
                    }
                }
                time2Generators[tss.Period] = auxTableGen;

                Dictionary<EnergyStorageSystem, NetComponentState> auxTableESS = new Dictionary<EnergyStorageSystem, NetComponentState>();
                foreach (EnergyStorageSystem ess in NetworkData.EnergyStorageSystems)
                {
                    NetComponentState foundNCS = null;

                    foreach (NetComponentState ncs in tss.StateList)
                    {
                        if (ncs.NetComponent == ess)
                        {
                            foundNCS = ncs;
                            break;
                        }
                    }

                    if (foundNCS != null)
                    {
                        auxTableESS[ess] = foundNCS;
                    }
                    else
                    {
                        throw new Exception();
                    }
                }
                time2ESSs[tss.Period] = auxTableESS;

                foreach (NetComponentState ncs in tss.StateList)
                {
                    if( ncs.NetComponent is Generator )
                    {
                        Generator g = ncs.NetComponent as Generator;

                        bool success = generators2Time.TryGetValue(g, out IDictionary<int, NetComponentState> auxTable);
                        if( !success)
                        {
                            auxTable = new Dictionary<int, NetComponentState>();
                            generators2Time[g] = auxTable;
                        }
                        auxTable[tss.Period] = ncs;
                    }
                    else if( ncs.NetComponent is EnergyStorageSystem)
                    {
                        EnergyStorageSystem ess = (EnergyStorageSystem)ncs.NetComponent;

                        bool success = ESS2Time.TryGetValue(ess, out IDictionary<int, NetComponentState> auxTable);
                        if( !success )
                        {
                            auxTable = new Dictionary<int, NetComponentState>();
                            ESS2Time[ess] = auxTable;
                        }
                        auxTable[tss.Period] = ncs;
                    }
                }
            }

            _lookupTableTime2Generators = time2Generators;
            _lookupTableTime2ESSs = time2ESSs;
            _lookupTableGenerators2Time = generators2Time;
            _lookupTableESS2Time = ESS2Time;
        }


        //public IEncodedSolution ShallowCopy()
        //{
        //    return new EnergyNetEncoding(this);
        //}


        public bool CheckLogicalFeasibility()
        {
            bool isValid = true;

            // Check existence of all timesteps
            for (int i = 1; i <= NTimeSteps; i++)
            {
                // necessary ?
            }

            // Check minimal up and down times
            foreach (Generator g in NetworkData.Generators)
            {
                int currentLength = 1;
                bool isUp = _lookupTableTime2Generators[0][g].State == 1;

                // TODO: Maybe provide lookup via generator and not via time?
                for (int i = 0; i < NTimeSteps; i++)
                {
                    bool willBeUp = _lookupTableTime2Generators[i][g].State == 1;
                    if (willBeUp == isUp)
                    {
                        currentLength++;
                    }
                    else
                    {
                        // Check min times:
                        if (isUp)
                        {
                            if (currentLength < g.MinUpTime)
                            {
                                //logger.Fatal($"Minimal upTime {g.MinUpTime} for generator {g.Id} in timeslot {i} is violated! ({currentLength})");
                                isValid = false;
                            }
                        }
                        else
                        {
                            if( currentLength < g.MinDownTime)
                            {
                                //logger.Fatal($"Minimal downTime {g.MinDownTime} for generator {g.Id} in timeslot {i} is violated! ({currentLength})");
                                isValid = false;
                            }
                        }

                        currentLength = 1;
                    }

                    isUp = willBeUp;
                }
            }

            // check necessary power production
            foreach (TimeStepStates tss in StatesPerTimeStep)
            {
                double loads = 0;
                double maxProduction = 0;
                double npgProduction = 0;

                foreach (NetComponentState ncs in tss.StateList)
                {
                    if (ncs.NetComponent is Generator)
                    {
                        Generator g = ncs.NetComponent as Generator;
                        if ((int)_lookupTableTime2Generators[tss.Period][g].State == 1)
                        {
                            maxProduction += g.MaxRealPowerOutput;
                        }
                    }
                    else if (ncs.NetComponent is EnergyStorageSystem)
                    {
                        EnergyStorageSystem ess = ncs.NetComponent as EnergyStorageSystem;
                        int essState = (int)_lookupTableTime2ESSs[tss.Period][ess].State;
                        if (essState == 1)
                        {
                            maxProduction += ess.MaxDischargingPower;
                        }
                        else if( essState == -1 )
                        {
                            loads += ess.MinChargingPower;
                        }
                    }
                    else if (ncs.NetComponent is Load)
                    {
                        //Load l = ncs.NetComponent as Load;
                        loads += ncs.State;
                    }
                    else if (ncs.NetComponent is NonProgrammableGenerator)
                    {
                        npgProduction += ncs.State;
                    }
                }

                if (maxProduction + npgProduction < loads * NetworkData.SeamlessIndex)
                {
                    //logger.Fatal($"Maximal power production ({maxProduction}) is lower as loads ({loads}) in timeslot {tss.Period}!");
                    isValid = false;
                }

            }
            
            return isValid;
        }

        public string PrintComponentTable()
        {
            StringBuilder sb = new StringBuilder();

            sb.AppendLine().Append(" G: ");
            for (int i = 0; i < NTimeSteps; i++) {
                sb.Append(i.ToString().PadLeft(2)).Append("|");
            }
            sb.AppendLine();
            foreach( Generator g in NetworkData.Generators)
            {
                sb.Append(g.Id.ToString().PadLeft(2)).Append(": ");
                for( int i=0; i<NTimeSteps; i++)
                {
                    sb.Append(_lookupTableGenerators2Time[g][i].State.ToString().PadLeft(2)).Append("|");
                }
                sb.AppendLine();
            }
            foreach( EnergyStorageSystem ess in NetworkData.EnergyStorageSystems)
            {
                sb.Append(ess.Id.ToString().PadLeft(2)).Append(": ");
                for( int i=0; i<NTimeSteps; i++)
                {
                    sb.Append(_lookupTableESS2Time[ess][i].State.ToString().PadLeft(2)).Append("|");
                }
                sb.AppendLine();
            }

            string s = sb.ToString();
            return s;
        }


        public void LogComponentTable()
        {
            string str = PrintComponentTable();
            //logger.Info(str);
        }
    }
}
