# 11月份数据分析看板的demo

import os

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq

import plotly.express as px
import pandas as pd

app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)
app.title = 'Nov. data analysis'
server = app.server
# app.config['suppress_callback_exceptions'] = True #不懂什么意思

# font and background colors associated with each themes
bkg_color = '#F3F6FA'
grid_color = '#C8D4E3'
text_color = '#506784'

app.layout = html.Div(
    id='mainContainer',
    style={'display': 'flex', 'flex-direction': 'column'},
    children=[
        # dcc.Store(id='aggregate_data')
        html.Div(id='output_clientside'),
        html.Div(
            id='header',
            className='row flex-display',
            style={'margin-bottom': '25px'},
            children=[
                html.Div(
                    className='one-third column',
                    children=[
                        html.Img(
                            src=app.get_asset_url('dash-logo.png'),
                            id='plotly-image',
                            style={
                                'height': '60px',
                                'width': 'auto',
                                'margin-bottom': '25px'
                            }
                        )
                    ]
                ),
                html.Div(
                    id='title',
                    className='one-half column',
                    children=[
                        html.H3(
                            'Nov. data analysis',
                            style={'margin-bottom': '0px'}
                        ),
                        html.H5(
                            'Production Overview', 
                            style={'margin-top': '0px'}
                        )
                    ]
                ),
                html.Div(
                    id='button',
                    className='one-third column',
                    children=[
                        html.A(
                            html.Button('Learn More', id='learn-more-button'),
                            href='https://plot.ly/dash/pricing'
                        )
                    ]
                )
            ]
        )
    ]
)


# main
if __name__ == '__main__':
    app.run_server(debug=True)



