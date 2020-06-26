import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
from models.forecast import Forecast
from layouts import home, page1, page2, page3, page4
from components.functions import *
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import *
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import copy
import calendar


def register_callbacks(app, av, fc):
    global acc_view 
    global frcst
    acc_view = av
    frcst = fc

    #######################
    #
    # HEADER
    #
    #######################

    # callback to switch page content
    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/home/':
            return home
        elif pathname == '/page1/':
            return page1
        elif pathname == '/page2/':
            return page2
        elif pathname == '/page3/':
            return page3
        elif pathname == '/page4/':
            return page4
        else:
            return None

    @app.callback(Output('per-picker-dd2', 'options'),
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd1', 'options')])
    def update_var_summary(val, options):
        start = datetime.strptime(val, '%Y-%m-%d').date()
        start_dates = [op['label'] for op in options]
        start_dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in start_dates]
        end_dates = [date + relativedelta(months=+1, day=1) - timedelta(days=1) for date in start_dates]
        end_dates = [date for date in end_dates if date > start]
        end_dates.sort(reverse=True)
        return [{'label': '{}'.format(date), 'value': date} for date in end_dates]

    #######################
    #
    # HOME
    #
    #######################

    # HOME - TABLES
    @app.callback(Output('var-summary-table', 'data'),
                  [Input('home-var-dropdown', 'value')])
    def update_var_summary(val):
        acc_view.df_exp_month_cat.to_csv('hi.csv')
        return update_summary_table(acc_view, frcst, 'VAR')

    @app.callback(Output('fix-summary-table', 'data'),
                  [Input('home-var-dropdown', 'value')])
    def update_var_summary(val):
        return update_summary_table(acc_view, frcst, 'FIX')

    # HOME - GAUGES
    @app.callback(Output('home-gauge', 'figure'),
                  [Input('home-var-dropdown', 'value')])
    def update_gauge(cat):
        var_act_exp, var_prev_act_exp, var_mon_bdgt_exp = calc_gauge_vals(acc_view, frcst, 'VAR')
        fix_act_exp, fix_prev_act_exp, fix_mon_bdgt_exp = calc_gauge_vals(acc_view, frcst, 'FIX')

        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "indicator"}, {"type": "indicator"}]]
        )

        # FIXED GAUGE
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=var_act_exp,
            title={'text': "Variable EXP", 'font': {'size': 24}},
            delta={'reference': var_prev_act_exp},  #change triangle
            gauge={
                'axis': {'range': [None, var_mon_bdgt_exp + 1000], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "white"},
                'bgcolor': "white",
                'borderwidth': 2, # of the curve
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, var_mon_bdgt_exp], 'color': '#228C22'},
                    {'range': [var_mon_bdgt_exp, var_mon_bdgt_exp * 1.25], 'color': '#FFBF00'},
                    {'range': [var_mon_bdgt_exp * 1.25, var_mon_bdgt_exp + 1000], 'color': '#ff4500'}
                  ],
            }),
                      row=1, col=1)

        # VARIABLE GAUGE
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=fix_act_exp,
            title={'text': "Fixed EXP", 'font': {'size': 24}},
            delta={'reference': fix_prev_act_exp},  # change triangle
            gauge={
                'axis': {'range': [None, fix_mon_bdgt_exp + 1000], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "white"},
                'bgcolor': "white",
                'borderwidth': 2,  # of the curve
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, fix_mon_bdgt_exp], 'color': '#228C22'},
                    {'range': [fix_mon_bdgt_exp, fix_mon_bdgt_exp * 1.25], 'color': '#FFBF00'},
                    {'range': [fix_mon_bdgt_exp * 1.25, fix_mon_bdgt_exp + 1000], 'color': '#ff4500'}
                ],
            }),
                      row=1, col=2)

        fig.update_layout(height=600, showlegend=False)

        return fig

    #######################
    #
    # PAGE 1
    #
    #######################

    # P1 - Update Table, Description, CNT and SUM
    @app.callback([Output('stat-datatable', 'data'),
                   Output('count-sum-text', 'children'),
                   Output('descrip-date', 'children')],
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd2', 'value'),
                   Input('cat-dropdown', 'value'),
                   Input('acc-checklist', 'value')])
    def update_p1_table(start_date, end_date, categories, accounts):
        update_av_fc(start_date, end_date)
        data = update_datatable(acc_view, start_date, end_date, categories, accounts)

        disp_text = 'Number of Rows:' + str(len(data)) + ' | ' + \
                    'Sum of Rows:' + str(data['Amount'].sum())

        start_date_string, end_date_string = convert_picker_dates(start_date, end_date)
        days_selected = (datetime.strptime(end_date[:10], '%Y-%m-%d') -
                         datetime.strptime(start_date[:10], '%Y-%m-%d')).days
        string_prefix = 'Start Date: ' + start_date_string + \
                        '| End Date: ' + end_date_string + \
                        '| Period Length: ' + str(days_selected + 1) + ' Days'

        return[data.to_dict("rows"), disp_text, string_prefix]

    #######################
    #
    # PAGE 2
    #
    #######################

    # P2 - Expenses/Income Area Graph
    @app.callback(Output('in-out-area-graph', 'figure'),
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd2', 'value')])
    def update_p2_area_graph(start_date, end_date):
        update_av_fc(start_date, end_date)

        df_credit = copy.deepcopy(av.df_inc)
        df_debit = copy.deepcopy(av.df_exp)

        df_credit = df_credit[df_credit['Category'].isin(['INTEREST', 'INCOME'])].groupby(pd.Grouper(key='Date', freq='M')).sum()
        df_debit = df_debit.groupby(pd.Grouper(key='Date', freq='M')).sum()

        data = [go.Scatter(x=[mon.strftime('%B') for mon in df_credit.index],
                           y=df_credit['Amount'],
                           name='INCOME',
                           fill='tonexty'),
                go.Scatter(x=[mon.strftime('%B') for mon in df_debit.index],
                           y=df_debit['Amount'].abs(),
                           name='EXPENSES',
                           fill='tonexty')]
        layout = go.Layout()
        return {'data': data, 'layout': None}

    # P2 - Expenses Stacked Bar Graph
    @app.callback(Output('exp-stacked', 'figure'),
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd2', 'value'),
                   Input('p2-exp-radio', 'value')])
    def update_p2_stacked(start_date, end_date, type):
        update_av_fc(start_date, end_date)
        df_exp_cat = copy.deepcopy(av.df_exp_month_cat).reset_index()

        order = list(df_exp_cat['Date'].unique())

        if type == 'FIX':
            exp_cat = av.fix_exp
        else:
            exp_cat = av.var_exp

        data = []
        for cat in exp_cat:
            trace = go.Bar(x=df_exp_cat['Date'].dt.strftime('%b-%Y'),
                           y=df_exp_cat[df_exp_cat['Combined'] == cat]['sum'].abs(),
                           name=cat.split()[0].capitalize() + ' (' + cat.split()[1].capitalize() + ')')
            data.append(trace)

        layout = go.Layout(barmode='stack', xaxis={'categoryorder': 'array', 'categoryarray': order})
        return {'data': data, 'layout': layout}

    # P2 - Expenses Pie
    @app.callback(Output('exp-pie', 'figure'),
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd2', 'value'),
                   Input('p2-exp-radio', 'value')])
    def update_p2_var(start_date, end_date, type):
        update_av_fc(start_date, end_date)
        df_exp_cat = copy.deepcopy(av.df_exp_month_cat).reset_index()

        if type == 'FIX':
            exp_cat = av.fix_exp
        else:
            exp_cat = av.var_exp

        df_exp = df_exp_cat[df_exp_cat['Combined'].isin(exp_cat)]

        data = [go.Pie(labels=df_exp['Combined'], values=df_exp['sum'].abs())]
        layout = go.Layout()
        return {'data': data, 'layout': None}

    # P2 - Expenses Stacked Bar Graph
    @app.callback(Output('p2-exp-datatable', 'data'),
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd2', 'value')])
    def update_p2_table(start_date, end_date):
        update_av_fc(start_date, end_date)
        df_var = av.df_var_exp_month
        df_fix = av.df_fix_exp_month

        df_var = df_var.reset_index()
        df_fix = df_fix.reset_index()

        df_var_fix = pd.merge(df_var[['Date', 'sum']], df_fix[['Date', 'sum']], how='outer', on='Date', suffixes=('_var', '_fix'))
        df_var_fix = df_var_fix.fillna(0).reset_index()
        df_var_fix['Total'] = df_var_fix['sum_var'] + df_var_fix['sum_fix']
        df_var_fix['Date'] = df_var_fix["Date"].dt.strftime('%b-%Y')
        df_var_fix.rename(columns={'Date': 'Month', 'sum_var': 'Variable', 'sum_fix': 'Fixed'}, inplace=True)

        return df_var_fix.to_dict("rows")

    #######################
    #
    # PAGE 3
    #
    #######################

    # P3 - Toggle Multi/Mono Mode
    @app.callback(Output('p3-cat-dropdown', 'multi'),
                  [Input('p3-mode-dropdown', 'value')])
    def update_options(mode_value):
        if mode_value == 'MULTI':
            return True
        else:
            return False

    # P3 - Drop Down Values
    @app.callback(Output('p3-cat-dropdown', 'value'),
                  [Input('p3-mode-dropdown', 'value')])
    def update_options(mode_value):
        if mode_value == 'MONO':
            return 'AMAZON'
        else:
            return ['AMAZON', 'GROCERIES']

    # P3 - Box Plot
    @app.callback(Output('p3-box-plot', 'figure'),
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd2', 'value'),
                   Input('p3-cat-dropdown', 'value'),
                   Input('p3-mode-dropdown', 'value')])
    def update_p3_box(start_date, end_date, categories, mode):
        df_period = av.df_exp
        data = []

        if mode == 'MULTI':
            for cat in categories:
                trace = go.Box(y=df_period[df_period['Category'] == cat]['Amount'].abs(),
                               name=cat)
                data.append(trace)

        elif mode == 'MONO':
            start = datetime.strptime(start_date[:10], '%Y-%m-%d').strftime('%m')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d').strftime('%m')

            for mon in range(int(start), int(end)+1):
                df_mon = df_period[df_period['Date'].dt.month == mon]
                trace = go.Box(y=df_mon[df_mon['Category'] == categories]['Amount'].abs(),
                               name=calendar.month_abbr[mon]+'-2020')
                data.append(trace)

        layout = go.Layout()
        return {'data': data, 'layout': None}

    # P3 - Bar Graph
    @app.callback(Output('p3-bar-plot', 'figure'),
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd2', 'value'),
                   Input('p3-cat-dropdown', 'value'),
                   Input('p3-mode-dropdown', 'value')])
    def update_p3_bar(start_date, end_date, categories, mode):
        df_period = av.df_exp
        data = []
        order = df_period.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum']).index.strftime('%b-%Y')

        if mode == 'MULTI':
            for cat in categories:
                df_cat = df[df['Category'] == cat]
                df_cat_grouped = df_cat.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum'])
                trace = go.Bar(x=df_cat_grouped.index.strftime('%b-%Y'),
                               y=df_cat_grouped['sum'].abs(),
                               name=cat)
                data.append(trace)

        elif mode == 'MONO':
            df_cat = df[df['Category'] == categories]
            df_cat_grouped = df_cat.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum'])
            trace = go.Bar(x=df_cat_grouped.index.strftime('%b-%Y'),
                           y=df_cat_grouped['sum'].abs(),
                           name=categories)
            data.append(trace)

        layout = go.Layout(xaxis={'categoryorder': 'array', 'categoryarray': order})
        return {'data': data, 'layout': layout}

    # P3 - Time series
    @app.callback(Output('p3-time-plot', 'figure'),
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd2', 'value'),
                   Input('p3-cat-dropdown', 'value'),
                   Input('p3-mode-dropdown', 'value')])
    def update_p3_time(start_date, end_date, categories, mode):
        df_period = av.df_exp
        data = []
        order = df_period.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum']).index.strftime('%b-%Y')

        if mode == 'MULTI':
            for cat in categories:
                df_cat = df_period[df_period['Category'] == cat]
                df_cat_grouped = df_cat.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum'])
                trace = go.Scatter(x=df_cat_grouped.index.strftime('%b-%Y'),
                                   y=df_cat_grouped['sum'].abs(),
                                   name=cat)
                data.append(trace)

        elif mode == 'MONO':
            df_cat = df_period[df_period['Category'] == categories]
            df_cat_grouped = df_cat.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum'])
            trace = go.Scatter(x=df_cat_grouped.index.strftime('%b-%Y'),
                               y=df_cat_grouped['sum'].abs(),
                               name=categories)
            data.append(trace)

        layout = go.Layout(xaxis={'categoryorder': 'array', 'categoryarray': order})
        return {'data': data, 'layout': layout}

    @app.callback(
        Output('p3-cat-datatable', 'data'),
        [Input('p3-time-plot', 'clickData'),
         Input('p3-box-plot', 'clickData'),
         Input('p3-bar-plot', 'clickData'),
         Input('per-picker-dd1', 'value'),
         Input('per-picker-dd2', 'value'),
         Input('p3-cat-dropdown', 'value'),
         Input('p3-mode-dropdown', 'value')],
        [State('p3-time-plot', 'hoverData'),
         State('p3-box-plot', 'hoverData'),
         State('p3-bar-plot', 'hoverData')]
        )
    def callback_image(*args):
        dp_start_date = args[-7]
        dp_end_date = args[-6]
        categories = args[-5]
        mode = args[-4]
        timeData = args[-3]
        boxData = args[-2]
        barData = args[-1]

        if timeData:
            month_year = timeData['points'][0]['x']

            month = datetime.strptime(month_year + '-1', '%b-%Y-%d').strftime('%m')
            year = datetime.strptime(month_year + '-1', '%b-%Y-%d').strftime('%Y')
            eom = calendar.monthrange(int(year), int(month))[1]

            start_date = datetime.strptime(month_year+'-1', '%b-%Y-%d').strftime('%Y-%m-%d')
            end_date = datetime.strptime(month_year+'-'+str(eom), '%b-%Y-%d').strftime('%Y-%m-%d')

            return update_p3_table_df(start_date, end_date, categories, mode)
        if boxData:
            if mode == 'MULTI':
                category = [boxData['points'][0]['x']]
                start_date = datetime.strptime(dp_start_date[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
                end_date = datetime.strptime(dp_end_date[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
            elif mode == 'MONO':
                category = categories
                month_year = boxData['points'][0]['x']

                month = datetime.strptime(month_year + '-1', '%b-%Y-%d').strftime('%m')
                year = datetime.strptime(month_year + '-1', '%b-%Y-%d').strftime('%Y')
                eom = calendar.monthrange(int(year), int(month))[1]

                start_date = datetime.strptime(month_year + '-1', '%b-%Y-%d').strftime('%Y-%m-%d')
                end_date = datetime.strptime(month_year + '-' + str(eom), '%b-%Y-%d').strftime('%Y-%m-%d')

            return update_p3_table_df(start_date, end_date, category, mode)

        elif barData:
            month_year = barData['points'][0]['x']

            month = datetime.strptime(month_year + '-1', '%b-%Y-%d').strftime('%m')
            year = datetime.strptime(month_year + '-1', '%b-%Y-%d').strftime('%Y')
            eom = calendar.monthrange(int(year), int(month))[1]

            start_date = datetime.strptime(month_year+'-1', '%b-%Y-%d').strftime('%Y-%m-%d')
            end_date = datetime.strptime(month_year+'-'+str(eom), '%b-%Y-%d').strftime('%Y-%m-%d')

            return update_p3_table_df(start_date, end_date, categories, mode)
        return pd.DataFrame().to_dict('rows')

    #######################
    #
    # PAGE 4
    #
    #######################

    # P4 - Time series
    @app.callback(Output('p4-time-forecast-plot', 'figure'),
                  [Input('per-picker-dd1', 'value'),
                   Input('per-picker-dd2', 'value'),
                   Input('p4-month-dropdown', 'value')])
    def update_p4_time(start_date, end_date, months):
        update_av_fc(start_date, end_date, length=int(months))
        df_acc_mon_tot, df_forecast = frcst.calculate_forecast()

        actual = go.Scatter(x=df_acc_mon_tot.index.strftime('%b-%Y'),
                            y=df_acc_mon_tot['sum'].abs(),
                            name='actual')

        traces = [actual]
        for scenario in list(df_forecast.columns):
            # print(scenarios[scenario])
            trace = go.Scatter(x=df_forecast.index.strftime('%b-%Y'),
                               y=df_forecast[scenario],
                               name=scenario)
            traces.append(trace)

        return {'data': traces, 'layout': None}
    
    def update_av_fc(start_date, end_date, length=3):
        start_date, end_date = convert_picker_dates(start_date, end_date)
        print('Start: {}, END: {}'.format(start_date, end_date))
        if start_date != acc_view.start_date or end_date != acc_view.end_date or length != frcst.length:
            print('Recalculating...')
            acc_view.set_start_end_date(start_date, end_date)
            acc_view.update_views()
            frcst.set_account_views(acc_view, length)
