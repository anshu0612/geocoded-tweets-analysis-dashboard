# import dash_table
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash_html_components.Img import Img

from constants.dash_constants import NAVBAR_TITLE, TWITTER_LOGO_PATH, APP_LOGO

NAVBAR = dbc.Row(
    children=[
        Img(
            style={'margin': '0.4em', 'width': '3em'},
            src=APP_LOGO
        ),
        html.P(NAVBAR_TITLE,
               style={'fontSize': '1.2em', 'marginTop': '0.4em', 'color': '#26466D'}),
        # html.P('Interactive dashboard built using PLotly'),
        Img(
            style={'margin': '0 0.7em', 'width': '1.8%', 'height': '1%'},
            src=TWITTER_LOGO_PATH
        ),
    ],
    style={'justifyContent':  'center', 'fontSize': '1.2em'},
    className='main-navbar'
)
