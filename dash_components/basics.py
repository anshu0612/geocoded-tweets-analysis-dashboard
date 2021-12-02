import json
import pandas as pd
from datetime import datetime as dt

# import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from constants.country_config import COUNTRY

import plotly.express as px

from constants.dash_constants import BASICS_PATH, DASH_TEMPLATE, \
    TWEETS_STATS_HEADING, DAILY_TWEETS_PATH, DAILY_TWEETS_HEADING, \
    DATE_FORMAT, \
    DASH_NO_YEAR_FORMAT, DASH_FORMAT,\
    PSTS_HEADING, PSTS_INFO_CONTENT, \
    MENTIONS_HASHTAGS_SENTIMENT_HEADING, MENTIONS_HASHTAGS_SENTIMENT_INFO_CONTENT, \
    POTENTIALLY_SENSITIVE_TWEETS_COUNT_PATH, POTENTIALLY_SENSITIVE_TWEETS_DEFAULT_PERCENTILE

# Load basic stats data
with open(BASICS_PATH) as json_file:
    basic_data = json.load(json_file)

MIN_DATE = basic_data['min_date']
MAX_DATE = basic_data['max_date']

BASIC_STATS = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4(TWEETS_STATS_HEADING,
                        className='card-title'),
                html.Div(
                    [html.P([
                        html.Span(basic_data['total_tweets'], style={
                            'fontWeight': 'bold'}),
                        html.Span(' tweets')
                    ]
                    ),
                        html.P([
                            html.Span('{} to {}'.format(
                                dt.strftime(dt.strptime(
                                    basic_data['min_date'], DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                dt.strftime(dt.strptime(
                                    basic_data['max_date'], DATE_FORMAT), DASH_FORMAT)),
                                style={'fontWeight': 'bold'}),
                            html.Span(' duration')
                        ]),
                        html.P([
                            html.Span(basic_data['users_count'], style={
                                'fontWeight': 'bold'}),
                            html.Span(
                                ' unique {}-based twitter users'.format(COUNTRY))
                        ]),
                        html.P([
                            html.Span(basic_data['avg_tweets'], style={
                                'fontWeight': 'bold'}),
                            html.Span(
                                ' average no. of tweets per day')
                        ])]
                )
            ],
            className='tweets-stats-body'
        ),
    ],
    style={'width': '100%', 'marginTop': '6em'}
)


# Load daily tweets data
df_tweets_daily_count = pd.read_csv(DAILY_TWEETS_PATH)
fig_tweets_daily_count = px.line(
    df_tweets_daily_count, x='tweet_date', y='count',
    color_discrete_sequence=['#1ca9c9'], template=DASH_TEMPLATE)
fig_tweets_daily_count.update_layout(title=DAILY_TWEETS_HEADING,
                                     font=dict(
                                         family='Verdana, monospace',
                                         size=14
                                     ),

                                     margin=dict(l=0, r=0, t=100, b=0),
                                     xaxis_title=None,
                                     yaxis_title=None)

DAILY_TWEETS = dcc.Loading(
    id='loading-daily-tweets',
    children=[
        dcc.Graph(figure=fig_tweets_daily_count)],
    type='dot'
)


DATEPICK_MENTIONS_HASHTAGS_SENTIMENT = dcc.DatePickerRange(
    id='hash-mention-sent-datepick',
    min_date_allowed=basic_data['min_date'],
    max_date_allowed=basic_data['max_date'],
    initial_visible_month=basic_data['min_date'],
    start_date=basic_data['min_date'],
    end_date=basic_data['max_date']
)


MENTIONS_HASHTAGS_SENTIMENT = [
    dbc.Col(
        dcc.Loading(
            id='loading-hashtags',
            children=[
                dcc.Graph(id='fig-hashtags')],
            type='dot',

        ), className='col-md-4'),
    dbc.Col(
        dcc.Loading(
            id='loading-mentions',
            children=[
                dcc.Graph(id='fig-mentions')],
            type='dot'
        ), className='col-md-4'),
    dbc.Col(
        dcc.Loading(
            id='loading-sentiments',
            children=[
                dcc.Graph(id='fig-sentiments')],
            type='dot'
        ), className='col-md-4')
]

