import os
import sys
from datetime import date, datetime, timedelta, time
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))

import pandas as pd
#import budget_badger.classifier.expense_classifier as ec

classified_exp = '../data/classified_exp.csv'

if __name__ == "__main__":
    exp_df = pd.read_csv(classified_exp)
    print(exp_df.head())
