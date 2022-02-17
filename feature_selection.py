# %%
from tkinter import Y
from matplotlib import pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import mutual_info_classif
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, recall_score


# %%
data = pd.read_csv(
    "/Users/julesbressan/Documents/GitHub/Enea_Task/processed_data.csv",
    index_col=["ACCIDENT_NO", "VEHICLE_ID", "PERSON_ID",],
    low_memory=False,
)
data = data.drop(columns=["Lat", "Long", "ACCIDENTTIME", "ACCIDENTDATE"])
TARGET = "INJ_LEVEL"
ORDINAL_FEATURRES = ["AGE", TARGET, "SPEED_ZONE", "TARE_WEIGHT"]
CATEGORICAL_FEATURES = [
    column for column in data.columns if column not in ORDINAL_FEATURRES
]
data.loc[:, TARGET] = data[TARGET].apply(lambda x: 1 - int(x > 2.5))
# %%
def set_dtypes(data: pd.DataFrame) -> pd.DataFrame:
    dtypes = {}

    for column in data.columns:
        if column in ORDINAL_FEATURRES:
            dtypes[column] = "int64"
        else:
            dtypes[column] = "string"

    return data.astype(dtypes)


#%%
def encode_data(data: pd.DataFrame) -> pd.DataFrame:
    encoded_data = data
    for column in CATEGORICAL_FEATURES:
        dummies = pd.get_dummies(data[column], prefix=column)
        encoded_data = pd.merge(
            left=encoded_data, right=dummies, left_index=True, right_index=True,
        )
        encoded_data = encoded_data.drop(columns=column)

    encoded_data = encoded_data[
        [column for column in encoded_data.columns if column != TARGET] + [TARGET]
    ]
    return encoded_data


#%%
def split_input_tragets(data: pd.DataFrame) -> pd.DataFrame:

    X = data.drop(columns=[TARGET]).values
    y = data[TARGET].values
    return X, y


# %%
def prepare_data(data: pd.DataFrame) -> tuple:
    df = set_dtypes(data)
    encoded_df = encode_data(df)
    X, y = split_input_tragets(encoded_df)

    return X, y, encoded_df


# %%
X, y, encoded_df = prepare_data(data)

fs = SelectKBest(score_func=mutual_info_classif, k="all")
fs.fit(X, y)

#%%
scores = pd.DataFrame(
    {"features": encoded_df.columns[: len(fs.scores_)], "score": fs.scores_}
)
scores = scores.sort_values("score", ascending=False)
threshold_selection = 0.01
#%%
# plot the scores
plt.figure(figsize=(40, 10), dpi=1000)
plt.bar("features", "score", data=scores)

plt.axhline(
    y=threshold_selection, color="r", linestyle="-",
)
plt.xticks(rotation=90)
plt.title(
    "Feature selection : mutual info classification score", loc="left", fontsize=30
)

plt.show()

#%%
relevant_columns = [
    encoded_df.columns[i]
    for i in range(len(fs.scores_))
    if fs.scores_[i] > threshold_selection
]

corr = encoded_df[relevant_columns].corr()

nb_correlations = (abs(corr) > 0.9).sum()
redundant_columns = nb_correlations[nb_correlations > 1].index
print(f"Redundant : {redundant_columns}")

#%%
discarded_redundants = ["SEX_M", "SEATING_POSITION_D"]

kept_columns = [
    column for column in relevant_columns if column not in discarded_redundants
]
print(f"columns kept : {kept_columns}")

# %%

selected_features_data = encoded_df[kept_columns + [TARGET]]

X_reduced, y_reduced = split_input_tragets(selected_features_data)

X_reduced_train, X_reduced_test, y_train, y_test = train_test_split(
    X_reduced,
    y_reduced,
    test_size=0.3,
    random_state=4,
    stratify="yes",  # we have unbalanced targets
)


# The next step would be to train a decision tree and get the main rules from it.
# Below the code with a gridsearch.

# %%
tree_para = {
    "criterion": ["gini", "entropy"],
    "splitter": ["best", "random"],
    "class_weight": ["balanced"],  # label classes are unbalanced
    "max_depth": [15, 18, 20, 23, 25, 30, 100, 200, 300],
    "min_samples_leaf": [0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.01],
}
clf = GridSearchCV(DecisionTreeClassifier(), tree_para, cv=5, n_jobs=-1)
clf.fit(X_reduced_train, y_train)

print(recall_score(clf.best_estimator_.predict(X_reduced_test), y_test))
print(f1_score(clf.best_estimator_.predict(X_reduced_test), y_test))

# I didn't manage to get a score good enough using f1_score and recall_score (< 0.3 is pretty low).
# Some hipothesis about that :
# - Decision trees are really sensitive to noise, we might want to go deeper into cleaning some outliers and noise during preprcoessing
# - When preprocessing we might have oversimplified some features
# - Transforming labels into a binary label might have confused information


# %%
# I also tried with a "black box model" with a RandomForestClassifier
# Below the code with a gridsearch.
# The score

forest_para = {
    "n_estimators": [5, 10, 20, 100, 200],
    "criterion": ["gini", "entropy"],
    "class_weight": ["balanced"],
    "max_depth": [3, 4, 5, 6, 7, 8, 9],
    "min_samples_leaf": [0.002, 0.005, 0.01],
}
clf_forest = GridSearchCV(RandomForestClassifier(), forest_para, cv=5, n_jobs=-1)
clf_forest.fit(X_reduced_train, y_train)

print(recall_score(clf_forest.best_estimator_.predict(X_reduced_test), y_test))
print(f1_score(clf_forest.best_estimator_.predict(X_reduced_test), y_test))
