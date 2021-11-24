import json
import pandas as pd
from datetime import datetime as dt

# import dash_table
# import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash_html_components.Img import Img

import plotly.express as px
import plotly.graph_objects as go

from constants import *
from dash_constants import *
from utils.common import human_format

# Load basic stats data
with open(BASICS_PATH) as json_file:
    basic_data = json.load(json_file)

# Load daily tweets data
df_tweets_daily_count = pd.read_csv(DAILY_TWEETS_PATH)
fig_tweets_daily_count = px.line(
    df_tweets_daily_count, x='tweet_date', y='count', template=DASH_TEMPLATE)
fig_tweets_daily_count.update_layout(title="Daily tweets count",
                                     font=dict(
                                         family="Verdana, monospace",
                                         size=14
                                     ),
                                     margin=dict(l=0, r=0, t=100, b=0),
                                     xaxis_title=None,
                                     yaxis_title=None)

# Load potentially sensitive tweets data
c_sg_tweets_pst = pd.read_csv(POTENTIALLY_SENSITIVE_TWEETS_COUNT_PATH)
spike_value = c_sg_tweets_pst['count'].quantile(
    POTENTIALLY_SENSITIVE_TWEETS_DEFAULT_PERCENTILE)
colors = ["red" if cc > spike_value else "green" for cc in c_sg_tweets_pst['count']]
fig_psts = px.bar(c_sg_tweets_pst, x="tweet_date", y="count", template=DASH_TEMPLATE, color=colors,
                  width=700, height=420)
fig_psts.update_layout(title="Daily potentially sensitive tweets count",
                       font=dict(
                           family="Verdana, monospace",
                           size=10
                       ),
                       margin=dict(l=0, r=0, t=30, b=0),
                       showlegend=False,
                       xaxis_title=None,
                       yaxis_title=None)

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
                        html.A(html.P(style={'fontSize': '1em',
                                      'color': '#000'}, children=tw["quoted_tweet_text"]),
                               target="blank_",
                               href=TWITTER_STATUS_PATH.format(tw["quoted_user_screenname"], tw["quoted_tweet_id"])),
                        html.P(
                            className="quoted-info",
                            children=[
                                html.Span('Posted by: '),
                                html.Span(tw["quoted_user_screenname"]),
                                html.Span(children=' ☑' if tw["quoted_user_verified"] else '', style={
                                    'color': '#0096FF'}),
                                html.Span(
                                    Img(
                                        className='quoted-flag',
                                        # src="https://cdn.countryflags.com/thumbs/singapore/flag-400.png"
                                        src="https://cdn.countryflags.com/thumbs/{}/flag-400.png".format(
                                            tw['quoted_user_geo_coding'].lower())
                                    )
                                ),

                                html.Span(" | Created on: " +
                                          dt.strftime(dt.strptime(
                                              tw["quoted_tweet_date"], DATE_FORMAT), DASH_FORMAT)),

                                # tw["quoted_tweet_date"].strftime("%m/%d/%Y")),
                                html.Span(
                                    " | 🔁 ", className='quoted-endorsements'),
                                html.Span(
                                    "+", className='quoted-endorsements'),
                                html.Span(
                                    "🤍 : ", className='quoted-endorsements'),
                                html.Span(human_format(tw["total_engagement"]))

                            ]),

                        dbc.Progress(
                            value=str(tw["spread_rate"]),
                            max="100",
                            # animated=True,
                            children=str(tw["spread_rate"]) + "%",
                            className="mb-3",
                            color="#32CD32" if str(
                                tw["spread_type"]) == 'positive' else '#C70039',
                            style={'height': '1.4em', 'fontSize': '0.8em'}
                        )

                    ],
                ),
            ],
                className="tw-card-body"
            )))


