import os
import sys
from datetime import date, datetime, timedelta, time
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))

import pandas as pd
import numpy as np
import data_processing.expense_classifier as ec

classified_exp = './trained_clf/data/classified_exp.csv'

if __name__ == "__main__":
    ####
    #
    # CLASSIFIER
    #
    ####
    # exp_df = pd.read_csv(classified_exp)
    # result_cat, result_scat = ec.classify_expenses(exp_df)
    # ec.read_write_classifier('./trained_clf/classifier' +
    #                          datetime.today().strftime('%y_%m_%d_%H%M%S') +
    #                          '_cat.sav',
    #                          result_cat, write=True)
    # ec.read_write_classifier('./trained_clf/classifier' +
    #                          datetime.today().strftime('%y_%m_%d_%H%M%S') +
    #                          '_scat.sav',
    #                          result_scat, write=True)

    ####
    #
    # LABEL-ER
    #
    ####
    ec.classify_pnc_files()
    ec.classify_chase_files()
    # data.load_amazon_csv()
