import numpy as np

import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

import dash_daq as daq

# from dash_daq_drivers import keithley_instruments

# Define the app
app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}]
)
server = app.server
app.config['suppress_callback_exceptions'] = False

#  font and background colors associated with each themes
bkg_color = {"dark": "#2a3f5f", "light": "#F3F6FA"}
grid_color = {"dark": "white", "light": "#C8D4E3"}
text_color = {"dark": "white", "light": "#506784"}


'''
test if a string can be a com of gpib port
def is_instrument_port(port_name)
'''


class UsefulVariables:
    '''Class to store information useful to callbacks'''

    def __init__(self) -> None:
        self.n_clicks = 0
        self.n_clicks_clear_graph = 0
        self.n_refresh = 0
        self.source = 'V'
        self.is_source_being_changed = False
        self.mode = 'single'
        self.sourced_values = []
        self.measured_values = []

    def change_n_clicks(self, nclicks):
        self.n_clicks = nclicks

    def change_n_clicks_clear_graph(self, nclicks):
        self.n_clicks_clear_graph = nclicks

    def reset_n_clicks(self):
        self.n_clicks = 0
        self.n_clicks_clear_graph = 0

    def change_n_refresh(self, nrefresh):
        self.n_refresh = nrefresh

    def reset_interval(self):
        self.n_refresh = 0

    def clear_graph(self):
        self.sourced_values = []
        self.measured_values = []

    def sorted_values(self):
        ''' Sort the data so they are ascending according to the source'''
        data_array = np.vstack([local_vars.sourced_values, local_vars.measured_values])
        # np.vstack: 将两个数组上下组合在一起
        data_array = data_array[:, data_array[0, :].argsort()]
        # data_array[0,:].argsort() 按第一行排序，并返回列名

        return data_array


local_vars = UsefulVariables()


def get_source_units(source='V'):
    '''units for source/measure elements'''
    if source == 'V':
        # source voltage(电压) and measure current(电流)
        source_unit = 'V'
        measure_unit = 'A'
    elif source == 'I':
        # source current and measure voltage
        source_unit = 'μA'
        measure_unit = 'V'

    return source_unit, measure_unit


def get_source_labels(source="V"):
    """labels for source/measure elements"""
    if source == "V":
        # we source voltage and measure current
        source_label = "Voltage"
        measure_label = "Current"
    elif source == "I":
        # we source current and measure voltage
        source_label = "Current"
        measure_label = "Voltage"

    return source_label, measure_label


def get_source_max(source='V'):
    '''units for source/measure elements'''
    if source == 'V':
        return 20
    elif source == 'I':
        return 100


h_style = {
    "display": "flex",
    "flex-direction": "row",
    "alignItems": "center",
    "justifyContent": "space-between",
    "margin": "5px",
}


# Create controls using a function
def generate_main_layout(
    theme='light', src_type='V', mode_val='single', fig=None
):
    '''generate the layout of the app'''

    source_label, measure_label = get_source_labels(src_type)
    source_unit, measure_unit = get_source_units(src_type)
    source_max = get_source_max(src_type)

    if mode_val == 'single':
        single_style = {
            "display": "flex",
            "flex-direction": "column",
            "alignItems": "center"
        }
        sweep_style = {'display': 'none'}
        label_btn = 'Single measure'
    else:
        single_style = {'display': 'none'}
        sweep_style = {
            "display": "flex",
            "flex-direction": "column",
            "alignItems": "center"
        }
        label_btn = 'Start sweep'
    
    # 由于触发器度量btn将通过重新加载布局来重置其n_clicks，因此我们也需要重置此度量
    local_vars.reset_n_clicks()

    # 不清除图片的数据
    if fig is None:
        data = []
    else:
        data = fig['data']

    html_layout = [
        html.Div(
            className='row',
            children=[
                # 追踪测量结果的图
                html.Div(
                    id='IV_graph_div',
                    className='eight columns',
                    style={'margin': '20px'},
                    children=[
                        dcc.Graph(
                            id='IV_graph',
                            figure={
                                'data': data,
                                'layout': dict(
                                    paper_bgcolor=bkg_color[theme],
                                    plot_bgcolor=bkg_color[theme],
                                    font=dict(color=text_color[theme], size=15),
                                    xaxis={
                                        'color': grid_color[theme],
                                        'gridcolor': grid_color[theme]
                                    },
                                    yaxis={
                                        'color': grid_color[theme],
                                        'gridcolor': grid_color[theme]
                                    }
                                )
                            }
                        )
                    ]
                ),
                # 与仪器连接的控件
                html.Div(
                    id='instr_controls',
                    className='two columns',
                    children=[
                        html.H4('wobudaoa'),
                        # 仪器开关按钮
                        html.Div(
                            children=[
                                html.Div(
                                    id='power_button_div',
                                    children=daq.PowerButton(
                                        id='Power_button', on='false'
                                    )
                                ),
                                html.Br(),
                                html.Div(
                                    children=daq.Indicator(
                                        id='mock_indicator',
                                        value=False, #
                                        label='is mock?'
                                    ),
                                    style={'margin': '20px'},
                                    title='If the indicator is on, it means the instrument is in mock mode'
                                )
                            ],
                            style=h_style
                        )
                    ]
                )
            ]
        )
    ] 