from typing import Tuple, List
from base64 import b64decode
import io
from dash import dash, dcc, html, dash_table, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_daq as daq


class LMT_Statistics:
    def __init__(self,
                 statistic_file: str = "history.csv",
                 font_size: int = 24,
                 font_family: str = "IBM Plex Sans",
                 ):
        """
            Web application for LMT statistics.
            Supports launching a default dash server via LMT_Statistics.run_server() method or returning a dash.html.Div object via LMT_Statistics.init() method.

            :param statistic_file: path to csv file
            :type statistic_file: str
            :param font_size: font size
            :type font_size: int
            :param font_family: font family
            :type font_family: str
            """
        self.web_layout = None
        self.statistic_file = statistic_file
        self.uploaded = False
        self.font_size = font_size
        self.font_family = font_family
        self.data = self.import_data()
        self.card_element = self.card()
        self.data_table_element = self.data_table()
        self.web_layout = None

    def import_data(self) -> pd.DataFrame:
        """
            Imports data from csv file. Converts timestamps.

            :return: DataFrame from csv file
            :rtype: pd.DataFrame
            """

        if not self.uploaded:
            data = pd.read_csv(self.statistic_file)
        else:
            data = self.data
        data['data_collection_time'] = pd.to_datetime(data['data_collection_time'])
        return data

    @staticmethod
    def tick_vals(min_value: float, max_value: float, is_percentage: bool = False) -> tuple[
        list[float], list[str]]:
        """
            Generates tick values and tick labels based on specified parameters for use with graphs

            :param min_value: minimum value
            :type min_value: float
            :param max_value: maximum value
            :type max_value: float
            :param is_percentage: if True, generates tick values and tick labels for percentage graphs
            :type is_percentage: bool
            :return: tick values and tick labels
            :rtype: list
            """
        if is_percentage:
            tick_values = [i / 10 for i in range(11)]
            tick_labels = [f"{i * 10}%" for i in range(11)]
        else:
            if min_value > max_value:
                min_value, max_value = max_value, min_value

            tick_values = [min_value, max_value]
            tick_labels = [f"{min_value:,}", f"{max_value:,}"]

        return tick_values, tick_labels

    def bar_chart(self, _df: pd.DataFrame, _title: str, logarithmic_y_axis: bool, _x: list, _y: list,
                  _labels: dict = {}, tick_values: list = [], tick_labels: list = [], traces: list = [],
                  layout_hovermode: str = "x", layout_hoverlabel: dict = {}, layout_legend: dict = {},
                  html_id: str = '', _text_auto=False) -> html.Div:
        """
            Generates a div with a bar chart based on specified parameters

            :param _df: DataFrame
            :type _df: pd.DataFrame
            :param _title: title of the chart
            :type _title: str
            :param logarithmic_y_axis: if True, y-axis is logarithmic
            :type logarithmic_y_axis: bool
            :param _x: list of x values to use
            :type _x: list
            :param _y: list of y values to use
            :type _y: list
            :param _labels: dictionary of labels to use
            :type _labels: dict
            :param tick_values: list of tick values (for making simpler y-axis divisions)
            :type tick_values: list
            :param tick_labels: list of tick labels
            :type tick_labels: list
            :param traces: list of traces to use in update_traces() for a graph
            :type traces: list
            :param layout_hovermode: hovermode for the graph (in update_layout())
            :type layout_hovermode: str
            :param layout_hoverlabel: hoverlabel for the graph (in update_layout())
            :type layout_hoverlabel: dict
            :param layout_legend: legend for the graph (in update_layout())
            :type layout_legend: dict
            :param html_id: id of the div containing the graph (if empty, no id is set)
            :type html_id: str
            :return: A Dash HTML div containing the bar chart
            :rtype: html.Div
            """
        graph = dcc.Graph(
            figure=(
                px.bar(_df, title=_title, x=_x, y=_y, log_y=logarithmic_y_axis, labels=_labels,
                       text_auto=_text_auto) if len(_x) > 0 and len(_y) > 0 else px.bar(_df, title=_title,
                                                                                        log_y=logarithmic_y_axis,
                                                                                        labels=_labels,
                                                                                        text_auto=_text_auto)
            )
            .update_yaxes(tickvals=tick_values, ticktext=tick_labels)
            .update_traces(traces)
            .update_layout(
                legend_title_text="",
                height=600,
                font=dict(family=self.font_family, size=self.font_size, color="black"),
                hovermode=layout_hovermode,
                hoverlabel=layout_hoverlabel,
                legend=layout_legend
            )
        )
        if html_id != '':
            graph.__setattr__("id", html_id)
        div = html.Div([
            graph,
        ])
        return div

    def data_table(self) -> html.Div:
        """
            Generates a div with a dataTable based on specified parameters

            :return: A Dash HTML div containing the dataTable
            :rtype: html.Div
            """
        div = html.Div([
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {"name": i, "id": i} for i in self.data.columns
                ],
                data=self.data.to_dict('records'),
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                page_current=0,
                page_size=10,
                style_table={'overflowX': 'scroll'},
            )])
        return div

    def bar_chart2(self, _df: pd.DataFrame, _title: str, logarithmic_y_axis: bool, _x: list, _y: list,
                   _labels: dict = {}, tick_values: list = [], tick_labels: list = [], traces: list = [],
                   layout_hovermode: str = "x", layout_hoverlabel: dict = {}, layout_legend: dict = {},
                   html_id: str = '', _text_auto=False):
        """
            Generates a div with a bar chart based on specified parameters

            :param _df: DataFrame
            :type _df: pd.DataFrame
            :param _title: title of the chart
            :type _title: str
            :param logarithmic_y_axis: if True, y-axis is logarithmic
            :type logarithmic_y_axis: bool
            :param _x: list of x values to use
            :type _x: list
            :param _y: list of y values to use
            :type _y: list
            :param _labels: dictionary of labels to use
            :type _labels: dict
            :param tick_values: list of tick values (for making simpler y-axis divisions)
            :type tick_values: list
            :param tick_labels: list of tick labels
            :type tick_labels: list
            :param traces: list of traces to use in update_traces() for a graph
            :type traces: list
            :param layout_hovermode: hovermode for the graph (in update_layout())
            :type layout_hovermode: str
            :param layout_hoverlabel: hoverlabel for the graph (in update_layout())
            :type layout_hoverlabel: dict
            :param layout_legend: legend for the graph (in update_layout())
            :type layout_legend: dict
            :param html_id: id of the div containing the graph (if empty, no id is set)
            :type html_id: str
            :return: A Dash HTML div containing the bar chart
            :rtype: html.Div
            """
        graph = dcc.Graph(
            figure=(
                px.bar(_df, title=_title, x=_x, y=_y, log_y=logarithmic_y_axis, labels=_labels,
                       text_auto=_text_auto) if len(_x) > 0 and len(_y) > 0 else px.bar(_df, title=_title,
                                                                                        log_y=logarithmic_y_axis,
                                                                                        labels=_labels,
                                                                                        text_auto=_text_auto)
            )
            .update_yaxes(tickvals=tick_values, ticktext=tick_labels)
            .update_traces(traces)
            .update_layout(
                legend_title_text="",
                height=600,
                font=dict(family=self.font_family, size=self.font_size, color="black"),
                hovermode=layout_hovermode,
                hoverlabel=layout_hoverlabel,
                legend=layout_legend
            )
        )
        if html_id != '':
            graph.__setattr__("id", html_id)
        return dcc.figure(
            px.bar(_df, title=_title, x=_x, y=_y, log_y=logarithmic_y_axis, labels=_labels,
                   text_auto=_text_auto) if len(_x) > 0 and len(_y) > 0 else px.bar(_df, title=_title,
                                                                                    log_y=logarithmic_y_axis,
                                                                                    labels=_labels,
                                                                                    text_auto=_text_auto)
        ).update_yaxes(tickvals=tick_values, ticktext=tick_labels).update_traces(traces).update_layout(
            legend_title_text="",
            height=600,
            font=dict(family=self.font_family, size=self.font_size, color="black"),
            hovermode=layout_hovermode,
            hoverlabel=layout_hoverlabel,
            legend=layout_legend
        )

    def card(self) -> html.Div:
        """
            Generates a div with a card based on specified parameters

            :return: div with a bar chart
            :rtype: html.Div
            """
        _data = self.calculate_card()
        _labels = ["Average number of software instances per endpoint", "Average number of endpoints per customer"]
        div = html.Div([
            html.Div([html.H3([l], className="card-title"), html.Span([f"{d:.3f}"], className="card-text")]
                     , className="card-body")
            for l, d in zip(_labels, _data)
        ], className="card-container")
        return div

    def calculate_card(self):
        """
            Calculates the average number of software instances per endpoint and the average number of endpoints per customer.
            :return: tuple of average number of software instances per endpoint and average number of endpoints per customer
            :rtype: tuple
        """
        # only to mitigate the bug with loading new data
        software_instances_avg_per_endpoint = self.get_avg_instance_per_endpoints()
        endpoints_per_customer = self.get_avg_endpoints_per_customer()
        return software_instances_avg_per_endpoint, endpoints_per_customer

    def change_cards(self):
        """
            Updates the card values.

            :return: None
        """
        values = self.calculate_card()
        self.card_element.children[0].children[1].children = f"{values[0]:.3f}"
        self.card_element.children[1].children[1].children = f"{values[1]:.3f}"

    def change_datatable(self) -> None:
        temp_element =  html.Div([
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {"name": i, "id": i} for i in self.data.columns
                ],
                data=self.data.to_dict('records'),
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                page_current=0,
                page_size=10,
                style_table={'overflowX': 'scroll'},
            )])
        self.data_table_element.children = temp_element.children

    @staticmethod
    def barchart_endpoints_percentage(_df, period_type):
        filtered = _df.copy(deep=True)
        # fixes bug with loading new data
        filtered['data_collection_time'] = pd.to_datetime(filtered['data_collection_time'])

        if period_type == "M":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("M")
        elif period_type == "Q":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("Q")

        grouped = filtered.groupby("year_month")[["endpoints_all", "endpoints_disconnected"]].sum().reset_index()
        grouped["year_month"] = grouped["year_month"].dt.to_timestamp()

        grouped["disconnected_percent"] = grouped["endpoints_disconnected"] / grouped["endpoints_all"]
        grouped["connected_percent"] = 1 - grouped["disconnected_percent"]

        # print(grouped.head())

        fig = px.bar(grouped, x='year_month', y=['connected_percent', 'disconnected_percent'],
                     labels={'year_month': 'Date', 'value': 'Endpoints percentage'})

        fig.update_yaxes(tickvals=[i / 10 for i in range(11)], ticktext=[f"{i * 10}%" for i in range(11)])

        fig.update_traces(
            hoverinfo='all',
            hovertemplate='<b>%{y:.2%}</b><extra></extra>')

        fig.update_layout(
            legend_title_text="",
            height=600,
            font=dict(
                family="IBM Plex Sans",
                size=24,
                color="black"
            ),
            hovermode="x",
            hoverlabel=dict(
                bgcolor="white",
                font_size=24,
                font_family="IBM Plex Sans",
                font_color="black",
                bordercolor="black",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        fig.update_xaxes(tickvals=grouped['year_month'], ticktext=format_xaxis(period_type, grouped['year_month']))

        div = html.Div([
            html.H2("Endpoints All", id='endpoints-chart-title'),
            dcc.Graph(
                id='graph-endpoints-over-time',
                figure=fig
            )
        ])

        return div

    @staticmethod
    def barchart_endpoints_value(_df, period_type):
        filtered = _df.copy(deep=True)
        # fixes bug with loading new data
        filtered['data_collection_time'] = pd.to_datetime(filtered['data_collection_time'])

        if period_type == "M":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("M")
        elif period_type == "Q":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("Q")

        grouped = filtered.groupby("year_month")[["endpoints_all", "endpoints_disconnected"]].sum().reset_index()
        grouped["year_month"] = grouped["year_month"].dt.to_timestamp()

        grouped["endpoints_connected"] = grouped["endpoints_all"] - grouped["endpoints_disconnected"]

        # print(grouped.head())

        fig = px.bar(grouped, x='year_month', y=['endpoints_connected', 'endpoints_disconnected'],
                     labels={'year_month': 'Date', 'value': 'Endpoints value'})  # , log_y=True)

        fig.update_traces(
            hoverinfo='all',
            hovertemplate='<b>%{y:}</b><extra></extra>')

        fig.update_layout(
            legend_title_text="",
            height=600,
            font=dict(
                family="IBM Plex Sans",
                size=24,
                color="black"
            ),
            hovermode="x",
            hoverlabel=dict(
                bgcolor="white",
                font_size=24,
                font_family="IBM Plex Sans",
                font_color="black",
                bordercolor="black",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        fig.update_xaxes(tickvals=grouped['year_month'], ticktext=format_xaxis(period_type, grouped['year_month']))

        div = html.Div([
            html.H2("Endpoints All", id='endpoints-chart-title'),
            dcc.Graph(
                id='graph-endpoints-over-time',
                figure=fig
            )
        ])

        return div

    @staticmethod
    def barchart_database_percentage(_df, period_type):
        filtered = _df.copy(deep=True)

        filtered['data_collection_time'] = pd.to_datetime(filtered['data_collection_time'])

        if period_type == "M":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("M")
        elif period_type == "Q":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("Q")

        filtered["year_month"] = filtered["year_month"].dt.to_timestamp()
        grouped = filtered.groupby(["year_month", "lmt_database_type"]).size().unstack(fill_value=0)

        grouped['total'] = grouped.sum(axis=1)
        grouped_percentage = grouped.div(grouped['total'], axis=0) * 1

        grouped_percentage.drop(columns=['total'], inplace=True)

        # print(grouped.head())

        fig = px.bar(grouped_percentage, labels={'year_month': 'Date', 'value': 'Types percentage'})

        fig.update_yaxes(tickvals=[i / 10 for i in range(11)], ticktext=[f"{i * 10}%" for i in range(11)])

        fig.update_traces(
            hoverinfo='all',
            hovertemplate='<b>%{y:.2%}</b><extra></extra>')

        fig.update_layout(
            legend_title_text="",
            height=600,
            font=dict(
                family="IBM Plex Sans",
                size=24,
                color="black"
            ),
            hovermode="x",
            hoverlabel=dict(
                bgcolor="white",
                font_size=24,
                font_family="Arial",
                font_color="black",
                bordercolor="black",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        fig.update_xaxes(tickvals=grouped.index, ticktext=format_xaxis(period_type, grouped.index))

        div = html.Div([
            html.H2("Database types", id='chart-title'),
            dcc.Graph(
                id='graph-database-type-over-time',
                figure=fig
            )
        ])

        return div

    @staticmethod
    def barchart_database_value(_df, period_type):
        filtered = _df.copy(deep=True)

        filtered['data_collection_time'] = pd.to_datetime(filtered['data_collection_time'])

        if period_type == "M":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("M")
        elif period_type == "Q":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("Q")

        filtered["year_month"] = filtered["year_month"].dt.to_timestamp()
        grouped = filtered.groupby(["year_month", "lmt_database_type"]).size().unstack(fill_value=0)

        # print(grouped.head())

        fig = px.bar(grouped, labels={'year_month': 'Date', 'value': 'Types value'})

        fig.update_traces(
            hoverinfo='all',
            hovertemplate='<b>%{y:}</b><extra></extra>')

        fig.update_layout(
            legend_title_text="",
            height=600,
            font=dict(
                family="IBM Plex Sans",
                size=24,
                color="black"
            ),
            hovermode="x",
            hoverlabel=dict(
                bgcolor="white",
                font_size=24,
                font_family="Arial",
                font_color="black",
                bordercolor="black",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        fig.update_xaxes(tickvals=grouped.index, ticktext=format_xaxis(period_type, grouped.index))

        div = html.Div([
            html.H2("Database types", id='chart-title'),
            dcc.Graph(
                id='graph-database-type-over-time',
                figure=fig
            )
        ])

        return div

    @staticmethod
    def get_os_breakdown(_df: pd.DataFrame) -> tuple:
        """
            Returns the total number of endpoints per os.

            :param _df: DataFrame containing the data
            :type _df: pd.DataFrame
            :return: columns of total number of endpoints per os and labels
            :rtype: tuple
            """
        os_columns = [col for col in _df.columns if col.startswith('endpoints_os_')]
        os_totals = _df[os_columns].sum(axis=0).sort_values(ascending=False)
        os_labels = [
            col.replace('endpoints_os_', '').replace('_', ' ').capitalize().replace('Ibm', 'IBM').replace('Hpux',
                                                                                                          'HP-UX').replace(
                'sparc', 'Sparc') for col in os_totals.axes[0]]
        return os_totals, os_labels

    @staticmethod
    def get_endpoints_per_os(_df: pd.DataFrame) -> tuple:
        """
            Returns the average number of endpoints per os.

            :param _df: DataFrame containing the data
            :type _df: pd.DataFrame
            :return: columns of average number of endpoints per os and labels
            :rtype: tuple
            """
        os_columns = [col for col in _df.columns if col.startswith('endpoints_os_')]
        os_avgs = _df[os_columns].mean(axis=0).round(3).sort_values(ascending=False)
        os_labels = [
            col.replace('endpoints_os_', '').replace('_', ' ').capitalize().replace('Ibm', 'IBM').replace('Hpux',
                                                                                                          'HP-UX').replace(
                'sparc', 'Sparc') for col in os_avgs.axes[0]]
        return os_avgs, os_labels

    def get_avg_instance_per_endpoints(self) -> float:
        """
            Returns average number of instances per endpoint.

            :param _df: DataFrame containing the data
            :type _df: pd.DataFrame
            :return: average number of instances per endpoint
            :rtype: float
            """
        endpoints_all = self.data['endpoints_all'].sum()
        instances_all = self.data['instances_all'].sum()
        avg = (instances_all / endpoints_all)
        return avg

    def get_avg_endpoints_per_customer(self) -> float:
        """
            Returns average number of endpoints per customer (or data length).

            :param _df: DataFrame containing the data
            :type _df: pd.DataFrame
            :return: average number of endpoints per customer
            :rtype: float
            """
        endpoints_all = self.data['endpoints_all'].sum()
        avg = (endpoints_all / len(self.data))
        return avg

    @staticmethod
    def create_upload() -> html.Div:
        """
            Creates a div with an upload component for csv files.

            :return: div with an upload component for csv files
            :rtype: html.Div
            """
        div = html.Div([
            dcc.Upload(
                id='upload_data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                multiple=False,
                style={
                    'width': '20%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px auto',
                }
            ),
            html.Div(id='output_data_upload')
        ], id="upload_div")
        return div

    def make_graphs(self, return_to_self: bool = False) -> html.Div:
        """
            Initializes and computes data based on specified csv file. Returns either a dash.html.Div layout or sets up layout for default web server (LMT.web_layout and LMT.run_server()).
            Call before LMT_Statistics.run_server() method.

            :param return_to_self: if True, returns an empty dash.html.Div and sets LMT_Statistics.web_layout
            :type return_to_self: bool
            :return: dash.html.Div web layout or empty dash.html.Div
            :rtype: dash.html.Div
            """

        data = self.import_data()

        # Disconnected endpoints over time disconnected_endpoints_over_time =
        # self.get_disconnected_endpoints_over_time(data) disconnected_endpoints_over_time_tick_vals,
        # disconnected_endpoints_over_time_tick_labels = self.tick_vals(0,100,is_percentage=True)

        # # Database types over time database_types_over_time = self.get_database_types_over_time(data)
        # database_types_over_time_tick_vals, database_types_over_time_tick_labels = self.tick_vals(0,100,
        # is_percentage=True)

        # Breakdown of OSes total
        os_breakdown, os_labels_breakdown = self.get_os_breakdown(data)
        os_endpoint_breakdown_tick_vals, os_endpoint_breakdown_tick_labels = self.tick_vals(
            min(os_breakdown[os_breakdown > 0]), max(os_breakdown))

        # Average number of endpoints for customer
        os_avgs, os_labels_avgs = self.get_endpoints_per_os(data)
        endpoint_avg_per_customer_tick_vals, endpoint_avg_per_customer_tick_labels = self.tick_vals(
            min(os_avgs[os_avgs > 0]), max(os_avgs))

        # Average number of software instances per endpoint
        # it doesn't change value as of now after update
        software_instances_avg_per_endpoint = self.get_avg_instance_per_endpoints()

        # Average number of endpoints per customer
        # it doesn't change value as of now after update
        endpoints_per_customer = self.get_avg_endpoints_per_customer()

        card = self.card()
        traces = dict(
            hoverinfo='all',
            hovertemplate='<b>%{y:.2%}</b><extra></extra>'
        )

        hoverlabel = dict(
            bgcolor="white",
            font_size=self.font_size,
            font_family=self.font_family,
            font_color="black",
            bordercolor="black",
        )

        legend = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        )

        # Make dictionary for both os breakdown and endpoints per os average
        checkbox_os_breakdown = dict(zip(os_labels_breakdown, os_breakdown.axes[0]))
        checkbox_os_avg = dict(zip(os_labels_avgs, os_avgs.axes[0]))

        # file uploader element
        file_uploader = self.create_upload()

        def generate_column_options(df):
            available_columns = [{'label': col, 'value': col} for col in df.columns if
                                 col != 'data_collection_time' and col != 'lmt_server_install_time' and col != 'lmt_scanner_version_oldest' and col != 'lmt_server_version' and col != 'lmt_database_version' and col != 'lmt_database_type' and col != 'last_import_status']
            return available_columns

        layout = html.Div([
            html.Div(
                className="full-screen",
                id="top",
                children=[
                    html.A(html.Button("More", className="btn"), href="#first")
                ]
            ),

            html.H1(id="first"),

            html.Nav(
                className="navbar",
                children=[
                    html.Div("LMT Statistics — Dashboard", className="logo", id="logo"),
                    html.Ul(
                        className="nav-links",
                        children=[
                            html.Li(html.A("Compare Charts", href="#compare-charts")),
                            html.Li(html.A("Endpoints / Databases", href="#endpoints-chart-title")),
                            html.Li(html.A("OS Charts", href="#graph-os-endpoint-breakdown-title")),
                            html.Li(html.A("Upload file", href="#refresh-div")),
                        ],
                    ),
                    html.Div(
                        className="burger",
                        children=[
                            html.Div(className="line1"),
                            html.Div(className="line2"),
                            html.Div(className="line3"),
                        ],
                    ),
                ],
            ),

            html.Div(id="main-content", children=[
                # html.Div(
                #     className="goto-top",
                #     children=[
                #         html.A("^", href="#first")
                #     ]
                # ),

                html.Div(id="compare-charts"),

                dcc.Dropdown(
                    id='period-selector',
                    options=[
                        {'label': 'Monthly', 'value': 'M'},
                        {'label': 'Quarterly', 'value': 'Q'}
                    ],
                    value='M'
                ),

                html.Div(className='two-columns', children=[
                    html.Div([
                        dcc.Dropdown(
                            id='column-dropdown-1',
                            options=generate_column_options(data),
                            value=generate_column_options(data)[0]['value'] if generate_column_options(data) else None
                        ),

                        dcc.Graph(id='graph-1'),
                    ]),

                    html.Div([
                        dcc.Dropdown(
                            id='column-dropdown-2',
                            options=generate_column_options(data),
                            value=generate_column_options(data)[0]['value'] if generate_column_options(data) else None
                        ),

                        dcc.Graph(id='graph-2')
                    ]),
                ]),

                html.Div([
                    html.Div(id='toggle-output', className='toggle-output'),

                    daq.ToggleSwitch(
                        id='toggle-switch',
                        value=True,
                        label=["VALUES", "PERCENTAGES"]
                    )
                ]),

                html.Div(className='two-columns', children=[
                    html.Div([
                        html.H2("Breakdown of OS Endpoints", id='graph-os-endpoint-breakdown-title'),

                        dcc.Checklist(
                            id="breakdown-checklist",
                            options=[{'label': key, 'value': value} for key, value in checkbox_os_breakdown.items()],
                            value=os_breakdown.axes[0],
                            inline=True,
                            labelStyle={'font-size': self.font_size, 'font-family': self.font_family, 'margin': '10px'}
                        ),

                        self.bar_chart(
                            pd.DataFrame({
                                'OS': os_labels_breakdown, 'Endpoints': os_breakdown
                            }),
                            "", True, 'OS', 'Endpoints',
                            {'index': 'OS', 'y': 'Endpoints'},
                            os_endpoint_breakdown_tick_vals, os_endpoint_breakdown_tick_labels,
                            layout_hoverlabel=dict(
                                bgcolor="white",
                                font_size=self.font_size,
                                font_family=self.font_family,
                                font_color="black",
                                bordercolor="black",
                            ),
                            layout_legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1,
                            ),
                            _text_auto=False,
                            html_id='graph-os-endpoint-breakdown'
                        ),
                    ]),

                    html.Div([
                        html.H2("Average number of endpoints per OS", id='graph-endpoints-per-os-avg-title'),

                        dcc.Checklist(
                            id="average-checklist",
                            options=[{'label': key, 'value': value} for key, value in checkbox_os_avg.items()],
                            value=os_avgs.axes[0],
                            inline=True,
                            labelStyle={'font-size': self.font_size, 'font-family': self.font_family, 'margin': '10px'}
                        ),

                        self.bar_chart(
                            pd.DataFrame({
                                'OS': os_labels_avgs, 'Endpoints': os_avgs
                            }),
                            "", True, 'OS', 'Endpoints',
                            {'index': 'OS', 'y': 'Endpoints'},
                            endpoint_avg_per_customer_tick_vals, endpoint_avg_per_customer_tick_labels,
                            layout_hoverlabel=hoverlabel, layout_legend=legend, _text_auto='.3f',
                            html_id='graph-endpoints-per-os-avg'
                        ),
                    ]),
                ]),

                self.card_element,

                self.data_table_element,

                # html.Div(className='all-charts', children=[ html.Div([dcc.Graph(id=f'graph-{i}',
                # figure=self.create_all_charts(data, column)) for i, column in enumerate(data.columns) if column !=
                # 'data_collection_time']) ])

                html.Br(),

                html.Div(className='file-uploader', children=[
                    file_uploader,
                    html.Button('Load file', id='refresh-button', n_clicks=0,
                                style={
                                    'width': '20%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px auto',
                                }),

                    html.Div(id='refresh-div')
                ])

            ])

        ], className="dashboard"
        )
        self.callbacks()
        if return_to_self:
            self.web_layout = layout
            return html.Div()
        return layout

    def update_graph(self, selected_columns, graph_type: int = 0):
        data = self.import_data()
        if graph_type == 0:
            os_breakdown, _ = self.get_os_breakdown(data)
            filtered_data = os_breakdown[selected_columns]
            filtered_data_labels = [
                col.replace('endpoints_os_', '').replace('_', ' ').capitalize().replace('Ibm', 'IBM').replace('Hpux',
                                                                                                              'HP-UX').replace(
                    'sparc', 'Sparc') for col in filtered_data.axes[0]]
            dt = pd.DataFrame({
                'OS': filtered_data_labels,
                'Endpoints': filtered_data})
            tick_values, tick_labels = self.tick_vals(min(os_breakdown[os_breakdown > 0]), max(os_breakdown))
        else:
            os_breakdown, _ = self.get_endpoints_per_os(data)
            filtered_data = os_breakdown[selected_columns]
            filtered_data_labels = [
                col.replace('endpoints_os_', '').replace('_', ' ').capitalize().replace('Ibm', 'IBM').replace('Hpux',
                                                                                                              'HP-UX').replace(
                    'sparc', 'Sparc') for col in filtered_data.axes[0]]
            dt = pd.DataFrame({
                'OS': filtered_data_labels,
                'Endpoints': filtered_data})
            tick_values, tick_labels = self.tick_vals(min(os_breakdown[os_breakdown > 0]), max(os_breakdown))

        fig = px.bar(dt, x='OS', y='Endpoints')

        fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=self.font_size,
                font_family=self.font_family,
                font_color="black",
                bordercolor="black",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            font=dict(
                family="IBM Plex Sans",
                size=24,
                color="black"
            ),
            hovermode='x',
            yaxis_type='log',
            height=600,
        )
        fig.update_traces(hoverinfo='y', hovertemplate='<b>%{y:}</b><extra></extra>')
        fig.update_yaxes(tickvals=tick_values, ticktext=tick_labels)
        return fig

    def update_title(self, hdata):
        data = self.import_data()
        os_breakdown, _ = self.get_os_breakdown(data)
        # print(os_breakdown.index)
        os_breakdown.index = os_breakdown.index.str.replace('endpoints_os_', '').str.replace('_',
                                                                                             ' ').str.capitalize().str.replace(
            'Ibm', 'IBM').str.replace('Hpux', 'HP-UX').str.replace('sparc', 'Sparc')
        if hdata is not None:
            # print(hdata)
            percentage = str(round(100 * os_breakdown[hdata['points'][0]['x']] / os_breakdown.sum(), 2)) + '%'
            return 'Breakdown of OS Endpoints - ' + hdata['points'][0]['x'].replace('endpoints_os_', '').replace('_',
                                                                                                                 ' ').capitalize().replace(
                'Ibm', 'IBM').replace('Hp-ux', 'HP-UX').replace('sparc', 'Sparc') + ": " + percentage
        else:
            return 'Breakdown of OS Endpoints'

    def create_line_chart(self, df, selected_column, period_type):
        filtered = df.copy(deep=True)
        # fixes bug with loading new data
        filtered['data_collection_time'] = pd.to_datetime(filtered['data_collection_time'])

        if period_type == "M":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("M")
        elif period_type == "Q":
            filtered["year_month"] = filtered["data_collection_time"].dt.to_period("Q")

        grouped = filtered.groupby("year_month")[selected_column].sum().reset_index()
        grouped["year_month"] = grouped["year_month"].dt.to_timestamp()

        fig = go.Figure(data=[go.Scatter(x=grouped['year_month'], y=grouped[selected_column])])

        fig.update_traces(
            hoverinfo='all',
            hovertemplate='<b>%{y:}</b><extra></extra>')

        fig.update_layout(
            title="Chart - " + selected_column,
            xaxis_title="Date",
            yaxis_title=selected_column,
            legend_title_text="",
            height=600,
            font=dict(
                family="IBM Plex Sans",
                size=18,
                color="black"
            ),
            hovermode="x",
            hoverlabel=dict(
                bgcolor="white",
                font_size=18,
                font_family="IBM Plex Sans",
                font_color="black",
                bordercolor="black",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        fig.update_xaxes(tickvals=grouped['year_month'], ticktext=format_xaxis(period_type, grouped['year_month']))

        return fig

    def callbacks(self):
        @callback(
            Output('refresh-div', 'children'),
            [Input('refresh-button', 'n_clicks')]
        )
        def refresh_page(n_clicks):
            if n_clicks:
                return dcc.Location(href='/', id='id')

        @callback(
            Output('graph-1', 'figure'),
            [Input('column-dropdown-1', 'value'),
             Input('period-selector', 'value')]
        )
        def update_graph_1(selected_col, period_type):
            return self.create_line_chart(self.data, selected_col, period_type)

        # Callback dla drugiego wykresu
        @callback(
            Output('graph-2', 'figure'),
            [Input('column-dropdown-2', 'value'),
             Input('period-selector', 'value')]
        )
        def update_graph_2(selected_column, period_type):
            return self.create_line_chart(self.data, selected_column, period_type)

        @callback(
            Output('graph-os-endpoint-breakdown', 'figure'),
            Input('breakdown-checklist', 'value')
        )
        def update_graph(selected_columns, graph_type=0):
            return self.update_graph(selected_columns, graph_type)

        @callback(
            Output('graph-endpoints-per-os-avg', 'figure'),
            Input('average-checklist', 'value')
        )
        def update_graph(selected_columns, graph_type=1):
            return self.update_graph(selected_columns, graph_type)

        @callback(
            Output('graph-os-endpoint-breakdown-title', 'children'),
            Input('graph-os-endpoint-breakdown', 'hoverData')
        )
        def update_title(hoverData):
            return self.update_title(hoverData)

        @callback(
            Output('toggle-output', 'children'),
            [Input('toggle-switch', 'value'),
             Input('period-selector', 'value')]
        )
        def update_output(value, period_type):
            if value:
                return self.barchart_endpoints_percentage(self.data, period_type), self.barchart_database_percentage(
                    self.data, period_type)
            else:
                return self.barchart_endpoints_value(self.data, period_type), self.barchart_database_value(self.data,
                                                                                                           period_type)

        @callback(
            Output("output_data_upload", "children"),
            [Input("upload_data", "contents"),
             Input("upload_data", "filename")]
        )
        def update_output(contents, filename):
            # filename is not used at the moment hence the underline
            if contents is not None:
                # checking if file is csv
                content_type, content_string = contents.split(',')
                decoded = b64decode(content_string)
                if filename.endswith("csv"):
                    save_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                    if 'data_collection_time' not in save_data.columns and len(save_data.columns) != 46:
                        return
                    # save_data.to_csv(self.statistic_file, index=False)
                    self.data = save_data
                    self.change_cards()
                    self.change_datatable()
                    self.web_layout = self.make_graphs(return_to_self=False)
                    # a bit of brute force to update the layout
                    # necessary evil for now :)
                    self.uploaded = True

    def server_handle(self, _name: str = __name__, _debug: bool = False, assets_folder: str = "assets"):
        """
            Runs a default dash server. Call after LMT_Statistics.init() method or set LMT_Statistics.web_layout
            to either LMT_Statistics.init() output or custom html layout.

            :param _name: name of the app
            :type _name: str
            :param _debug: debug mode for dash app
            :type _debug: bool
            :param assets_folder: path to assets folder
            :type assets_folder: str
            """
        if self.web_layout is not None:
            app = dash.Dash(name=_name, title="LMT Statistics", assets_folder=assets_folder)
            app.layout = self.web_layout
            return app.server
        else:
            raise RuntimeError(
                "LMT_Statistics.init() must be called or LMT_Statistics.web_layout must be set before "
                "LMT_Statistics.run_server()")

    def overwrite_file(self):
        self.data.to_csv(self.statistic_file, index=False)


def format_xaxis(period_type, dates):
    if period_type == "M":
        return [date.strftime("%b %Y") for date in dates]
    elif period_type == "Q":
        return [f"{date.year} Q{date.quarter}" for date in dates]


if __name__ == '__main__':
    lmt = LMT_Statistics("history.csv")
    lmt.make_graphs(return_to_self=True)
    lmt.server_handle(_debug=False).run(port=8050, debug=True)
    lmt.overwrite_file()
