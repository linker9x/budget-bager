from models.accounts.checking_account import PNCAccount
from models.accounts.credit_account import ChaseAccount
import pandas as pd
import copy


class AccountViews:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        self.fix_exp = []  # list of FIX expense labels
        self.var_exp = []  # list of VAR expense labels
        self._set_fix_var_exp()

        self.checking = None
        self.credit = []

        self.df_exp = pd.DataFrame()            # debit entries between start and end
        self.df_inc = pd.DataFrame()            # credit entries between start and end
        self.df_fix_exp = pd.DataFrame()        # FIX exp between start and end
        self.df_var_exp = pd.DataFrame()        # VAR exp between start and end
        self.df_var_exp_month = pd.DataFrame()  # sum, avg and std of VAR exp grouped by month
        self.df_fix_exp_month = pd.DataFrame()  # sum, avg and std of FIX exp grouped by month
        self.df_exp_month_cat = pd.DataFrame()  # sum, avg and std of exp grouped by month and cat
        self.df_inc_month_cat = pd.DataFrame()  # sum, avg and std of inc grouped by month and cat
        self.update_views()


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
               'Filters: {}\n'.format(self.start_date,
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
                                       'df_inc_month_cat': self.df_inc_month_cat.empty}
                                      )

    def set_start_end_date(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def update_views(self):
        self.checking = PNCAccount('./exp_data/PNC', self.start_date, self.end_date)
        self.credit = [ChaseAccount('./exp_data/Chase', self.start_date, self.end_date)]
        print('self start:{} self end:{}'.format(self.start_date, self.end_date))
        self._check_exp_labels()

        self._filter_exp_inc()
        self._filter_fix_var_exp()
        self._filter_fix_var_exp_month()
        self._filter_exp_inc_month_cat()

    def _set_fix_var_exp(self):
        df_budget = pd.read_csv('./exp_data/budgeted_amts.csv')
        df_budget['Combined'] = df_budget['Category'] + ' ' + df_budget['Subcategory']

        self.fix_exp = list(df_budget[df_budget['Type'] == 'FIX']['Combined'].unique())
        self.var_exp = list(df_budget[df_budget['Type'] == 'VAR']['Combined'].unique())

    def _check_exp_labels(self):
        df_chk = self.checking.get_debits()
        df_crdt = self.credit[0].get_debits()

        labels = self.fix_exp\
                 + self.var_exp\
                 + ['SAVINGS SAVINGS', 'PAYMENT PAYMENT', 'FEE FEE']
        labels = set(labels)

        if len(set(df_chk['Combined'].unique()) - labels) != 0:
            print(set(df_chk['Combined'].unique()) - labels)
            raise Exception('Checking expenses mislabeled.')

        if len(set(df_crdt['Combined'].unique()) - labels) != 0:
            print(set(df_crdt['Combined'].unique()) - labels)
            raise Exception('Credit expenses mislabeled.')

    def _filter_exp_inc(self):
        df_bs = copy.deepcopy(self.checking.get_debits())
        df_cs = copy.deepcopy(self.credit[0].get_debits())

        refunds = copy.deepcopy(self.credit[0].get_credits())
        refunds = refunds[refunds['Category'] != 'PAYMENT']

        bs_ids = set(df_bs[df_bs['Category'] == 'PAYMENT']['ID'].to_list())
        cs_ids = set(df_cs['ID'].unique())

        if len(bs_ids - cs_ids) != 0:
            raise Exception('Missing Payment ID.')

        balance = df_bs[df_bs['Category'] == 'PAYMENT'][['ID', 'Amount', 'Date']].reset_index(drop=True)
        credit = df_cs[df_cs['ID'].isin(bs_ids)].groupby('ID').sum().reset_index()
        
        comp = pd.merge(balance, credit, on='ID', suffixes=('_bal', '_crd')).round(2)
        comp = pd.merge(comp, refunds[['ID', 'Amount']], on='ID')
        comp['Amount_crd'] = (comp['Amount_crd'] + comp['Amount']).round(2)

        issues = comp[comp['Amount_bal'] != comp['Amount_crd']]
        if not issues.empty:
            raise Exception(issues)

        df_cs_pay_date = pd.merge(df_cs, balance[['ID', 'Date']], on='ID', how='left', suffixes=('_old', ''))
        df_cs_pay_date.drop('Date_old', axis=1, inplace=True)

        df_exp_tmp = pd.concat([df_bs[~df_bs['Category'].isin(['PAYMENT', 'SAVINGS'])],
                                 df_cs_pay_date[df_cs_pay_date['ID'].isin(bs_ids)]])
        df_inc_tmp = pd.concat([self.checking.get_credits(), refunds])

        self.df_exp = df_exp_tmp[(df_exp_tmp['Date'] >= self.start_date) & (df_exp_tmp['Date'] <= self.end_date)]
        self.df_inc = df_inc_tmp[(df_inc_tmp['Date'] >= self.start_date) & (df_inc_tmp['Date'] <= self.end_date)]

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
