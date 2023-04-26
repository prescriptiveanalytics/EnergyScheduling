using System.Collections.Generic;
using System.Text;
using NetworkDataGenerator.App.Domain.Data;

namespace NetworkDataGenerator.App.Domain
{
    public class TimeStepStates /*: IEncodedSolutionItem*/
    {
        public string Identifier => Period.ToString();
        public int Period { get; }
        public IList<NetComponentState> StateList { get; }

        public TimeStepStates(int period, IList<NetComponentState> stateList)
        {
            Period = period;
            StateList = stateList;
        }

        public TimeStepStates(TimeStepStates other)
        {
            Period = other.Period;
            StateList = new List<NetComponentState>();
            foreach (var state in other.StateList)
            {
                StateList.Add(new NetComponentState(state));
            }
        }


        public NetComponentState Get(Generator gen)
        {
            NetComponentState ncs_ = null;

            foreach (NetComponentState ncs in StateList)
            {
                if (ncs.NetComponent is Generator)
                {
                    Generator generator = ncs.NetComponent as Generator;
                    if (generator.Equals(gen))
                    {
                        ncs_ = ncs;
                        break;
                    }
                }
            }

            return ncs_;
        }

        public NetComponentState Get(EnergyStorageSystem ess)
        {
            NetComponentState ncsEss = null;

            foreach (NetComponentState ncs in StateList)
            {
                if (ncs.NetComponent is EnergyStorageSystem)
                {
                    EnergyStorageSystem essnc = ncs.NetComponent as EnergyStorageSystem;
                    if (essnc.Equals(ess))
                    {
                        ncsEss = ncs;
                        break;
                    }
                }
            }

            return ncsEss;
        }

        public override string ToString()
        {
            StringBuilder sb = new StringBuilder();
            sb.Append($"TimeStep={Period}: ");
            foreach (var state in StateList)
            {
                //sb.Append($"({state.NetComponent.Id}={state.State}) ");
                if (state.NetComponent is Generator)
                {
                    sb.Append($"(G{state.NetComponent.Id}={state.State}) ");
                }
                /*if (state.NetComponent is Load)
                {
                    sb.Append($"(L{state.NetComponent.Id}={state.State}) ");
                }*/
                if (state.NetComponent is EnergyStorageSystem)
                {
                    sb.Append($"(ESS{state.NetComponent.Id}={state.State}) "); // TODO ? can we save dispatch in state (and remove dispatch) ?
                }
                /*if (state.NetComponent is NonProgrammableGenerator
                    && (state.NetComponent as NonProgrammableGenerator).Type == NonProgrammableGeneratorType.Photovoltaic)
                {
                    sb.Append($"(PV{state.NetComponent.Id}={state.State}) ");
                }*/
            }
            return sb.ToString();
        }
    }
}