BASIC_STATS = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Tweets Stats",
                        className="card-title"),
                html.Div(
                    [html.P([
                        html.Span(basic_data['total_tweets'], style={
                            "fontWeight": 'bold'}),
                        html.Span(" tweets")
                    ]
                    ),
                        html.P([
                            html.Span("{} to {}".format(
                                dt.strftime(dt.strptime(
                                    basic_data["min_date"], DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                dt.strftime(dt.strptime(
                                    basic_data["max_date"], DATE_FORMAT), DASH_FORMAT)),
                                style={"fontWeight": 'bold'}),
                            html.Span(" duration")
                        ]),
                        html.P([
                            html.Span(basic_data['users_count'], style={
                                "fontWeight": 'bold'}),
                            html.Span(
                                " unique Singapore-based twitter users")
                        ]),
                        html.P([
                            html.Span(basic_data['avg_tweets'], style={
                                "fontWeight": 'bold'}),
                            html.Span(
                                " average no. of tweets per day")
                        ])]
                )
            ],
            className='tweets-stats-body'
        ),
    ],
    style={'width': '100%', 'marginTop': '6em'}
)


DAILY_TWEETS = dcc.Loading(
    id="loading-daily-tweets",
    children=[
        dcc.Graph(figure=fig_tweets_daily_count)],
    type="dot"
)

MENTIONS_HASHTAGS_SENTIMENT = [
    dbc.Col(
        dcc.Loading(
            id="loading-hashtags",
            children=[
                dcc.Graph(id="fig_hashtags")],
            type="dot",

        ), className="col-md-4"),
    dbc.Col(
        dcc.Loading(
            id="loading-mentions",
            children=[
                dcc.Graph(id="fig_mentions")],
            type="dot"
        ), className="col-md-4"),
    dbc.Col(
        dcc.Loading(
            id="loading-sentiments",
            children=[
                dcc.Graph(id="fig_sentiments")],
            type="dot"
        ), className="col-md-4")
]

DATEPICK_MENTIONS_HASHTAGS_SENTIMENT = dcc.DatePickerRange(
    id='hash-mention-sent-datepick',
    min_date_allowed=basic_data["min_date"],
    max_date_allowed=basic_data["max_date"],
    initial_visible_month=basic_data["min_date"]
    # end_date=date()
)

MENTIONS_HASHTAGS_SENTIMENT_INFO = dbc.Jumbotron(
    dbc.Row(
        [dbc.Col(
            children=[
                html.Span("Trending hashtags, mentions and public sentiment",
                          style={'color': '#0096FF', 'marginRight': '10px'}),
                html.P(MENTIONS_HASHTAGS_SENTIMENT_INFO_CONTENT)
            ],
            className="col-md-8"
        ),
            dbc.Col([
                html.Span("Filter by date", style={
                    "fontSize": "0.8em"}),
                DATEPICK_MENTIONS_HASHTAGS_SENTIMENT
            ],
            className="col-md-4"
        ),
        ],
        className="col-md-12"
    ),
    style={'margin': '1em 0 2em 0'},
    className="col-md-12")


DATEPICK_PSTS = dcc.DatePickerSingle(
    id='psts-datepick',
    className="datepick-label",
    min_date_allowed=basic_data["min_date"],
    max_date_allowed=basic_data["max_date"],
    initial_visible_month=basic_data["min_date"],
    date=basic_data["min_date"],
    style={"width": "3em"}
)


PSTS_INFO = dbc.Jumbotron(
    dbc.Row(
        [dbc.Col(
            children=[
                html.Span("Potentially sensitive tweets: ",
                          style={'color': '#0096FF', 'marginRight': '10px'}),
                html.P(PSTS_INFO_CONTENT)
            ],
            className="col-md-8"
        ),
            dbc.Col([
                html.Span("Filter by date", style={
                    "fontSize": "0.8em"}),
                DATEPICK_PSTS
            ],
            className="col-md-4"
        ),
        ],
        className="col-md-12"
    ),
    style={'margin': '1em 0 2em 0'},
    className="col-md-12")

PSTS = [
    dbc.Col(
        dcc.Loading(
            id="loading-psts",
            children=[
                dcc.Graph(figure=fig_psts)],
            type="dot"
        ),
        className="col-md-8"
    ),

    dbc.Col(
        dcc.Loading(
            id="loading-psts-tweets",
            children=[
                dcc.Graph(id="freq-count-psts-tweets")],
            type="dot",
        ),
        className="col-md-4"
    )
]


