# from os import path
from matplotlib.pyplot import title
import pandas as pd
import warnings

import dash
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import dash_html_components as html
from wordcloud import WordCloud, STOPWORDS
import plotly.express as px
from dash.exceptions import PreventUpdate


from constants import BASE_PATH
from components import *
from dash_constants import *
from utils.common import human_format
from dash_modules.basics import generate_dash_hashtags, \
    generate_dash_mentions, \
    generate_dash_sentiments, \
    get_date_range


# setup
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
# app.layout = html.Div(children=[NAVBAR, MAIN_CONTAINER])

ROUTE_TITLE_STYLE = {'margin': '1em 1em', 'color': 'rgb(0, 150, 255)'}
app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    dbc.Row(
        [dcc.Link('Tweets', href=HOME_PATH, style=ROUTE_TITLE_STYLE),
         dcc.Link('Retweets/Quoted Tweets', href=ENGAGEMENTS_PATH,
                  style=ROUTE_TITLE_STYLE),
         dcc.Link('Influencers', href=INFLUENCERS_PATH,
                  style=ROUTE_TITLE_STYLE),
         dcc.Link('Networking', href=NETWORKING_PATH, style=ROUTE_TITLE_STYLE)],
        style={'display': 'flex', 'justifyContent': 'center'}
    ),
    # content will be rendered in this element
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == NETWORKING_PATH:
        return html.Div(children=[NAVBAR, NETWORKING])
    elif pathname == ENGAGEMENTS_PATH:
        return html.Div(children=[NAVBAR, VIRAL_ENGAGEMENTS])
    elif pathname == INFLUENCERS_PATH:
        return html.Div(children=[NAVBAR, INFLUENCERS])
    else:
        return html.Div(children=[NAVBAR, TWEETS])


# load the tweets
sg_tweets = pd.read_csv(SG_TWEETS_PATH)

min_date, max_date = get_date_range(sg_tweets)

# influencial countries
top_countries_data = pd.read_csv(TOP_COUNTRIES_CLEANED_DATA)
influential_users = pd.read_csv(INFLUENTIAL_USERS_PATH)
country_data = pd.read_csv(TOP_COUNTRY_INFLUENCER_PATH)


dummy_fig = px.treemap(
    names=[ERROR_INSUFFICIENT_TWEETS],
    parents=['']
)
dummy_fig.update_layout(margin=dict(t=40, l=40, r=40, b=25))


def generate_rts_info(tw):
    return (
        dbc.CardBody(
            [
                html.A(html.P(style={'fontSize': '1em',
                              'color': '#000'}, children=tw['tweet_text_']),
                       target='blank_',
                       href=TWITTER_STATUS_PATH.format(
                           tw['retweeted_user_screenname'], tw['retweeted_tweet_id']),
                       ),

                html.P(
                    className='quoted-info',
                    children=[
                        html.Span('Posted by: '),
                        html.Span(tw['retweeted_user_screenname']),
                        html.Span(
                            Img(
                                className='quoted-flag',
                                src=FLAG_URL.format(
                                    tw['retweeted_user_geo_coding'].lower().replace(
                                        ' ', '-')
                                    if tw['retweeted_user_geo_coding'].lower() != 'united states' else FLAG_FIX_USA)
                            )
                        ),
                        html.Span(' | Created on: ' +
                                  dt.strftime(dt.strptime(
                                      tw['retweeted_tweet_date'], DATE_FORMAT), DASH_FORMAT)),
                        html.Span(
                            ' | 🔁 ', className='quoted-endorsements'),
                        html.Span(
                            '+', className='quoted-endorsements'),
                        html.Span(
                            '🤍 : ', className='quoted-endorsements'),
                        html.Span(human_format(tw['total_engagement']),
                                  className='quoted-endorsements'),
                        html.Span(
                            '| Sentiment : ', className='quoted-endorsements'),
                        html.Span(tw['tweet_sentiment'],
                                  style={
                            'color': 'green' if tw['tweet_sentiment'] == 'positive' else '#C70039'}
                        )
                    ]
                )
            ],
            className='tw-card-body',
            style={'borderRight':  '10px solid {}'.format(tw['color']),
                   'borderBottom':  '2px solid {}'.format(tw['color'])
                   }
        ))

    # ])


