using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using NetworkDataGenerator.App.Domain.Data;

namespace NetworkDataGenerator.App.Domain
{
    public class MatCaseDataWriter
    {
        private readonly CaseProblemData _problemData;

        public MatCaseDataWriter(CaseProblemData problemData)
        {
            _problemData = problemData;
        }

        public string GetSolutionString(NetPowerFlow solution)
        {
                NetPowerFlow powerFlow = solution as NetPowerFlow;

                StringBuilder sb = new StringBuilder();
                string separator = " ";
                CultureInfo culture = CultureInfo.InvariantCulture;

            sb.AppendLine("# name: baseMVA");
            sb.AppendLine("# type: scalar");
            sb.AppendLine(_problemData.BaseMVA.ToString(culture));
            sb.AppendLine();
            sb.AppendLine();
            sb.AppendLine("# name: bus");
            sb.AppendLine("# type: matrix");
            sb.AppendLine("# rows: 5");
            sb.AppendLine("# columns: 13");

            for (int i = 0; i < _problemData.Bus.Count; ++i)
            {
                IList<double> originalBusData = _problemData.Bus[i];
                Bus encodingBus = powerFlow.EnergyNet.NetworkData.Buses[i];

                // TODO: which of the values need to be replaced?
                // 0        1       2   3   4   5   6       7   8   9       10      11      12
                // bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin
                sb.Append(separator);
                sb.Append(encodingBus.Id);
                sb.Append(separator);
                sb.Append((int)encodingBus.Type);
                sb.Append(separator);
                sb.Append(originalBusData[2].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[3].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[4].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[5].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[6].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[7].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[8].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[9].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[10].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[11].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[12].ToString(culture));
                sb.Append(Environment.NewLine);
            }

            sb.AppendLine();
            sb.AppendLine();
            sb.AppendLine("# name: gen");
            sb.AppendLine("# type: matrix");
            sb.AppendLine("# rows: 5");
            sb.AppendLine("# columns: 21");

            for (int i = 0; i < _problemData.Gen.Count; ++i)
            {
                IList<double> originalGenData = _problemData.Gen[i];
                Generator encodingGen = powerFlow.EnergyNet.NetworkData.Generators[i];

                // TODO: which of the values need to be replaced?
                // 0    1   2   3       4       5   6       7       8       9       10  11  12      13      14      15      16          17      18      19      20
                // bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin	Pc1	Pc2	Qc1min	Qc1max	Qc2min	Qc2max	ramp_agc	ramp_10	ramp_30	ramp_q	apf
                sb.Append(separator);
                sb.Append(encodingGen.Bus.Id);
                sb.Append(separator);
                sb.Append(originalGenData[1].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[2].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[3].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[4].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[5].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[6].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[7].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[8].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[9].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[10].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[11].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[12].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[13].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[14].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[15].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[16].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[17].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[18].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[19].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[20].ToString(culture));
                sb.Append(Environment.NewLine);
            }

            sb.AppendLine();
            sb.AppendLine();
            sb.AppendLine("# name: branch");
            sb.AppendLine("# type: matrix");
            sb.AppendLine("# rows: 6");
            sb.AppendLine("# columns: 13");

            for (int i = 0; i < _problemData.Branch.Count; ++i)
            {
                IList<double> originalBranchData = _problemData.Branch[i];

                // 0    1       2   3   4   5       6       7       8       9       10      11      12      13  14  15  16  17      18      19          20
                // fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax	Pf	Qf	Pt	Qt	mu_Sf	mu_St	mu_angmin	mu_angmax
                sb.Append(separator);
                sb.Append(originalBranchData[0].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[1].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[2].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[3].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[4].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[5].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[6].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[7].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[8].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[9].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[10].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[11].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[12].ToString(culture));
                sb.Append(Environment.NewLine);
            }

            sb.AppendLine();
            sb.AppendLine();
            sb.AppendLine("# name: gencost");
            sb.AppendLine("# type: matrix");
            sb.AppendLine("# rows: 5");
            sb.AppendLine("# columns: 6");

            for (int i = 0; i < _problemData.GenCost.Count; ++i)
            {
                IList<double> originalGenCostData = _problemData.GenCost[i];

                // 0   1       2           3 4  ....
                // 1   startup shutdown    n x1  y1  ... xn yn
                // 2   startup shutdown    n c(n-1) ...	c0
                sb.Append(separator);
                sb.Append(originalGenCostData[0].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenCostData[1].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenCostData[2].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenCostData[3].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenCostData[4].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenCostData[5].ToString(culture));
                sb.Append(Environment.NewLine);
            }

            return sb.ToString();
            }

        public void WriteSolution(NetPowerFlow solution, string pathAndFilename)
        {
            string directoryName = Path.GetDirectoryName(pathAndFilename);
            if (!string.IsNullOrEmpty(directoryName) && !Directory.Exists(directoryName))
                Directory.CreateDirectory(directoryName);

            using var sw = new StreamWriter(pathAndFilename);
            sw.Write(GetSolutionString(solution));
        }