INFLUENTIAL_USERS_INFO = dbc.Jumbotron(
    dbc.Row(
        [dbc.Col(
            children=[
                html.Span("Interactions graph: ",
                          style={'color': '#000', 'marginRight': '10px'}),
                html.P(INTERACTIONS_GRAPH_INFO_CONTENT),
                html.Span("Influential users: ",
                          style={'color': '#0096FF', 'marginRight': '10px'}),
                html.P(INFLUENTIAL_USERS_INFO_CONTENT),
            ],
            className="col-md-8"
        ),
            dbc.Col([
                html.Span("Filter by country", style={
                    "fontSize": "0.8em"}),
                dcc.Dropdown(
                    id="dropdown-top-influence-users-countries",
                    options=[
                        {"label": i, "value": i}
                        for i in influential_users_countries
                    ],
                    value='Singapore')],
                    className="col-md-4"
                    ),
        ],
        className="col-md-12"
    ),
    style={'margin': '1em 0 2em 0'},
    className="col-md-12")


INFLUENTIAL_COUNTRIES_INFO = dbc.Jumbotron(
    dbc.Row(
        [dbc.Col(
            children=[
                html.Span("Influential countries: ",
                          style={'color': '#0096FF', 'marginRight': '10px'}),
                html.P(INFLUENTIAL_COUNTRIES_INFO_CONTENT),
            ],
            className="col-md-8"
        ),
            dbc.Col([
                html.Span("Filter by country", style={
                    "fontSize": "0.8em"}),
                dcc.Dropdown(
                    id="dropdown-top-influence-countries",
                    # clearable=False, style={"cursor": "pointer", 'borderRadius': 0, "width": "200px",
                    #                         "margin": '0.5em', "fontSize": "0.8em"},
                    options=[
                        {"label": i, "value": i}
                        for i in sorted(list(country_data['country']))
                    ],
                    value=most_influential_country)
            ],
            className="col-md-4",
        ),
        ],
        className="col-md-12"
    ),
    style={'margin': '1em 0 2em 0'},
    className="col-md-12")


INFLUENTIAL_USERS = [
    dbc.Row(
        html.H5(["Influential users"]),
        className="col-md-12"
    ),
    dbc.Row(
        INFLUENTIAL_USERS_INFO,
        className="col-md-12"
    ),
    dbc.Row(
        children=[],
        id="influencers-chips-row"
    )]


INFLUENTIAL_COUNTRIES = [
    dbc.Col(
        dcc.Loading(
            id="loading-influential-country_map",
            children=[
                dcc.Graph(
                    id='fig-world-influence'
                )],
            type="dot",
        ),
        className="col-md-8"
    ),
    dbc.Col(
        dcc.Loading(
            id="loading-influential-country_words",
            children=[
                dcc.Graph(id="word-cloud-influential-country")],
            type="dot",
        ),
        className="col-md-4"
    )
]


BURSTY_QUOTED_TWEETS = [
    dbc.Row(
        html.H5(["Reactive tweets"]),
        className="col-md-12"
    ),
    dbc.Row(
        dbc.Jumbotron(
            dbc.Row(
                [dbc.Col(
                    children=[
                        html.Span("Viral quoted tweets: ",
                                  style={'color': '#000', 'marginRight': '10px'}),
                        html.P(

                            VIRAL_QUOTED_INFO_CONTENT.format(
                                dt.strftime(dt.strptime(
                                            basic_data["min_date"], DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                dt.strftime(dt.strptime(
                                            basic_data["max_date"], DATE_FORMAT), DASH_FORMAT))
                        ),
                        html.Span("Reactive tweets: ",
                                  style={'color': '#0096FF', 'marginRight': '10px'}),
                        html.P(REACTIVE_TWEETS_INFO_CONTENT),
                    ],
                    className="col-md-12"
                )
                ],
                className="col-md-12"
            ),
            style={'margin': '1em 0 2em 0'},
            className="col-md-12"),
        className="col-md-12"
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Alert("Positive outburst",
                              className="alert-heading", style={"color": 'green'}),
                    dbc.Row(children=[create_quoted_card(
                        tw) for _, tw in quoted_spread_data_pos.iterrows()])
                ], className="outburst", style={"maxHeight": "40em", "overflowY": "scroll"}
            ),
            dbc.Col(
                [
                    dbc.Alert("Negative outburst",
                              className="alert-heading", style={"color": '#C70039'}),
                    dbc.Row(id="neg-quotes-sentiment", className="outburst", style={"maxHeight": "40em", "overflowY": "scroll"},
                            children=[create_quoted_card(tw) for _, tw in quoted_spread_data_neg.iterrows()])
                ]
            )
        ]
    ),

]