def plotly_wordcloud(tweets_text, filtered_for):

    if len(tweets_text) < 10:
        return None

    text = ' '.join(tweets_text)

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
        template=DASH_TEMPLATE,
        x=freq_list_top[::-1],
        y=word_list_top[::-1],
        orientation='h'
    )

    frequency_fig_data.update_traces(marker_color='#1ca9c9')
    frequency_fig_data.update_layout(
        title='Frequent words on {} tweets for {}'.format(
            len(tweets_text), filtered_for),
        font=dict(
            family='Verdana, monospace',
            size=10
        ),
        margin=dict(l=10, r=10, t=40, b=60),
        xaxis_title=None,
        yaxis_title=None
    )
    return frequency_fig_data


@app.callback(
    [Output('fig-hashtags', 'figure'),
     Output('fig-mentions', 'figure'),
     Output('fig-sentiments', 'figure')],
    Input('url', 'pathname'),
    Input('hash-mention-sent-datepick', 'start_date'),
    Input('hash-mention-sent-datepick', 'end_date'))
def update_hash_mentions_sent_output(pathname, start_date, end_date):
    if not pathname == HOME_PATH:
        raise PreventUpdate

    df_hashtags = generate_dash_hashtags(sg_tweets, start_date, end_date)
    fig_hashtags = px.bar(df_hashtags, x='counts', y='hashtag',
                          color_discrete_sequence=['#E49B0F'],
                          orientation='h', template=DASH_TEMPLATE)
    fig_hashtags.update_layout(
        title='Top hashtags distribution',
        margin=dict(l=200, r=0, t=30, b=4),
        xaxis_title=None,
        yaxis_title=None
    )

    df_mentions = generate_dash_mentions(sg_tweets, start_date, end_date)
    fig_mentions = px.bar(df_mentions, x='counts', y='mention',
                          color_discrete_sequence=['#009ACD'],
                          orientation='h', template=DASH_TEMPLATE)
    fig_mentions.update_layout(
        title='Top mentions distribution',
        margin=dict(l=0, r=0, t=30, b=4),
        xaxis_title=None,
        yaxis_title=None
    )

    df_sentiments = generate_dash_sentiments(sg_tweets, start_date, end_date)
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

    return (fig_hashtags, fig_mentions, fig_sentiments)


