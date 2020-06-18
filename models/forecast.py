import pandas as pd
import numpy as np
from datetime import timedelta
from dateutil.relativedelta import *
from models.accountviews import AccountViews


class Forecast:
    def __init__(self, account_views, length=3):
        self.budget = pd.read_csv('./exp_data/budgeted_amts.csv')
        self.account_views = account_views
        self.length = length
        self.forecast = pd.DataFrame()

        self.budget['Combined'] = self.budget['Category'] + ' ' + self.budget['Subcategory']

        self.calculate_forecast()

    def __str__(self):
        return 'cat'

    def set_account_views(self, av, length=3):
        self.length = length
        self.account_views = av
        self.calculate_forecast()

    def __forecast_var_exp(self, row):
        if row['Combined'][0] == 'CAR OTHER':
            forecast = 0
        elif row['Percent'][0] > .20:
            forecast = row['sum']['mean'] - row['std']['mean']*.5
        elif row['Percent'][0] < .20:
            forecast = row['sum']['mean']
        return forecast

    def calculate_forecast(self):
        mon_var_exp = list(self.budget[self.budget['Type'] == 'VAR']['Combined'].unique())
        mon_fix_exp = list(self.budget[(self.budget['Type'] == 'FIX') & (self.budget['Period'] == 1)]['Combined'].unique())
        hy_fix_exp = list(self.budget[(self.budget['Type'] == 'FIX') & (self.budget['Period'] == 6)]['Combined'].unique())

        av = self.account_views

        df_exp_month_cat = av.df_exp_month_cat.reset_index()

        df_var_exp = df_exp_month_cat[df_exp_month_cat['Combined'].isin(mon_var_exp)].reset_index(drop=True)
        df_var_exp = df_var_exp.groupby(['Combined'])[['sum', 'std']].agg(['mean']).abs().reset_index()
        df_var_exp['Percent'] = df_var_exp['std']['mean'] / df_var_exp['sum']['mean']
        df_var_exp['Base'] = df_var_exp.apply(self.__forecast_var_exp, axis=1)
        var_mon_total = df_var_exp['Base'].sum()
        var_mon_mean_std = df_var_exp['sum']['mean'].std()

        df_mon_fix_exp = self.budget[self.budget['Combined'].isin(mon_fix_exp)].reset_index(drop=True)
        mon_fix_total = df_mon_fix_exp['Amount'].sum()

        df_hy_fix_exp = self.budget[self.budget['Combined'].isin(hy_fix_exp)].reset_index(drop=True)
        hy_fix_total = df_hy_fix_exp['Amount'].sum()/6

        total_mon_exp = var_mon_total + mon_fix_total + hy_fix_total
        scenarios = {'best': round(total_mon_exp - var_mon_mean_std, 2),
                     'base': round(total_mon_exp, 2),
                     'worst': round(total_mon_exp + var_mon_mean_std, 2)}

        chk_acc_bal = av.checking.balance_log

        df_acc_mon_tot = chk_acc_bal.groupby(pd.Grouper(key='Date', freq='M'))['Account Balance'].agg(['sum'])

        last_month = df_acc_mon_tot.tail(1)
        dict_lm = {last_month.index[0]: last_month['sum'].to_list()[0]}

        for i in range(self.length):
            fore_date = last_month.index[0] + relativedelta(months=+2 + i, day=1) - timedelta(days=1)
            temp_dict = {}

            for key in scenarios:
                temp_dict[key] = last_month['sum'].to_list()[0] - (scenarios[key] * (i + 1))

            dict_lm[fore_date] = temp_dict

        self.forecast = pd.DataFrame(dict_lm).T
        self.forecast.index.name = 'Date'

        return df_acc_mon_tot, self.forecast
