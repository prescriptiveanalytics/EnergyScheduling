namespace Build;

public sealed class BuildTeardown : FrostingTeardown<BuildContext>
{
    public override void Teardown(BuildContext context, ITeardownContext info)
    {
        if (info.ThrownException != null) return; // something went wrong -> do not try to end SonarQube

        Exception? sonarError = null;
        if (context.DoSonarAnalysis && context.SonarToken != null)
        {
            context.Log.Information("Ending SonarQube analysis");
            try
            {
                context.SonarQubeEnd(context.SonarToken);
            }
            catch (Exception ex)
            {
                sonarError = ex; // must probably quality gate failure
            }
        }

        if (!context.BuildSystem.IsLocalBuild)
        {
            try
            {
                context.Log.Information("Shutting down dotnet build server");
                context.DotNetBuildServerShutdown(); // shutdown build servers to prevent .sonarqube/bin/*.dll being locked
            }
            catch (Exception ex)
            {
                context.Log.Warning("Could not shutdown dotnet build server! {0}", ex.ToString());
            }
        }

        // throw Exception from Sonar at the end (so builder-servers are shutdown)
        if (sonarError != null) throw sonarError;
    }
}
