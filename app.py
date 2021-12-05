import json
import pandas as pd
import warnings

import dash
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go


from constants.common import COUNTRY
from constants.dash_constants import *

from utils.wordcloud import plotly_wordcloud
from dash_modules_generators.basics import generate_dash_hashtags, \
    generate_dash_mentions, \
    generate_dash_sentiments, \
    get_date_range

from dash_components.influencers import INFLUENCERS
from dash_components.networking import NETWORKING
from dash_components.navbar import NAVBAR
from dash_components.basics import TWEETS
from dash_components.engagements import *
from dash_components.reusables import *

# setup
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),
    NAVBAR,
    dbc.Row(
        [dcc.Link('Tweets', href=HOME_PATH, style=ROUTE_TITLE_STYLE),
         dcc.Link('Retweets/Quoted Tweets', href=ENGAGEMENTS_PATH,
                  style=ROUTE_TITLE_STYLE),
         dcc.Link('Influencers', href=INFLUENCERS_PATH,
                  style=ROUTE_TITLE_STYLE),
         dcc.Link('Networking', href=NETWORKING_PATH, style=ROUTE_TITLE_STYLE)],
        style={'display': 'flex', 'justifyContent': 'center'}
    ),
    html.Hr(),
    html.Div(id='page-content')
])


# --------------------------- Data Loading ----------------------------------
# tweets
tweets = pd.read_csv(TWEETS_PATH)

#  tweets date range
min_date, max_date = get_date_range(tweets)

# influential users
influential_users = pd.read_csv(INFLUENTIAL_USERS_PATH)

# influencial countries data
# ---- list of influencial countries
influential_countries = pd.read_csv(TOP_COUNTRY_INFLUENCER_PATH)
# --- tweets from the influencial countries
influential_countries_tweets = pd.read_csv(TOP_COUNTRY_INFLUENCER_TWEETS_PATH)

# potentially sensitive tweets
pst_tweets = pd.read_csv(POTENTIALLY_SENSITIVE_TWEETS_PATH)

# viral tweets through retweets
# -------- local
# local is only valid for country-specific tweets
if COUNTRY:
    all_local_rts_trend = pd.read_csv(ALL_LOCAL_RTS_TREND_PATH)
    all_local_rts_info = pd.read_csv(ALL_LOCAL_RTS_INFO_PATH)

    pos_local_rts_trend = pd.read_csv(POS_LOCAL_RTS_TREND_PATH)
    pos_local_rts_info = pd.read_csv(POS_LOCAL_RTS_INFO_PATH)

    neg_local_rts_trend = pd.read_csv(NEG_LOCAL_RTS_TREND_PATH)
    neg_local_rts_info = pd.read_csv(NEG_LOCAL_RTS_INFO_PATH)

# -------- global
all_global_rts_trend = pd.read_csv(ALL_GLOBAL_RTS_TREND_PATH)
all_global_rts_info = pd.read_csv(ALL_GLOBAL_RTS_INFO_PATH)

pos_global_rts_trend = pd.read_csv(POS_GLOBAL_RTS_TREND_PATH)
pos_global_rts_info = pd.read_csv(POS_GLOBAL_RTS_INFO_PATH)

neg_global_rts_trend = pd.read_csv(NEG_GLOBAL_RTS_TREND_PATH)
neg_global_rts_info = pd.read_csv(NEG_GLOBAL_RTS_INFO_PATH)

# communities tweets
with open(COMMUNITIES_TWEETS_PATH, 'r') as f:
    communities_tweets = json.load(f)

# communities users
with open(COMMUNITIES_USERS_PATH, 'r') as f:
    communities_users = json.load(f)

# communities network graph
with open(NETWORKING_DATA, 'r') as f:
    networking_graph_data = json.load(f)

# ----------------------------  Callbacks ----------------------------------

# routing callback


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def get_display_page(pathname):
    if pathname == NETWORKING_PATH:
        return html.Div(children=[NETWORKING])
    elif pathname == ENGAGEMENTS_PATH:
        return html.Div(children=[VIRAL_ENGAGEMENTS])
    elif pathname == INFLUENCERS_PATH:
        return html.Div(children=[INFLUENCERS])
    else:
        return html.Div(children=[TWEETS])


