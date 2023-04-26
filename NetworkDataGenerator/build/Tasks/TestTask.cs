namespace Build.Tasks;

[TaskName("Test")]
public sealed class TestTask : FrostingTask<BuildContext>
{
    public override void Run(BuildContext context)
    {
        context.EnsureDirectoryExists(context.TestOutputDir);

        foreach (var project in context.Build.Projects)
        {
            switch (project.Name)
            {
                case ProjectName.TemplateApp:
                    TestDotNet(context, context.SourceDir);
                    break;
                default:
                    throw new NotImplementedException();
            }
        }
    }

    private static void TestDotNet(BuildContext context, ConvertableDirectoryPath dir)
    {
        context.Log.Information("Running .NET test projects under '{0}'", dir);

        var settings = new DotNetTestSettings()
        {
            Configuration = context.Build.Configuration.ToString(),
            ResultsDirectory = context.TestOutputDir,
            Verbosity = DotNetVerbosity.Minimal,
            Loggers = new[] { "junit;LogFileName={assembly}-results.xml;MethodFormat=Class;FailureBodyFormat=Verbose" }
        };

        if (context.Build.Configuration == Configuration.Debug)
        {
            // code coverage can only be done in Debug
            settings.Collectors = new[] { "XPlat Code Coverage" };
            settings.Settings = context.BuildDir + context.File("coverlet.runsettings");
        }
        else
        {
            context.Log.Warning("No code coverage can be generated as this is not a Debug build!");
        }

        context.DotNetTest(dir, settings);
    }
}
