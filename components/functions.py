import pandas as pd
from datetime import datetime
import copy


def convert_picker_dates(start_date, end_date):
    start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
    start_date_string = start_date.strftime('%Y-%m-%d')

    end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')
    end_date_string = end_date.strftime('%Y-%m-%d')
    return start_date_string, end_date_string


def update_summary_table(acc_view, frcst, type):
    df_bdgt_amt = copy.deepcopy(frcst.budget)
    df_bdgt_amt['Combined'] = df_bdgt_amt['Category'] + ' ' + df_bdgt_amt['Subcategory']
    df_bdgt_exp = df_bdgt_amt[(df_bdgt_amt['Type'] == type)]
    df_bdgt_exp = df_bdgt_exp.reset_index(drop=True)
    expenses = df_bdgt_exp['Combined'].unique()

    df_act = copy.deepcopy(acc_view.df_exp_month_cat).abs()
    df_act_exp = df_act.unstack(fill_value=0).stack().reset_index()
    df_act_exp = df_act_exp[df_act_exp['Combined'].isin(expenses)]
    df_act_exp_prev_mon = df_act_exp[df_act_exp['Date'] == df_act_exp['Date'].max()]
    df_act_exp_prev_mon = df_act_exp_prev_mon.reset_index(drop=True)
    df_act_exp_prev_mon.drop(['mean', 'std'], axis=1, inplace=True)

    df_combined = pd.merge(df_bdgt_exp,
                           df_act_exp_prev_mon,
                           on='Combined',
                           how='inner')
    if type == 'FIX':
        df_combined = df_combined[df_combined['sum'] != 0.0]

    df_combined = df_combined.sort_values(by=['sum', 'Amount'], ascending=False)
    df_combined = df_combined.filter(['Category', 'Subcategory', 'sum', 'Amount'])
    df_combined.rename(columns={'Amount': 'Budget', 'sum': 'Actual'}, inplace=True)
    df_combined['Diff'] = (df_combined['Budget'] - df_combined['Actual']).round(2)
    return df_combined.to_dict("rows")


def calc_gauge_vals(acc_view, frcst, type):
    type ='VAR' if type == 'VAR' else 'FIX'

    df_bdgt_amt = copy.deepcopy(frcst.budget)
    df_bdgt_amt['Combined'] = df_bdgt_amt['Category'] + ' ' + df_bdgt_amt['Subcategory']
    df_bdgt_exp = df_bdgt_amt[(df_bdgt_amt['Type'] == type)].reset_index(drop=True)
    expenses = df_bdgt_exp['Combined'].unique()

    df_act_exp = copy.deepcopy(acc_view.df_exp_month_cat).abs().reset_index()
    df_act_exp = df_act_exp[df_act_exp['Combined'].isin(expenses)]

    EOM = df_act_exp['Date'].unique()[-1]
    EOM = datetime.strptime(str(EOM)[:10], '%Y-%m-%d')
    EOM = EOM.strftime('%Y-%m-%d')

    prev_EOM = df_act_exp['Date'].unique()[-2]
    prev_EOM = datetime.strptime(str(prev_EOM)[:10], '%Y-%m-%d')
    prev_EOM = prev_EOM.strftime('%Y-%m-%d')

    act_exp = df_act_exp[df_act_exp['Date'] == EOM]
    prev_act_exp = df_act_exp[df_act_exp['Date'] == prev_EOM]

    df_combined_act = pd.merge(df_bdgt_exp, act_exp, on='Combined', how='inner')
    if type == 'FIX':
        df_combined_act = df_combined_act[df_combined_act['sum'] != 0.0]

    return df_combined_act['sum'].sum(), prev_act_exp['sum'].sum(), df_combined_act['Amount'].sum()


def update_datatable(acc_view, start_date, end_date, categories, accounts):
    start_date_string, end_date_string = convert_picker_dates(start_date, end_date)

    df_sub = copy.deepcopy(acc_view.df_exp)
    df_sub = df_sub[(df_sub['Date'] >= start_date_string) & (df_sub['Date'] <= end_date_string)
                    & df_sub['Category'].isin(categories)
                    & df_sub['Source'].isin(accounts)].sort_values(by=['Date'], ascending=False).reset_index(drop=True)
    return df_sub.round(2)


def update_p3_table_df(av, start_date_string, end_date_string, categories, mode):
    df_sub = copy.deepcopy(av.df_exp)

    if mode == 'MULTI':
        df_sub = df_sub[(df_sub['Date'] >= start_date_string) & (df_sub['Date'] <= end_date_string) &
                        df_sub['Category'].isin(categories)].sort_values(by=['Category', 'Date']).reset_index(drop=True)
    else:
        df_sub = df_sub[(df_sub['Date'] >= start_date_string) & (df_sub['Date'] <= end_date_string) &
                        df_sub['Category'].isin([categories])].sort_values(by=['Date']).reset_index(drop=True)
    return df_sub.to_dict("rows")
