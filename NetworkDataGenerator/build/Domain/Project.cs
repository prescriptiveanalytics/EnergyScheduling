namespace Build.Domain;

public enum ProjectName
{
    TemplateApp
}

public record Project(
    ProjectName Name,
    ConvertableDirectoryPath Source,
    ConvertableDirectoryPath BuildOutput
)
{
    public static IEnumerable<Project> BuildUp(IEnumerable<ProjectName> projects, BuildContext context)
    {
        foreach (var project in projects)
        {
            yield return Create(project);
        }

        Project Create(ProjectName project)
            => new(
                project,
                context.SourceDir + project switch
                {
                    ProjectName.TemplateApp => context.Directory("Template.App"),
                    _ => throw new NotImplementedException(),
                },
                context.BuildOutputDir + context.Directory(project.ToString())
            );
    }
}
