import os
import sys
from datetime import date, datetime, timedelta, time
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))

import pandas as pd
import numpy as np
import data_processing.classifier.expense_classifier as ec
import data_processing.data_processor as dp

classified_exp = './classifier/trained_clf/data/classified_exp.csv'

if __name__ == "__main__":
    # exp_df = pd.read_csv(classified_exp)
    # print("Expense Data Shape: {}".format(exp_df.shape))
    # print("Expense Value Counts: \n{}".format(exp_df['Category'].value_counts()))
    # result = ec.classify_expenses(exp_df)
    # ec.read_write_classifier('./classifier/trained_clf/classifier' + datetime.today().strftime('%y_%m_%d_%H%M%S') + '.sav',
    #                          result, write=True)

    data = dp.DataProcessor()
    # data.load_pnc_csv()
    data.load_chase_csv()
    # data.load_amazon_csv()
