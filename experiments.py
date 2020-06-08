from models.accounts.checking_account import PNCAccount
from models.accounts.credit_account import ChaseAccount
from models.accountviews import AccountViews
import os
import sys
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))
import pandas as pd
import numpy as np


if __name__ == "__main__":
    acc_views = AccountViews('2020-01-01', '2020-04-30')
    print(acc_views)
    # chk_acc = PNCAccount('./exp_data/PNC', '2020-01-01', '2020-04-30')
    # print('chk_acc')
    # print(chk_acc)
    # print('chk_acc.balance_log')
    # print(chk_acc.balance_log)
    # print('chk_acc.card_payments')
    # print(chk_acc.card_payments)
    #
    # crt_acc = ChaseAccount('./exp_data/Chase', '2020-02-01', '2020-04-30')
    # print('crt_acc')
    # print(crt_acc)
    # print('crt_acc.balance_log')
    # print(crt_acc.balance_log)
    # print('crt_credits')
    # print(crt_acc.get_credits())
    # print('crt_debits')
    # print(crt_acc.get_debits())
