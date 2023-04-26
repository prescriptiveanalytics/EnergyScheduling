using Build;

var projectDir = new DirectoryInfo(".");
System.Environment.CurrentDirectory = projectDir.Parent?.FullName ?? "."; // switch to repo. root

return new CakeHost()
    .InstallTool(new Uri("nuget:?package=GitVersion.CommandLine&version=5.8.1"))
    .InstallTool(new Uri("nuget:?package=dotnet-sonarscanner&version=5.8.0"))
    .UseContext<BuildContext>()
    .UseSetup<BuildSetup>()
    // .UseTeardown<BuildTeardown>()
    .Run(args);
