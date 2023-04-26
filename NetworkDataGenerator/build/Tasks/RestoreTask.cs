namespace Build.Tasks;

[TaskName("Restore")]
public sealed class RestoreTask : FrostingTask<BuildContext>
{
    public override void Run(BuildContext context)
    {
        foreach (var project in context.Build.Projects)
        {
            switch (project.Name)
            {
                case ProjectName.TemplateApp:
                    RestoreDotNet(context, project);
                    break;
                default:
                    throw new NotImplementedException();
            }
        }
    }

    private static void RestoreDotNet(BuildContext context, Project project)
    {
        context.Log.Information("Restoring .NET project '{0}'", project.Name);
        context.DotNetRestore(project.Source, new DotNetRestoreSettings()
        {
            ArgumentCustomization = args => args.Append($"-p:Configuration={context.Build.Configuration}"),
            Verbosity = DotNetVerbosity.Minimal
        });
    }
}
