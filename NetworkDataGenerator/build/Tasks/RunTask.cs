namespace Build.Tasks;

[TaskName("Run")]
[IsDependentOn(typeof(BuildTask))]
public sealed class RunTask : FrostingTask<BuildContext>
{
  public override void Run(BuildContext context)
  {
    context.CleanDirectory(context.RunOutputDir);
    context.EnsureDirectoryExists(context.RunOutputDir);

    var runner = new MultiCommandRunner(context, context.RunOutputDir, context.ToolsDir);
    runner.EnsureRunnerInstalled();

    foreach (var project in context.Build.Projects)
    {
      switch (project.Name)
      {
        case ProjectName.TemplateApp:
          AddDotNet(context, project, runner);
          break;
        default:
          break;
      }
    }
    runner.Run();
  }

  private static void AddDotNet(
    BuildContext context,
    Project project,
    MultiCommandRunner runner,
    bool autoStart = true,
    Action<ProcessArgumentBuilder>? args = null)
  {
    if (context.DoWatchSources)
    {
      runner.AddCommand(
        project.Name.ToString(),
        context.Tools.Resolve("dotnet.exe"),
        args: builder =>
        {
          builder
            .Append("watch")
            .AppendSwitchQuoted("--project", project.Source)
            .Append("--")
            .Append("run")
            .AppendSwitch("-c", context.Build.Configuration.ToString());
          if (args != null)
          {
            builder.Append("--");
            args.Invoke(builder);
          }
        },
        autoStart: autoStart
      );
    }
    else
    {
      var exeFile = Directory
        .EnumerateFiles(project.BuildOutput, "*.exe")
        .First();
      runner.AddCommand(
        project.Name.ToString(),
        exeFile,
        args: builder =>
        {
          if (args != null)
          {
            args.Invoke(builder);
          }
        },
        autoStart: autoStart
      );
    }
  }
}
