import os
import pickle
import pandas as pd
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import dcc, html


# multi-dropdown 选项
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS


app = dash.Dash(
    __name__, meta_tags=[{'name': 'viewport', 'content':'width=device_width'}]
)
app.title = 'Oil and Gas Wells'
server = app.server


# 加载数据集
path = os.getcwd()
df = pd.read_csv('C:/Users/pro/Desktop/dashboard_demo/my_demo/data/wellspublic.csv', low_memory=False)

# 预处理数据集
df["Date_Well_Completed"] = pd.to_datetime(df["Date_Well_Completed"])
df = df[df["Date_Well_Completed"] > dt.datetime(1960, 1, 1)]

trim = df[["API_WellNo", "Well_Type", "Well_Name"]]
trim.index = trim["API_WellNo"]
dataset = trim.to_dict(orient="index") # 会报错？


# 加载pickle文件
points = pickle.load('C:/Users/pro/Desktop/dashboard_demo/my_demo/data/points.pkl')


# 创建控制器
# 县的选项
county_options = [
    {'label': str(COUNTIES[county]), 'value': str(county)} for county in COUNTIES
]
# 油井状态的选项
well_status_options = [
    {'label': str(WELL_STATUSES[well_status]), 'value': str(well_status)}
    for well_status in WELL_STATUSES
]
# 油井类型的选择
well_type_options = [
    {'label': str(WELL_TYPES[well_type]), 'value': str(well_type)}
    for well_type in WELL_TYPES
]


# 创建全局图标模板
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

layout = dict(
    autosize = True,
    automargin = True,
    margin = dict(l=30, r=30, b=20, t=40),
    hovermode = 'closest',
    plot_bgcolor = '#F9F9F9',
    paper_bgcolor = '#F9F9F9',
    legend = dict(font=dict(size=10), orientation='h'),
    title = 'Satellite Overview',
    mapbox = dict(
        accesstoken=mapbox_access_token,
        style='light',
        center=dict(lon=-78.05, lat=42.54),
        zoom=7
    )
)


# 创建布局
app.layout = html.Div(
    [
        dcc.Store(id='aggregate_data'),
        # 清空Div以触发javascript文件以调整图形大小
        html.Div(id='output_clientside'),
        # 标题栏
        html.Div(
            [   
                # 左上角图标
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column"                    
                ),
                # 中间放总标题
                html.Div(
                    [
                        html.H3(
                            'New York Oil and Gas',
                            style={'margin-bottom': '0px'}
                        ),
                        html.H5(
                            'Production Overview', style={'margin-top': '0px'}
                        )
                    ],
                    className='one-half column',
                    id='title'
                ),
                # 右上角放链接按钮
                html.Div(
                    [
                        html.A(
                            html.Button('Learn More', id='learn-more-button'),
                            href='https://plot.ly/dash/pricing'
                        )
                    ],
                    className='one-third column',
                    id='button'
                )
            ],
            id='header',
            className='row flex-display',
            style={'margin-bottom': '25px'}
        ),
        # 总控制器栏+重点信息显示器+主图
        html.Div(
            [   
                # 总控制器栏
                html.Div(
                    [   
                        # 控制器的段落标签
                        html.P(
                            'Filter by construction date (or select range in histogram):',
                            className='control_label'
                        ),
                        # 范围滑动控制器：最小1960最大2017，初始1990~2010
                        dcc.RangeSlider(
                            id='year_slider',
                            min=1960,
                            max=2017,
                            value=[1990, 2010],
                            className='dcc_control'
                        ),
                        # 控制器的段落标签
                        html.P('Filter by well status:', className='control_label'),
                        # 圆点选项控制器：三个选项，初始为'active'
                        dcc.RadioItems(
                            id='well_status_selector',
                            options=[
                                {'label': 'All', 'value': 'all'},
                                {'label': 'Active only', 'value': 'active'},
                                {'label': 'Customize', 'value': 'custom'}
                            ],
                            value='active',
                            labelStyle={'display': 'inline-block'},
                            className='dcc_control'
                        ),
                        # 下拉选项控制器：选项为well_status的全部内容，初始全选
                        dcc.Dropdown(
                            id='well_statuses',
                            options=well_status_options,
                            multi=True,
                            value=list(WELL_STATUSES.keys()),
                            className='dcc_control'
                        ),
                        # 清单控制器(打勾二选一)：初始值为空，不打勾
                        dcc.Checklist(
                            id='lock_selector',
                            options=[{'label': 'Lock camera', 'value': 'locked'}],
                            className='dcc_control',
                            value=[]
                        ),
                        html.P('Filter by well type:', className='control_label'),
                        dcc.RadioItems(
                            id='well_type_selector',
                            options=[
                                {'label': 'All', 'value': 'all'},
                                {'label': 'Productive only', 'value': 'productive'},
                                {'label': 'Customize', 'value': 'custom'}
                            ],
                            value='productive',
                            labelStyle={'display': 'inline-block'},
                            className='dcc_control'
                        ),
                        # 下拉选项控制器：选项为well_status的全部内容，初始全选
                        dcc.Dropdown(
                            id='well_types',
                            options=well_type_options,
                            multi=True,
                            value=list(WELL_TYPES.keys()),
                            className='dcc_control'
                        )
                    ],
                    className='pretty_container four columns',
                    id='cross-filter-options'
                ),
                # 重点信息显示器
                html.Div(
                    [   
                        # 小型容器
                        html.Div(
                            [   
                                # html.H6只有对应id，先放置一个空的标题栏
                                html.Div(
                                    [html.H6(id='well_text'), html.P('No. of Wells')],
                                    id='wells',
                                    className='mini_container'
                                ),
                                html.Div(
                                    [html.H6(id='gasText'), html.P('Gas')],
                                    id='gas',
                                    className='mini_container'
                                ),
                                html.Div(
                                    [html.H6(id='oilText'), html.P('Oil')],
                                    id='oil',
                                    className='mini_container'
                                )
                            ],
                            id='info-container',
                            className='row container-display'
                        ),
                        # 主图容器
                        html.Div(
                            [dcc.Graph(id='count_graph')],
                            id='countGraphContainer',
                            className='pretty_container'
                        ),
                    ],
                    id='right-column',
                    className='eight columns'
                )
            ],
            className='row flex-display'
        ),
        # 第二行图部分
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id='main_graph')],
                    className='pretty_container seven columns'
                ),
                html.Div(
                    [dcc.Graph(id='individual_graph')],
                    className='pretty_container five columns'
                )
            ],
            className='row flex-display'
        ),
        # 第三行图部分
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id='pie_graph')],
                    className='pretty_container seven columns'
                ),
                html.Div(
                    [dcc.Graph(id='aggregate_graph')],
                    className='pretty_container five columns'
                )
            ],
            className='row flex-display'
        )
    ],
    id='mainContanier',
    style={'display': 'flex', 'flex-direction': 'column'}
)


# main
if __name__ == '__main__':
    app.run_server(debug=True)