# callback for hashtags, mentions and sentiments update by `start_date` and `end_date`
@app.callback(
    [Output('fig-hashtags', 'figure'),
     Output('fig-mentions', 'figure'),
     Output('fig-sentiments', 'figure')],
    Input('url', 'pathname'),
    Input('hash-mention-sent-datepick', 'start_date'),
    Input('hash-mention-sent-datepick', 'end_date'))
def get_hash_mentions_sentiment_by_dates(pathname, start_date, end_date):
    if not pathname == HOME_PATH:
        raise PreventUpdate

    # hashtags
    df_hashtags = generate_dash_hashtags(tweets, start_date, end_date)
    if len(df_hashtags):
        fig_hashtags = px.bar(df_hashtags, x='counts', y='hashtag',
                              color_discrete_sequence=['#E49B0F'],
                              orientation='h', template=DASH_TEMPLATE)
        fig_hashtags.update_layout(
            title='Top hashtags distribution',
            margin=dict(l=200, r=0, t=30, b=4),
            xaxis_title=None,
            yaxis_title=None
        )
    else:
        fig_hashtags = get_dummy_fig(ERROR_INSUFFICIENT_HASHTAGS)

    # mentions
    df_mentions = generate_dash_mentions(tweets, start_date, end_date)
    if len(df_mentions):
        fig_mentions = px.bar(df_mentions, x='counts', y='mention',
                              color_discrete_sequence=['#009ACD'],
                              orientation='h', template=DASH_TEMPLATE)
        fig_mentions.update_layout(
            title='Top mentions distribution',
            margin=dict(l=0, r=0, t=30, b=4),
            xaxis_title=None,
            yaxis_title=None
        )
    else:
        fig_mentions = get_dummy_fig(ERROR_INSUFFICIENT_MENTIONS)

    # sentiments
    df_sentiments = generate_dash_sentiments(tweets, start_date, end_date)
    if len(df_sentiments):
        fig_sentiments = px.bar(df_sentiments, x='count', y='tweet_sentiment',
                                color_discrete_sequence=[
                                    '#1ca9c9', '#A6D785', '#cd5c5c'],
                                orientation='h', template=DASH_TEMPLATE, color='tweet_sentiment')
        fig_sentiments.update_layout(
            title='Sentiments distribution',
            margin=dict(l=0, r=0, t=30, b=4),
            xaxis_title=None,
            yaxis_title=None
        )
    else:
        fig_sentiments = get_dummy_fig(ERROR_INSUFFICIENT_SENTIMENTS)

    return (fig_hashtags, fig_mentions, fig_sentiments)


# callback for potentially sensitive tweets' frequent words update by `date`
@app.callback(
    Output('freq-count-psts-tweets', 'figure'),
    Input('url', 'pathname'),
    Input('psts-datepick', 'date'))
def get_potentially_sensitive_tweets_by_date(pathname, date=min_date):
    if not pathname == HOME_PATH:
        raise PreventUpdate

    pst_tweets_by_date = pst_tweets[
        pst_tweets['processed_tweet_text'].notna() &
        pst_tweets['tweet_date'].between(
            date, date, inclusive='both')]['processed_tweet_text']

    words_freq = plotly_wordcloud(list(pst_tweets_by_date), str(date))

    if not words_freq:
        words_freq = get_dummy_fig(ERROR_INSUFFICIENT_TWEETS)

    return words_freq


# callback for influential users update by `country`


@app.callback(
    Output('influencers-chips-row', 'children'),
    Input('url', 'pathname'),
    Input('dropdown-top-influence-users-countries', 'value')
)
def get_infuential_users_by_country(pathname, country='All'):
    if not pathname == INFLUENCERS_PATH:
        raise PreventUpdate
    if country == 'All':
        filtered_users = influential_users
    else:
        filtered_users = influential_users[influential_users['user_geo_coding'] == country]
    return [generate_influential_users(i, tw) for i, tw in filtered_users.iterrows()]


