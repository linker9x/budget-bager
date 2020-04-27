import os
import pandas as pd

import budget_badger.classifier.expense_classifier as ec

class DataProcessor(object):

    def __init__(self):
        self.pnc = None
        self.chase = None
        self.amazon = None

    def __str__(self):
        return 'PNC: {}\nCHASE: {}\nAMAZON:{}\n'.format(self.pnc, self.chase, self.amazon)

    def load_pnc_csv(self):
        pnc_df = pd.DataFrame()
        for file in os.listdir('../statements/PNC/'):
            if file.endswith(".csv"):
                filepath = '../statements/PNC/' + file
                temp_df = pd.read_csv(filepath)
                if pnc_df.empty:
                    pnc_df = temp_df
                else:
                    pnc_df = pd.concat([pnc_df, temp_df], sort=False)

        pnc_df['Withdrawals'] = pnc_df['Withdrawals'].str.replace(',', '').str.replace('$', '').astype(float)
        pnc_df['Deposits'] = pnc_df['Deposits'].str.replace(',', '').str.replace('$', '').astype(float)
        pnc_df = pnc_df.fillna(0)
        pnc_df['Amount'] = pnc_df.apply(lambda row: row.Deposits - row.Withdrawals, axis=1)
        pnc_df.drop(pnc_df[['Withdrawals', 'Deposits', 'Balance']], axis=1, inplace=True)
        pnc_df.reset_index(inplace=True, drop=True)

        pnc_df['Category'] = ec.classify_df(pnc_df)

        pnc_df.info()
        pnc_df.to_csv('../statements/PNC/clf/PNC_new.csv', index=False)
        print(pnc_df)

    def load_chase_csv(self):
        chase_df = pd.DataFrame()
        for file in os.listdir('../statements/Chase/'):
            if file.endswith(".csv"):
                filepath = '../statements/Chase/' + file
                temp_df = pd.read_csv(filepath)
                if chase_df.empty:
                    chase_df = temp_df
                else:
                    chase_df = pd.concat([chase_df, temp_df], sort=False)

        chase_df = chase_df.fillna(0)
        chase_df.drop(chase_df[['Post Date', 'Category', 'Type']], axis=1, inplace=True)
        chase_df.rename(columns={'Transaction Date': 'Date'}, inplace=True)
        chase_df.reset_index(inplace=True, drop=True)

        chase_df['Category'] = ec.classify_df(chase_df)

        chase_df.info()

        chase_df.to_csv('../statements/Chase/clf/Chase_new.csv', index=False)
        print(chase_df)

    def load_amazon_csv(self):
        amzn_df = pd.DataFrame()
        for file in os.listdir('../statements/Amazon/'):
            if file.endswith(".csv"):
                filepath = '../statements/Amazon/' + file
                temp_df = pd.read_csv(filepath)
                if amzn_df.empty:
                    amzn_df = temp_df
                else:
                    amzn_df = pd.concat([amzn_df, temp_df], sort=False)

        amzn_df.reset_index(inplace=True, drop=True)
        print(amzn_df)

    # # find the rows with deposits
# indexNames = pnc[pnc['Withdrawals'].isnull()].index
#
# # separate DF for deposits
# pnc_deposits = pnc.loc[indexNames]
# # remove from withdrawals
# pnc.drop(indexNames, axis=0, inplace=True)
#
# # rename amount col
# pnc.rename(columns={'Withdrawals': 'Amount'}, inplace=True)
# pnc_deposits.rename(columns={'Deposits': 'Amount'}, inplace=True)
# # drop unnecessary cols
# pnc.drop(['Deposits', 'Balance'], axis=1, inplace=True)
# pnc_deposits.drop(['Withdrawals', 'Balance'], axis=1, inplace=True)
#
# # drop unnecessary cols, move category to end and rename 'Trans Date'
# chase.drop(['Post Date', 'Type'], axis=1, inplace=True)
# chase['Category'] = chase.pop('Category')
# chase.rename(columns={'Transaction Date': 'Date'}, inplace=True)
#
# # find the rows with deposits
# indexNames = chase[chase['Amount'] > 0].index
#
# # separate DF for deposits
# chase_payments = chase.loc[indexNames]
# # remove from withdrawals
# chase.drop(indexNames, axis=0, inplace=True)
#
# # abs of amount
# chase['Amount'] = chase['Amount'].abs()
#
# pnc.head()
#
# chase.head()
