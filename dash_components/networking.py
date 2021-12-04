import json

import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from constants.common import *
from constants.dash_constants import *

with open(COMMUNITIES_USERS_PATH, 'r') as f:
    clusters_users = json.load(f)

with open(NETWORKING_DATA, 'r') as f:
    cyto_data = json.load(f)

graph_stylesheet = []
for cluster_no in range(len(clusters_users)):
    obj = {
        'selector': '.' + str(cluster_no),
        'style': {
            'background-color': CLUSTER_COLORS_DICT[str(cluster_no)],
            'content': 'data(label)',
            'height': CIRCLE_SIZE,
            'width': CIRCLE_SIZE,
            'font-size': FONT_SIZE
        }
    }
    graph_stylesheet.append(obj)

graph_stylesheet.append(
    {
        "selector": 'edge',
        'style': {
            "curve-style": "bezier",
            "opacity": 0.3,
            "line-color": "#687C97",
            'width': 1
        }
    }
)

NETWORKING_GRAPH = cyto.Cytoscape(
    id='cytoscape-nodes',
    layout={'name': 'cose'},
    style={'width': '100%', 'height': NETWORKING_GRAPH_HEIGHT, 'margin': '0'},
    elements=cyto_data['data'],
    stylesheet=graph_stylesheet
)

CLUSTERS_INFO = dbc.Jumbotron(
    dbc.Row(
        [dbc.Col(
            children=[
                html.Span('Clustered users/communities',
                          style={'color': '#0096FF', 'marginRight': '10px'})
            ] +
            [html.Div(
                [COMMUNITIES_INFO_CONTENT.format(len(clusters_users))] +
                [html.P('C' + k, style={"color": v['color'], 'margin': '0 0.4em', 'fontSize': '1.2em'})
                 for k, v in clusters_users.items()], style={"display": "flex"})], className='col-md-8'),
            dbc.Col([
                html.Span('Filter by cluster', style={
                    'fontSize': '0.8em'}),
                dcc.Dropdown(
                    id='dropdown-clusters',
                    options=[
                        {'label': i, 'value': i}
                        for i in clusters_users.keys()
                    ],
                    value='0')],
                    className='col-md-4'
                    ),
         ],
        className='col-md-12'
    ),
    style={'margin': '1em 0 2em 0'},
    className='col-md-12')

CLUSTERS_TWEETS_WORD_FREQ = dcc.Loading(
    id='loading-clusters-tweets',
    children=[
        dcc.Graph(id='word-freq-clusters')],
    type='dot',
)

# networking
NETWORKING = dbc.Container([
    dbc.Row(CLUSTERS_INFO),
    dbc.Row([
        dbc.Col(
            [
                dbc.Row(dbc.Button("Reset Graph", id='bt-reset',
                        color="primary", className="me-1", size="sm")),
                dbc.Row(NETWORKING_GRAPH),
                dbc.Row(
                    [
                        dbc.Row(dbc.Alert(
                            [html.P(NETWORKING_NOTE_CONTENT,
                                    style={'color': '#893843', 'fontSize': '0.7em'}),
                                NETWORKING_HELPER_CONTENT],
                            color="light"))]),
            ], className='col-md-8'
        ),
        dbc.Col(
            CLUSTERS_TWEETS_WORD_FREQ, className='col-md-4')
    ]),
    html.Hr(),
    html.P("List of users in the selected cluster.",
           style={'textAlign': 'center'}),
    html.Hr(),
    dbc.Row(id='clusters-users'),
    html.Hr()
])
