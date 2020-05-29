import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html

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

__fixed_cat = ['CAR', 'HEALTHCARE', 'FITNESS', 'PHONE']
__var_cat = ['AMAZON', 'TRAVEL', 'PERSONAL', 'SHOPPING', 'ENTERTAINMENT', 'CATS',
             'GROCERIES', 'RESTAURANT', 'GAS']


def register_callbacks(app):
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


    # HOME - TABLES
    @app.callback(Output('var-summary-table', 'data'),
                  [Input('home-var-dropdown', 'value')])
    def update_var_summary(val):
        return update_summary_table('VAR')

    @app.callback(Output('fix-summary-table', 'data'),
                  [Input('home-var-dropdown', 'value')])
    def update_var_summary(val):
        return update_summary_table('FIX')

    # HOME - GAUGES
    @app.callback(Output('home-gauge', 'figure'),
                  [Input('home-var-dropdown', 'value')])
    def update_gauge(cat):
        var_act_exp, var_prev_act_exp, var_mon_bdgt_exp = calc_gauge_vals('VAR')
        fix_act_exp, fix_prev_act_exp, fix_mon_bdgt_exp = calc_gauge_vals('FIX')

        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "indicator"}, {"type": "indicator"}]]
        )

        # FIXED GAUGE
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=var_act_exp,
            title={'text': "Variable EXP", 'font': {'size': 24}},
            delta={'reference': var_prev_act_exp}, #change triangle
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

    # P1 - Update Table, Description, CNT and SUM
    @app.callback([Output('stat-datatable', 'data'),
                   Output('count-sum-text', 'children'),
                   Output('descrip-date', 'children')],
                  [Input('stat-date-picker', 'start_date'),
                   Input('stat-date-picker', 'end_date'),
                   Input('cat-dropdown', 'value'),
                   Input('acc-checklist', 'value')])
    def update_p1_table(start_date, end_date, categories, accounts):
        data_1 = update_datatable(start_date, end_date, categories, accounts)

        disp_text = 'Number of Rows:' + str(len(data_1)) + ' | ' + \
                    'Sum of Rows:' + str(data_1['Amount'].sum())

        start_date_string, end_date_string = convert_picker_dates(start_date, end_date)
        days_selected = (datetime.strptime(end_date[:10], '%Y-%m-%d') -
                         datetime.strptime(start_date[:10], '%Y-%m-%d')).days
        string_prefix = 'Start Date: ' + start_date_string + \
                        '| End Date: ' + end_date_string + \
                        '| Period Length: ' + str(days_selected + 1) + ' Days'

        return[data_1.to_dict("rows"), disp_text, string_prefix]

    # P2 - Expenses/Income Area Graph
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
                           name='EXPENSES',
                           fill='tonexty')]
        layout = go.Layout()
        return {'data': data, 'layout': None}

    # P2 - Stacked Bar Graph
    @app.callback(Output('fixed-var-stacked', 'figure'),
                  [Input('p2-date-picker', 'start_date'),
                   Input('p2-date-picker', 'end_date')])
    def update_p2_stacked(start_date, end_date):
        df_period = update_period_df(start_date, end_date)
        order = agg_by_month(start_date, end_date).index.strftime('%b-%Y')
        total_exp = get_var_exp()

        data = []
        for cat in total_exp:
            df_cat = df_period[df_period['Combined'] == cat].groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum'])

            trace = go.Bar(x=df_cat.index.strftime('%b-%Y'),
                           y=df_cat['sum'].abs(),
                           name=cat.split()[0] + ' (' + cat.split()[1] + ')')
            data.append(trace)

        layout = go.Layout(barmode='stack', xaxis={'categoryorder': 'array', 'categoryarray': order})
        return {'data': data, 'layout': layout}

    # P2 - Fixed Pie
    @app.callback(Output('fixed-pie', 'figure'),
                  [Input('p2-date-picker', 'start_date'),
                   Input('p2-date-picker', 'end_date')])
    def update_p2_fixed(start_date, end_date):
        df_period = update_period_df(start_date, end_date)
        df_cat = df_period.groupby('Combined')['Amount'].agg(['sum'])
        fix_cat = get_fix_exp()
        df_fixed = df_cat[df_cat.index.isin(fix_cat)]

        data = [go.Pie(labels=df_fixed.index, values=df_fixed['sum'].abs())]
        layout = go.Layout()
        return {'data': data, 'layout': None}

    # P2 - Var Pie
    @app.callback(Output('var-pie', 'figure'),
                  [Input('p2-date-picker', 'start_date'),
                   Input('p2-date-picker', 'end_date')])
    def update_p2_var(start_date, end_date):
        df_period = update_period_df(start_date, end_date)
        df_cat = df_period.groupby('Combined')['Amount'].agg(['sum'])
        var_cat = get_var_exp()
        df_var = df_cat[df_cat.index.isin(var_cat)]

        data = [go.Pie(labels=df_var.index, values=df_var['sum'].abs())]
        layout = go.Layout()
        return {'data': data, 'layout': None}

    # P3 - Multi
    @app.callback(Output('p3-cat-dropdown', 'multi'),
                  [Input('p3-mode-dropdown', 'value')])
    def update_options(mode_value):
        if mode_value == 'MULTI':
            return True
        else:
            return False

    @app.callback(Output('p3-cat-dropdown', 'value'),
                  [Input('p3-mode-dropdown', 'value')])
    def update_options(mode_value):
        if mode_value == 'MONO':
            return 'AMAZON'
        else:
            return ['AMAZON', 'GROCERIES']

    # P3 - Box Plot
    @app.callback(Output('p3-box-plot', 'figure'),
                  [Input('p3-date-picker', 'start_date'),
                   Input('p3-date-picker', 'end_date'),
                   Input('p3-cat-dropdown', 'value'),
                   Input('p3-mode-dropdown', 'value')])
    def update_p3_box(start_date, end_date, categories, mode):
        df = update_period_df(start_date, end_date)
        data = []

        if mode == 'MULTI':
            for cat in categories:
                trace = go.Box(y=df[df['Category'] == cat]['Amount'].abs(),
                               name=cat)
                data.append(trace)

        elif mode == 'MONO':
            start = datetime.strptime(start_date[:10], '%Y-%m-%d').strftime('%m')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d').strftime('%m')

            for mon in range(int(start), int(end)+1):
                df_mon = df[df['Date'].dt.month == mon]
                trace = go.Box(y=df_mon[df_mon['Category'] == categories]['Amount'].abs(),
                               name=calendar.month_abbr[mon]+'-2020')
                data.append(trace)

        layout = go.Layout()
        return {'data': data, 'layout': None}

    # P3 - Bar Graph
    @app.callback(Output('p3-bar-plot', 'figure'),
                  [Input('p3-date-picker', 'start_date'),
                   Input('p3-date-picker', 'end_date'),
                   Input('p3-cat-dropdown', 'value'),
                   Input('p3-mode-dropdown', 'value')])
    def update_p3_bar(start_date, end_date, categories, mode):
        df = update_period_df(start_date, end_date)
        data = []
        order = df.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum']).index.strftime('%b-%Y')

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
                  [Input('p3-date-picker', 'start_date'),
                   Input('p3-date-picker', 'end_date'),
                   Input('p3-cat-dropdown', 'value'),
                   Input('p3-mode-dropdown', 'value')])
    def update_p3_time(start_date, end_date, categories, mode):
        df = update_period_df(start_date, end_date)
        data = []
        order = df.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum']).index.strftime('%b-%Y')

        if mode == 'MULTI':
            for cat in categories:
                df_cat = df[df['Category'] == cat]
                df_cat_grouped = df_cat.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum'])
                trace = go.Scatter(x=df_cat_grouped.index.strftime('%b-%Y'),
                                   y=df_cat_grouped['sum'].abs(),
                                   name=cat)
                data.append(trace)

        elif mode == 'MONO':
            df_cat = df[df['Category'] == categories]
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
         Input('p3-date-picker', 'start_date'),
         Input('p3-date-picker', 'end_date'),
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

        # print('START\n{}\n{}\nEND'.format(categories, mode))
        # print('START\n{}\n{}\n{}\n END'.format(timeData, boxData, barData))

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

    # P4 - Time series
    @app.callback(Output('p4-time-forecast-plot', 'figure'),
                  [Input('p4-date-picker', 'start_date'),
                   Input('p4-date-picker', 'end_date'),
                   Input('p4-month-dropdown', 'value')])
    def update_p4_time(start_date, end_date, months):
        bdgt_amt = return_budget()

        bdgt_amt_var = bdgt_amt[bdgt_amt['Type'] == 'VAR']
        var_cat = bdgt_amt_var['Category'] + ' ' + bdgt_amt_var['Subcategory']

        bdgt_amt_fix1 = bdgt_amt[(bdgt_amt['Type'] == 'FIX') & (bdgt_amt['Period'] == 1)]
        fix1_cat = bdgt_amt_fix1['Category'] + ' ' + bdgt_amt_fix1['Subcategory']
        fixed_exp1 = bdgt_amt_fix1['Amount'].sum()

        bdgt_amt_fix6 = bdgt_amt[(bdgt_amt['Type'] == 'FIX') & (bdgt_amt['Period'] == 6)]

        df = update_period_df_all(start_date, end_date)
        df['Combined'] = df['Category'] + ' ' + df['Subcategory']

        # bal of prev month + curr mon in + curr mon out should equal EOM balance
        # df_in = df[(df['Amount'] >= 0) & (df['Source'] == 'PNC')].groupby(pd.Grouper(key='Date', freq='M')).sum()
        # print(df_in)
        # df_out = df[(df['Amount'] < 0) & (df['Source'] == 'PNC')].groupby(pd.Grouper(key='Date', freq='M')).sum()
        # print(df_out)

        # These should be equal
        # df_chase = df[(df['Source'] == 'Chase') & (df['Category'] == 'PAYMENT')].groupby(pd.Grouper(key='Date', freq='M')).sum()
        # print(df_chase)
        # df_pnc = df[(df['Source'] == 'PNC') & (df['Category'] == 'PAYMENT')].groupby(pd.Grouper(key='Date', freq='M')).sum()
        # print(df_pnc)

        df_mon_var = df.copy()
        df_mon_var['Amount'] = df_mon_var['Amount'].abs()
        df_mon_var = df_mon_var[(df_mon_var['Amount'] < 200) &
                                df_mon_var['Combined'].isin(var_cat.unique())]
        df_mon_var = df_mon_var.groupby(['Combined',
                                         pd.Grouper(key='Date', freq='M')]).sum().unstack(fill_value=0).stack()

        df_mon_var_agg = df_mon_var.groupby(['Combined']).agg(['mean', 'std'])
        df_mon_var_agg = df_mon_var_agg.fillna(0)
        df_mon_var_agg['worst'] = df_mon_var_agg['Amount']['mean'] \
                                  + df_mon_var_agg['Amount']['std'] * .5
        df_mon_var_agg['best'] = df_mon_var_agg['Amount']['mean'] - \
                                 df_mon_var_agg['Amount']['std'] * .5

        var_exp_base = df_mon_var_agg['Amount']['mean'].sum()
        var_exp_worst = df_mon_var_agg['worst'].sum()
        var_exp_best = df_mon_var_agg['best'].sum()

        df_mon_fix1 = df
        df_mon_fix1['Amount'] = df_mon_fix1['Amount'].abs()
        df_mon_fix1 = df_mon_fix1[df_mon_fix1['Combined'].isin(fix1_cat.unique())]
        df_mon_fix1 = df_mon_fix1.groupby(['Combined',
                                           pd.Grouper(key='Date', freq='M')]).sum().unstack(fill_value=0).stack()
        fixed1_exp = df_mon_fix1.groupby(['Combined']).agg(['mean']).sum()

        best = var_exp_best + fixed1_exp
        base = var_exp_base + fixed1_exp
        worst = var_exp_worst + fixed1_exp
        scenarios = {'best': best.to_list()[0], 'base': base.to_list()[0], 'worst': worst.to_list()[0]}

        df_group = return_balance(start_date, end_date).groupby(pd.Grouper(key='Date', freq='M'))['Account Balance'].agg(['sum'])
        last_month = df_group.tail(1)
        forecast = {last_month.index[0]: last_month['sum'].to_list()[0]}

        for i in range(int(months) + 1):
            fore_date = last_month.index[0] + relativedelta(months=+2 + i, day=1) - timedelta(days=1)
            temp_dict = {}

            for key in scenarios:
                temp_dict[key] = last_month['sum'].to_list()[0] - (scenarios[key] * (i + 1))

            forecast[fore_date] = temp_dict
        df_forecast = pd.DataFrame(forecast).T

        actual = go.Scatter(x=df_group.index.strftime('%b-%Y'),
                            y=df_group['sum'].abs(),
                            name='actual')

        traces = [actual]
        for key in scenarios:
            # print(scenarios[key])
            trace = go.Scatter(x=df_forecast.index.strftime('%b-%Y'),
                               y=df_forecast[key],
                               name=key)
            traces.append(trace)

        return {'data': traces, 'layout': None}
