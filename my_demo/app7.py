import os
import pathlib

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_daq as daq

import pandas as pd

app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)
app.title = 'Manufacturing SPC Dashboard'
server = app.server
app.config['suppress_callback_exceptions'] = True #

# 获取数据集文件的路径并读取
APP_PATH = str(pathlib.Path(__file__).parent.resolve()) # 1返回当前文件路径 2的上级目录 3的绝对路径
df = pd.read_csv(os.path.join(APP_PATH, os.path.join('data', 'spc_data.csv')))

params = list(df) # 所有列名
max_length = len(df)

suffix_row = '_row'
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"
suffix_count = "_count"
suffix_ooc_n = "_OOC_number"
suffix_ooc_g = "_OOC_graph"
suffix_indicator = "_indicator"


def build_banner():

    return html.Div(
        [
            html.Div(
                [
                    html.H5('Manufacturing SPC Dashboard'),
                    html.H6('Process Control and Exception Reporting')
                ],
                id='banner-text'
            ),
            html.Div(
                [
                    html.A(
                        html.Button(children='ENTERPRISE DEMO'),
                        href='https://plotly.com/get-demo'
                    ),
                    html.Button(
                        id='learn-more-button', children='LEARN MORE', n_clicks=0
                    ),
                    html.A(
                        html.Img(id='logo', src=app.get_asset_url('dash-logo-new.png')),
                        href='https://plotly.com/dash/'
                    )
                ],
                id='banner-logo'
            )
        ],
        id='banner',
        className='banner'
    )


# dcc.Tabs创建多个分表，dcc.Tab控制一个分表
def build_tabs():
    
    return html.Div(
        [
            dcc.Tabs(
                [
                    dcc.Tab(
                        id='Specs-tab',
                        label='Specification Settings',
                        value='tab1',
                        className='custom-tab',
                        selected_className='custom-tab--selected'
                    ),
                    dcc.Tab(
                        id='Control-chart-tab',
                        label='Control Charts Dashboard',
                        value='tab2',
                        className='custom-tab',
                        selected_className='custom-tab--selected'
                    )
                ],
                id='app-tabs',
                value='tab2',
                className='custom-tabs'
            )
        ],
        id='tabs',
        className='tabs'
    )


# 计算离群值的占比
def populate_occ(data, ucl, lcl):
    occ_count = 0
    ret = []
    for i in range(len(data)):
        if data[i] >= ucl or data[i] <= lcl:
            occ_count += 1
            ret.append(occ_count / (i + 1))
        else:
            ret.append(occ_count / (i + 1))
    return ret


# 初始化数据集
def init_df():
    ret = {}
    for col in list(df[1:]): # list(df[1:])：df所有列名的列表
        data = df[col]
        stats = data.describe()

        std = stats['std'].tolist()
        # 箱线图的四个端点值
        ucl = (stats["mean"] + 3 * stats["std"]).tolist() 
        lcl = (stats["mean"] - 3 * stats["std"]).tolist()
        usl = (stats["mean"] + stats["std"]).tolist()
        lsl = (stats["mean"] - stats["std"]).tolist()

        ret.update(
            {
                col: {
                    "count": stats["count"].tolist(),
                    "data": data,
                    "mean": stats["mean"].tolist(),
                    "std": std,
                    "ucl": round(ucl, 3),
                    "lcl": round(lcl, 3),
                    "usl": round(usl, 3),
                    "lsl": round(lsl, 3),
                    "min": stats["min"].tolist(),
                    "max": stats["max"].tolist(),
                    "ooc": populate_occ(data, ucl, lcl)
                }
            }
        )
    
    return ret


state_dict = init_df() # 获得初始化数据集后的字典


# 初始化原始数据集以作备用
def init_value_setter_store():
    state_dict = init_df()
    return state_dict


# 开始制作分表1
def build_tab1():
    return [
        # 手动选择指标
        html.Div(
            children=html.P("Use historical control limits to establish a benchmark, or set new values."),
            id='set-specs-intro-container',
            className='twelve columns'
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label(id='metric-select-title', children='Select Metrics'),
                        html.Br(),
                        dcc.Dropdown(
                            id='metric-select-dropdown',
                            options=[{'label': param, 'value': param} for param in params[1:]],
                            value=params[1]
                        )
                    ],
                    id='metric-select-menu',
                    className='five columns'
                ),
                html.Div(
                    [
                        html.Div(id='value-setter-panel'),
                        html.Br(),
                        html.Div(
                            [
                                html.Button('update', id='value-setter-set-btn'),
                                html.Button(
                                    'View current setup',
                                    id='value-setter-view-btn',
                                    n_clicks=0
                                )
                            ],
                            id='button-div'
                        ),
                        html.Div(
                            id="value-setter-view-output", className="output-datatable"
                        )
                    ],
                    id='value-setter-menu',
                    className='six columns'
                )
            ]
        )
    ]
