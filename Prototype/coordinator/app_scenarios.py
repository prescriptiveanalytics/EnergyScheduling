import requests
import json
import pandas as pd
import plotly.graph_objects as go
import datetime
from dash import Dash, html, dcc, Input, Output, State
import logging
import coordinator
from pathlib import Path

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = "config.json"
with open(config_file, "r") as input_file:
    config = json.load(input_file)

model_path = Path('models/generation/')
scenarios = [ 'hgb_east_10kwp', 'hgb_south_5kwp_east_5kwp', 'hgb_south_5kwp_west_5kwp', 'hgb_south_7kwp_east_1.5kwp_west1.5kwp', 'hgb_south_10kwp', 'hgb_west_10kwp' ]
# scenario 3 consumers
#pv_identifier = '8bee677b-b929-4d52-ba2d-d8619b86e199'
# scenario 1 consumer
pv_identifier = "12b277c0-ec01-448b-bffe-d081c11fd200"


mapbox_token = open("token").read()
logging.debug(f"read config file: {config}")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "spa - power network scenario analyzer"

# rewrite from here onwards

app.layout = html.Div([
    html.Header(children='spa - power network demo application - scenario analyzer', style={"fontSize": "20px", "textAlign": "center"}),
    html.Div("Date (yyyy-mm-dd)", style={"fontSize": "15px"}),
    dcc.Input(id="input-date", value="2023-08-01", type="text"),
    html.Button('Calculate scenarios', id='submit-date', n_clicks=0),
    html.Div(id="input-date-result", children=""),
    html.Div("Network"),
    dcc.Graph(id="map"),
    html.Div("Generation profiles"),
    dcc.Graph(id="generation-profiles"),
    html.Div("Load profile"),
    dcc.Graph(id="load-profiles"),
    html.Div("Grid consumption vs. overall production"),
    dcc.Graph(id="grid-consumption-overall-production")
])

