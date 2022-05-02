import csv
import pickle

from sklearn.neural_network import MLPRegressor
from sklearn.metrics import r2_score, explained_variance_score, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold

import numpy as np

from utilities import *

# CSV_NAME = "new_data.csv"
CSV_NAME = "values_normalized.csv"
MODEL_NAME = "model.p"
LOAD_MODEL = None
KFOLD = None
HYPERPARAMS = {
    "hidden_layer_size": [20] * 10,
}


def read_data():
    """Read data from csv"""
    X = []
    y = []
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)

        training_fields = set(csv_reader.fieldnames) - {"tas"}
        for row in csv_reader:
            # Remove rows which are missing values for any variable
            empty_fields = [f for f in row if row[f] == ""]
            if empty_fields:
                continue
            features = {k: float(v) for k, v in row.items() if k in training_fields}
            X.append(features)
            y.append(float(row["tas"]))

    return np.array(X), np.array(y)


def cross_val(X, y):
    """Split into several train/test sets for cross-validation."""
    kf = KFold(n_splits=5, shuffle=False).split(X, y)
    return kf

def split_data(X, y):
    """Simple split into train and test sets. No cross-validation."""
    ## Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, shuffle=True)
    return X_train, X_test, y_train, y_test

def strip_days(X_train, X_test, y_train, y_test):
    """Separate out the days variable into its own arrays.
    
    Called after splitting X and y into X_train, X_test, y_train, y_test.
    """
    y_train = np.array(y_train, dtype=np.double)
    y_test = np.array(y_test, dtype=np.double)
    days_test = np.array([row["day"] for row in X_test], dtype=np.double)
    days_train = np.array([row["day"] for row in X_train], dtype=np.double)
    X_train = np.array([[v for k, v in row.items() if k != "day"] for row in X_train], dtype=np.double)
    X_test = np.array([[v for k, v in row.items() if k != "day"] for row in X_test], dtype=np.double)
    return X_train, X_test, y_train, y_test, days_train, days_test


def save_model(name, *args):
    ## Save model
    with open(name, "wb") as f:
        pickle.dump(args, f)

def load_model():
    with open(MODEL_NAME, "rb") as f:
        return pickle.load(f)


def train_net(X_train, y_train):
    clf = MLPRegressor(verbose=True, hidden_layer_sizes=HYPERPARAMS["hidden_layer_size"], tol=1e-10)
    clf.fit(X_train, y_train)
    return clf


def get_data():
    if LOAD_MODEL and KFOLD:
        raise RuntimeError("Must regen model to do cross validation -- cannot LOAD_MODEL")

    if LOAD_MODEL:
        return load_model()

    X, y = read_data()
    if not KFOLD:
        return strip_days(*split_data(X, y))

    for fold_num, (train_ind, test_ind) in enumerate(cross_val(X, y)):
        X_train, X_test, y_train, y_test = X[train_ind], X[test_ind], y[train_ind], y[test_ind]
        X_train, X_test, y_train, y_test, days_train, days_test = strip_days(X_train, X_test, y_train, y_test)

        clf = train_net(X_train, y_train)
        save_model(f"model k{fold_num}.p", clf, X, y, X_train, X_test, y_train, y_test, days_train, days_test)
    
        yield clf, X, y, X_train, X_test, y_train, y_test, days_train, days_test


def predict(clf, X_test, y_test):
    y_pred = clf.predict(X_test)
    print("r2_score: ", r2_score(y_test, y_pred))
    print("explained_variance_score: ", explained_variance_score(y_test, y_pred))
    print("mean_squared_error: ", mean_squared_error(y_test, y_pred))
    return y_pred


def plot(y_test, days_test, y_pred):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.scatter(days_test, y_test, c='#1f77b4', s=3, alpha=.1, label='Actual')
    xyears = np.array([int(get_date_from_offset(int(r), output_format="%Y")) for r in days_test])
    xticks = np.arange(0, len(days_test), step=365*3)
    yticks = np.arange(np.min(y_test), np.max(y_test), step=0.1)
    ytemps = [round(unnormalize(yt), 2) for yt in yticks]
    plt.xticks(np.sort(days_test)[xticks], xyears[xticks])
    plt.yticks(yticks, ytemps)

    ## Trend line
    # z = np.polyfit(days_test, y_test, 1)
    # p = np.poly1d(z)
    # ax.plot(days_test,p(days_test),"r--")

    ax.scatter(days_test, y_pred, s=3, alpha=.1, c='#ff7f0e', label='Predicted')
    ax.legend(labelcolor=('#1f77b4', '#ff7f0e'))

    plt.title("Global Average Surface Temperature")
    plt.ylabel("Global Average Surface Temp K")
    plt.xlabel("Year")
    fig.canvas.draw()
    fig.canvas.flush_events()


if __name__ == "__main__":
    LOAD_MODEL = False
    KFOLD = True
    for clf, X, y, X_train, X_test, y_train, y_test, days_train, days_test in get_data():
        y_pred = predict(clf, X_test, y_test)
        plot(y_test, days_test, y_pred)