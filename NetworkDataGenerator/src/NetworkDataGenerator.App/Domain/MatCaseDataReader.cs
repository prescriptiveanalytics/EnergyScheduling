using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;

namespace NetworkDataGenerator.App.Domain
{
    public class MatCaseDataReader
    {
        public CaseProblemData ProblemData { get; private set; }

        public MatCaseDataReader(StreamReader reader, StreamReader readerAux1, StreamReader readerAux2, StreamReader readerAux3, StreamReader readerAux4)
        {
            ProblemData = new CaseProblemData();
            ReadMatFile(reader);
            if (readerAux1 != null)
                ReadMatFile(readerAux1);
            if (readerAux2 != null)
                ReadMatFile(readerAux2);
            if (readerAux3 != null)
                ReadMatFile(readerAux3);
            if (readerAux4 != null)
                ReadMatFile(readerAux4);
        }

        public void ReadMatFile(StreamReader reader)
        {
            string line = reader.ReadLine();
            while (line != null)
            {
                if (line.ToLower().Equals("# name: basemva"))
                {
                    while (line.StartsWith("#"))
                        line = reader.ReadLine();
                    bool success = double.TryParse(line, NumberStyles.Any, CultureInfo.InvariantCulture, out double val);
                    if (success) ProblemData.BaseMVA = val;
                }

                if (line.ToLower().Equals("# name: bus"))
                {
                    ParseArray(line, reader, ProblemData.Bus);
                }

                if (line.ToLower().Equals("# name: gen"))
                {
                    ParseArray(line, reader, ProblemData.Gen);
                }

                if (line.ToLower().Equals("# name: branch"))
                {
                    ParseArray(line, reader, ProblemData.Branch);
                }

                if (line.ToLower().Equals("# name: gencost"))
                {
                    ParseArray(line, reader, ProblemData.GenCost);
                }

                if (line.ToLower().Equals("# name: objval"))
                {
                    while (line.StartsWith("#"))
                        line = reader.ReadLine();

                    bool success = double.TryParse(line, NumberStyles.Any, CultureInfo.InvariantCulture, out double val);
                    if (success) ProblemData.ObjVal = val;
                }

                if (line.ToLower().Equals("# name: success"))
                {
                    while (line.StartsWith("#"))
                        line = reader.ReadLine();

                    ProblemData.Converged = Convert.ToBoolean(int.Parse(line));
                }

                if (line.ToLower().Equals("# name: genauxdata"))
                {
                    ParseArray(line, reader, ProblemData.GenAuxiliaryData);
                }

                if (line.ToLower().Equals("# name: ess"))
                {
                    ParseArray(line, reader, ProblemData.EnergyStorageSystem);
                }

                if (line.ToLower().Equals("# name: marketprice"))
                {
                    ParseArray(line, reader, ProblemData.MarketPrice);
                }

                if (line.ToLower().Equals("# name: pv"))
                {
                    ParseArray(line, reader, ProblemData.NonProgrammableGenerator);
                }

                line = reader.ReadLine();
            }
        }

        private void ParseArray(string line, StreamReader reader, IList<IList<double>> doubleArray)
        {
            while (line.StartsWith("#"))
                line = reader.ReadLine();

            while (!string.IsNullOrEmpty(line) && !string.IsNullOrWhiteSpace(line))
            {
                string[] rowValues = line.Split(" ", StringSplitOptions.RemoveEmptyEntries);
                IList<double> row = new List<double>();
                foreach (string sval in rowValues)
                {
                    bool success = double.TryParse(sval, NumberStyles.Any, CultureInfo.InvariantCulture, out double val);
                    if (success) row.Add(val);
                }
                doubleArray.Add(row);

                line = reader.ReadLine();
            }
        }
    }
}