@app.callback(
    [Output('fig-world-influence', 'figure'),
        Output('word-cloud-influential-country', 'figure')],
    Input('url', 'pathname'),
    Input('dropdown-top-influence-countries', 'value'),
)
def gen_influential_countries_wordfreq(pathname, country):
    if not pathname == INFLUENCERS_PATH:
        raise PreventUpdate

    x = top_countries_data[top_countries_data['retweeted_user_geo_coding']
                           == country]['processed_tweet_text']
    # most_influential_country = str(
    #     country_data.iloc[country_data['count'].idxmax()]['country'])

    fig_world_influence = go.Figure(go.Scattermapbox(
        mode='markers+lines',
        lon=[SG_LONG],
        lat=[SG_LAT],
        name='Singapore',
        text=['Singapore'],
        marker={'size': 2}))

    selected_country_data = country_data[country_data['country'] == country].to_dict('records')[
        0]
    for _, row in country_data.iterrows():
        fig_world_influence.add_trace(go.Scattermapbox(
            mode='markers+lines',
            lon=[row['long'], SG_LONG],
            lat=[row['lat'], SG_LAT],
            name=row['country'],
            text=[row['country'], 'Singapore'],
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
        words_freq = dummy_fig

    return (fig_world_influence, words_freq)


pst_tweets = pd.read_csv(POTENTIALLY_SENSITIVE_TWEETS_PATH)
# pst_tweets = generate_dash_potentially_sensitive_tweets(sg_tweets)


@app.callback(
    Output('freq-count-psts-tweets', 'figure'),
    Input('url', 'pathname'),
    Input('psts-datepick', 'date'))
def psts_output(pathname, date=min_date):
    if not pathname == HOME_PATH:
        raise PreventUpdate

    pst_tweets_by_date = pst_tweets[
        pst_tweets['processed_tweet_text'].notna() &
        pst_tweets['tweet_date'].between(
            date, date, inclusive='both')]['processed_tweet_text']

    words_freq = plotly_wordcloud(list(pst_tweets_by_date), str(date))

    if not words_freq:
        words_freq = dummy_fig

    return words_freq


# df_hashtags = pd.read_csv(HASHTAGS_PATH)
# df_mentions = pd.read_csv(MENTIONS_PATH)
# df_sentiments = pd.read_csv(SENTIMENTS_PATH)

# local --------
all_local_rts_trend = pd.read_csv(ALL_LOCAL_RTS_TREND_PATH)
all_local_rts_info = pd.read_csv(ALL_LOCAL_RTS_INFO_PATH)

pos_local_rts_trend = pd.read_csv(POS_LOCAL_RTS_TREND_PATH)
pos_local_rts_info = pd.read_csv(POS_LOCAL_RTS_INFO_PATH)

neg_local_rts_trend = pd.read_csv(NEG_LOCAL_RTS_TREND_PATH)
neg_local_rts_info = pd.read_csv(NEG_LOCAL_RTS_INFO_PATH)


# global --------
all_global_rts_trend = pd.read_csv(ALL_GLOBAL_RTS_TREND_PATH)
all_global_rts_info = pd.read_csv(ALL_GLOBAL_RTS_INFO_PATH)

pos_global_rts_trend = pd.read_csv(POS_GLOBAL_RTS_TREND_PATH)
pos_global_rts_info = pd.read_csv(POS_GLOBAL_RTS_INFO_PATH)

neg_global_rts_trend = pd.read_csv(NEG_GLOBAL_RTS_TREND_PATH)
neg_global_rts_info = pd.read_csv(NEG_GLOBAL_RTS_INFO_PATH)


@app.callback(
    [
        Output('local-rts-cumulative', 'figure'),
        Output('local-rts-delta', 'figure'),
        Output('local-rts', 'children'),
        # Output('local-rts-table', 'columns')
        # Output('local-rts-table', 'colors')
    ],
    Input('url', 'pathname'),
    Input('local-rts-sentiment-select', 'value')
    # ],
)
def get_local_rts_trend(pathname, selected_sentiment):
    if not pathname == ENGAGEMENTS_PATH:
        raise PreventUpdate

    trend_data = all_local_rts_trend
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
                            template=GRAPHS_TEMPLATE)
    fig_trend_cum.update_traces(textposition='bottom right')
    fig_trend_cum.update_layout(
        # autosize=True,
        # width=900,'
        height=400,
        showlegend=False,
        title=None,
        xaxis_title='Retweet date',
        yaxis_title='Cumulative engagements'
    )
    # fig_trend_cum.update_layout(
    #     legend=dict(
    #         x=0,
    #         y=1,
    #         # title='Anshu',
    #         t: {text: None},
    #         # traceorder='reversed',
    #         title_font_family='Times New Roman',
    #         font=dict(
    #             family='Courier',
    #             size=12,
    #             color='black'
    #         ),
    #         bgcolor='LightSteelBlue',
    #         bordercolor='Black',
    #         borderwidth=2
    #     )
    # )

    fig_trend_delta = px.line(trend_data,
                              color_discrete_sequence=px.colors.qualitative.Alphabet,
                              x='tweet_date',
                              y='delta_engagement',
                              hover_name='retweeted_user_screenname',
                              hover_data={
                                  'retweeted_user_screenname': False, 'retweeted_tweet_id': False},
                              color='retweeted_tweet_id',
                              text='delta_engagement',
                              template=GRAPHS_TEMPLATE)

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

    rts_info = [generate_rts_info(tw) for _, tw in info_data.iterrows()]

    # data = info_data.to_dict('records')
    # columns = [{'name': i, 'id': i} for i in info_data.columns]

    return (fig_trend_cum, fig_trend_delta, rts_info)


@app.callback(
    [
        Output('global-rts-cumulative', 'figure'),
        Output('global-rts-delta', 'figure'),
        Output('global-rts', 'children'),
        # Output('global-rts-table', 'columns')
        # Output('global-rts-table', 'colors')
    ],
    Input('url', 'pathname'),
    Input('global-rts-sentiment-select', 'value')
    # ],
)
def get_global_rts_trend(pathname, selected_sentiment):
    if not pathname == ENGAGEMENTS_PATH:
        raise PreventUpdate

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
                            color_discrete_sequence=px.colors.qualitative.Alphabet,
                            x='tweet_date',
                            y='total_engagement',
                            hover_name='retweeted_user_screenname',
                            hover_data={'retweeted_user_screenname': False,
                                        'retweeted_tweet_id': False},
                            color='retweeted_tweet_id',
                            text='total_engagement',
                            template=GRAPHS_TEMPLATE)
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
                              template=GRAPHS_TEMPLATE)

    fig_trend_delta.update_traces(textposition='bottom right')
    fig_trend_delta.update_layout(
        showlegend=False,
        title=None,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title='Retweet date',
        yaxis_title='Increment in engagements'
    )

    rts_info = [generate_rts_info(tw) for _, tw in info_data.iterrows()]

    return (fig_trend_cum, fig_trend_delta, rts_info)