MENTIONS_HASHTAGS_SENTIMENT_INFO = dbc.Jumbotron(
    dbc.Row(
        [dbc.Col(
            children=[
                html.Span(MENTIONS_HASHTAGS_SENTIMENT_HEADING,
                          style={'color': '#0096FF', 'marginRight': '10px'}),
                html.P(MENTIONS_HASHTAGS_SENTIMENT_INFO_CONTENT)
            ],
            className='col-md-8'
        ),
            dbc.Col([
                html.Span('Filter by date range ', style={
                    'fontSize': '0.8em'}),
                DATEPICK_MENTIONS_HASHTAGS_SENTIMENT
            ],
            className='col-md-4'
        ),
        ],
        className='col-md-12'
    ),
    style={'margin': '1em 0 2em 0'},
    className='col-md-12')


# Load potentially sensitive tweets data
c_tweets_pst = pd.read_csv(POTENTIALLY_SENSITIVE_TWEETS_COUNT_PATH)
spike_value = c_tweets_pst['count'].quantile(
    POTENTIALLY_SENSITIVE_TWEETS_DEFAULT_PERCENTILE)
colors = ['R' if cc > spike_value else
          'G' for cc in c_tweets_pst['count']]
fig_psts = px.bar(c_tweets_pst, x='tweet_date', y='count',
                  color_discrete_sequence=['#CD5C5C', '#8B0000'],
                  template=DASH_TEMPLATE, color=colors,
                  width=700, height=420)
fig_psts.update_layout(title='Daily potentially sensitive tweets count',
                       font=dict(
                           family='Verdana, monospace',
                           size=10
                       ),
                       margin=dict(l=0, r=0, t=30, b=0),
                       showlegend=False,
                       xaxis_title=None,
                       yaxis_title=None)


DATEPICK_PSTS = dcc.DatePickerSingle(
    id='psts-datepick',
    className='datepick-label',
    min_date_allowed=basic_data['min_date'],
    max_date_allowed=basic_data['max_date'],
    initial_visible_month=basic_data['min_date'],
    date=basic_data['min_date'],
    style={'width': '3em'}
)


PSTS_INFO = dbc.Jumbotron(
    dbc.Row(
        [dbc.Col(
            children=[
                html.Span(PSTS_HEADING,
                          style={'color': '#0096FF', 'marginRight': '10px'}),
                html.P(PSTS_INFO_CONTENT)
            ],
            className='col-md-8'
        ),
            dbc.Col([
                html.Span('Filter by date', style={
                    'fontSize': '0.8em'}),
                DATEPICK_PSTS
            ],
            className='col-md-4'
        ),
        ],
        className='col-md-12'
    ),
    style={'margin': '1em 0 2em 0'},
    className='col-md-12')

PSTS = [
    dbc.Col(
        dcc.Loading(
            id='loading-psts',
            children=[
                dcc.Graph(figure=fig_psts)],
            type='dot'
        ),
        className='col-md-8'
    ),

    dbc.Col(
        dcc.Loading(
            id='loading-psts-tweets',
            children=[
                dcc.Graph(id='freq-count-psts-tweets')],
            type='dot',
        ),
        className='col-md-4'
    )
]


# tweets
TWEETS = dbc.Container([
    dbc.Row(
        [
            dbc.Col(
                BASIC_STATS,
                className='col-md-4'
            ),
            dbc.Col(
                DAILY_TWEETS,
                className='col-md-8'
            )
        ]),

    html.Hr(),
    dbc.Row(
        MENTIONS_HASHTAGS_SENTIMENT_INFO,
        className='col-md-12'
    ),
    dbc.Row(
        MENTIONS_HASHTAGS_SENTIMENT,
        style={'margin': '3em 0'},
        className='col-md-12'
    ),
    html.Hr(),

    dbc.Row(
        PSTS_INFO,
        className='col-md-12'
    ),
    dbc.Row(
        PSTS
    ),
    html.Hr()
])