# callback for influential countries' tweets' frequent words update by `country`
@app.callback(
    [Output('fig-world-influence', 'figure'),
        Output('word-cloud-influential-country', 'figure')],
    Input('url', 'pathname'),
    Input('dropdown-top-influence-countries', 'value'),
)
def get_influential_countries_word_frequency_by_country(pathname, country):
    if not pathname == INFLUENCERS_PATH:
        raise PreventUpdate

    x = influential_countries_tweets[influential_countries_tweets['retweeted_user_geo_coding']
                                     == country]['processed_tweet_text']

    selected_country_data = influential_countries[influential_countries['country'] == country].to_dict('records')[
        0]

    # make country-centric with lines only if country-specific tweets collected
    if COUNTRY:
        country_data = influential_countries[influential_countries['country'] == COUNTRY]
        country_lat = country_data['lat']
        country_long = country_data['long']

        fig_world_influence = go.Figure(go.Scattermapbox(
            mode='markers+lines',
            lon=[country_long],
            lat=[country_lat],
            name=COUNTRY,
            text=[COUNTRY],
            marker={'size': 2}))

        for _, row in influential_countries.iterrows():
            fig_world_influence.add_trace(go.Scattermapbox(
                mode='markers+lines',
                lon=[row['long'], country_long],
                lat=[row['lat'], country_lat],
                name=row['country'],
                text=[row['country'], COUNTRY],
                marker={'size': [row['size'], 2]}))

    else:
        fig_world_influence = go.Figure(go.Scattermapbox())
        for _, row in influential_countries.iterrows():
            if row['country'] == COUNTRY:
                continue
            fig_world_influence.add_trace(go.Scattermapbox(
                mode='markers',
                lon=[row['long']],
                lat=[row['lat']],
                name=row['country'],
                text=[row['country']],
                marker={'size': [row['size'], 2]}))

    fig_world_influence.update_traces(
        textposition='bottom right', hoverinfo='text',)
    fig_world_influence.update_layout(
        # height=300,
        margin={'l': 0, 't': 0, 'b': 50, 'r': 0},
        dragmode=False,
        showlegend=True,
        mapbox={
            'style': 'open-street-map',
            'center': {'lon': selected_country_data['long'], 'lat':  selected_country_data['lat']},
            'zoom': 2})

    fig_world_influence.update_layout(legend=dict(
        yanchor='top',
        y=0.99,
        xanchor='left',
        x=0.01
    ))

    words_freq = plotly_wordcloud(list(x), country)

    if not words_freq:
        words_freq = get_dummy_fig(ERROR_INSUFFICIENT_TWEETS)

    return (fig_world_influence, words_freq)


# callback for viral local tweets (via retweeting) update by `sentiment`
@app.callback(
    [
        Output('local-rts-cumulative', 'figure'),
        Output('local-rts-delta', 'figure'),
        Output('local-rts', 'children'),
    ],
    Input('url', 'pathname'),
    Input('local-rts-sentiment-select', 'value')
)
def get_local_retweets_trend_by_sentiments(pathname, selected_sentiment):
    if not pathname == ENGAGEMENTS_PATH:
        raise PreventUpdate

    if not COUNTRY:
        # do not show this graph if not country specific
        raise PreventUpdate

    trend_data = all_local_rts_trend

    if len(trend_data):
        info_data = all_local_rts_info
        if selected_sentiment == 'Negative':
            trend_data = neg_local_rts_trend
            info_data = neg_local_rts_info
        elif selected_sentiment == 'Positive':
            trend_data = pos_local_rts_trend
            info_data = pos_local_rts_info

        fig_trend_cum = px.line(trend_data,
                                labels={},
                                color_discrete_sequence=px.colors.qualitative.Alphabet,
                                x='tweet_date',
                                y='total_engagement',
                                hover_name='retweeted_user_screenname',
                                hover_data={'retweeted_user_screenname': False,
                                            'retweeted_tweet_id': False},
                                color='retweeted_tweet_id',
                                text='total_engagement',
                                template=DASH_TEMPLATE)
        fig_trend_cum.update_traces(textposition='bottom right')
        fig_trend_cum.update_layout(
            height=400,
            showlegend=False,
            title=None,
            xaxis_title='Retweet date',
            yaxis_title='Cumulative engagements'
        )

        fig_trend_delta = px.line(trend_data,
                                  color_discrete_sequence=px.colors.qualitative.Alphabet,
                                  x='tweet_date',
                                  y='delta_engagement',
                                  hover_name='retweeted_user_screenname',
                                  hover_data={
                                    'retweeted_user_screenname': False, 'retweeted_tweet_id': False},
                                  color='retweeted_tweet_id',
                                  text='delta_engagement',
                                  template=DASH_TEMPLATE)

        fig_trend_delta.update_traces(textposition='bottom right')
        fig_trend_delta.update_layout(
            # width=900,
            height=400,
            showlegend=False,
            title=None,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title='Retweet date',
            yaxis_title='Increment in engagements'
        )

        rts_info = [generate_rewteets_info(tw)
                    for _, tw in info_data.iterrows()]
    else:
        rts_info = ERROR_LOCAL_RETWEETS
        fig_trend_delta = get_dummy_fig(ERROR_LOCAL_RETWEETS)
        fig_trend_cum = get_dummy_fig(ERROR_LOCAL_RETWEETS)

    return (fig_trend_cum, fig_trend_delta, rts_info)

