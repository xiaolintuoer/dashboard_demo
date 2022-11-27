import os
import pandas as pd
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import dcc, html


# multi-dropdown 选项
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS


# 加载数据集
path = os.getcwd()
df = pd.read_csv(os.path.join(path, os.path.join('data', 'wellspublic.csv')))
# 预处理数据集



# external_stylesheets = ['/assets/spc-custom-styles.css']
app = dash.Dash(
    __name__,
    # external_stylesheets=external_stylesheets,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}],
)
app.title = 'Oil & Gas Wells'
server = app.server


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


app.layout = html.Div(
    [
        dcc.Store(id='aggregate_data'),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id='output_clientside'),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url('dash-logo.png'), #
                            id='plotly-image',
                            style={
                                'height': '60px',
                                'width': 'auto',
                                'margin-bottom': '25px'
                            }
                        )
                    ],
                    className='one-third column'
                ),
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
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            'Filter by construction date (or select range in histogram):',
                            className='control_label'
                        ),
                        dcc.RangeSlider(
                            id='year_slider',
                            min=1960,
                            max=2017,
                            value=[1990, 2010],
                            className='dcc_control'
                        ),
                        html.P('Filter by well status:', className='control_label'),
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
                        dcc.Dropdown(
                            id='well_statuses',
                            options=well_status_options,
                            multi=True,
                            value=list(WELL_STATUSES.keys()),
                            className='dcc_control'
                        ),
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
                html.Div(
                    [
                        html.Div(
                            [
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
        )
    ],
    id='mainContanier',
    style={'display': 'flex', 'flex-direction': 'column'}
)


# Helper functions
def human_format(num):
    if num == 0:
        return '0'

    magnitude = int(math.log(num, 1000))
    mantissa = str(int(num / (1000 * magnitude)))
    return mantissa + ['', 'K', 'M', 'G', 'T', 'P'][magnitude]


def filter_dataframe(df, well_statuses, well_types, year_slider):
    dff = df[
        df['Well_Status'].isin(well_statuses) &
        df['Well_Type'].isin(well_types) &
        (df['Date_Well_Completed'] > dt.datetime(year_slider[0], 1, 1)) &
        (df['Date_Well_Completed'] < dt.datetime(year_slider[1], 1, 1))
    ]
    return dff


def produce_individual(api_well_num):
    try:
        points[api_well_num]
    except:
        return None, None, None, None

    index = list(range(min(points[api_well_num].keys()), max(points[api_well_num].keys()) + 1))
    gas = []
    oil = []
    water = []

    for year in index:
        try:
            gas.append(points[api_well_num][year]['Gas Produced, MCF'])
        except:
            gas.append(0)
        try:
            oil.append(points[api_well_num][year]['Oil Produced, bbl'])
        except:
            oil.append(0)
        try:
            water.append(points[api_well_num][year]['Water Produced, bbl'])
        except:
            water.append(0)

    return index, gas, oil, water


def produce_aggregate(selected, year_slider):
    index = list(range(max(year_slider[0], 1985), 2016))
    gas = []
    oil = []
    water = []

    for year in index:
        count_gas = 0
        count_oil = 0
        count_water = 0
        for api_well_num in selected:
            try:
                count_gas += points[api_well_num][year]['Gas Produced, MCF']
            except:
                pass
            try:
                count_oil += points[api_well_num][year]['Oil Produced, bbl']
            except:
                pass
            try:
                count_water += points[api_well_num][year]['Water Produced, bbl']
            except:
                pass
        gas.append(count_gas)
        oil.append(count_oil)
        water.append(count_water)

    return index, gas, oil, water


# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='resize'),
    Output('output-clientside', 'children'),
    [Input('count_graph', 'figure')]
)


@app.callback(
    Output('aggregate_data', 'data')
    [
        Input('well_statuses', 'value'),
        Input('well_types', 'value'),
        Input('year_slider', 'value')
    ]
)
def update_production_text(well_statuses, well_types, year_slider):
    dff = filter_dataframe(df, well_statuses, well_types, year_slider)
    selected = dff['API_WellNo'].values
    index, gas, oil, water = produce_aggregate(selected, year_slider)
    
    return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]


# Radio -> multi
@app.callback(
    Output('well_statuses', 'value'),
    [Input('well_status_selector', 'value')]
)
def display_status(selector):
    if selector == 'all':
        return list(WELL_STATUSES.keys())
    elif selector == 'active':
        return ['AC']
    return []


# Radio -> multi
@app.callback(
    Output('well_types', 'value'),
    [Input('well_type_selector', 'value')]
)
def display_type(selector):
    if selector == 'all':
        return list(WELL_TYPES.keys())
    elif selector == 'productive':
        return ['GD', 'GE', 'GW', 'IG', 'IW', 'OD', 'OE', 'OW']
    return []


# Slider -> count graph
@app.callback(
    Output('year_slider', 'value'),
    [Input('count_graph', 'selectData')]
)
def update_year_slider(count_graph_selected):
    if count_graph_selected is None:
        return [1990, 2010]

    nums = [int(point['pointNumber']) for point in count_graph_selected['points']]
    return [min(nums) + 1960, max(nums) + 1961]


# Selectors -> well text
@app.callback(
    Output('well_text', 'children')
    [
        Input('well_statuses', 'value'),
        Input('well_type', 'value'),
        Input('year_slider', 'value')
    ]
)
def update_well_text(well_statuses, well_types, year_slider):
    dff = filter_dataframe(df, well_statuses, well_types, year_slider)
    return dff.shape[0]


@app.callback(
    [
        Output('gasText', 'children')
        Output('oilText', 'children')
        Output('waterText', 'children')
    ],
    [Input('aggregate_data', 'data')]
)


# main
if __name__ == '__main__':
    app.run_server(debug=True)