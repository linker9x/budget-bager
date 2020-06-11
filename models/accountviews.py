from models.accounts.checking_account import PNCAccount
from models.accounts.credit_account import ChaseAccount
import pandas as pd


class AccountViews:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        self.checking = PNCAccount('./exp_data/PNC', start_date, end_date)
        self.credit = [ChaseAccount('./exp_data/Chase', start_date, end_date)]

        self.fix_exp = []                       # list of FIX expense labels
        self.var_exp = []                       # list of VAR expense labels

        self.df_exp = pd.DataFrame()            # debit entries between start and end
        self.df_inc = pd.DataFrame()            # credit entries between start and end

        self.df_fix_exp = pd.DataFrame()        # FIX exp between start and end
        self.df_var_exp = pd.DataFrame()        # VAR exp between start and end

        self.df_var_exp_month = pd.DataFrame()  # sum, avg and std of VAR exp grouped by month
        self.df_fix_exp_month = pd.DataFrame()  # sum, avg and std of FIX exp grouped by month

        self.df_exp_month_cat = pd.DataFrame()  # sum, avg and std of exp grouped by month and cat
        self.df_inc_month_cat = pd.DataFrame()  # sum, avg and std of inc grouped by month and cat

        self.df_rec_items = pd.DataFrame()      # problems

        self._reconcile()

        # set all attributes
        self._set_fix_var_exp()
        self._filter_exp_inc()
        self._filter_fix_var_exp()
        self._filter_fix_var_exp_month()
        self._filter_exp_inc_month_cat()

        # print(self.df_exp)
        # print(self.df_inc)
        # print(self.df_fix_exp)
        # print(self.df_var_exp)
        # print(self.df_var_exp_month)
        # print(self.df_fix_exp_month)
        # print(self.df_exp_month_cat)
        # print(self.df_inc_month_cat)

    def __str__(self):
        return 'Start: {}, End: {}\n' \
               'Fix: {}\n' \
               'Var: {}\n' \
               'Filters: {}\n' \
               'Rec Items:\n{}'.format(self.start_date,
                                      self.end_date,
                                      self.fix_exp,
                                      self.var_exp,
                                      {'df_exp': self.df_exp.empty,
                                       'df_inc': self.df_inc.empty,
                                       'df_fix_exp': self.df_fix_exp.empty,
                                       'df_var_exp': self.df_var_exp.empty,
                                       'df_var_exp_month': self.df_var_exp_month.empty,
                                       'df_fix_exp_month': self.df_fix_exp_month.empty,
                                       'df_exp_month_cat': self.df_exp_month_cat.empty,
                                       'df_inc_month_cat': self.df_inc_month_cat.empty},
                                      self.df_rec_items
                                      )

    def _set_fix_var_exp(self):
        df_budget = pd.read_csv('./exp_data/budgeted_amts.csv')
        df_budget['Combined'] = df_budget['Category'] + ' ' + df_budget['Subcategory']

        self.fix_exp = list(df_budget[df_budget['Type'] == 'FIX']['Combined'].unique())
        self.var_exp = list(df_budget[df_budget['Type'] == 'VAR']['Combined'].unique())

        self._check_exp_labels()

    def _check_exp_labels(self):
        df_chk = self.checking.get_debits()
        df_crdt = self.credit[0].get_debits()

        labels = self.fix_exp\
                 + self.var_exp\
                 + ['SAVINGS SAVINGS', 'PAYMENT PAYMENT', 'FEE FEE']
        labels = set(labels)

        if len(set(df_chk['Combined'].unique()) - labels) != 0:
            raise Exception('Checking expenses mislabeled.')

        if len(set(df_crdt['Combined'].unique()) - labels):
            raise Exception('Credit expenses mislabeled.')

    def _filter_exp_inc(self):
        self.df_exp = pd.concat([self.checking.get_debits(), self.credit[0].get_debits()])
        self.df_inc = pd.concat([self.checking.get_credits(), self.credit[0].get_credits()])

    def _filter_fix_var_exp(self):
        self.df_fix_exp = self.df_exp[self.df_exp['Combined'].isin(self.fix_exp)]
        self.df_var_exp = self.df_exp[self.df_exp['Combined'].isin(self.var_exp)]

    def _filter_fix_var_exp_month(self):
        self.df_fix_exp_month = self.df_fix_exp.groupby([pd.Grouper(key='Date', freq='M')])['Amount'].agg(
            ['sum',
             'mean',
             'std']).round(2)
        self.df_var_exp_month = self.df_var_exp.groupby([pd.Grouper(key='Date', freq='M')])['Amount'].agg(
            ['sum',
             'mean',
             'std']).round(2)

    def _filter_exp_inc_month_cat(self):
        self.df_exp_month_cat = self.df_exp.groupby(['Combined',
                                                     pd.Grouper(key='Date', freq='M')])['Amount'].agg(
            ['sum',
             'mean',
             'std'])
        self.df_exp_month_cat = self.df_exp_month_cat.unstack(fill_value=0).round(2).stack()

        self.df_inc_month_cat = self.df_inc.groupby(['Combined',
                                                     pd.Grouper(key='Date', freq='M')])['Amount'].agg(
            ['sum',
             'mean',
             'std'])
        self.df_inc_month_cat = self.df_inc_month_cat.unstack(fill_value=0).round(2).stack()

    def _reconcile(self):
        # Payments reflected on Chase statements
        df_chase_pymnt = self.credit[0].get_credits()
        df_chase_pymnt = df_chase_pymnt[df_chase_pymnt['Category'] == 'PAYMENT']
        df_chase_pymnt = df_chase_pymnt.filter(['ID', 'Amount']).reset_index(drop=True)

        # Returns on Chase statements
        df_chase_other = self.credit[0].get_credits()
        df_chase_other = df_chase_other[df_chase_other['Category'] != 'PAYMENT']
        df_chase_other = df_chase_other.filter(['ID', 'Amount']).reset_index(drop=True)

        # Agg expenses from Chase statements by payment ID
        df_chase_chrg = self.credit[0].get_debits()
        df_chase_chrg = df_chase_chrg.groupby(['ID'])['Amount'].agg(['sum']).reset_index()

        # Merge three to confirm that expenses are covered by payments or returns !!!
        df_rec = pd.merge(df_chase_pymnt, df_chase_chrg, how='outer', on='ID')
        df_rec = pd.merge(df_rec, df_chase_other, how='outer', on='ID', suffixes=('_pymnt', '_other')).fillna(0)
        df_rec['abs_diff'] = df_rec['Amount_pymnt'] + df_rec['sum'] + df_rec['Amount_other']
        df_rec['abs_diff'] = df_rec['abs_diff'].abs()
        df_rec = df_rec[df_rec['abs_diff'] > 0.0001].round(2)

        # Payments to Chase reflected on PNC statements
        df_pnc_pymnt = self.checking.get_debits()
        df_pnc_pymnt = df_pnc_pymnt[df_pnc_pymnt['Category'] == 'PAYMENT']
        df_pnc_pymnt = df_pnc_pymnt.filter(['Date', 'Amount']).reset_index(drop=True)
        df_pnc_pymnt['Amount'] = df_pnc_pymnt['Amount'].abs()

        # Merge Payments reflected on Chase and PNC Statements to confirm they match ***
        df_payments = pd.merge(df_chase_pymnt, df_pnc_pymnt, how='outer', on='Amount', indicator=True)
        df_payments = df_payments[df_payments['_merge'] != 'both']
        df_payments.drop('_merge', axis=1, inplace=True)

        # Merge !!! and *** to try and reconcile the issues. This should resolve most timing problems.
        df_final = pd.merge(df_payments,
                            df_rec,
                            how='outer',
                            left_on='Amount',
                            right_on='abs_diff',
                            suffixes=('_PNC', '_Chase'),
                            indicator=True).round(2)
        df_final = df_final[df_final['_merge'] != 'both']

        self.df_rec_items = df_final
