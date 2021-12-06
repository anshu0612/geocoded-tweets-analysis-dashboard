import pandas as pd
from datetime import datetime as dt

# import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash_html_components.Img import Img

from constants.common import *
from constants.dash_constants import *
from utils.common import human_format
from dash_components.basics import MAX_DATE, MIN_DATE

# Static data
quoted_spread_data = pd.read_csv(QUOTED_SENTIMENT_SPEAD_PATH)
quoted_spread_data_pos = quoted_spread_data[quoted_spread_data['spread_type'] == 'positive']
quoted_spread_data_neg = quoted_spread_data[quoted_spread_data['spread_type'] == 'negative']


def create_quoted_card(tw):
    return (
        dbc.CardBody(
            dbc.Row([
                dbc.Col(
                    [
                        html.P(style={'fontSize': '1em',
                                      'color': '#000'}, children=tw['quoted_tweet_text']),
                        html.P(
                            className='quoted-info',
                            children=[
                                html.Span('Posted by: ',
                                          className='more-info'),
                                html.Span(tw['quoted_user_screenname']),
                                html.Span(children=' ✅' if tw['quoted_user_verified'] else '', style={
                                    'color': '#0096FF'}),
                                html.Span(
                                    Img(
                                        className='quoted-flag',
                                        src=FLAG_URL.format(
                                            tw['quoted_user_geo_coding'].lower().replace(
                                                ' ', '-')
                                            if tw['quoted_user_geo_coding'].lower() != 'united states' else FLAG_FIX_USA)
                                    )
                                ),

                                html.Span(' | Created on: ',
                                          className='more-info'),
                                html.Span(dt.strftime(dt.strptime(
                                    tw['quoted_tweet_date'], DATE_FORMAT), DASH_NO_YEAR_FORMAT)),
                                html.Span(
                                    ' | 🔁 ', className='quoted-endorsements'),
                                html.Span(
                                    '+', className='quoted-endorsements'),
                                html.Span(
                                    '🤍 : ', className='quoted-endorsements'),
                                html.Span(human_format(tw['total_engagement']))

                            ]),

                        dbc.Progress(
                            value=str(tw['spread_rate']),
                            max='100',
                            # animated=True,
                            children=str(tw['spread_rate']) + '%',
                            className='mb-3',
                            color='#32CD32' if str(
                                tw['spread_type']) == 'positive' else '#C70039',
                            style={'height': '1.4em', 'fontSize': '0.8em'}
                        )

                    ],
                ),
            ],
                className='tw-card-body'
            )))


neg_bursty_quotes_children = [create_quoted_card(tw) for _, tw in quoted_spread_data_neg.iterrows()]
pos_bursty_quotes_children = [create_quoted_card(tw) for _, tw in quoted_spread_data_pos.iterrows()]

BURSTY_QUOTED_TWEETS = [
    dbc.Row(
        html.H5(['Reactive tweets']),
        className='col-md-12'
    ),
    dbc.Row(
        dbc.Jumbotron(
            dbc.Row(
                [dbc.Col(
                    children=[
                        html.Span('Viral quoted tweets: ',
                                  style={'color': '#000', 'marginRight': '10px'}),
                        html.P(
                            VIRAL_QUOTED_INFO_CONTENT.format(
                                dt.strftime(dt.strptime(
                                            MIN_DATE, DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                dt.strftime(dt.strptime(
                                            MAX_DATE, DATE_FORMAT), DASH_NO_YEAR_FORMAT))
                        ),
                        html.Span('Reactive tweets: ',
                                  style={'color': '#0096FF', 'marginRight': '10px'}),
                        html.P(REACTIVE_TWEETS_INFO_CONTENT),
                    ],
                    className='col-md-12'
                )
                ],
                className='col-md-12'
            ),
            style={'margin': '1em 0 2em 0'},
            className='col-md-12'),
        className='col-md-12'
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Alert('Positive outburst' + ('' if len(quoted_spread_data_pos) else " not found"),
                              className='alert-heading', style={'color': 'green'}),
                    dbc.Row(children=pos_bursty_quotes_children)
                ], className='outburst col-md-6', style={'maxHeight': '40em', 'overflowY': 'scroll'},
            ),
            dbc.Col(
                [
                    dbc.Alert('Negative outburst' + ('' if len(quoted_spread_data_neg) else " not found"),
                              className='alert-heading', style={'color': '#C70039'}),
                    dbc.Row(children=neg_bursty_quotes_children)
                ],  style={'maxHeight': '40em', 'overflowY': 'scroll'},
            )
        ], className='outburst col-md-12'
    ),

]


