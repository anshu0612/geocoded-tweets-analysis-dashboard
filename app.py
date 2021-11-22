from dash_data.basics import generate_dash_hashtags, generate_dash_mentions, generate_dash_sentiments
import os
import warnings
from components import *
# from base_algos.image_tsne import generate_image_tsne_plot
# from base_algos.generate_wordcloud import plotly_wordcloud
from utils.common import human_format
import pandas as pd
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input
import dash
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
# import pycountry
# import json
# import dload
# import math
# from datetime import datetime as dt
from constant import BASE_URL

app_env = 'prod'  # 'local'

# DEPLOY_PATH = "https://rpm-dashboard-data.s3.ap-southeast-1.amazonaws.com"
# LOCAL_PATH = "dash-data"

# DATA_PATH = DEPLOY_PATH

########################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# server = app.server
# style={'backgroundColor': '#ffffff'}
app.layout = html.Div(children=[NAVBAR, MAIN_CONTAINER])


BASE_PATH = 'data/'
sg_tweets = pd.read_csv(BASE_PATH + "sg.csv")


# local --------
all_local_rts_trend = pd.read_csv(
    BASE_URL + 'output/rts/local/all_local_rts_trend.csv')
all_local_rts_info = pd.read_csv(
    BASE_URL + 'output/rts/local/all_local_rts_info.csv', index_col=0)

pos_local_rts_trend = pd.read_csv(
    BASE_URL + 'output/rts/local/pos_local_rts_trend.csv')
pos_local_rts_info = pd.read_csv(
    BASE_URL + 'output/rts/local/pos_local_rts_info.csv', index_col=0)

neg_local_rts_trend = pd.read_csv(
    BASE_URL + 'output/rts/local/neg_local_rts_trend.csv')

neg_local_rts_info = pd.read_csv(
    BASE_URL + 'output/rts/local/neg_local_rts_info.csv', index_col=0)


# global --------
all_global_rts_trend = pd.read_csv(
    BASE_URL + 'output/rts/global/all_global_rts_trend.csv')
all_global_rts_info = pd.read_csv(
    BASE_URL + 'output/rts/global/all_global_rts_info.csv', index_col=0)

pos_global_rts_trend = pd.read_csv(
    BASE_URL + 'output/rts/global/pos_global_rts_trend.csv')
pos_global_rts_info = pd.read_csv(
    BASE_URL + 'output/rts/global/pos_global_rts_info.csv', index_col=0)

neg_global_rts_trend = pd.read_csv(
    BASE_URL + 'output/rts/global/neg_global_rts_trend.csv')

neg_global_rts_info = pd.read_csv(
    BASE_URL + 'output/rts/global/neg_global_rts_info.csv', index_col=0)


# influencial countries
top_countries_data = pd.read_csv(
    BASE_URL + 'output/influencers/top_countries_data.csv')


influential_users = pd.read_csv(
    BASE_URL + 'output/influencers/top_users.csv')


country_data = pd.read_csv(BASE_URL + 'output/influencers/top_countries.csv')


GRAPHS_TEMPLATE = 'plotly_white'


def generate_rts_info(tw):
    return (
        dbc.CardBody(
            [
                html.P(style={'fontSize': '1em',
                              'color': '#000'}, children=tw["tweet_text_"]),

                html.P(
                    className="quoted-info",
                    children=[
                        html.Span('Posted by: '),
                        html.Span(tw["retweeted_user_screenname"]),
                        html.Span(" | Created on: " +
                                  dt.strftime(dt.strptime(
                                      tw["tweet_date"], DATE_FORMAT), DASH_FORMAT)),
                        html.Span(
                            " | 🔁 ", className='quoted-endorsements'),
                        html.Span(
                            "+", className='quoted-endorsements'),
                        html.Span(
                            "🤍 : ", className='quoted-endorsements'),
                        html.Span(human_format(tw["total_engagement"]),
                                  className='quoted-endorsements'),
                        html.Span(
                            "| Sentiment : ", className='quoted-endorsements'),
                        html.Span(tw["tweet_sentiment"],
                                  style={
                            "color": "green" if tw["tweet_sentiment"] == 'positive' else "#C70039"}
                        )
                    ]
                )
            ],
            className="tw-card-body",
            style={"borderLeft":  '10px solid {}'.format(tw["color"]),
                   "borderBottom":  '2px solid {}'.format(tw["color"])
                   }
        ))

    # ])


COUNTRY = 'Singapore'


def plotly_wordcloud(tweets_text, filtered_for):
    text = " ".join(list(tweets_text))

    STOPWORDS.update([COUNTRY])

    word_cloud = WordCloud(
        stopwords=set(STOPWORDS)
    )

    word_cloud.generate(text)
    word_list = []
    freq_list = []

    for (word, freq), _, _, _, _ in word_cloud.layout_:
        word_list.append(word)
        freq_list.append(freq)

    word_list_top = word_list[:25]
    freq_list_top = freq_list[:25]

    frequency_fig_data = px.bar(
        template="plotly_white",
        x=freq_list_top[::-1],
        y=word_list_top[::-1],
        orientation='h'
    )

    frequency_fig_data.update_traces(marker_color='#40B5AD')
    frequency_fig_data.update_layout(
        title="Frequent words for " + filtered_for,
        font=dict(
            family="Verdana, monospace",
            size=10
        ),
        margin=dict(l=10, r=10, t=40, b=60),
        xaxis_title=None,
        yaxis_title=None
    )
    return frequency_fig_data


