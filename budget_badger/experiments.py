import os
import sys
from datetime import date, datetime, timedelta, time
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))

import pandas as pd
import numpy as np
import budget_badger.classifier.expense_classifier as ec
import budget_badger.data_processor as dp

classified_exp = '../data/classified_exp.csv'

if __name__ == "__main__":
    # exp_df = pd.read_csv(classified_exp)
    # print("Expense Data Shape: {}".format(exp_df.shape))
    # print("Expense Value Counts: \n{}".format(exp_df['Category'].value_counts()))
    # result = ec.classify_expenses(exp_df)
    # ec.read_write_classifier('./trained_clf/classifier' + datetime.today().strftime('%y_%m_%d_%H%M%S') + '.sav', result, write=True)

    # pnc_df = pd.read_csv('../statements/Chase/clf/Chase_new.csv')
    # result = ec.classify_df(pnc_df)
    #
    # result.to_csv('./result_' + datetime.today().strftime('%y_%m_%d_%H%M%S') + '.csv', index=False)

    data = dp.DataProcessor()
    data.load_pnc_csv()
    # data.load_chase_csv()
    # data.load_amazon_csv()