# callback for viral global tweets (via retweeting) update by `sentiment`


@app.callback(
    [
        Output('global-rts-cumulative', 'figure'),
        Output('global-rts-delta', 'figure'),
        Output('global-rts', 'children')
    ],
    Input('url', 'pathname'),
    Input('global-rts-sentiment-select', 'value')
)
def get_global_retweets_trend_by_sentiment(pathname, selected_sentiment):
    if not pathname == ENGAGEMENTS_PATH:
        raise PreventUpdate

    trend_data = all_global_rts_trend

    if len(trend_data):
        info_data = all_global_rts_info
        if selected_sentiment == 'Negative':
            trend_data = neg_global_rts_trend
            info_data = neg_global_rts_info
        elif selected_sentiment == 'Positive':
            trend_data = pos_global_rts_trend
            info_data = pos_global_rts_info

        # pull csv based on sentiment
        fig_trend_cum = px.line(trend_data,
                                color_discrete_sequence=px.colors.qualitative.Alphabet,
                                x='tweet_date',
                                y='total_engagement',
                                hover_name='retweeted_user_screenname',
                                hover_data={'retweeted_user_screenname': False,
                                            'retweeted_tweet_id': False},
                                color='retweeted_tweet_id',
                                text='total_engagement',
                                template=DASH_TEMPLATE)
        fig_trend_cum.update_traces(textposition='bottom right')
        fig_trend_cum.update_layout(
            showlegend=False,
            title=None,
            xaxis_title='Retweet date',
            yaxis_title='Cumulative engagements'
        )

        fig_trend_delta = px.line(trend_data,
                                  color_discrete_sequence=px.colors.qualitative.Alphabet,
                                  x='tweet_date',
                                  y='delta_engagement',
                                  hover_name='retweeted_user_screenname',
                                  hover_data={
                                    'retweeted_user_screenname': False, 'retweeted_tweet_id': False},
                                  color='retweeted_tweet_id',
                                  text='delta_engagement',
                                  template=DASH_TEMPLATE)

        fig_trend_delta.update_traces(textposition='bottom right')
        fig_trend_delta.update_layout(
            showlegend=False,
            title=None,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title='Retweet date',
            yaxis_title='Increment in engagements'
        )

        rts_info = [generate_rewteets_info(tw)
                    for _, tw in info_data.iterrows()]

    else:
        rts_info = ERROR_LOCAL_RETWEETS
        fig_trend_delta = get_dummy_fig(ERROR_LOCAL_RETWEETS)
        fig_trend_cum = get_dummy_fig(ERROR_LOCAL_RETWEETS)

    return (fig_trend_cum, fig_trend_delta, rts_info)

# callback for community's frequent words by `country`


@app.callback(
    [Output('word-freq-communities', 'figure'),
     Output('communities-users', 'children')],
    Input('url', 'pathname'),
    Input('dropdown-communities', 'value')
)
def get_communities_word_frequency_by_country(pathname, community):
    if not pathname == NETWORKING_PATH:
        raise PreventUpdate

    words_freq = plotly_wordcloud(
        communities_tweets[community], 'Community ' + community, COMMUNITIES_COLORS_DICT[community])
    if not words_freq:
        words_freq = get_dummy_fig(ERROR_INSUFFICIENT_TWEETS)

    communities_users_ui_list = []
    for idx, u in enumerate(communities_users[community]['users']):
        communities_users_ui_list.append(
            communities_users_ui(idx, u)
        )

    return (words_freq, communities_users_ui_list)

# reset the networking graph


@app.callback(
    [Output('networking-graph-nodes', 'zoom'),
     Output('networking-graph-nodes', 'elements')],
    [Input('networking-graph-btn-reset', 'n_clicks')]
)
def reset_networking_graph(n_clicks):
    return [1, networking_graph_data['data']]


# ----------------------------  Flask Server -----------------
warnings.filterwarnings('ignore')
if __name__ == '__main__':
    app.run_server(debug=True,
                   host='localhost',
                   port=5000)
