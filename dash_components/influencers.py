import pandas as pd

# import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from constants.dash_constants import INTERACTIONS_GRAPH_INFO_CONTENT, \
    INFLUENTIAL_USERS_INFO_CONTENT, INFLUENTIAL_USERS_PATH, \
    TOP_COUNTRY_INFLUENCER_PATH, \
    INFLUENTIAL_COUNTRIES_INFO_CONTENT 
    
from constants.country_config import COUNTRY

# Load influential users
influential_users = pd.read_csv(INFLUENTIAL_USERS_PATH)
influential_users_countries = list(
    influential_users['user_geo_coding'].unique())
influential_users_countries.append('All')
influential_users_countries = sorted(influential_users_countries)

# Load influential users
country_data = pd.read_csv(TOP_COUNTRY_INFLUENCER_PATH)
most_influential_country = str(
    country_data.iloc[country_data['count'].idxmax()]['country'])

INFLUENTIAL_USERS_INFO = dbc.Jumbotron(
    dbc.Row(
        [dbc.Col(
            children=[
                html.Span('Interactions graph: ',
                          style={'color': '#000', 'marginRight': '10px'}),
                html.P(INTERACTIONS_GRAPH_INFO_CONTENT),
                html.Span('Influential users: ',
                          style={'color': '#0096FF', 'marginRight': '10px'}),
                html.P(INFLUENTIAL_USERS_INFO_CONTENT),
            ],
            className='col-md-8'
        ),
            dbc.Col([
                html.Span('Filter by country', style={
                    'fontSize': '0.8em'}),
                dcc.Dropdown(
                    id='dropdown-top-influence-users-countries',
                    options=[
                        {'label': i, 'value': i}
                        for i in influential_users_countries
                    ],
                    value=COUNTRY)],
                    className='col-md-4'
                    ),
        ],
        className='col-md-12'
    ),
    style={'margin': '1em 0 2em 0'},
    className='col-md-12')

INFLUENTIAL_USERS = [
    dbc.Row(
        html.H5(['Influential users']),
        className='col-md-12'
    ),
    dbc.Row(
        INFLUENTIAL_USERS_INFO,
        className='col-md-12'
    ),
    dbc.Row(
        children=[],
        id='influencers-chips-row'
    )]


INFLUENTIAL_COUNTRIES_INFO = dbc.Jumbotron(
    dbc.Row(
        [dbc.Col(
            children=[
                html.Span('Influential countries: ',
                          style={'color': '#0096FF', 'marginRight': '10px'}),
                html.P(INFLUENTIAL_COUNTRIES_INFO_CONTENT),
            ],
            className='col-md-8'
        ),
            dbc.Col([
                html.Span('Filter by country', style={
                    'fontSize': '0.8em'}),
                dcc.Dropdown(
                    id='dropdown-top-influence-countries',
                    # clearable=False, style={'cursor': 'pointer', 'borderRadius': 0, 'width': '200px',
                    #                         'margin': '0.5em', 'fontSize': '0.8em'},
                    options=[
                        {'label': i, 'value': i}
                        for i in sorted(list(country_data['country']))
                    ],
                    value=most_influential_country)
            ],
            className='col-md-4',
        ),
        ],
        className='col-md-12'
    ),
    style={'margin': '1em 0 2em 0'},
    className='col-md-12')

INFLUENTIAL_COUNTRIES = [
    dbc.Col(
        dcc.Loading(
            id='loading-influential-country_map',
            children=[
                dcc.Graph(
                    id='fig-world-influence'
                )],
            type='dot',
        ),
        className='col-md-8'
    ),
    dbc.Col(
        dcc.Loading(
            id='loading-influential-country_words',
            children=[
                dcc.Graph(id='word-cloud-influential-country')],
            type='dot',
        ),
        className='col-md-4'
    )
]


# influencers
INFLUENCERS = dbc.Container([
    dbc.Row(
        INFLUENTIAL_USERS,
        style={'margin': '3em 0'},
        className='col-md-12'
    ),
    html.Hr(),
    dbc.Row(
        [
            dbc.Row(
                html.H5(['Foreign influence']),
                className='col-md-12'
            ),
            dbc.Row(
                INFLUENTIAL_COUNTRIES_INFO,
                className='col-md-12'
            ),
            dbc.Row(
                INFLUENTIAL_COUNTRIES, className='col-md-12'
            )],
        style={'margin': '3em 0'},
        className='col-md-12'
    ),
    html.Hr(),
])
