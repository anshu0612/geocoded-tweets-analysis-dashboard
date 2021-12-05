from utils.common import human_format
from datetime import datetime as dt

import plotly.express as px
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_html_components.Img import Img

from constants.dash_constants import DASH_DATE_FORMAT, ERROR_INSUFFICIENT_TWEETS
from constants.common import FLAG_FIX_USA, FLAG_URL, DATE_FORMAT, TWITTER_BASE_URL

# dummy figure


def get_dummy_fig(msg):
    dummy_fig = px.treemap(
        names=[msg],
        parents=['']
    )
    dummy_fig.update_layout(margin=dict(t=20, l=0, r=0, b=0))
    return dummy_fig


def generate_rewteets_info(tw):
    return (
        dbc.CardBody(
            [
                html.P(style={'fontSize': '1em',
                                          'color': '#000'}, children=tw['tweet_text_']),
                html.P(
                    className='quoted-info',
                    children=[
                        html.Span('Posted by: ', className='more-info'),
                        html.A(html.Span(tw['retweeted_user_screenname']),
                               target='_blank',
                               href=TWITTER_BASE_URL + tw['retweeted_user_screenname']),
                        html.Span(
                            children=' ✅' if tw['retweeted_user_verified'] else ''),
                        html.Span(
                            Img(
                                className='quoted-flag',
                                src=FLAG_URL.format(
                                    tw['retweeted_user_geo_coding'].lower().replace(
                                        ' ', '-')
                                    if tw['retweeted_user_geo_coding'].lower() != 'united states' else FLAG_FIX_USA)
                            )
                        ),
                        html.Span(' | Created on: ', className='more-info'),
                        html.Span(dt.strftime(dt.strptime(
                            tw['retweeted_tweet_date'], DATE_FORMAT), DASH_DATE_FORMAT)),
                        html.Span(
                            ' | 🔁 ', className='quoted-endorsements'),
                        html.Span(
                            '+', className='quoted-endorsements'),
                        html.Span(
                            '🤍 : ', className='quoted-endorsements'),
                        html.Span(human_format(tw['total_engagement']),
                                  className='quoted-endorsements'),
                        html.Span(
                            '| Sentiment : ', className='quoted-endorsements more-info'),
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
                        href=TWITTER_BASE_URL + tw['user_screenname'], className="twitter-user"),
                    html.Span(children=' ✅' if tw['user_verified'] else '', style={
                              'fontSize': '0.6em'}),
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


def communities_users_ui(idx, username):
    return html.P(html.A(html.Span(str(
        idx + 1) + '. ' + username),
        className='twitter-user',
        target='blank_',
        href=TWITTER_BASE_URL + username))
