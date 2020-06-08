import os
import sys
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))

from spacy.lang.en import English
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

import pickle
stmnt_filepath = '../exp_data/'


# tokenize the text from the description field
def spacy_tokenizer(descrip):

    # parser for the description field
    parser = English()
    mytokens = parser(descrip)
    mytokens = [word.lower_ for word in mytokens]
    return mytokens


def classify_expenses(df):
    X_cat = df['Description']
    ylabels_cat = df['Category']
    X_train_cat, X_test_cat, y_train_cat, y_test_cat = train_test_split(X_cat, ylabels_cat, test_size=0.1)

    X_scat = df['Description'] + ' ' + df['Category']
    ylabels_scat = df['Subcategory']
    X_train_scat, X_test_scat, y_train_scat, y_test_scat = train_test_split(X_scat, ylabels_scat, test_size=0.1)

    bow_vector = CountVectorizer(tokenizer=spacy_tokenizer, ngram_range=(1, 2))
    # tfidf_vector = TfidfVectorizer(tokenizer=spacy_tokenizer)
    classifier = LogisticRegression(solver='lbfgs', multi_class='auto')

    # Create Category Pipe
    pipe_cat = Pipeline([('vectorizer', bow_vector),
                         ('classifier', classifier)])
    pipe_cat.fit(X_train_cat, y_train_cat)
    predicted_cat = pipe_cat.predict(X_test_cat)

    # Create Subcategory Pipe
    pipe_scat = Pipeline([('vectorizer', bow_vector),
                          ('classifier', classifier)])
    pipe_scat.fit(X_train_scat, y_train_scat)
    predicted_scat = pipe_scat.predict(X_test_scat)

    print("CATEGORY\n"
          "Accuracy: {}\n"
          "F1 Score: {}\n".format(metrics.accuracy_score(y_test_cat, predicted_cat),
                                  metrics.f1_score(y_test_cat, predicted_cat, average='weighted')))

    print("SUBCATEGORY\n"
          "Accuracy: {}\n"
          "F1 Score: {}\n".format(metrics.accuracy_score(y_test_scat, predicted_scat),
                                  metrics.f1_score(y_test_scat, predicted_scat, average='weighted')))

    # param_grid = [
    #     {'classifier': [LogisticRegression()],
    #      'classifier__penalty': ['l2'],
    #      'classifier__C': np.logspace(-4, 4, 20),
    #      'classifier__solver': ['liblinear', 'saga', 'lbfgs']},
    # ]
    #
    # # Create grid search object
    #
    # clf = GridSearchCV(pipe, param_grid=param_grid, cv=5, verbose=True, n_jobs=-1)
    #
    # # Fit on data
    #
    # best_clf = clf.fit(X_train, y_train)
    # predicted = best_clf.predict(X_test)

    return pipe_cat, pipe_scat


def read_write_classifier(filename, pipe=None, write=False):
    if write:
        pickle.dump(pipe, open(filename, 'wb'))
    else:
        return pickle.load(open(filename, 'rb'))


def classify_df(exp_df, type='Category'):
    if type == 'Category':
        loaded_pipe = read_write_classifier('./trained_clf/classifier_1_cat.sav')
    else:
        loaded_pipe = read_write_classifier('./trained_clf/classifier_1_scat.sav')
    predicted = loaded_pipe.predict(np.array(exp_df['Description']))
    frame = {'Descrip': np.array(exp_df['Description']), type: predicted}
    result = pd.DataFrame(frame)
    return result[type]


def classify_pnc_files():
    for file in os.listdir(stmnt_filepath + 'PNC/statements/'):
        if file.endswith(".csv"):
            filepath = stmnt_filepath + 'PNC/statements/' + file
            pnc_df = pd.read_csv(filepath)

            if 'Subcategory' not in pnc_df.columns:
                print('Classifying file {}'.format(filepath))
                pnc_df['Withdrawals'] = pnc_df['Withdrawals'].str.replace(',', '').str.replace('$', '').astype(
                    float)
                pnc_df['Deposits'] = pnc_df['Deposits'].str.replace(',', '').str.replace('$', '').astype(float)
                pnc_df = pnc_df.fillna(0)
                pnc_df['Amount'] = pnc_df.apply(lambda row: row.Deposits - row.Withdrawals, axis=1)
                pnc_df.drop(pnc_df[['Withdrawals', 'Deposits', 'Balance']], axis=1, inplace=True)
                pnc_df.reset_index(inplace=True, drop=True)

                pnc_df['Category'] = classify_df(pnc_df, type='Category')
                pnc_df['Subcategory'] = classify_df(pnc_df, type='Subcategory')

                pnc_df.info()
                pnc_df.to_csv(filepath, index=False)

            print('Classification of {} finished.'.format(filepath))


def classify_chase_files():
    for file in os.listdir(stmnt_filepath + 'Chase/statements/'):
        if file.endswith(".csv"):
            filepath = stmnt_filepath + 'Chase/statements/' + file
            chase_df = pd.read_csv(filepath)

            if 'Subcategory' not in chase_df.columns:
                print('Classifying file {}'.format(filepath))
                chase_df = chase_df.fillna(0)
                chase_df.drop(chase_df[['Post Date', 'Category', 'Type']], axis=1, inplace=True)
                chase_df.rename(columns={'Transaction Date': 'Date'}, inplace=True)
                chase_df.reset_index(inplace=True, drop=True)

                chase_df['Category'] = classify_df(chase_df, type='Category')
                chase_df['Subcategory'] = classify_df(chase_df, type='Subcategory')

                chase_df.info()
                chase_df.to_csv(filepath, index=False)

            print('Classification of {} finished.'.format(filepath))


# def load_amazon_csv(self):
#     amzn_df = pd.DataFrame()
#     for file in os.listdir('./statements/Amazon/'):
#         if file.endswith(".csv"):
#             filepath = './statements/Amazon/' + file
#             temp_df = pd.read_csv(filepath)
#             if amzn_df.empty:
#                 amzn_df = temp_df
#             else:
#                 amzn_df = pd.concat([amzn_df, temp_df], sort=False)
#
#     amzn_df.reset_index(inplace=True, drop=True)
#     print(amzn_df)