from dash import dash, dcc, html
import pandas as pd
import plotly.express as px

class LMT_Statistics:
    def __init__(self,
                 statistic_file: str,
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
        self.statistic_file = statistic_file
        self.font_size = font_size
        self.font_family = font_family

    def import_data(self)->pd.DataFrame:
        """
        Imports data from csv file. Converts timestamps.

        :return: DataFrame from csv file
        :rtype: pd.DataFrame
        """

        data = pd.read_csv(self.statistic_file)
        data['data_collection_time'] = pd.to_datetime(data['data_collection_time'])
        return data


    def tick_vals(self, min_value:float, max_value:float,is_percentage:bool=False)->list:
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

    def bar_chart(self,_df:pd.DataFrame, _title:str,logarithmic_y_axis:bool, _x:list, _y:list,_labels:dict={}, tick_values:list=[], tick_labels:list=[], traces:list=[], layout_hovermode:str="x", layout_hoverlabel:dict={},layout_legend:dict={},html_id:str='')->html.Div:
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
                px.bar(_df, title=_title, x=_x, y=_y, log_y=logarithmic_y_axis, labels=_labels) if len(_x) > 0 and len(_y) > 0 else px.bar(_df, title=_title, log_y=logarithmic_y_axis, labels=_labels)
            )
            .update_yaxes(tickvals=tick_values, ticktext=tick_labels)
            .update_traces(traces)
            .update_layout(
                legend_title_text="",
                height=600,
                font=dict(family=self.font_family, size=self.font_size, color="black"),
                hovermode=layout_hovermode,
                hoverlabel=layout_hoverlabel,
                legend=layout_legend,
            )
        ) 
        if html_id != '':
            graph.__setattr__("id",html_id)
        div = html.Div([
            graph,
        ])
        return div

    def card(self,_data:list,_labels:list)->html.Div:
        """
        Generates a div with a card based on specified parameters

        :param _data: list of values
        :type _data: list
        :param _labels: list of labels
        :type _labels: list
        :return: div with a bar chart
        :rtype: html.Div
        """
        div = html.Div([
            html.Div([html.H3([l], className="card-title"), html.Pre([str(d)], className="card-text")]
                    ,className="card-body")
                    for l, d in zip(_labels, _data)
            ], className="card-container")
        return div


    def get_disconnected_endpoints_over_time(self,_df:pd.DataFrame):
        """
        Generates a bar chart showing the percentage of disconnected endpoints over time.

        :param _df: DataFrame containing the data
        :return: A Dash HTML div containing the bar chart
        """
        # Copy the DataFrame to avoid modifying the original data
        filtered = _df.copy(deep=True)

        # Group the data by year and month
        filtered["year_month"] = filtered["data_collection_time"].dt.to_period("M")
        grouped = filtered.groupby("year_month")[["endpoints_all", "endpoints_disconnected"]].sum().reset_index()
        grouped["year_month"] = grouped["year_month"].dt.to_timestamp()

        # Calculate the percentage of disconnected endpoints
        grouped["disconnected_percent"] = grouped["endpoints_disconnected"] / grouped["endpoints_all"]
        grouped["connected_percent"] = 1 - grouped["disconnected_percent"]

        return grouped
    
    def get_database_types_over_time(self,_df:pd.DataFrame):
        """
        Generates a bar chart showing the percentage of different database types over time.

        :param _df: DataFrame containing the data
        :return: A Dash HTML div containing the bar chart
        """
        # Copy the DataFrame to avoid modifying the original data
        filtered = _df.copy(deep=True)

        # Group the data by year and month and database type
        filtered["year_month"] = filtered["data_collection_time"].dt.to_period("M")
        filtered["year_month"] = filtered["year_month"].dt.to_timestamp()
        grouped = filtered.groupby(["year_month", "lmt_database_type"]).size().unstack(fill_value=0)

        # Calculate the percentage of each database type
        grouped['total'] = grouped.sum(axis=1)
        grouped_percentage = grouped.div(grouped['total'], axis=0) * 1
        grouped_percentage.drop(columns=['total'], inplace=True)

        return grouped_percentage

    def get_os_breakdown(self,_df:pd.DataFrame)->tuple:
        """
        Returns the total number of endpoints per os.

        :param _df: DataFrame containing the data
        :type _df: pd.DataFrame
        :return: columns of total number of endpoints per os and labels
        :rtype: tuple
        """
        os_columns = [col for col in _df.columns if col.startswith('endpoints_os_')]
        os_totals = _df[os_columns].sum(axis=0).sort_values(ascending=False)
        os_labels = [col.replace('endpoints_os_', '').replace('_',' ').capitalize() for col in os_columns]
        return os_totals, os_labels

    def get_endpoints_per_os(self,_df:pd.DataFrame)->tuple:
        """
        Returns the average number of endpoints per os.

        :param _df: DataFrame containing the data
        :type _df: pd.DataFrame
        :return: columns of average number of endpoints per os and labels
        :rtype: tuple
        """
        os_columns = [col for col in _df.columns if col.startswith('endpoints_os_')]
        os_avgs = _df[os_columns].mean(axis=0).round(2).sort_values(ascending=False)
        os_labels = [col.replace('endpoints_os_', '').replace('_',' ').capitalize() for col in os_columns]
        return os_avgs, os_labels

    def get_avg_instance_per_endpoints(self,_df:pd.DataFrame)->float:
        """
        Returns average number of instances per endpoint.

        :param _df: DataFrame containing the data
        :type _df: pd.DataFrame
        :return: average number of instances per endpoint
        :rtype: float
        """
        endpoints_all = _df['endpoints_all'].sum()
        instances_all = _df['instances_all'].sum()
        avg = (instances_all/endpoints_all) 
        return avg

    def get_avg_endpoints_per_customer(self,_df:pd.DataFrame)->float:
        """
        Returns average number of endpoints per customer (or data length).
        
        :param _df: DataFrame containing the data
        :type _df: pd.DataFrame
        :return: average number of endpoints per customer
        :rtype: float
        """
        endpoints_all = _df['endpoints_all'].sum()
        avg = (endpoints_all/len(_df))
        return avg


    def init(self,return_to_self:bool=False)->html.Div:
        """
        Initializes and computes data based on specified csv file. Returns either a dash.html.Div layout or sets up layout for default web server (LMT.web_layout and LMT.run_server()).
        Call before LMT_Statistics.run_server() method.

        :param return_to_self: if True, returns an empty dash.html.Div and sets LMT_Statistics.web_layout
        :type return_to_self: bool
        :return: dash.html.Div web layout or empty dash.html.Div
        :rtype: dash.html.Div
        """

        data = self.import_data()

        # Disconnected endpoints over time
        disconnected_endpoints_over_time = self.get_disconnected_endpoints_over_time(data)
        disconnected_endpoints_over_time_tick_vals, disconnected_endpoints_over_time_tick_labels = self.tick_vals(0,100,is_percentage=True)

        # Database types over time
        database_types_over_time = self.get_database_types_over_time(data)
        database_types_over_time_tick_vals, database_types_over_time_tick_labels = self.tick_vals(0,100,is_percentage=True)

        # Breakdown of OSes total
        os_breakdown, os_labels_breakdown = self.get_os_breakdown(data)
        os_endpoint_breakdown_tick_vals, os_endpoint_breakdown_tick_labels = self.tick_vals(min(os_breakdown[os_breakdown > 0]),max(os_breakdown))

        # Average number of endpoints for customer
        os_avgs, os_labels_avgs = self.get_endpoints_per_os(data)
        endpoint_avg_per_customer_tick_vals, endpoint_avg_per_customer_tick_labels = self.tick_vals(min(os_avgs[os_avgs > 0]),max(os_avgs))

        # Average number of software instances per endpoint
        software_instances_avg_per_endpoint = self.get_avg_instance_per_endpoints(data)

        # Average number of endpoints per customer
        endpoints_per_customer = self.get_avg_endpoints_per_customer(data)

        traces = dict(
            hoverinfo='all',
            hovertemplate='<b>%{y:.2%}</b><extra></extra>'
        )

        hoverlabel=dict(
            bgcolor="white",
            font_size=self.font_size,
            font_family=self.font_family,
            font_color="black",
            bordercolor="black",
        )

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        )

        layout = html.Div([
            
            html.H1(["LMT Statistics"," — ","Dashboard"],style={"textAlign": "center"}),

            html.H2("Disconnected Endpoints Over Time"),
            self.bar_chart(
                disconnected_endpoints_over_time,
                "Endpoints All", False,
                'year_month', ['connected_percent', 'disconnected_percent'],
                _labels={'year_month': 'Date', 'value': 'Endpoints percentage'},
                tick_values=disconnected_endpoints_over_time_tick_vals, tick_labels=disconnected_endpoints_over_time_tick_labels,
                traces=traces,layout_hoverlabel=hoverlabel,layout_legend=legend,html_id='graph-endpoints-over-time'
            ),

            html.H2("Database Types Over Time"),
            self.bar_chart(
                database_types_over_time,
                "Database types", False, '', '',
                _labels={'year_month': 'Date', 'value': 'Types percentage'},
                tick_values=database_types_over_time_tick_vals, tick_labels=database_types_over_time_tick_labels,
                traces=traces,layout_hoverlabel=hoverlabel,layout_legend=legend,html_id='graph-database-type-over-time'
            ),

            html.H2("Breakdown of OS Endpoints"),
            self.bar_chart(
                pd.DataFrame({
                    'OS': os_labels_breakdown, 'Endpoints': os_breakdown
                }),
                "", True, 'OS', 'Endpoints',
                {'index': 'OS', 'y': 'Endpoints'},
                os_endpoint_breakdown_tick_vals, os_endpoint_breakdown_tick_labels,
                layout_hoverlabel=hoverlabel,layout_legend=legend
            ),
            
            html.H2("Average number of endpoints per OS"),
            self.bar_chart(
                pd.DataFrame({
                    'OS': os_labels_avgs, 'Endpoints': os_avgs
                }),
                "", True, 'OS', 'Endpoints',
                {'index': 'OS', 'y': 'Endpoints'},
                endpoint_avg_per_customer_tick_vals, endpoint_avg_per_customer_tick_labels,
                layout_hoverlabel=hoverlabel,layout_legend=legend
            ),

            self.card([
                f"{software_instances_avg_per_endpoint:.3f}",
                f"{endpoints_per_customer:.3f}"],
                ["Average number of software instances per endpoint",
                "Average number of endpoints per customer"]
            ),   
        ], className="dashboard"
        )

        if(return_to_self):
            self.web_layout = layout
            return html.Div()
        else:
            return layout


    def run_server(self, _name:str=__name__, _debug:bool=False, assets_folder:str="assets"):
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
        if hasattr(self, 'web_layout'):
            app = dash.Dash(name=_name, title="LMT Statistics", assets_folder=assets_folder)
            app.layout = self.web_layout
            app.run_server(debug=_debug)
        else:
            raise Exception("LMT_Statistics.init() must be called or LMT_Statistics.web_layout must be set before LMT_Statistics.run_server()")


if __name__ == '__main__':
    lmt = LMT_Statistics("example.csv")
    lmt.init(return_to_self=True)
    lmt.run_server(_debug=True)