VIRAL_LOCAL_RETWEETS = [
    dbc.Row(
        html.H5(['Viral local Retweets']),
        className='col-md-12'
    ),
    dbc.Row(
        dbc.Jumbotron(
            dbc.Row(
                [dbc.Col(
                    children=[
                        html.Span('Viral local retweets:',
                                  style={'color': '#0096FF', 'marginRight': '10px'}),
                        html.Span(
                            VIRAL_RETWEETS_DATE_INFO_CONTENT
                            .format(
                                dt.strftime(dt.strptime(
                                            MIN_DATE, DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                dt.strftime(dt.strptime(
                                            MAX_DATE, DATE_FORMAT), DASH_NO_YEAR_FORMAT)), className='rts-jumbotron'),
                        html.Span('{}-based accounts '.format(COUNTRY),
                                  className='country-rts-jumbotron'),
                        html.Span(VIRAL_RETWEETS_INFO_CONTENT,
                                  className='rts-jumbotron'),
                    ],
                    className='col-md-8'
                ),
                    dbc.Col([
                        html.Span('Filter by sentiment',
                                  style={'fontSize': '0.8em'}),
                        dcc.Dropdown(
                            id='local-rts-sentiment-select',
                            options=[
                                {'label': i, 'value': i}
                                for i in ['All', 'Positive', 'Negative']
                            ],
                            value='Negative')],
                            className='col-md-4'
                            ),
                ],
                className='col-md-12'
            ),
            style={'margin': '1em 0 2em 0'},
            className='col-md-12'),
        className='col-md-12'
    ),
    dbc.Row([
        dbc.Col(
            dbc.Row(
                html.Div(id='local-rts', className='rts')),
            style={'maxHeight': '50em', 'overflow-y': 'scroll'},
            className='col-md-5'
        ),
        dbc.Col(
            [
                dbc.Row(
                    dcc.Graph(id='local-rts-cumulative')
                ),
                dbc.Row(
                    dcc.Graph(id='local-rts-delta')
                )
            ],
            className='col-md-6'

        )
    ])
]


VIRAL_GLOBAL_RETWEETS = [
    dbc.Row(
        html.H5(['Viral global Retweets']),
        className='col-md-12'
    ),
    dbc.Row(
        dbc.Jumbotron(
            dbc.Row(
                [dbc.Col(
                    children=[
                        html.Span('Viral global retweets:',
                                  style={'color': '#0096FF', 'marginRight': '10px'}),
                        html.Span(
                            VIRAL_RETWEETS_DATE_INFO_CONTENT.
                            format(
                                dt.strftime(dt.strptime(
                                            MIN_DATE, DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                dt.strftime(dt.strptime(
                                            MAX_DATE, DATE_FORMAT), DASH_NO_YEAR_FORMAT)), className='rts-jumbotron'),
                        html.Span('non-{}-based accounts '.format(COUNTRY),
                                  className='country-rts-jumbotron'),
                        html.Span(
                            VIRAL_RETWEETS_INFO_CONTENT, className='rts-jumbotron'),
                    ],
                    className='col-md-8'
                ),
                    dbc.Col([
                        html.Span('Filter by sentiment',
                                  style={'fontSize': '0.8em'}),
                        dcc.Dropdown(
                            id='global-rts-sentiment-select',
                            options=[
                                {'label': i, 'value': i}
                                for i in ['All', 'Positive', 'Negative']
                            ],
                            value='Negative')],
                            className='col-md-4'
                            ),
                ],
                className='col-md-12'
            ),
            style={'margin': '1em 0 2em 0'},
            className='col-md-12'),
        className='col-md-12'
    ),
    dbc.Row([
        dbc.Col(
            dbc.Row(
                html.Div(id='global-rts', className='rts')),
            style={'maxHeight': '50em', 'overflow-y': 'scroll'},
            className='col-md-5'
        ),
        dbc.Col(
            [
                dbc.Row(
                    dcc.Graph(id='global-rts-cumulative')
                ),
                dbc.Row(
                    dcc.Graph(id='global-rts-delta')
                )
            ],
            className='col-md-6'

        )
    ])
]

# engagements
viral_engagements_content = [
    dbc.Row(
        BURSTY_QUOTED_TWEETS,
        style={'margin': '3em 0'},
        className='col-md-12'
    ),
    html.Hr(),
    dbc.Row(
        VIRAL_GLOBAL_RETWEETS,
        style={'margin': '3em 0'},
        className='col-md-12'),
    html.Hr()]

if COUNTRY:
    viral_engagements_content.extend(
        [dbc.Row(
            VIRAL_LOCAL_RETWEETS,
            style={'margin': '3em 0'},
            className='col-md-12'),
         html.Hr()]
    )

VIRAL_ENGAGEMENTS = dbc.Container(viral_engagements_content)
