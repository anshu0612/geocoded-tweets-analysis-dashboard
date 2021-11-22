import json
from dash_bootstrap_components._components.CardBody import CardBody
from dash_bootstrap_components._components.Row import Row
from dash_core_components.Graph import Graph
from dash_html_components.Div import Div
from dash_html_components.Hr import Hr
from dash_html_components.Img import Img
from dash_html_components.Span import Span
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash_html_components.Br import Br
import dash_table
import plotly.express as px
import pandas as pd
from constant import *
from datetime import datetime as dt
from datetime import date
import urllib.request
# import dash_cytoscape as cyto
from utils.common import human_format

import pandas as pd

# add basic json
quoted_spread_data = pd.read_csv(
    BASE_URL + 'output/quoted/sentiment_spread.csv')
quoted_spread_data_pos = quoted_spread_data[quoted_spread_data['spread_type'] == 'positive']
quoted_spread_data_neg = quoted_spread_data[quoted_spread_data['spread_type'] == 'negative']


country_data = pd.read_csv(BASE_URL + 'output/influencers/top_countries.csv')
most_influential_country = str(
    country_data.iloc[country_data['count'].idxmax()]['country'])

# cytoscape_data = None
# with open('data/output/interactions/cytoscape.json') as json_file:
#     cytoscape_data = json.load(json_file)

# with urllib.request.urlopen(BASE_URL + 'output/basics/basic.json') as url:
#     basic_data = json.loads(url.read().decode())


with open(BASE_URL + 'output/basics/basic.json') as json_file:
    basic_data = json.load(json_file)


