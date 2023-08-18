namespace Build.Extensions;

public static class SonarQubeExtensions
{
	public static readonly string ToolName = "net5.0/*/SonarScanner.MSBuild.dll";

	public static void SonarQubeBegin(
		this ICakeContext context,
		string projectKey,
		string token,
		FilePath configFile
	)
	{
		context.DotNetExecute(
			context.Tools.Resolve(ToolName),
			new ProcessArgumentBuilder()
				.Append("begin")
				.AppendQuoted($"/k:\"{projectKey}\"")
				.AppendQuoted($"/d:sonar.login=\"{token}\"")
								.AppendQuoted($"/s:\"{configFile.MakeAbsolute(context.Environment)}\"")
		);
	}

	public static void SonarQubeEnd(
		this ICakeContext context,
		string token
	)
	{
		context.DotNetExecute(
			context.Tools.Resolve(ToolName),
			new ProcessArgumentBuilder()
				.Append("end")
				.AppendQuoted($"/d:sonar.login=\"{token}\"")
		);
	}
}
