from models.accounts.checking_account import PNCAccount
from models.accounts.credit_account import ChaseAccount
import pandas as pd


class AccountViews:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        self.checking = PNCAccount('./exp_data/PNC', start_date, end_date)
        self.credit = [ChaseAccount('./exp_data/Chase', start_date, end_date)]

        self.fix_exp = []
        self.var_exp = []

        self.df_exp = pd.DataFrame()                      # entries between start and end
        self.df_inc = pd.DataFrame()

        self.df_exp_month_sum_avg_std = pd.DataFrame()    # sum, avg and std of exp grouped by month
        self.df_type_month_sum_avg_std = pd.DataFrame()   # sum, avg and std of exp grouped by month and type
        self.df_cat_month_sum_avg_std = pd.DataFrame()    # sum, avg and std of exp grouped by month and cat

        self.df_inc_month_sum_avg_std = pd.DataFrame()

        # throw error
        self._reconcile()

        # set all attributes
        self._set_fix_var_exp()
        self._filter_exp_inc()
        self._filter_exp_inc_month()
        self._filter_exp_month_type()
        self._filter_exp_month_cat()

    def __str__(self):
        return 'Start: {}, End: {}\nFix: {}\nVar: {}\nFilters: {}'.format(self.start_date,
                                                                          self.end_date,
                                                                          self.fix_exp,
                                                                          self.var_exp,
                                                                          [self.df_exp.empty,
                                                                           self.df_inc.empty,
                                                                           self.df_exp_month_sum_avg_std.empty,
                                                                           self.df_type_month_sum_avg_std.empty,
                                                                           self.df_cat_month_sum_avg_std.empty,
                                                                           self.df_inc_month_sum_avg_std.empty]
                                                                          )

    def _set_fix_var_exp(self):
        df_chk = self.checking.get_debits()
        df_crdt = self.credit[0].get_debits()
        print(df_chk[df_chk['Type'] == None])
        print(df_crdt)
        self.fix_exp = []
        self.var_exp = []

    def _filter_exp_inc(self):
        self.df_exp = pd.DataFrame()
        self.df_inc = pd.DataFrame()

    def _filter_exp_inc_month(self):
        self.df_exp_month_sum_avg_std = pd.DataFrame()
        self.df_inc_month_sum_avg_std = pd.DataFrame()

    def _filter_exp_month_type(self):
        self.df_type_month_sum_avg_std = pd.DataFrame()

    def _filter_exp_month_cat(self):
        self.df_cat_month_sum_avg_std = pd.DataFrame()

    def _reconcile(self):
        pass
