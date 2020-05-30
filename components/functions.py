import pandas as pd
from datetime import datetime
import copy

df_balance = pd.read_csv('./data/balances.csv')
df_balance['Date'] = pd.to_datetime(df_balance['Date'])

df_budget = pd.read_csv('./data/budgeted_amts.csv')
df_budget['Combined'] = df_budget['Category'] + ' ' + df_budget['Subcategory']

df_pnc = pd.read_csv('./data/PNC_12M.csv')
df_chase = pd.read_csv('./data/Chase_12M.csv')
df = pd.concat([df_pnc, df_chase]).reset_index(drop=True).sort_values(by=['Date'])
df['Date'] = pd.to_datetime(df['Date'])
df['Combined'] = df['Category'] + ' ' + df['Subcategory']

__fix_exp = df_budget[df_budget['Type'] == 'FIX']['Combined'].unique().tolist()
__var_exp = df_budget[df_budget['Type'] == 'VAR']['Combined'].unique().tolist()

df_exp_tot_by_month = df[(df['Combined'].isin(__fix_exp + __var_exp))].groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum'])

df_exp_fix_by_month = df[(df['Amount'] < 0) & (df['Combined'].isin(__fix_exp))].groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum'])

df_exp_var_by_month = df[(df['Amount'] < 0) & (df['Combined'].isin(__var_exp))].groupby(pd.Grouper(key='Date', freq='M'))['Amount'].agg(['sum'])

df_cat_tot_by_month = df.groupby(['Combined', pd.Grouper(key='Date', freq='M')])['Amount'].agg(['sum']).unstack(fill_value=0).stack()


def convert_picker_dates(start_date, end_date):
    if start_date is not None:
        start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
    if end_date is not None:
        end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')
    return start_date_string, end_date_string


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
    return df_sub


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
    df_bdgt_exp = df_bdgt_amt[(df_bdgt_amt['Type'] == type)].reset_index(drop=True)

    expenses = df_bdgt_exp['Combined'].unique()

    df_act = copy.deepcopy(df)
    df_act['Combined'] = df_act['Category'] + ' ' + df_act['Subcategory']
    df_act_exp = df_act[(df_act['Amount'] < 0) &
                        df_act['Combined'].isin(expenses)].groupby(['Combined', pd.Grouper(key='Date', freq='M')]).sum()
    df_act_exp = df_act_exp.unstack(fill_value=0).stack().reset_index()

    prev_EOM = df_act_exp['Date'].unique()[-1]
    prev_EOM = datetime.strptime(str(prev_EOM)[:10], '%Y-%m-%d')
    prev_EOM = prev_EOM.strftime('%Y-%m-%d')

    pprev_EOM = df_act_exp['Date'].unique()[-2]
    pprev_EOM = datetime.strptime(str(pprev_EOM)[:10], '%Y-%m-%d')
    pprev_EOM = pprev_EOM.strftime('%Y-%m-%d')

    act_exp = df_act_exp[(df_act_exp['Date'] == prev_EOM) & (df_act_exp['Amount'] != 0.0)]
    prev_act_exp = df_act_exp[(df_act_exp['Date'] == pprev_EOM) & (df_act_exp['Amount'] != 0.0)]

    if type == 'FIX':
        df_combined_act = pd.merge(df_bdgt_exp, act_exp, on='Combined', how='right')
    else:
        df_combined_act = pd.merge(df_bdgt_exp, act_exp, on='Combined', how='outer')

    print(df_combined_act)

    return df_combined_act['Amount_y'].sum() * -1, prev_act_exp['Amount'].sum() * -1, df_combined_act['Amount_x'].sum()


def update_summary_table(type):
    df_bdgt_amt = copy.deepcopy(df_budget)
    df_bdgt_amt['Combined'] = df_bdgt_amt['Category'] + ' ' + df_bdgt_amt['Subcategory']
    df_bdgt_exp = df_bdgt_amt[(df_bdgt_amt['Type'] == type)]
    df_bdgt_exp = df_bdgt_exp.reset_index(drop=True)

    expenses = df_bdgt_exp['Combined'].unique()

    df_act = copy.deepcopy(df)
    df_act['Combined'] = df_act['Category'] + ' ' + df_act['Subcategory']
    df_act_exp = df_act[(df_act['Amount'] < 0) &
                        df_act['Combined'].isin(expenses)].groupby(['Combined', pd.Grouper(key='Date', freq='M')]).sum()
    df_act_exp = df_act_exp.unstack(fill_value=0).stack().reset_index()
    df_act_exp_prev_mon = df_act_exp[df_act_exp['Date'] == df_act_exp['Date'].max()]

    df_act_exp_prev_mon = df_act_exp_prev_mon.reset_index(drop=True)

    if type == 'FIX':
        df_combined = pd.merge(df_bdgt_exp, df_act_exp_prev_mon[df_act_exp_prev_mon['Amount'] != 0.0], on='Combined', how='right')
    else:
        df_combined = pd.merge(df_bdgt_exp, df_act_exp_prev_mon, on='Combined', how='outer')

    df_combined = df_combined.filter(['Category', 'Subcategory', 'Amount_x', 'Amount_y'])

    df_combined['Amount_y'] = df_combined['Amount_y'].abs()
    df_combined.rename(columns={'Amount_x': 'Budget', 'Amount_y': 'Actual'}, inplace=True)
    df_combined['Diff'] = df_combined['Budget'] - df_combined['Actual']
    return df_combined.to_dict("rows")

def return_budget():
    return df_budget


def filter_fix_exp_df(unsort_df=df):
    df_fix = copy.deepcopy(unsort_df[unsort_df['Combined'].isin(__fix_exp)])
    return df_fix


def filter_var_exp_df(unsort_df=df):
    df_var = copy.deepcopy(unsort_df[unsort_df['Combined'].isin(__var_exp)])
    return df_var


def agg_by_month(start_date, end_date):
    start_date_str, end_date_str = convert_picker_dates(start_date, end_date)
    df_filtered = df_exp_tot_by_month[(df_exp_tot_by_month.index >= start_date_str) &
                                      (df_exp_tot_by_month.index <= end_date_str)]
    return df_filtered


def agg_fix_by_month(start_date, end_date):
    start_date_str, end_date_str = convert_picker_dates(start_date, end_date)
    df_filtered = df_exp_fix_by_month[(df_exp_fix_by_month.index >= start_date_str) &
                                      (df_exp_fix_by_month.index <= end_date_str)]
    return df_filtered


def agg_var_by_month(start_date, end_date):
    start_date_str, end_date_str = convert_picker_dates(start_date, end_date)
    df_filtered = df_exp_var_by_month[(df_exp_var_by_month.index >= start_date_str) &
                                      (df_exp_var_by_month.index <= end_date_str)]
    return df_filtered


def agg_by_cat_month():
    return copy.deepcopy(df_cat_tot_by_month)


def get_fix_exp():
    return __fix_exp


def update_p2_varfix_table(start_date, end_date):
    df_var = agg_var_by_month(start_date, end_date)
    df_fixed = agg_fix_by_month(start_date, end_date)

    df_merged = df_var.join(df_fixed, how='outer', lsuffix='_var', rsuffix='_fix')
    df_merged = df_merged.fillna(0).reset_index()
    df_merged['Total'] = df_merged['sum_var'] + df_merged['sum_fix']
    df_merged['Date'] = df_merged["Date"].dt.strftime('%b-%Y')
    df_merged.rename(columns={'Date': 'Month', 'sum_var': 'Variable', 'sum_fix': 'Fixed'}, inplace=True)

    return df_merged


def get_var_exp():
    return __var_exp
