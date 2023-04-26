
namespace Build;

public sealed class BuildSetup : FrostingSetup<BuildContext>
{
    public override void Setup(BuildContext context, ISetupContext setup)
    {
        if (context.Log.Verbosity >= Verbosity.Normal)
        {
            AnsiConsole.Write(context.Build.Describe());
        }

        StartSonarAnalysis(context);
    }

    private void StartSonarAnalysis(BuildContext context)
    {
        if (!context.DoSonarAnalysis) return;
        if (context.SonarToken == null)
            throw new ArgumentNullException(nameof(context.SonarToken), "Sonar token must be set!");

        context.Log.Information("Starting SonarQube analysis");
        context.SonarQubeBegin("miba_aet", context.SonarToken, context.SonarConfigFile);
    }
}
