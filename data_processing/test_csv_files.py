import pandas as pd
import os
stmnt_filepath = '../exp_data/'

if __name__ == "__main__":
    CHASE_set_combined = set()
    PNC_set_combined = set()
    for file in os.listdir(stmnt_filepath + 'Chase/statements/'):
        if file.endswith(".csv"):
            filepath = stmnt_filepath + 'Chase/statements/' + file
            chase_df = pd.read_csv(filepath)

            chase_df['combined'] = chase_df['Category'] + '-' + chase_df['Subcategory']

            values = list(chase_df['combined'].unique())
            CHASE_set_combined.update(values)

    for file in os.listdir(stmnt_filepath + 'PNC/statements/'):
        if file.endswith(".csv"):
            filepath = stmnt_filepath + 'PNC/statements/' + file
            chase_df = pd.read_csv(filepath)

            chase_df['combined'] = chase_df['Category'] + '-' + chase_df['Subcategory']

            values = list(chase_df['combined'].unique())
            PNC_set_combined.update(values)

    print(CHASE_set_combined)
    pd.DataFrame(CHASE_set_combined).to_csv('Chase_Cats.csv')
    print(PNC_set_combined)
    pd.DataFrame(PNC_set_combined).to_csv('PNC_Cats.csv')