@app.callback(
    Output("input-date-result", "children"),
    Output("map", "figure"),
    Output("generation-profiles", "figure"),
    Output("load-profiles", "figure"),
    Output("grid-consumption-overall-production", "figure"),
    Input("submit-date", "n_clicks"),
    State("input-date", "value")
)
def input_date(n_clicks, value):
    fig_map = go.Figure()
    fig_generation_profiles = go.Figure()
    fig_load_profiles = go.Figure()
    fig_grid_consumption_overall_production = go.Figure()

    if n_clicks == 0:
        return [f"", fig_map, fig_generation_profiles, fig_load_profiles, fig_grid_consumption_overall_production]
    try:
        dt = datetime.datetime.strptime(value, '%Y-%m-%d')
    except:
        return ["Error while parsing " + value, fig_map, fig_generation_profiles, fig_load_profiles, fig_grid_consumption_overall_production]
    
    start_timestamp = int(dt.timestamp())
    interval = 900
    number_intervals = 96
    query_times = [start_timestamp + i*interval for i in range(0, number_intervals)]

    try:
        logging.debug(f"query consumers")
        consumers = coordinator.query_consumers(config['consumer_api'])
        logging.debug(f"got {len(consumers)} results")
        logging.debug(f"query generators")
        generators = coordinator.query_generators(config['generator_api'])
        logging.debug(f"got {len(generators)} results")
        logging.debug(f"query network")
        network = coordinator.query_network(config['network_api'])
        nodes_df = coordinator.get_nodes(consumers, generators, network)
        lines_df = coordinator.get_line_connections(consumers, generators, network)
        logging.debug(f"running {len(scenarios)} scenarios, this may take some time")
        collected_scenarios = {}
        for scenario in scenarios:
            files = { 'model_file': open(model_path / scenario, 'rb') }
        
            requests.post(f'{config["generator_api"]}/generator/{pv_identifier}/model', files=files)

            opfs = coordinator.query_range(query_times, config['network_api'])
            collected_scenarios[scenario] = opfs

        logging.debug(f"queried {len(collected_scenarios)} scenarios, start data processing")
        collected_sum_grid_dfs = []
        collected_sum_load_dfs = []
        collected_sum_gen_dfs = []
        for key, cs in collected_scenarios.items():
            logging.debug(f"processing scenario {key}")
            result = coordinator.get_scenario_dataframes(nodes_df, cs, key)
            collected_sum_load_dfs.append(result[0])
            collected_sum_grid_dfs.append(result[1])
            collected_sum_gen_dfs.append(result[2])

        logging.debug(f"scenarios processed, generating dataframes")
        sum_grid_ts = pd.concat(collected_sum_grid_dfs)
        sum_load_ts = pd.concat(collected_sum_load_dfs)
        sum_gen_ts = pd.concat(collected_sum_gen_dfs)
        sum_grid_get_from_grid = sum_grid_ts[sum_grid_ts['p_mw'] > 0][['p_mw', 'scenario']].groupby('scenario').sum()
        sum_grid_push_to_grid = sum_grid_ts[sum_grid_ts['p_mw'] < 0][['p_mw', 'scenario']].groupby('scenario').sum()
        sum_grid_scenario = sum_grid_ts[['p_mw', 'scenario']].groupby('scenario').sum()
        sum_generation = sum_gen_ts[['p_mw', 'scenario']].groupby('scenario').sum()

        scenario_df = sum_grid_get_from_grid.merge(sum_generation, on='scenario', suffixes=('_from_grid', '_generation'))
        scenario_df = scenario_df.rename(columns={'p_mw': 'p_mw_gen'})
        scenario_df = scenario_df.reset_index()

        logging.debug(f"data preparation finished, generating plots")
        # logging.debug(f"query opf")
        # opfs = coordinator.query_range(query_times, config['network_api'])
        # logging.debug(f"got {len(opfs)} results")
       
        # logging.debug(f"extract nodes information")
        # nodes_df = coordinator.get_nodes(consumers, generators, network)
        # logging.debug(f"got {len(nodes_df)} nodes")

        # opf_keys = [k for k in sorted(opfs.keys())]
        # logging.debug(f"extract lines")
        # lines_df = coordinator.get_line_connections(consumers, generators, network)
        # logging.debug(f"got {len(lines_df)} lines")
       
        # logging.debug(f"extract load")
        # load_df = coordinator.create_load_dataframe(consumers, network, opfs[opf_keys[0]])
        load_map_df = nodes_df[nodes_df['type'] == "load"]
        generator_map_df = nodes_df[nodes_df['type'] == "generator"]
        network_map_df = nodes_df[nodes_df['type'] == "network"]

        # add lines
        fig_map.add_trace(go.Scattermapbox(
            mode = 'lines',
            lon = lines_df['longitude'],
            lat = lines_df['latitude']
        ))

        # nodes
        fig_map.add_trace(go.Scattermapbox(
            mode = "markers",
            lon = load_map_df['longitude'],
            lat = load_map_df['latitude'],
            marker = go.scattermapbox.Marker(
                color="red"
            ),
            hoverinfo = 'text',
            text = load_map_df['name'] # + '<br>' + 'load: ' + load_map_df['load'].astype(str) + " MW"
        ))

        fig_map.add_trace(go.Scattermapbox(
            mode = "markers",
            lon = network_map_df['longitude'],
            lat = network_map_df['latitude'],
            marker = go.scattermapbox.Marker(
                color="blue"
            ),
            hoverinfo = 'text',
            text = network_map_df['name'] # + '<br>' + 'load: ' + load_map_df['load'].astype(str) + " MW"
        ))

        fig_map.add_trace(go.Scattermapbox(
            mode = "markers",
            lon = generator_map_df['longitude'],
            lat = generator_map_df['latitude'],
            marker = go.scattermapbox.Marker(
                color="green"
            ),
            hoverinfo = 'text',
            text = generator_map_df['name'] # + '<br>' + 'load: ' + load_map_df['load'].astype(str) + " MW"
        ))

        fig_map.update_layout(    
            margin ={'l':0,'t':0,'b':0,'r':0},
            mapbox_style = "dark",
            mapbox = {
                'center': { 'lon': nodes_df['longitude'].mean(), 'lat': nodes_df['latitude'].mean() },
                'zoom': 15,
                'style': "open-street-map"},
            mapbox_accesstoken=mapbox_token)


        for scenario in scenarios:
            df = sum_gen_ts[sum_gen_ts['scenario'] == scenario]

            fig_generation_profiles.add_trace(go.Scatter(x=df['time'], y=df['p_mw'],
                                                         mode='markers+lines',
                                                         name=scenario))
            
        for scenario in scenarios:
            df = sum_load_ts[sum_load_ts['scenario'] == scenario]

            fig_load_profiles.add_trace(go.Scatter(x=df['time'], y=df['p_mw'],
                                                         mode='markers+lines',
                                                         name=scenario))

        for scenario in scenarios:
            df = scenario_df[scenario_df['scenario'] == scenario]
            fig_grid_consumption_overall_production.add_trace(go.Scatter(x=df['p_mw_generation'], y=df['p_mw_from_grid'],
                                                                        mode='markers',
                                                                        name=scenario))
        fig_grid_consumption_overall_production.update_layout(
            xaxis_title = "pv generation",
            yaxis_title = "grid consumption",
            legend_title = "scenarios"
        )
        logging.debug(f"scenario.head()={scenario_df.head()}")

        return [f"Solved {1} intervals", fig_map, fig_generation_profiles, fig_load_profiles, fig_grid_consumption_overall_production]
    except:
        return [f"Error during requests", fig_map, fig_generation_profiles, fig_load_profiles, fig_grid_consumption_overall_production]

if __name__ == '__main__':
    app.run(debug=True, port='8060')