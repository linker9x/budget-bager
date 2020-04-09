import os
import sys
from datetime import date, datetime, timedelta, time
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))

import pandas as pd
import numpy as np
import budget_badger.classifier.expense_classifier as ec

classified_exp = '../data/classified_exp.csv'

if __name__ == "__main__":
    exp_df = pd.read_csv(classified_exp)
    print("Expense Data Shape: {}".format(exp_df.shape))
    print("Expense Value Counts: \n{}".format(exp_df['Category'].value_counts()))
    #result = ec.classify_expenses(exp_df)
    #ec.read_write_classifier('./classifier.sav', result, write=True)

    loaded_pipe = ec.read_write_classifier('./classifier_09042020.sav')

    predicted = loaded_pipe.predict(np.array(exp_df['Description']))

    frame = {'Descrip': np.array(exp_df['Description']), 'Prediction': predicted}
    result = pd.DataFrame(frame)

    result.to_csv('./result.csv', index=False)