@app.callback(
    [Output("fig-world-influence", "figure"),
        Output("word-cloud-influential-country", "figure")],
    Input("dropdown-top-influence-countries", "value"),
)
def gen_global_temporal_tweets_count(country):

    x = top_countries_data[top_countries_data['retweeted_user_geo_coding']
                           == country]['processed_tweet_text']
    # most_influential_country = str(
    #     country_data.iloc[country_data['count'].idxmax()]['country'])

    fig_world_influence = go.Figure(go.Scattermapbox(
        mode="markers+lines",
        lon=[SG_LONG],
        lat=[SG_LAT],
        name='Singapore',
        text=['Singapore'],
        marker={'size': 2}))

    selected_country_data = country_data[country_data['country'] == country].to_dict('records')[
        0]
    for _, row in country_data.iterrows():
        fig_world_influence.add_trace(go.Scattermapbox(
            mode="markers+lines",
            lon=[row['long'], SG_LONG],
            lat=[row['lat'], SG_LAT],
            name=row['country'],
            text=[row['country'], 'Singapore'],
            marker={'size': [row['size'], 2]}))

    fig_world_influence.update_traces(
        textposition="bottom right", hoverinfo="text",)
    fig_world_influence.update_layout(
        # height=300,
        margin={'l': 0, 't': 0, 'b': 50, 'r': 0},
        dragmode=False,
        showlegend=True,
        mapbox={
            'style': "open-street-map",
            'center': {'lon': selected_country_data['long'], 'lat':  selected_country_data['lat']},
            'zoom': 2})

    fig_world_influence.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    return (fig_world_influence, plotly_wordcloud(list(x), country))


pst_tweets = pd.read_csv(BASE_URL + "output/basics/pst_tweets.csv")


@app.callback(
    Output('freq-count-psts-tweets', 'figure'),
    Input('psts-datepick', 'date'))
def psts_output(date):
    pst_tweets_by_date = pst_tweets[
        pst_tweets['processed_tweet_text'].notna() &
        pst_tweets['tweet_date'].between(
        date, date, inclusive='both')]['processed_tweet_text']
    return plotly_wordcloud(list(pst_tweets_by_date), str(date))


@app.callback(
    [Output('fig_hashtags', 'figure'),
     Output('fig_mentions', 'figure'),
     Output('fig_sentiments', 'figure')],
    Input('hash_mention_sent_datepick', 'start_date'),
    Input('hash_mention_sent_datepick', 'end_date'))
def update_hash_mentions_sent_output(start_date, end_date):
    df_hashtags = generate_dash_hashtags(sg_tweets, start_date, end_date)
    fig_hashtags = px.bar(df_hashtags, x="counts", y="hashtag",
                          orientation='h', template="plotly_white")

    fig_hashtags.update_layout(
        title="Top hashtags distribution",
        margin=dict(l=0, r=0, t=30, b=4),
        xaxis_title=None,
        yaxis_title=None
    )

    df_mentions = generate_dash_mentions(sg_tweets, start_date, end_date)
    fig_mentions = px.bar(df_mentions, x="counts", y="mention",
                          orientation='h', template="plotly_white")
    fig_mentions.update_layout(
        title="Top mentions distribution",
        margin=dict(l=0, r=0, t=30, b=4),
        xaxis_title=None,
        yaxis_title=None
    )

    df_sentiments = generate_dash_sentiments(sg_tweets, start_date, end_date)
    fig_sentiments = px.bar(df_sentiments, x="count", y="tweet_sentiment",
                            orientation='h', template="plotly_white", color="tweet_sentiment")
    fig_sentiments.update_layout(
        title="Sentiments distribution",
        margin=dict(l=0, r=0, t=30, b=4),
        xaxis_title=None,
        yaxis_title=None
    )

    return (fig_hashtags, fig_mentions, fig_sentiments)


