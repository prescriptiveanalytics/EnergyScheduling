using YamlDotNet.Serialization;
using Cake.Common.Net;

namespace Build.Extensions;

public class MultiCommandRunner
{
  public static string[] MprocsExecutableNames = {
    "mprocs",
    "mprocs.exe"
  };

  private readonly ICakeContext context;
  private readonly DirectoryPath outputDir;
  private readonly DirectoryPath toolsDir;
  private readonly List<Command> commands;

  public MultiCommandRunner(ICakeContext context, DirectoryPath outputDir, DirectoryPath toolsDir)
  {
    this.context = context;
    this.outputDir = outputDir;
    this.toolsDir = toolsDir;

    commands = new();
  }

  public MultiCommandRunner AddCommand(
    string name,
    FilePath file,
    Action<ProcessArgumentBuilder>? args = null,
    DirectoryPath? workingDirectory = null,
    Action<DictionaryBuilder<string, string>>? environmentVariables = null,
    bool autoStart = true
  )
  {
    var argsBuilder = new ProcessArgumentBuilder();
    args?.Invoke(argsBuilder);
    var envs = new DictionaryBuilder<string, string>();
    environmentVariables?.Invoke(envs);

    var command = new Command(
      name,
      file,
      argsBuilder,
      workingDirectory,
      envs.Build(),
      autoStart
    );
    commands.Add(command);

    return this;
  }

  public void EnsureRunnerInstalled()
  {
    FilePath file;
    Uri uri;
    if (OperatingSystem.IsLinux())
    {
      uri = new Uri("https://github.com/pvolok/mprocs/releases/download/v0.6.4/mprocs-0.6.4-linux64.tar.gz");
      file = new FilePath("mprocs-0.6.4-linux64.tar.gz");
    }
    else if (OperatingSystem.IsWindows())
    {
      uri = new Uri("https://github.com/pvolok/mprocs/releases/download/v0.6.4/mprocs-0.6.4-win64.zip");
      file = new FilePath("mprocs-0.6.4-win64.zip");
    }
    else
      throw new NotImplementedException("Unsupported OS for MultiCommandRunner!");

    var downloadFile = outputDir.CombineWithFilePath(file);
    if (context.FileExists(downloadFile)) return;

    context.DownloadFile(uri.ToString(), downloadFile);

    if (file.GetExtension() == ".zip")
    {
      context.Unzip(downloadFile, toolsDir);
      context.DeleteFile(downloadFile);
    }
    // TODO Linux support
  }

  public void Run()
  {
    var config = MprocsConfig.FromCommands(commands);

    var configFile = outputDir.CombineWithFilePath(
      new FilePath("mprocs.yaml")
    );
    Yaml.Save(config, configFile);

    context.StartProcess(
      context.Tools.Resolve(MprocsExecutableNames),
      new ProcessSettings()
      {
        Arguments = new ProcessArgumentBuilder()
          .AppendSwitchQuoted("--config", configFile.MakeAbsolute(context.Environment).FullPath)
      }
    );
  }

  public record Command(
    string Name,
    FilePath File,
    ProcessArgumentBuilder Arguments,
    DirectoryPath? WorkingDirectory = null,
    ImmutableDictionary<string, string>? EnvironmentVariables = null,
    bool AutoStart = true
  );

  public record MprocsConfig(
    [property: YamlMember(Alias = "procs")]
    Dictionary<string, MprocsConfig.Process> Processes
  )
  {
    public static MprocsConfig FromCommands(IEnumerable<Command> commands)
    {
      return new(
        commands.ToDictionary(c => c.Name, c => ToProcess(c))
      );

      Process ToProcess(Command command)
      {
        var commandLine = new List<string>();
        commandLine.Add(command.File.FullPath);
        var args = command.Arguments
          .Select(a => a.Render())
          .SelectMany(s => s.Split(' ')) // split switches into own rags
          .Select(s => s.Trim('"')) // trim double quotes (not needed in YAML)
          ;
        commandLine.AddRange(args);

        return new(
          Command: commandLine.ToArray(),
          WorkingDirectory: command.WorkingDirectory?.FullPath,
          EnvironmentVariables: command.EnvironmentVariables?.ToDictionary(
            e => e.Key, e => e.Value
          ),
          AutoStart: command.AutoStart
        );
      }
    }

    public record Process(
      [property: YamlMember(Alias = "shell")]
      string? Shell = null,
      [property: YamlMember(Alias = "cmd")]
      string[]? Command = null,
      [property: YamlMember(Alias = "cwd")]
      string? WorkingDirectory = null,
      [property: YamlMember(Alias = "env")]
      Dictionary<string, string>? EnvironmentVariables = null,
      [property: YamlMember(Alias = "autostart")]
      bool AutoStart = true
    );
  }
}