        public void WriteSolution(TimeStepStates encodedItem, string pathAndFilename)
        {
            TimeStepStates timeStep = encodedItem as TimeStepStates;

            StringBuilder sb = new StringBuilder();
            string separator = " ";
            CultureInfo culture = CultureInfo.InvariantCulture;

            sb.AppendLine("# name: baseMVA");
            sb.AppendLine("# type: scalar");
            sb.AppendLine(_problemData.BaseMVA.ToString(culture));
            sb.AppendLine();
            sb.AppendLine();
            sb.AppendLine("# name: bus");
            sb.AppendLine("# type: matrix");
            sb.AppendLine("# rows: " + _problemData.Bus.Count);
            sb.AppendLine("# columns: 13");

            for (int i = 0; i < _problemData.Bus.Count; ++i)
            {
                IList<double> originalBusData = _problemData.Bus[i];
                var load = timeStep.StateList.FirstOrDefault(x => x.NetComponent is Load && (x.NetComponent as Load).Bus.Id == (int)originalBusData[0]);
                string realPowerDemand = originalBusData[2].ToString(culture);
                if (load != null) realPowerDemand = load.State.ToString(culture);

                // TODO: which of the values need to be replaced?
                // 0        1       2   3   4   5   6       7   8   9       10      11      12
                // bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin
                sb.Append(separator);
                sb.Append(originalBusData[0].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[1].ToString(culture));
                sb.Append(separator);
                sb.Append(realPowerDemand);
                sb.Append(separator);
                sb.Append(originalBusData[3].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[4].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[5].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[6].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[7].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[8].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[9].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[10].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[11].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBusData[12].ToString(culture));
                sb.Append(Environment.NewLine);
            }

            sb.AppendLine();
            sb.AppendLine();
            sb.AppendLine("# name: gen");
            sb.AppendLine("# type: matrix");
            sb.AppendLine("# rows: " + _problemData.Gen.Count);
            sb.AppendLine("# columns: 21");

            for (int i = 0; i < _problemData.Gen.Count; ++i)
            {
                IList<double> originalGenData = _problemData.Gen[i];
                // The ID of the generator is index + 1! Using the first field or originalGenData is wrong since that is
                // the busID which is not unique (several generator units can occur at one bus).
                int id = i + 1;
                double state = timeStep.StateList.First(s => s.NetComponent.Id == id).State;

                // TODO: which of the values need to be replaced?
                // 0    1   2   3       4       5   6       7       8       9       10  11  12      13      14      15      16          17      18      19      20
                // bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin	Pc1	Pc2	Qc1min	Qc1max	Qc2min	Qc2max	ramp_agc	ramp_10	ramp_30	ramp_q	apf
                sb.Append(separator);
                sb.Append(originalGenData[0].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[1].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[2].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[3].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[4].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[5].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[6].ToString(culture));
                sb.Append(separator);
                sb.Append(state.ToString());
                sb.Append(separator);
                sb.Append(originalGenData[8].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[9].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[10].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[11].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[12].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[13].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[14].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[15].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[16].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[17].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[18].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[19].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenData[20].ToString(culture));
                sb.Append(Environment.NewLine);
            }

            sb.AppendLine();
            sb.AppendLine();
            sb.AppendLine("# name: branch");
            sb.AppendLine("# type: matrix");
            sb.AppendLine("# rows: " + _problemData.Branch.Count);
            sb.AppendLine("# columns: 13");

            for (int i = 0; i < _problemData.Branch.Count; ++i)
            {
                IList<double> originalBranchData = _problemData.Branch[i];

                // 0    1       2   3   4   5       6       7       8       9       10      11      12      13  14  15  16  17      18      19          20
                // fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax	Pf	Qf	Pt	Qt	mu_Sf	mu_St	mu_angmin	mu_angmax
                sb.Append(separator);
                sb.Append(originalBranchData[0].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[1].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[2].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[3].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[4].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[5].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[6].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[7].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[8].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[9].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[10].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[11].ToString(culture));
                sb.Append(separator);
                sb.Append(originalBranchData[12].ToString(culture));
                sb.Append(Environment.NewLine);
            }

            sb.AppendLine();
            sb.AppendLine();
            sb.AppendLine("# name: gencost");
            sb.AppendLine("# type: matrix");
            sb.AppendLine("# rows: " + _problemData.Gen.Count());
            sb.AppendLine("# columns: " + (_problemData.GenCost[0].ElementAt(3) + 4));

            for (int i = 0; i < _problemData.GenCost.Count; ++i)
            {
                IList<double> originalGenCostData = _problemData.GenCost[i];

                // 0   1       2           3 4  ....
                // 1   startup shutdown    n x1  y1  ... xn yn
                // 2   startup shutdown    n c(n-1) ...	c0
                sb.Append(separator);
                sb.Append(originalGenCostData[0].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenCostData[1].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenCostData[2].ToString(culture));
                sb.Append(separator);
                sb.Append(originalGenCostData[3].ToString(culture));
                sb.Append(separator);
                int n = (int)originalGenCostData[3];
                for (int j = 1; j <= n - 1; j++)
                {
                    sb.Append(originalGenCostData[3 + j].ToString(culture));
                    sb.Append(separator);
                }
                sb.Append(originalGenCostData[3 + n].ToString(culture));
                sb.Append(Environment.NewLine);
            }


            string directoryName = Path.GetDirectoryName(pathAndFilename);
            if (!string.IsNullOrEmpty(directoryName) && !Directory.Exists(directoryName))
                Directory.CreateDirectory(directoryName);

            using var sw = new StreamWriter(pathAndFilename);
            sw.Write(sb.ToString());
        }
    }
}
