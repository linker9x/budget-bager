from dash.dependencies import Input, Output
from layouts import home, page1, page2
from components.functions import update_datatable, update_period_df
from datetime import datetime
from datetime import date, timedelta
import plotly.graph_objs as go
import pandas as pd
import numpy as np

__fixed_cat = ['CAR', 'HEALTHCARE', 'FITNESS']
__var_cat = ['AMAZON', 'TRAVEL', 'PERSONAL', 'SHOPPING', 'ENTERTAINMENT', 'CATS',
             'GROCERIES', 'RESTAURANT', 'GAS']

def register_callbacks(app):

    #### callback to switch page content
    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/home/':
            return home
        elif pathname == '/page1/':
            return page1
        elif pathname == '/page2/':
            return page2
        else:
            return None


    #### P1 - Date Picker Callback
    @app.callback(Output('descrip-date', 'children'),
                  [Input('stat-date-picker', 'start_date'),
                   Input('stat-date-picker', 'end_date')])
    def update_output(start_date, end_date):
        if start_date is not None:
            start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
            start_date_string = start_date.strftime('%B %d, %Y')
            string_prefix = 'Start Date: ' + start_date_string + '| '
        if end_date is not None:
            end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')
            end_date_string = end_date.strftime('%B %d, %Y')
            days_selected = (end_date - start_date).days
            prior_start_date = start_date - timedelta(days_selected + 1)
            prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
            prior_end_date = end_date - timedelta(days_selected + 1)
            prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
            string_prefix = string_prefix + 'End Date: ' + end_date_string + '| Period Length: ' + str(
                days_selected + 1) + ' Days'
        if len(string_prefix) == len('You have selected: '):
            return 'Select a date to see it displayed here'
        else:
            return string_prefix

    #### P1 - Table Callback
    @app.callback(Output('stat-datatable', 'data'),
                  [Input('stat-date-picker', 'start_date'),
                   Input('stat-date-picker', 'end_date'),
                   Input('cat-dropdown', 'value'),
                   Input('acc-checklist', 'value')])
    def update_data_1(start_date, end_date, categories, accounts):
        data_1 = update_datatable(start_date, end_date, categories, accounts)
        return data_1

    #### P2 - Area Graph
    @app.callback(Output('in-out-area-graph', 'figure'),
                  [Input('p2-date-picker', 'start_date'),
                   Input('p2-date-picker', 'end_date')])
    def update_p2_area_graph(start_date, end_date):
        df = update_period_df(start_date, end_date)
        df_in = df[df['Amount'] >= 0].groupby(pd.Grouper(key='Date', freq='M')).sum()
        df_out = df[df['Amount'] < 0].groupby(pd.Grouper(key='Date', freq='M')).sum()

        data = [go.Scatter(x=[mon.strftime('%B') for mon in df_in.index],
                           y=df_in['Amount'],
                           name='INCOME',
                           fill='tonexty'),
                go.Scatter(x=[mon.strftime('%B') for mon in df_out.index],
                           y=df_out['Amount'].abs(),
                           name='EXPENSE',
                           fill='tonexty')]
        layout = go.Layout()
        return {'data': data, 'layout': None}

    #### P2 - Stacked Bar Graph
    @app.callback(Output('fixed-var-stacked', 'figure'),
                  [Input('p2-date-picker', 'start_date'),
                   Input('p2-date-picker', 'end_date')])
    def update_p2_stacked(start_date, end_date):
        df = update_period_df(start_date, end_date)
        df_months = pd.DatetimeIndex(df['Date']).to_period('M').unique()

        data = [go.Bar(x=df_months.month,
                       y=df[df['Category'] == cat].groupby(pd.Grouper(key='Date', freq='M'))['Amount'].sum().abs(),
                       name=cat)
                for cat in __fixed_cat + __var_cat]
        layout = go.Layout(barmode='stack')
        return {'data': data, 'layout': layout}

    #### P2 - Fixed Pie
    @app.callback(Output('fixed-pie', 'figure'),
                  [Input('p2-date-picker', 'start_date'),
                   Input('p2-date-picker', 'end_date')])
    def update_p2_fixed(start_date, end_date):
        df = update_period_df(start_date, end_date)
        df_cat = df.groupby('Category')['Amount'].agg(['sum'])
        df_fixed = df_cat[df_cat.index.isin(__fixed_cat)]

        data = [go.Pie(labels=df_fixed.index, values=df_fixed['sum'].abs())]
        layout = go.Layout()
        return {'data': data, 'layout': None}

    #### P2 - Var Pie
    @app.callback(Output('var-pie', 'figure'),
                  [Input('p2-date-picker', 'start_date'),
                   Input('p2-date-picker', 'end_date')])
    def update_p2_var(start_date, end_date):
        df = update_period_df(start_date, end_date)
        df_cat = df.groupby('Category')['Amount'].agg(['sum'])
        df_var = df_cat[df_cat.index.isin(__var_cat)]

        data = [go.Pie(labels=df_var.index, values=df_var['sum'].abs())]
        layout = go.Layout()
        return {'data': data, 'layout': None}