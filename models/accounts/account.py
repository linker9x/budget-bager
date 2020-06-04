import os
import sys
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))

import pandas as pd
import datetime
from dateutil.relativedelta import *


class Account:

    def __init__(self, name, type, filepath, start_date, end_date):
        self.name = name
        self.type = type
        self.filepath = filepath
        self.start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        self.credits = None
        self.debits = None

        self.load_entries()

    def __str__(self):
        return 'Name: {}, Type: {}, Start Date: {}, End Date: {}'.format(self.name,
                                                                         self.type,
                                                                         self.start_date,
                                                                         self.end_date)

    def load_entries(self):
        bl_filepath = self.filepath + '/statements'
        cnt_months = self.end_date.month - self.start_date.month
        credit_frames = []
        debit_frames = []

        for i in range(cnt_months + 1):
            mon_year = self.start_date + relativedelta(months=i)
            statement_name = '/' + mon_year.strftime('%m_%Y') + '.csv'
            df_statement = pd.read_csv(bl_filepath + statement_name)
            credit_frames.append(df_statement[df_statement['Amount'] >= 0])
            debit_frames.append(df_statement[df_statement['Amount'] < 0])

        self.credits = pd.concat(credit_frames).reset_index(drop=True)
        self.debits = pd.concat(debit_frames).reset_index(drop=True)

        # print('Credit')
        # print(self.credits)
        # print('Debit')
        # print(self.debits)

        # for file in os.listdir(bl_filepath):
        #     print(file)

        # if os.path.isfile(bl_filepath):
        #     df_balance = pd.read_csv(bl_filepath)
        #     df_balance['Date'] = pd.to_datetime(df_balance['Date'])
        #
        #     self.balance_log = df_balance

    def get_credits(self):
        return self.credits

    def get_debits(self):
        return self.debits