def generate_quoted_data(tw):
    print("-"*10)
    print(tw)
    return (
        dbc.CardBody(
            dbc.Row([
                dbc.Col(
                    [
                        html.P(style={'fontSize': '1em',
                                      'color': '#000'}, children=tw["quoted_tweet_text"]),
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


# Static data
QUOTED_POS = []

# default_stylesheet = [
#     {
#         'selector': 'node',
#         'style': {
#             'background-color': '#BFD7B5',
#             'label': 'data(label)',
#             'width': "4%",
#             'height': "4%"
#         }
#     }
# ]

influential_users = pd.read_csv(
    BASE_URL + 'output/influencers/top_users.csv')
influential_users_countries = list(
    influential_users['user_geo_coding'].unique())
influential_users_countries.append('All')
influential_users_countries = sorted(influential_users_countries)

df_hashtags = pd.read_csv(BASE_URL + 'output/basics/hashtags.csv')
df_mentions = pd.read_csv(BASE_URL + 'output/basics/mentions.csv')
df_sentiments = pd.read_csv(BASE_URL + 'output/basics/sentiments.csv')

fig_hashtags = px.bar(df_hashtags, x="counts", y="hashtag",
                      orientation='h', template="plotly_white")
fig_hashtags.update_layout(
    title="Top hashtags distribution",
    margin=dict(l=0, r=0, t=30, b=4),
    xaxis_title=None,
    yaxis_title=None
)

fig_mentions = px.bar(df_mentions, x="counts", y="mention",
                      orientation='h', template="plotly_white")
fig_mentions.update_layout(
    title="Top mentions distribution",
    margin=dict(l=0, r=0, t=30, b=4),
    xaxis_title=None,
    yaxis_title=None
)

fig_sentiments = px.bar(df_sentiments, x="count", y="tweet_sentiment",
                        orientation='h', template="plotly_white", color="tweet_sentiment")
fig_sentiments.update_layout(
    title="Sentiments distribution",
    margin=dict(l=0, r=0, t=30, b=4),
    xaxis_title=None,
    yaxis_title=None
)


df_tweets_daily_count = pd.read_csv(
    BASE_URL + "output/basics/daily_tweets.csv")
fig_tweets_daily_count = px.line(
    df_tweets_daily_count, x='tweet_date', y='count', template="plotly_white")


c_sg_tweets_pst = pd.read_csv(BASE_URL + "output/basics/pst_counts.csv")
spike_value = c_sg_tweets_pst['count'].quantile(0.95)
colors = ["red" if cc > spike_value else "green" for cc in c_sg_tweets_pst['count']]
fig_psts = px.bar(c_sg_tweets_pst, x="tweet_date", y="count", template='plotly_white', color=colors,
                  height=spike_value)
fig_psts.update_layout(showlegend=False)
# fig.show()


MAIN_CONTAINER = dbc.Container([

    dbc.Row(
        [
            dbc.Col(

                dbc.Card(
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
                                            html.Span(basic_data['avg_tweets'], style={
                                                "fontWeight": 'bold'}),
                                            html.Span(
                                                " average no. of tweets per day")
                                        ])],
                                    style={'display': 'flex',
                                           'justifyContent': 'space-between'}
                                )
                            ],
                            className='tweets-stats-body'
                        ),
                    ],
                    style={'width': '100%', 'marginTop': '2em'}
                ),
                className="col-md-4"
            ),
            dbc.Col(
                dcc.Graph(
                    figure=fig_tweets_daily_count,
                    className="col-md-8"
                )
            )
        ]),
    dbc.Row(
        [
            html.Div(id="temp"),
            dcc.DatePickerRange(
                id='hash_mention_sent_datepick',
                min_date_allowed=basic_data["min_date"],
                max_date_allowed=basic_data["max_date"],
                initial_visible_month=basic_data["min_date"]
                # end_date=date()
            ),
        ],
        className="col-md-12"
    ),
    dbc.Row(
        [
            dcc.Graph(
                id="fig_hashtags",
                figure=fig_hashtags,
                className="col-md-4"
            ),
            dcc.Graph(
                id="fig_mentions",
                figure=fig_mentions,
                className="col-md-4"
            ),
            dcc.Graph(
                id="fig_sentiments",
                figure=fig_sentiments,
                className="col-md-4"
            )
        ],

        style={"margin": "3em 0"},
        className="col-md-12"
    ),

    dcc.DatePickerSingle(
        id='psts-datepick',
        min_date_allowed=basic_data["min_date"],
        max_date_allowed=basic_data["max_date"],
        initial_visible_month=basic_data["min_date"],
        date=basic_data["min_date"]
    ),
    dbc.Row(
        [
            dbc.Col(
                dcc.Graph(
                    figure=fig_psts,
                    className="col-md-8"
                )
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
    ),


    dbc.Row(
        [
            dbc.Row(
                html.H5(["Foreign influence"]),
                className="col-md-12"
            ),
            dbc.Row(
                dbc.Jumbotron(
                    dbc.Row(
                        [dbc.Col(
                            children=[
                                html.Span("Influential countries: ",
                                          style={'color': '#0096FF', 'marginRight': '10px'}),
                                html.P(
                                    "Tweets by non-Singapore based users with a high number of engagements - retweets and quoted tweets, by Singapore users."
                                    " Bubble sizes reflect the relative total engagements, received by country-specific tweets."),
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
                    className="col-md-12"),
                className="col-md-12"
            ),
            dbc.Row(
                [
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
                ], className="col-md-12"
            )],
        style={"margin": "3em 0"},
        className="col-md-12"
    ),

    dbc.Row(
        [
            dbc.Row(
                html.H5(["Bursty tweets"]),
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
                                    "Tweets created between {} and {} that are (1) highly quoted by count or (2)"
                                    " received an unusual number of endorsements - retweets and favorites"
                                    .format(
                                        dt.strftime(dt.strptime(
                                            basic_data["min_date"], DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                        dt.strftime(dt.strptime(
                                            basic_data["max_date"], DATE_FORMAT), DASH_FORMAT))
                                ),
                                html.Span("Bursty tweets: ",
                                          style={'color': '#0096FF', 'marginRight': '10px'}),
                                html.P(
                                    "Viral quoted tweets with high intensity ( >= 80% ) of extreme sentiments (positive and negative sentiments)"),
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
                            dbc.Row([generate_quoted_data(tw)
                                     for _, tw in quoted_spread_data_pos.iterrows()])
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Alert("Negative outburst",
                                      className="alert-heading", style={"color": '#C70039'}),
                            dbc.Row([generate_quoted_data(tw)
                                     for _, tw in quoted_spread_data_neg.iterrows()])
                        ]
                    )
                ]
            ),

        ],
        style={"margin": "3em 0"},
        className="col-md-12"
    ),

    dbc.Row(
        [
            dbc.Row(
                html.H5(["Influential users"]),
                className="col-md-12"
            ),
            dbc.Row(
                dbc.Jumbotron(
                    dbc.Row(
                        [dbc.Col(
                            children=[
                                html.Span("Interactions graph: ",
                                          style={'color': '#000', 'marginRight': '10px'}),
                                html.P(
                                    "A directed weighted graph of interactions - replies, retweets, and quoted tweets"
                                    " between the users.  The weights denote the number of interactions between two users."),
                                html.Span("Influential users: ",
                                          style={'color': '#0096FF', 'marginRight': '10px'}),
                                html.P(
                                    "Applied PageRanking on interactions graph to get the top 50 users."
                                    " The number signifies the ranking of a user. "),
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
                    className="col-md-12"),
                className="col-md-12"
            ),
            dbc.Row(
                children=[],
                id="influencers-chips-row"
            )],
        style={"margin": "3em 0"},
        className="col-md-12"
    ),

    dbc.Row(
        [
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
                                    "Tweets created between {} and {} that are (1) by "
                                    .format(
                                        dt.strftime(dt.strptime(
                                            basic_data["min_date"], DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                        dt.strftime(dt.strptime(
                                            basic_data["max_date"], DATE_FORMAT), DASH_FORMAT)), className="rts-jumbotron"),
                                html.Span("Singapore geocoded accounts ",
                                          className="country-rts-jumbotron"),
                                html.Span(
                                    "(2) highly retweeted by count or (3) received an unusual number of endorsements - retweets and favorites", className="rts-jumbotron"),
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
                    className="col-md-4"
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
                    className="col-md-8"

                )
            ])
        ],
        style={"margin": "3em 0"},
        className="col-md-12"
    ),


    dbc.Row(
        [
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
                                    "Tweets created between {} and {} that are (1) by ".
                                    format(
                                        dt.strftime(dt.strptime(
                                            basic_data["min_date"], DATE_FORMAT), DASH_NO_YEAR_FORMAT),
                                        dt.strftime(dt.strptime(
                                            basic_data["max_date"], DATE_FORMAT), DASH_FORMAT)), className="rts-jumbotron"),
                                html.Span("Non-Singapore geocoded accounts ",
                                          className="country-rts-jumbotron"),
                                html.Span(
                                    "(2) highly retweeted by count or (3) received an unusual number of endorsements - retweets and favorites", className="rts-jumbotron"),
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
                    className="col-md-4"
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
                    className="col-md-8"

                )
            ])
        ],
        style={"margin": "3em 0"},
        className="col-md-12"
    ),
])

NAVBAR = dbc.Navbar(
    children=[
        Img(
            style={"margin": "0 1em", "width": "4em"},
            src="https://cdn.countryflags.com/thumbs/{}/flag-400.png".format(
                'singapore')
        ),
        html.P("Singapore's Pulse Monitoring through Twitter's Lens"),
        Img(
            style={"margin": "0 1em", "width": "3%"},
            src="assets/twitter-logo.png"
        ),
    ],
    style={"justifyContent":  "center", "fontSize": "1.2em"},
    className='main-navbar',
    # color="#f5f5f5",
    dark=True,
    sticky="top",
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