VIRAL_LOCAL_RETWEETS = [
    dbc.Row(
        html.H5(["Viral local Retweets"]),
        className="col-md-12"
    ),
    dbc.Row(
        dbc.Jumbotron(
            dbc.Row(
                [dbc.Col(
                    children=[
                        html.Span("Viral local retweets:",
                                  style={'color': '#0096FF', 'marginRight': '10px'}),
                        html.Span(
                            VIRAL_RETWEETS_DATE_INFO_CONTENT
                            .format(
                                dt.strftime(dt.strptime(
                                            basic_data["min_date"], DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                dt.strftime(dt.strptime(
                                            basic_data["max_date"], DATE_FORMAT), DASH_FORMAT)), className="rts-jumbotron"),
                        html.Span("Singapore geocoded accounts ",
                                  className="country-rts-jumbotron"),
                        html.Span(VIRAL_RETWEETS_INFO_CONTENT,
                                  className="rts-jumbotron"),
                    ],
                    className="col-md-8"
                ),
                    dbc.Col([
                        html.Span("Filter by sentiment",
                                  style={"fontSize": "0.8em"}),
                        dcc.Dropdown(
                            id="local-rts-sentiment-select",
                            options=[
                                {"label": i, "value": i}
                                for i in ['All', 'Positive', 'Negative']
                            ],
                            value='Negative')],
                            className="col-md-4"
                            ),
                ],
                className="col-md-12"
            ),
            style={'margin': '1em 0 2em 0'},
            className="col-md-12"),
        className="col-md-12"
    ),
    dbc.Row([
        dbc.Col(
            dbc.Row(
                html.Div(id="local-rts", className='rts')),
            style={'maxHeight': '50em', 'overflow-y': "scroll"},
            className="col-md-5"
        ),
        dbc.Col(
            [
                dbc.Row(
                    dcc.Graph(id="local-rts-cumulative")
                ),
                dbc.Row(
                    dcc.Graph(id="local-rts-delta")
                )
            ],
            className="col-md-6"

        )
    ])
]


VIRAL_GLOBAL_RETWEETS = [
    dbc.Row(
        html.H5(["Viral global Retweets"]),
        className="col-md-12"
    ),
    dbc.Row(
        dbc.Jumbotron(
            dbc.Row(
                [dbc.Col(
                    children=[
                        html.Span("Viral global retweets:",
                                  style={'color': '#0096FF', 'marginRight': '10px'}),
                        html.Span(
                            VIRAL_RETWEETS_DATE_INFO_CONTENT.
                            format(
                                dt.strftime(dt.strptime(
                                            basic_data["min_date"], DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                dt.strftime(dt.strptime(
                                            basic_data["max_date"], DATE_FORMAT), DASH_FORMAT)), className="rts-jumbotron"),
                        html.Span("Non-Singapore geocoded accounts ",
                                  className="country-rts-jumbotron"),
                        html.Span(
                            VIRAL_RETWEETS_INFO_CONTENT, className="rts-jumbotron"),
                    ],
                    className="col-md-8"
                ),
                    dbc.Col([
                        html.Span("Filter by sentiment",
                                  style={"fontSize": "0.8em"}),
                        dcc.Dropdown(
                            id="global-rts-sentiment-select",
                            options=[
                                {"label": i, "value": i}
                                for i in ['All', 'Positive', 'Negative']
                            ],
                            value='Negative')],
                            className="col-md-4"
                            ),
                ],
                className="col-md-12"
            ),
            style={'margin': '1em 0 2em 0'},
            className="col-md-12"),
        className="col-md-12"
    ),
    dbc.Row([
        dbc.Col(
            dbc.Row(
                html.Div(id="global-rts", className='rts')),
            style={'maxHeight': '50em', 'overflow-y': "scroll"},
            className="col-md-5"
        ),
        dbc.Col(
            [
                dbc.Row(
                    dcc.Graph(id="global-rts-cumulative")
                ),
                dbc.Row(
                    dcc.Graph(id="global-rts-delta")
                )
            ],
            className="col-md-6"

        )
    ])
]

MAIN_CONTAINER = dbc.Container([
    dbc.Row(
        [
            dbc.Col(
                BASIC_STATS,
                className="col-md-4"
            ),
            dbc.Col(
                DAILY_TWEETS,
                className="col-md-8"
            )
        ]),

    html.Hr(),
    dbc.Row(
        MENTIONS_HASHTAGS_SENTIMENT_INFO,
        className="col-md-12"
    ),
    dbc.Row(
        MENTIONS_HASHTAGS_SENTIMENT,
        style={"margin": "3em 0"},
        className="col-md-12"
    ),
    html.Hr(),

    dbc.Row(
        PSTS_INFO,
        className="col-md-12"
    ),
    dbc.Row(
        PSTS
    ),
    html.Hr(),

    dbc.Row(
        INFLUENTIAL_USERS,
        style={"margin": "3em 0"},
        className="col-md-12"
    ),
    html.Hr(),

    dbc.Row(
        [
            dbc.Row(
                html.H5(["Foreign influence"]),
                className="col-md-12"
            ),
            dbc.Row(
                INFLUENTIAL_COUNTRIES_INFO,
                className="col-md-12"
            ),
            dbc.Row(
                INFLUENTIAL_COUNTRIES, className="col-md-12"
            )],
        style={"margin": "3em 0"},
        className="col-md-12"
    ),
    html.Hr(),

    dbc.Row(
        BURSTY_QUOTED_TWEETS,
        style={"margin": "3em 0"},
        className="col-md-12"
    ),
    html.Hr(),

    dbc.Row(
        VIRAL_LOCAL_RETWEETS,
        style={"margin": "3em 0"},
        className="col-md-12"
    ),
    html.Hr(),


    dbc.Row(
        VIRAL_GLOBAL_RETWEETS,
        style={"margin": "3em 0"},
        className="col-md-12"
    ),
    html.Hr()
])

NAVBAR = dbc.Row(
    children=[
        Img(
            style={"margin": "0.4em", "width": "3em"},
            src="assets/pulse.png"
        ),
        html.P("Singapore's Pulse Monitoring through Twitter's Lens",
               style={"fontSize": "1.2em", "marginTop": "0.4em", "color": "#C70039"}),
        Img(
            style={"margin": "0 0.7em", "width": "1.8%", "height": "1%"},
            src="assets/twitter-logo.png"
        ),
    ],
    style={"justifyContent":  "center", "fontSize": "1.2em"},
    className='main-navbar'
    # color="#f5f5f5",
    # dark=True,
    # sticky="top",
)


# html.Div([
#     cyto.Cytoscape(
#         id='cytoscape-two-nodes',
#         layout={'name': 'cose'},
#         style={'width': '900em', 'height': '100em', 'color': 'red', 'fontSize': '12px'},
#         elements=cytoscape_data['elements']['nodes']
#         # stylesheet=default_stylesheet

#         # elements= [
#         #     {'data': {'id': 'one', 'label': 'Node 1'},
#         #      'position': {'x': 75, 'y': 75}},
#         #     {'data': {'id': 'two', 'label': 'Node 2'},
#         #      'position': {'x': 200, 'y': 200}},
#         #     {'data': {'source': 'one', 'target': 'two'}}
#         # ]
#     )
# ]),


# cytoscape_data = None
# with open('data/output/interactions/cytoscape.json') as json_file:
#     cytoscape_data = json.load(json_file)

# with urllib.request.urlopen(BASE_PATH + 'output/basics/basic.json') as url:
#     basic_data = json.loads(url.read().decode())
