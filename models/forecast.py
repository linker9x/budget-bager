import pandas as pd
import numpy as np
from models.accountviews import AccountViews


class Forecast:
    def __init__(self, account_views, length=3):
        self.budget = pd.read_csv('./exp_data/budgeted_amts.csv')
        self.account_views = account_views
        self.length = length
        self.forecast = pd.DataFrame()

        self.budget['Combined'] = self.budget['Category'] + ' ' + self.budget['Subcategory']

        self._calculate_forecast()

    def __str__(self):
        return 'cat'

    def forecast_var_exp(self, row):
        if row['Percent'][0] > .20:
            forecast = row['sum']['mean'] - row['std']['mean']
        elif row['Percent'][0] < .20:
            forecast = row['sum']['mean']
        return forecast

    def _calculate_forecast(self):
        mon_var_exp = list(self.budget[self.budget['Type'] == 'VAR']['Combined'].unique())
        mon_fix_exp = list(self.budget[(self.budget['Type'] == 'FIX') & (self.budget['Period'] == 1)]['Combined'].unique())
        hy_fix_exp = list(self.budget[(self.budget['Type'] == 'FIX') & (self.budget['Period'] == 6)]['Combined'].unique())

        av = self.account_views

        df_exp_month_cat = av.df_exp_month_cat.reset_index()

        df_var_exp = df_exp_month_cat[df_exp_month_cat['Combined'].isin(mon_var_exp)].reset_index(drop=True)
        df_var_exp = df_var_exp.groupby(['Combined'])[['sum', 'std']].agg(['mean']).abs()
        df_var_exp['Percent'] = df_var_exp['std']['mean'] / df_var_exp['sum']['mean']
        df_var_exp['Base'] = df_var_exp.apply(self.forecast_var_exp, axis=1)
        print(df_var_exp['Base'].sum())

        df_mon_fix_exp = df_exp_month_cat[df_exp_month_cat['Combined'].isin(mon_fix_exp)].reset_index(drop=True)
        df_mon_fix_exp = df_mon_fix_exp.groupby(['Combined'])[['sum', 'std']].agg(['mean'])
        print(df_mon_fix_exp['sum']['mean'].sum())

        df_hy_fix_exp = df_exp_month_cat[df_exp_month_cat['Combined'].isin(hy_fix_exp)].reset_index(drop=True)
        df_hy_fix_exp = df_hy_fix_exp.groupby(['Combined'])[['sum', 'std']].agg(['mean'])
        print(df_hy_fix_exp['sum']['mean'].sum()/6)


        # DF of VAR BUD
        # DF of FIX1 BUD
        # BUD TOTAL AMT FIX6

        # All of exp

        #

        # bdgt_amt = return_budget()
        #
        # bdgt_amt_var = bdgt_amt[bdgt_amt['Type'] == 'VAR']
        # var_cat = bdgt_amt_var['Category'] + ' ' + bdgt_amt_var['Subcategory']
        #
        # bdgt_amt_fix1 = bdgt_amt[(bdgt_amt['Type'] == 'FIX') & (bdgt_amt['Period'] == 1)]
        # fix1_cat = bdgt_amt_fix1['Category'] + ' ' + bdgt_amt_fix1['Subcategory']
        #
        # bdgt_amt_fix6 = bdgt_amt[(bdgt_amt['Period'] == 6)]['Amount'].sum()
        #
        # df = update_period_df_all(start_date, end_date)
        # df['Combined'] = df['Category'] + ' ' + df['Subcategory']
        # !!!
        # df_mon_var = df.copy()
        # df_mon_var['Amount'] = df_mon_var['Amount'].abs()
        # df_mon_var = df_mon_var[(df_mon_var['Amount'] < 200) &
        #                         df_mon_var['Combined'].isin(var_cat.unique())]
        # df_mon_var = df_mon_var.groupby(['Combined',
        #                                  pd.Grouper(key='Date', freq='M')]).sum().unstack(fill_value=0).stack()
        #
        # df_mon_var_agg = df_mon_var.groupby(['Combined']).agg(['mean', 'std'])
        # df_mon_var_agg = df_mon_var_agg.fillna(0)
        # !!!!
        # df_mon_var_agg['worst'] = df_mon_var_agg['Amount']['mean'] \
        #                           + df_mon_var_agg['Amount']['std'] * .5
        # df_mon_var_agg['best'] = df_mon_var_agg['Amount']['mean'] - \
        #                          df_mon_var_agg['Amount']['std'] * .5
        #
        # var_exp_base = df_mon_var_agg['Amount']['mean'].sum()
        # var_exp_worst = df_mon_var_agg['worst'].sum()
        # var_exp_best = df_mon_var_agg['best'].sum()
        #
        # df_mon_fix1 = df
        # df_mon_fix1['Amount'] = df_mon_fix1['Amount'].abs()
        # df_mon_fix1 = df_mon_fix1[df_mon_fix1['Combined'].isin(fix1_cat.unique())]
        # df_mon_fix1 = df_mon_fix1.groupby(['Combined',
        #                                    pd.Grouper(key='Date', freq='M')]).sum().unstack(fill_value=0).stack()
        # fixed1_exp = df_mon_fix1.groupby(['Combined']).agg(['mean']).sum()
        #
        # best = var_exp_best + fixed1_exp + (bdgt_amt_fix6 / 6)
        # base = var_exp_base + fixed1_exp + (bdgt_amt_fix6 / 6)
        # worst = var_exp_worst + fixed1_exp + (bdgt_amt_fix6 / 6)
        # scenarios = {'best': best.to_list()[0], 'base': base.to_list()[0], 'worst': worst.to_list()[0]}
        #
        # df_group = return_balance(start_date, end_date).groupby(pd.Grouper(key='Date', freq='M'))[
        #     'Account Balance'].agg(
        #     ['sum'])
        # last_month = df_group.tail(1)
        # forecast = {last_month.index[0]: last_month['sum'].to_list()[0]}
        #
        # return scenarios, df_group, last_month, forecast

