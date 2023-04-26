namespace Build.Tasks;

[TaskName("Build-Clean")]
public sealed class BuildCleanTask : FrostingTask<BuildContext>
{
    public override bool ShouldRun(BuildContext context)
        => context.DoCleanBuild;

    public override void Run(BuildContext context)
    {
        if (context.DoWatchSources)
        {
            context.Log.Information("Cleaning {0}", context.SourceDir);
            context.CleanDirectories(BuildGlobForSource(context, context.Directory("bin/Debug")));
            context.CleanDirectories(BuildGlobForSource(context, context.Directory("obj/Debug")));
            context.CleanDirectories(BuildGlobForSource(context, context.Directory("bin/Release")));
            context.CleanDirectories(BuildGlobForSource(context, context.Directory("obj/Release")));
        }
        else
        {
            context.Log.Information("Cleaning {0}", context.BuildOutputDir);
            context.CleanDirectory(context.BuildOutputDir);
        }
    }

    private static GlobPattern BuildGlobForSource(BuildContext context, ConvertableDirectoryPath dir)
    => GlobPattern.FromString(context.SourceDir + context.Directory("**") + dir);

}

[TaskName("Build")]
[IsDependentOn(typeof(BuildCleanTask))]
[IsDependentOn(typeof(RestoreTask))]
public sealed class BuildTask : FrostingTask<BuildContext>
{
    public override void Run(BuildContext context)
    {
        context.EnsureDirectoryExists(context.BuildOutputDir);

        foreach (var project in context.Build.Projects)
        {
            context.EnsureDirectoryExists(project.BuildOutput);
            switch (project.Name)
            {
                case ProjectName.TemplateApp:
                    BuildDotNet(context, project);
                    break;
                default:
                    throw new NotImplementedException();
            }
        }
    }

    private void BuildDotNet(BuildContext context, Project project)
    {
        context.Log.Information("Building .NET project '{0}'", project.Name);
        if (context.DoWatchSources)
        {
            context.Log.Information("Nothing to do, as build is done during watch");
            return;
        }

        context.DotNetBuild(project.Source, new DotNetBuildSettings()
        {
            NoRestore = true,
            OutputDirectory = project.BuildOutput,
            Configuration = context.Build.Configuration.ToString(),
            Verbosity = DotNetVerbosity.Minimal,
            MSBuildSettings = new()
            {
                Version = context.Build.Version.ToFullString(),
                AssemblyVersion = context.Build.AssemblyVersion.ToString()
            }
        });
    }
}
