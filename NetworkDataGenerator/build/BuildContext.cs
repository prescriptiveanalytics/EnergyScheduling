namespace Build;

public class BuildContext : FrostingContext
{
    public BuildContext(ICakeContext context)
        : base(context)
    {
        RepoDir = context.Directory(".");
        SourceDir = RepoDir + context.Directory("src");

        DocDir = RepoDir + context.Directory("doc");

        BuildDir = RepoDir + context.Directory("build");
        OutputDir = BuildDir + context.Directory("out");
        BuildOutputDir = OutputDir + context.Directory("build");
        PackageOutputDir = OutputDir + context.Directory("package");
        TestOutputDir = OutputDir + context.Directory("test");
        RunOutputDir = OutputDir + context.Directory("run");

        ToolsDir = RepoDir + context.Directory("tools");

        SonarConfigFile = BuildDir + context.File("SonarQube.Analysis.xml");

        DoCleanBuild = context.HasArgument("clean");
        DoWatchSources = context.HasArgument("watch");
        DoSonarAnalysis = context.HasArgument("sonar");

        AllProjects = Project.BuildUp(
            Enum.GetValues<ProjectName>(),
            this
        ).ToImmutableDictionary(p => p.Name, p => p);

        SonarToken = context.EnvironmentVariable("SONAR_TOKEN");

        var config = context.Argument("config", Domain.Configuration.Debug);

        // Determine projects to build / restore / etc.
        var projectNames = context.Arguments<ProjectName>(
            "project", Enum.GetValues<ProjectName>()
        );
        var projects = projectNames
            .Select(p => AllProjects[p])
            .ToImmutableList();

        // Create default Build record (should be refined in BuildSetup)
        Build = new Domain.Build(
            config,
            projects,
            new(0, 0, 0),
            new(0, 0, 0),
            Commit: "",
            Branch: ""
        );
        BuildSystem = context.BuildSystem();
    }

    public ConvertableDirectoryPath RepoDir { get; }
    public ConvertableDirectoryPath SourceDir { get; }
    public ConvertableDirectoryPath DocDir { get; }
    public ConvertableDirectoryPath ToolsDir { get; }

    public ConvertableDirectoryPath BuildDir { get; }
    public ConvertableDirectoryPath OutputDir { get; }
    public ConvertableDirectoryPath BuildOutputDir { get; }
    public ConvertableDirectoryPath PackageOutputDir { get; }
    public ConvertableDirectoryPath TestOutputDir { get; }
    public ConvertableDirectoryPath RunOutputDir { get; }

    public ConvertableFilePath SonarConfigFile { get; }

    public ImmutableDictionary<ProjectName, Project> AllProjects { get; }

    public bool DoCleanBuild { get; }
    public bool DoWatchSources { get; }
    public bool DoSonarAnalysis { get; }

    public string SonarToken { get; }

    public BuildSystem BuildSystem { get; }
    public Domain.Build Build { get; internal set; }
}