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


# tokenize the text from the description field
def spacy_tokenizer(descrip):
    # parser for the description field
    parser = English()
    mytokens = parser(descrip)
    mytokens = [word.lower_ for word in mytokens]
    return mytokens


def classify_expenses(df):
    bow_vector = CountVectorizer(tokenizer=spacy_tokenizer, ngram_range=(1, 2))
    # tfidf_vector = TfidfVectorizer(tokenizer=spacy_tokenizer)
    X = df['Description']   # the features we want to analyze
    ylabels = df['Category']            # the labels, or answers, we want to test against

    X_train, X_test, y_train, y_test = train_test_split(X, ylabels, test_size=0.1)

    classifier = LogisticRegression(solver='lbfgs', multi_class='auto')

    # Create pipeline using tfidf
    pipe = Pipeline([('vectorizer', bow_vector),
                     ('classifier', classifier)])

    # model generation
    pipe.fit(X_train, y_train)

    # Predicting with a test dataset
    predicted = pipe.predict(X_test)

    print("Logistic Regression Accuracy:", metrics.accuracy_score(y_test, predicted))
    print("Logistic Regression Precision:", metrics.precision_score(y_test, predicted, average='weighted'))
    print("Logistic Regression Recall:", metrics.recall_score(y_test, predicted, average='weighted'))

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
    # print("Logistic Regression Accuracy:", metrics.accuracy_score(y_test, predicted))
    # print("Logistic Regression Precision:", metrics.precision_score(y_test, predicted, average='weighted'))
    # print("Logistic Regression Recall:", metrics.recall_score(y_test, predicted, average='weighted'))

    return pipe


def read_write_classifier(filename, pipe=None, write=False):
    if write:
        pickle.dump(pipe, open(filename, 'wb'))
    else:
        return pickle.load(open(filename, 'rb'))


def classify_df(exp_df):
    loaded_pipe = read_write_classifier('./classifier/trained_clf/classifier_1.sav')
    # print(loaded_pipe.best_estimator_)
    predicted = loaded_pipe.predict(np.array(exp_df['Description']))
    frame = {'Descrip': np.array(exp_df['Description']), 'Category': predicted}
    result = pd.DataFrame(frame)
    return result['Category']