@app.callback(
    [
        Output("local-rts-cumulative", "figure"),
        Output("local-rts-delta", "figure"),
        Output("local-rts", "children"),
        # Output("local-rts-table", "columns")
        # Output("local-rts-table", "colors")
    ],
    Input("local-rts-sentiment-select", "value")
    # ],
)
def get_local_rts_trend(selected_sentiment):

    trend_data = all_local_rts_trend
    info_data = all_local_rts_info
    if selected_sentiment == 'Negative':
        trend_data = neg_local_rts_trend
        info_data = neg_local_rts_info
    elif selected_sentiment == 'Positive':
        trend_data = pos_local_rts_trend
        info_data = pos_local_rts_info

    fig_trend_cum = px.line(trend_data,
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                            x="tweet_date",
                            y="total_engagement",
                            hover_name="retweeted_user_screenname",
                            hover_data={"retweeted_user_screenname": False,
                                        "retweeted_tweet_id": False},
                            color="retweeted_tweet_id",
                            text="total_engagement",
                            template=GRAPHS_TEMPLATE)
    fig_trend_cum.update_traces(textposition="bottom right")
    fig_trend_cum.update_layout(
        # autosize=True,
        # width=900,'
        height=400,
        showlegend=False,
        title=None,
        xaxis_title="Retweet date",
        yaxis_title="Cumulative engagements"
    )

    fig_trend_delta = px.line(trend_data,
                              color_discrete_sequence=px.colors.qualitative.Pastel,
                              x="tweet_date",
                              y="delta_engagement",
                              hover_name="retweeted_user_screenname",
                              hover_data={
                                  "retweeted_user_screenname": False, "retweeted_tweet_id": False},
                              color="retweeted_tweet_id",
                              text="delta_engagement",
                              template=GRAPHS_TEMPLATE)

    fig_trend_delta.update_traces(textposition="bottom right")
    fig_trend_delta.update_layout(
        # width=900,
        height=400,
        showlegend=False,
        title=None,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Retweet date",
        yaxis_title="Increment in engagements"
    )

    rts_info = [generate_rts_info(tw) for _, tw in info_data.iterrows()]

    # data = info_data.to_dict('records')
    # columns = [{"name": i, "id": i} for i in info_data.columns]

    return (fig_trend_cum, fig_trend_delta, rts_info)


@app.callback(
    [
        Output("global-rts-cumulative", "figure"),
        Output("global-rts-delta", "figure"),
        Output("global-rts", "children"),
        # Output("global-rts-table", "columns")
        # Output("global-rts-table", "colors")
    ],
    Input("global-rts-sentiment-select", "value")
    # ],
)
def get_global_rts_trend(selected_sentiment):

    trend_data = all_global_rts_trend
    info_data = all_global_rts_info
    if selected_sentiment == 'Negative':
        trend_data = neg_global_rts_trend
        info_data = neg_global_rts_info
    elif selected_sentiment == 'Positive':
        trend_data = pos_global_rts_trend
        info_data = pos_global_rts_info

    # pull csv based on sentiment
    fig_trend_cum = px.line(trend_data,
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                            x="tweet_date",
                            y="total_engagement",
                            hover_name="retweeted_user_screenname",
                            hover_data={"retweeted_user_screenname": False,
                                        "retweeted_tweet_id": False},
                            color="retweeted_tweet_id",
                            text="total_engagement",
                            template=GRAPHS_TEMPLATE)
    fig_trend_cum.update_traces(textposition="bottom right")
    fig_trend_cum.update_layout(
        showlegend=False,
        title=None,
        xaxis_title="Retweet date",
        yaxis_title="Cumulative engagements"
    )

    fig_trend_delta = px.line(trend_data,
                              color_discrete_sequence=px.colors.qualitative.Pastel,
                              x="tweet_date",
                              y="delta_engagement",
                              hover_name="retweeted_user_screenname",
                              hover_data={
                                  "retweeted_user_screenname": False, "retweeted_tweet_id": False},
                              color="retweeted_tweet_id",
                              text="delta_engagement",
                              template=GRAPHS_TEMPLATE)

    fig_trend_delta.update_traces(textposition="bottom right")
    fig_trend_delta.update_layout(
        showlegend=False,
        title=None,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Retweet date",
        yaxis_title="Increment in engagements"
    )

    rts_info = [generate_rts_info(tw) for _, tw in info_data.iterrows()]

    # data = info_data.to_dict('records')
    # columns = [{"name": i, "id": i} for i in info_data.columns]

    return (fig_trend_cum, fig_trend_delta, rts_info)


def generate_influential_users(idx, tw):
    return (

        dbc.Row(
            html.P(
                className="influencer-chip",
                children=[
                    html.Span(str(idx + 1) + ". " + tw["user_screenname"]),
                    html.Span(children=' ☑' if tw["user_verified"] else '', style={
                        'color': '#0096FF'}),
                    html.Span(
                        Img(
                            className="influencer-flag",
                            style={"width": "2em"},
                            src="https://cdn.countryflags.com/thumbs/{}/flag-400.png".format(
                                tw['user_geo_coding'].lower())
                            if tw['user_geo_coding'] != "Unknown" else ""
                        )
                    )
                ]),
            className='influencer-badge'
        )
    )


@app.callback(
    Output("influencers-chips-row", "children"),
    Input("dropdown-top-influence-users-countries", "value")
)
def gen_infuential_users_by_country(country):
    if country == 'All':
        filtered_users = influential_users
    else:
        filtered_users = influential_users[influential_users['user_geo_coding'] == country]

    return [generate_influential_users(i, tw) for i, tw in filtered_users.iterrows()]


warnings.filterwarnings('ignore')
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
