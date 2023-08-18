using NuGet.Versioning;
using Spectre.Console.Rendering;

namespace Build.Domain;

public record Build(
    Configuration Configuration,
    ImmutableList<Project> Projects,
    SemanticVersion Version,
    Version AssemblyVersion,
    string Commit,
    string Branch
)
{
    public IRenderable Describe()
    {
        var build = new Tree(":rocket: Build");
        build.AddNode(new Table()
            .HideHeaders()
            .AddColumns("Key", "Value")
            .AddRow("Configuration", Configuration.ToString())
            .AddRow(new Markup("Projects"), BuildProjects())
        );

        build.AddNode("[navy]:pencil: Version[/]")
            .AddNode(new Table()
                .HideHeaders()
                .AddColumns("Key", "Value")
                .AddRow("Full", Version.ToFullString())
                .AddRow("Assembly", AssemblyVersion.ToString())
            );

        build.AddNode("[olive]:toolbox: Git[/]")
            .AddNode(new Table()
                .HideHeaders()
                .AddColumns("Key", "Value")
                .AddRow("Commit", Commit)
                .AddRow("Branch", Branch)
            );
        return build;

        IRenderable BuildProjects()
        {
            var table = new Table();
            table.AddColumn("Entry").HideHeaders();
            table.Border = TableBorder.None;

            foreach (var project in Projects)
            {
                var panel = new Panel(new Table()
                    .HideHeaders()
                    .Border(TableBorder.None)
                    .AddColumns("Key", "Value")
                    .AddRow("Source", project.Source)
                    .AddRow("Build Out.", project.BuildOutput)
                );
                panel.Header = new PanelHeader(project.Name.ToString(), Justify.Left);

                table.AddRow(panel);
            }
            return table;
        }
    }
}