import os
import json
import pandas as pd
import plotly.graph_objects as go
import datetime
from dash import Dash, html, dcc, Input, Output, State
import logging

from spa_dat.application.application import DistributedApplication
from spa_dat.config import PayloadFormat, SocketConfig
from spa_dat.provider import SocketProviderFactory
from spa_dat.socket.mqtt import MqttConfig
from spa_dat.socket.typedef import SpaMessage, SpaSocket

import coordinator as coordinator

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = "config.json"
with open(config_file, "r") as input_file:
    config = json.load(input_file)

config["host"] = os.getenv("MQTT_HOST", config["host"])
config["port"] = os.getenv("MQTT_PORT", config["port"])

logging.debug("using config=%s", config)

mapbox_token = open("token").read()
logging.debug(f"read config file: {config}")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "spa - power network simulator"

app.layout = html.Div([
    html.Header(children='spa - power network demo application - network simulator', style={"fontSize": "20px", "textAlign": "center"}),
    html.Div("Date (yyyy-mm-dd)", style={"fontSize": "15px"}),
    dcc.Input(id="input-date", value="2023-08-01", type="text"),
    html.Button('Calculate', id='submit-date', n_clicks=0),
    html.Div(id="input-date-result", children=""),
    html.Div("Network"),
    dcc.Graph(id="map"),
    html.Div("Load"),
    html.Div(id='result-sum-values'),
    dcc.Graph(id="load")
])

@app.callback(
    Output("input-date-result", "children"),
    Output("map", "figure"),
    Output("load", "figure"),
    Output("result-sum-values", "children"),
    Input("submit-date", "n_clicks"),
    State("input-date", "value")
)
def input_date(n_clicks, value):
    fig_map = go.Figure()
    fig_load = go.Figure()

    if n_clicks == 0:
        return ["", fig_map, fig_load, f"grid load={0}, consumer load={0}"]
    try:
        dt = datetime.datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        logging.error("could not parse date=%s", value)
        return ["Error while parsing " + value, fig_map, fig_load, f"grid load={0}, consumer load={0}"]
    
    start_timestamp = int(dt.timestamp())
    interval = 900
    number_intervals = 96
    query_times = [start_timestamp + i*interval for i in range(0, number_intervals)]

    try:
        logging.debug("query consumers")
        coordinator.app_consumer.start()
        logging.debug("scenario_state.consumer=%s", coordinator.scenario_state.consumer)
        logging.debug("query generators")
        coordinator.app_generator.start()
        logging.debug("scenario_state.generator=%s", coordinator.scenario_state.generator)
        logging.debug("query network")
        coordinator.app_network.start()
        logging.debug("query opf using %s intervals", query_times)
        coordinator.scenario_state.query_times = query_times
        logging.debug("query opf using %s intervals", len(query_times))
        coordinator.app_network_opf.start()
        opfs = coordinator.scenario_state.network_opf
        logging.debug("got %s opf results", len(opfs))
       
        consumers = coordinator.scenario_state.consumer['consumers']
        generators = coordinator.scenario_state.generator['generators']
        network = coordinator.scenario_state.network['network']
        logging.debug(f"extract nodes information")
        nodes_df = coordinator.get_nodes(consumers, generators, network)
        logging.debug(f"got {len(nodes_df)} nodes")

        opf_keys = [k for k in sorted(opfs.keys())]
        logging.debug(f"extract lines")
        lines_df = coordinator.get_line_connections(consumers, generators, network)
        logging.debug(f"got {len(lines_df)} lines")
       
        logging.debug(f"extract load")
        load_df = coordinator.create_load_dataframe(consumers, network, opfs[opf_keys[0]])
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

        res_load_ts = coordinator.load_ts(nodes_df, opfs)

        load_nodes = set(res_load_ts['identifier'])
        inm = coordinator.create_identifier_name_mapping(nodes_df)

        for ln in load_nodes:
            data = res_load_ts[res_load_ts['identifier']==ln]
            fig_load.add_trace(go.Scatter(x=data['time'], y=data['p_mw'],
                            mode='markers+lines',
                            name=inm[ln]))

        res_load_ts = coordinator.load_ts(nodes_df, opfs)
        res_sum_load_ts = res_load_ts[['time', 'p_mw', 'q_mvar']].groupby(by=['time']).sum().reset_index().sort_values(by=['time'])
        fig_sum_load = go.Figure()

        res_ext_grid_ts = coordinator.ext_grid_ts(nodes_df, opfs)
        res_gen_ts = coordinator.gen_ts(nodes_df, opfs)

        fig_sum_load.add_trace(go.Scatter(x=res_sum_load_ts['time'], y=res_sum_load_ts['p_mw'],
                        mode='markers+lines',
                        name='consumer load'))

        fig_sum_load.add_trace(go.Scatter(x=res_ext_grid_ts['time'], y=res_ext_grid_ts['p_mw'],
                        mode='markers+lines',
                        name='grid load'))
        
        fig_sum_load.add_trace(go.Scatter(x=res_gen_ts['time'], y=res_gen_ts['p_mw'],
                mode='markers+lines',
                name='production'))
        
        fig_sum_load.update_xaxes(title_text="Date")
        fig_sum_load.update_yaxes(title_text="Energie [MWh]")

        sum_grid = res_ext_grid_ts['p_mw'].sum()
        sum_load = res_sum_load_ts['p_mw'].sum()
        sum_generation = res_gen_ts['p_mw'].sum()

        return [f"Solved {len(opfs)} intervals", fig_map, fig_sum_load, f"grid load={sum_grid}, consumer load={sum_load}, generation={sum_generation}"]
    except:
        return [f"Error during requests", fig_map, fig_load, f"grid load={0}, consumer load={0}"]

if __name__ == '__main__':
    app.run(debug=True, port='8050', host="0.0.0.0")
