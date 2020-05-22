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


def return_balance():
    return df_balance


def return_budget():
    return df_budget