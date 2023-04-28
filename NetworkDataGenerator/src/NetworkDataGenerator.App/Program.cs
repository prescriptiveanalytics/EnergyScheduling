using System.Reflection.PortableExecutable;
using System.Text;
using NetworkDataGenerator.App;
using NetworkDataGenerator.App.Domain;
using NetworkDataGenerator.App.Domain.Data;

Console.WriteLine("NetworkDataGeneratorApp");

Console.WriteLine("Setup configuration"); 
MatpowerDecoderConfigurationContext matpowerDecodingConfigurationContext = new MatpowerDecoderConfigurationContext()
{
    //DecodingStartedCallback = (context, state, solution) => { },
    //DecodingFinishedCallback = (context, state, solution) => { },
    //NewItemDecodingStartedCallback = (context, state, item) => { },
    //NewItemDecodingFinishedCallback = (context, state, item) => { },
    //CancellationCriterionCallback = state => false,
    //CancellationCallback = (context, state, solution) => { },
    //ExportSolutionCallback = (solution) => "",
    //DecodingStateInfo = new DecoderStateInformationDummy(),
    //Evaluator = evaluator,

    PathToOpfToolExe = @"C:\Program Files\GNU Octave\Octave-8.1.0\mingw64\bin\octave-cli.exe",
    OpfScriptFilePath = @"..\..\..\..\..\Resources\Scripts\callOpf.m",
    CaseFileDirectory = Path.GetFullPath(@"..\..\..\..\..\Resources\Data\"),
    CaseFileName = "case.mat",
    SolvedCaseFileName = "solvedcase.mat",

    RunParallel = false,
    MaxConcurrency = 1
};

string pathLoadProfile = @"..\..\..\..\..\Resources\LoadProfiles\identity_loadprofile.csv";

IDictionary<string, string> encoderArguments = new Dictionary<string, string>();
encoderArguments.Add("NumberOfTimeSteps", "1");
encoderArguments.Add("TimeResolutionInHours", "1");
encoderArguments.Add("DecoderType", "Matpower");
encoderArguments.Add("LoadProfile", pathLoadProfile);
encoderArguments.Add("CaseFileAuxiliaryData", "");
encoderArguments.Add("CaseFileESS", "");
encoderArguments.Add("CaseFileMarketPrice", "");
encoderArguments.Add("CaseFilePV", "");
encoderArguments.Add("PVProfile", "");
encoderArguments.Add("SeamlessIndex", "1.0");
encoderArguments.Add("ReserveFactor", "0.0");

string _caseFileAux = @"..\..\..\..\..\Resources\Data\case5.mat";
StreamReader reader = new StreamReader(_caseFileAux);
PowerGridProblemEncoder encoder = new PowerGridProblemEncoder(reader, encoderArguments);

EnergyNetEncoding encodedSolution = encoder.GenerateEncodedSolution();
MatpowerOpfDecoder matpowerDecoder = encoder.GetSolutionDecoder(matpowerDecodingConfigurationContext);
NetPowerFlow opf = matpowerDecoder.InitSolution(encodedSolution);

matpowerDecoder.Decode(encodedSolution, opf);

MatCaseDataWriter mcdw = encoder.GetDataWriter();
mcdw.WriteSolution(opf, @"..\..\..\..\..\Resources\Data\solution_test.mat");

for (int i = 0; i < 500; i += 10)
{
    encodedSolution.NetworkData.Buses[1].Loads[0].RealPowerDemand = i;
    var stateList = encodedSolution.StatesPerTimeStep.First();
    stateList.StateList[5].State = i;

    encodedSolution.PrintComponentTable();
    matpowerDecoder.Decode(encodedSolution, opf);

    StringBuilder output = new StringBuilder();
    output.Append(String.Format("{0,5}", i));

    for (int k = 0; k < opf.OpfPerTimeStep[0].RealPowerGeneration.Count; k++)
    {
        output.Append(' ');
        output.Append(String.Format("{0:N2}", opf.OpfPerTimeStep[0].RealPowerGeneration[k].Item2));
    }
    output.AppendLine();

    Console.WriteLine(output.ToString());


    // solved case would be the correct solution
    // the following statement would not work, because the problem data is not updated
    //mcdw.WriteSolution(opf, $@"..\..\..\..\..\Resources\Data\solution_test_{i}.mat");
}


