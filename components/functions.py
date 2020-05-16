import pandas as pd
from datetime import datetime
import copy

df_pnc = pd.read_csv('./data/PNC_12M.csv')
df_chase = pd.read_csv('./data/Chase_12M.csv')
df = pd.concat([df_pnc, df_chase]).reset_index(drop=True).sort_values(by=['Date'])
df['Date'] = pd.to_datetime(df['Date'])

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
                    & df_sub['Source'].isin(accounts)].reset_index().sort_values(by=['Date'])
    return df_sub.to_dict("rows")
