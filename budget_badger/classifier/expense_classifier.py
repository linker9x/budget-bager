import string
from spacy.lang.en import English
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

import pickle


# tokenize the text from the description field
def spacy_tokenizer(descrip):
    # parser for the description field
    parser = English()

    # parse the description
    mytokens = parser(descrip)

    # convert to lowercase
    mytokens = [word.lower_ for word in mytokens]

    # return preprocessed list of tokens
    return mytokens


class predictors(TransformerMixin):
    def transform(self, X, **transform_params):
        # Cleaning Text
        return [clean_text(text) for text in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}


def clean_text(text):
    return text.strip().lower()

def classify_expenses(df):
    # bow_vector = CountVectorizer(tokenizer = spacy_tokenizer, ngram_range=(1,1))
    tfidf_vector = TfidfVectorizer(tokenizer = spacy_tokenizer)

    X = df['Description'] # the features we want to analyze
    ylabels = df['Category'] # the labels, or answers, we want to test against

    X_train, X_test, y_train, y_test = train_test_split(X, ylabels, test_size=0.1)

    classifier = MLPClassifier(solver='lbfgs', activation='logistic')

    # Create pipeline using Bag of Words
    pipe = Pipeline([("cleaner", predictors()),
                     ('vectorizer', tfidf_vector),
                     ('classifier', classifier)])

    # model generation
    pipe.fit(X_train,y_train)

    # Predicting with a test dataset
    predicted = pipe.predict(X_test)

    print("Logistic Regression Accuracy:",metrics.accuracy_score(y_test, predicted))
    print("Logistic Regression Precision:",metrics.precision_score(y_test, predicted, average='weighted'))
    print("Logistic Regression Recall:",metrics.recall_score(y_test, predicted, average='weighted'))

    return pipe


def read_write_classifier(filename, pipe=None, write=False):
    if write:
        pickle.dump(pipe, open(filename, 'wb'))
    else:
        return pickle.load(open(filename, 'rb'))


# # find the rows with deposits
# indexNames = pnc[pnc['Withdrawals'].isnull()].index
#
# # separate DF for deposits
# pnc_deposits = pnc.loc[indexNames]
# # remove from withdrawals
# pnc.drop(indexNames, axis=0, inplace=True)
#
# # rename amount col
# pnc.rename(columns={'Withdrawals': 'Amount'}, inplace=True)
# pnc_deposits.rename(columns={'Deposits': 'Amount'}, inplace=True)
# # drop unnecessary cols
# pnc.drop(['Deposits', 'Balance'], axis=1, inplace=True)
# pnc_deposits.drop(['Withdrawals', 'Balance'], axis=1, inplace=True)
#
# # drop unnecessary cols, move category to end and rename 'Trans Date'
# chase.drop(['Post Date', 'Type'], axis=1, inplace=True)
# chase['Category'] = chase.pop('Category')
# chase.rename(columns={'Transaction Date': 'Date'}, inplace=True)
#
# # find the rows with deposits
# indexNames = chase[chase['Amount'] > 0].index
#
# # separate DF for deposits
# chase_payments = chase.loc[indexNames]
# # remove from withdrawals
# chase.drop(indexNames, axis=0, inplace=True)
#
# # abs of amount
# chase['Amount'] = chase['Amount'].abs()
#
# pnc.head()
#
# chase.head()
