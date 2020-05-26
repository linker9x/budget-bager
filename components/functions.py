import pandas as pd
from datetime import datetime
import copy

df_pnc = pd.read_csv('./data/PNC_12M.csv')
df_chase = pd.read_csv('./data/Chase_12M.csv')
df_balance = pd.read_csv('./data/balances.csv')
df_budget = pd.read_csv('./data/budgeted_amts.csv')
df = pd.concat([df_pnc, df_chase]).reset_index(drop=True).sort_values(by=['Date'])
df['Date'] = pd.to_datetime(df['Date'])
df_balance['Date'] = pd.to_datetime(df_balance['Date'])


def update_datatable(start_date, end_date, categories, accounts):
    if start_date is not None:
        start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
    if end_date is not None:
        end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')

    df_sub = copy.deepcopy(df)
    df_sub = df_sub[(df_sub['Date'] >= start_date_string) & (df_sub['Date'] <= end_date_string)
                    & df_sub['Category'].isin(categories)
                    & df_sub['Source'].isin(accounts)].sort_values(by=['Date']).reset_index(drop=True)
    return df_sub.to_dict("rows")


def update_period_df(start_date, end_date):
    if start_date is not None:
        start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
    if end_date is not None:
        end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')

    df_sub = copy.deepcopy(df)
    df_sub = df_sub[(df_sub['Date'] >= start_date_string) & (df_sub['Date'] <= end_date_string)
                    & ~df_sub['Category'].isin(['PAYMENT', 'SAVINGS'])].sort_values(by=['Date']).reset_index(drop=True)
    return df_sub


def update_period_df_all(start_date, end_date):
    if start_date is not None:
        start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
    if end_date is not None:
        end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')

    df_sub = copy.deepcopy(df)
    df_sub = df_sub[(df_sub['Date'] >= start_date_string) & (df_sub['Date'] <= end_date_string)].sort_values(
        by=['Date']).reset_index(drop=True)
    return df_sub


def update_p3_table_df(start_date_string, end_date_string, categories, mode):
    df_sub = copy.deepcopy(df)

    if mode == 'MULTI':
        df_sub = df_sub[(df_sub['Date'] >= start_date_string) & (df_sub['Date'] <= end_date_string)
                        & df_sub['Category'].isin(categories)].sort_values(by=['Category', 'Date']).reset_index(drop=True)
    else:
        df_sub = df_sub[(df_sub['Date'] >= start_date_string) & (df_sub['Date'] <= end_date_string)
                        & (df_sub['Category'] == categories)].sort_values(by=['Date']).reset_index(drop=True)
    return df_sub.to_dict("rows")


def return_df():
    return df


def return_balance(start_date_string, end_date_string):
    df_sub = copy.deepcopy(df_balance)
    df_sub = df_sub[(df_sub['Date'] >= start_date_string) & (df_sub['Date'] <= end_date_string)].reset_index(drop=True)
    return df_sub


def calc_gauge_vals(type):
    type ='VAR' if type == 'VAR' else 'FIX'

    df_bdgt_amt = copy.deepcopy(df_budget)
    df_bdgt_amt['Combined'] = df_bdgt_amt['Category'] + ' ' + df_bdgt_amt['Subcategory']
    df_bdgt_exp = df_bdgt_amt[df_bdgt_amt['Type'] == type]

    expenses = df_bdgt_exp['Combined'].unique()

    df = copy.deepcopy(return_df())
    df['Combined'] = df['Category'] + ' ' + df['Subcategory']
    df_act_exp = df[(df['Amount'] < 0) &
                    df['Combined'].isin(expenses)].groupby(['Combined', pd.Grouper(key='Date', freq='M')]).sum()
    df_act_exp = df_act_exp.unstack(fill_value=0).stack().reset_index()

    prev_EOM = df_act_exp['Date'].unique()[-1]
    prev_EOM = datetime.strptime(str(prev_EOM)[:10], '%Y-%m-%d')
    prev_EOM = prev_EOM.strftime('%Y-%m-%d')

    pprev_EOM = df_act_exp['Date'].unique()[-2]
    pprev_EOM = datetime.strptime(str(pprev_EOM)[:10], '%Y-%m-%d')
    pprev_EOM = pprev_EOM.strftime('%Y-%m-%d')

    act_exp = df_act_exp[(df_act_exp['Date'] == prev_EOM)]['Amount'].sum() * -1
    prev_act_exp = df_act_exp[(df_act_exp['Date'] == pprev_EOM)]['Amount'].sum() * -1

    mon_bdgt_exp = df_bdgt_exp['Amount'].sum()

    return act_exp, prev_act_exp, mon_bdgt_exp
