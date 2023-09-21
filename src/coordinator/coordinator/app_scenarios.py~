import json
import pandas as pd
import plotly.graph_objects as go
import datetime
from dash import Dash, html, dcc, Input, Output, State
import logging
import base64
import os

from pathlib import Path

from spa_dat.application.application import DistributedApplication
from spa_dat.config import PayloadFormat, SocketConfig
from spa_dat.provider import SocketProviderFactory
from spa_dat.socket.mqtt import MqttConfig
from spa_dat.socket.typedef import SpaMessage, SpaSocket

import coordinator_dat as coordinator

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = "config.json"
with open(config_file, "r") as input_file:
    config = json.load(input_file)

config["host"] = os.getenv("MQTT_HOST", config["host"])
config["port"] = os.getenv("MQTT_PORT", config["port"])

logging.debug("using config=%s", config)

model_path = Path('models/generator/')
scenarios = [ 'hgb_east_10kwp', 'hgb_south_5kwp_east_5kwp', 'hgb_south_5kwp_west_5kwp', 'hgb_south_7kwp_east_1.5kwp_west1.5kwp', 'hgb_south_10kwp', 'hgb_west_10kwp' ]
# scenario 3 consumers
pv_identifier = '8bee677b-b929-4d52-ba2d-d8619b86e199'
# scenario 1 consumer
#pv_identifier = "12b277c0-ec01-448b-bffe-d081c11fd200"


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
        logging.debug("query consumers")
        coordinator.app_consumer.start()
        logging.debug("scenario_state.consumer=%s", coordinator.scenario_state.consumer)
        logging.debug(f"query generators")
        coordinator.app_generator.start()
        logging.debug("scenario_state.generator=%s", coordinator.scenario_state.generator)
        logging.debug("query network")
        coordinator.app_network.start()

        consumers = coordinator.scenario_state.consumer['consumers']
        generators = coordinator.scenario_state.generator['generators']
        network = coordinator.scenario_state.network['network']

        nodes_df = coordinator.get_nodes(consumers, generators, network)
        lines_df = coordinator.get_line_connections(consumers, generators, network)
        coordinator.scenario_state.query_times = query_times
        logging.debug("running %s scenarios, this may take some time", len(scenarios))
        collected_scenarios = {}
        for scenario in scenarios:
            logging.debug("update model for generator=%s", pv_identifier)
            with open(model_path / scenario, "rb") as model_input_file:
                model_content = model_input_file.read()
                encoded_model = base64.b64encode(model_content).decode('ascii')
                coordinator.update_generator_model.identifier = pv_identifier
                coordinator.update_generator_model.encoded_model = encoded_model
            coordinator.app_generator_update_model.start()
            coordinator.app_network_opf.start()
            opfs = coordinator.scenario_state.network_opf
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

        logging.debug("data preparation finished, generating plots")
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