def generate_influential_users(idx, tw):
    return (

        dbc.Row(
            html.P(
                className='influencer-chip',
                children=[
                    html.A(html.Span(str(
                        idx + 1) + '. ' + tw['user_screenname']),
                        style={'cursor': 'pointer'},
                        target='blank_',
                        href=TWITTER_BASE_URL + tw['user_screenname'],),
                    html.Span(children=' ☑' if tw['user_verified'] else '', style={
                        'color': '#0096FF'}),
                    html.Span(
                        Img(
                            className='influencer-flag',
                            style={'width': '2em'},
                            src=FLAG_URL.format(
                                tw['user_geo_coding'].lower().replace(' ', '-') if tw['user_geo_coding'].lower() != 'united states' else FLAG_FIX_USA)
                            if tw['user_geo_coding'] != 'Unknown' else ''
                        )
                    )
                ]),
            className='influencer-badge'
        )
    )


@ app.callback(
    Output('influencers-chips-row', 'children'),
    Input('url', 'pathname'),
    Input('dropdown-top-influence-users-countries', 'value')
)
def gen_infuential_users_by_country(pathname, country):
    if not pathname == INFLUENCERS_PATH:
        raise PreventUpdate
    if country == 'All':
        filtered_users = influential_users
    else:
        filtered_users = influential_users[influential_users['user_geo_coding'] == country]

    return [generate_influential_users(i, tw) for i, tw in filtered_users.iterrows()]


with open(COMMUNITIES_TWEETS_PATH, 'r') as f:
    clusters_tweets = json.load(f)


with open(COMMUNITIES_PATH, 'r') as f:
    clusters_users = json.load(f)


def cluster_user_ui(idx, username):
    return html.P(html.A(html.Span(str(
        idx + 1) + '. ' + username),
        style={'cursor': 'pointer'},
        target='blank_',
        href=TWITTER_BASE_URL + username), className='influencer-badge')


@ app.callback(
    [Output('word-freq-clusters', 'figure'),
     Output('clusters-users', 'children')],
    Input('url', 'pathname'),
    Input('dropdown-clusters', 'value')
)
def gen_infuential_users_by_country(pathname, cluster):
    if not pathname == NETWORKING_PATH:
        raise PreventUpdate

    words_freq = plotly_wordcloud(
        clusters_tweets[cluster], 'Cluster ' + cluster)
    if not words_freq:
        words_freq = dummy_fig

    cluster_users_ui = []
    for idx, u in enumerate(clusters_users[cluster]):
        cluster_users_ui.append(
            cluster_user_ui(idx, u)
            # html.Div([html.A(u, href=TWITTER_BASE_URL + u)])
        )

    return (words_freq, cluster_users_ui)


warnings.filterwarnings('ignore')
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)


# @app.callback(
#     [Output('pos-quotes-sentiment', 'children'),
#      Output('neg-quotes-sentiment', 'children')],
#     Input('quoted-bursty-datepick', 'start_date'),
#     Input('quoted-bursty-datepick', 'end_date'))
# def update_quoted_sentiments_by_date(start_date, end_date):
#     min_date, max_date = get_date_range(sg_tweets)

#     tweet_enagagement_quotes = get_formatted_quoted_tweets(sg_tweets)
#     quoted_tweets = get_quoted_tweets_by_date(
#         tweet_enagagement_quotes, min_date, max_date, start_date, end_date)
#     bursty_quoted_tweets = get_bursty_quoted_tweets(quoted_tweets)

#     most_spread_quoted_by_sentiment_with_rate = get_most_spread_quoted_by_sentiment_with_rate(
#         bursty_quoted_tweets)
#     quoted_spread_data = generate_dash_bursty_quotes_by_sentiment(
#         bursty_quoted_tweets, most_spread_quoted_by_sentiment_with_rate)

#     quoted_spread_data = pd.read_csv(
#         BASE_PATH + 'output/quoted/sentiment_spread.csv')
#     quoted_spread_data_pos = quoted_spread_data[quoted_spread_data['spread_type'] == 'positive']
#     quoted_spread_data_neg = quoted_spread_data[quoted_spread_data['spread_type'] == 'negative']

#     bursty_pos = [create_quoted_card(tw)
#                   for _, tw in quoted_spread_data_pos.iterrows()]
#     bursty_neg = [create_quoted_card(tw)
#                   for _, tw in quoted_spread_data_neg.iterrows()]

#     print('bursty_pos ---- : ', len(bursty_pos))
#     print('bursty_neg --- : ', len(bursty_neg))

#     return (bursty_pos, bursty_neg)
