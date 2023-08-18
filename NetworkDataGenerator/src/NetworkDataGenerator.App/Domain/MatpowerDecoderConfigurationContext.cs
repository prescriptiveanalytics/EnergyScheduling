using System;
using System.IO;

namespace NetworkDataGenerator.App.Domain
{
    public class MatpowerDecoderConfigurationContext
    {
        //public IEvaluator Evaluator { get; set; }
        //public DecodingCancellationCriterionDelegate CancellationCriterionCallback { get; set; }
        //public SolutionDecodingActionDelegate CancellationCallback { get; set; }
        //public SolutionDecodingActionDelegate DecodingStartedCallback { get; set; }
        //public SolutionDecodingActionDelegate DecodingFinishedCallback { get; set; }
        //public SolutionDecodingItemActionDelegate NewItemDecodingStartedCallback { get; set; }
        //public SolutionDecodingItemActionDelegate NewItemDecodingFinishedCallback { get; set; }
        //public ExportSolutionDelegate ExportSolutionCallback { get; set; }
        //public ISolutionDecoderStateInformation DecodingStateInfo { get; set; }
        public string PathToOpfToolExe { get; set; }
        public string OpfScriptFilePath { get; set; }
        public string CaseFileDirectory { get; set; }
        public string CaseFileName { get; set; }
        public string SolvedCaseFileName { get; set; }
        public Func<StreamReader, StreamReader, StreamReader, StreamReader, StreamReader, CaseProblemData> ImportCaseFile { get; set; }
        //public Func<StreamReader, CaseProblemData> ImportCaseFile { get; set; }
        public Action<TimeStepStates, string> ExportCaseFile { get; set; }
        public bool RunParallel { get; set; }
        public int MaxConcurrency { get; set; }
    }
}
