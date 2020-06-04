from models.accounts.account import Account
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))


class ChaseAccount(Account):
    def __init__(self, filepath, start_date, end_date):
        Account.__init__(self,
                         'Chase',
                         'Credit',
                         filepath,
                         start_date,
                         end_date)
        self.balance_log = None

        self.load_balance_log()

    def load_balance_log(self):
        bl_filepath = self.filepath + '/balance_log.csv'

        if os.path.isfile(bl_filepath):
            df_balance = pd.read_csv(bl_filepath)
            df_balance['Date'] = pd.to_datetime(df_balance['Date'])

            start_date_string = self.start_date.strftime('%Y-%m-%d')
            end_date_string = self.end_date.strftime('%Y-%m-%d')
            self.balance_log = df_balance[(df_balance['Date'] >= start_date_string)
                                          & (df_balance['Date'] <= end_date_string)].reset_index(drop=True)
