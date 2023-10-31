using System.Text.Json;
using Fluxor;
using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Web;
using MudBlazor.Services;
using UserInterface.Data;

var builder = WebApplication.CreateBuilder(args);

// TODO: Remove me and add mqtt connection
using (StreamReader r = new StreamReader("Resources/opf_1641002400.json"))
{
    string json = r.ReadToEnd();
    Console.WriteLine(json);
    var solution = JsonSerializer.Deserialize<PowerFlow>(json);
    builder.Services.AddSingleton<PowerFlow>(solution);
}

// Add services to the container.
builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddSingleton<MqttServiceConfigurationContext>();
builder.Services.AddSingleton<MqttService>();
builder.Services.AddFluxor(options => options.ScanAssemblies(typeof(Program).Assembly));
builder.Services.AddMudServices();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();

app.UseStaticFiles();

app.UseRouting();

app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();
