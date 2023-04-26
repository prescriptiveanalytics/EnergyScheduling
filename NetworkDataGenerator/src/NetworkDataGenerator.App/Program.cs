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

string pathLoadProfile = @"..\..\..\..\..\Resources\LoadProfiles\loadprofile_industrial1_3.2.2016_max.csv";

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


