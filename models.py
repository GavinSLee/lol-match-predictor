from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn import tree
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import numpy as np

df = pd.read_csv('league_data.csv')
df_clean = df.copy() 
cols = ['gameId', 'redFirstBlood', 'redKills', 'redEliteMonsterKills', 'redDragonKills','redTotalMinionsKilled', 'redGoldDiff', 'redExpDiff', 'redHeraldKills',
       'blueGoldDiff', 'blueExpDiff', 'blueTotalMinionsKilled', 'blueAvgLvl', 'redWardsPlaced', 'redWardKills', 'redDeaths', 'redAssists', 'redTowerKills',
       'redTotalExp', 'redTotalGold', 'redAvgLvl', 'onBlueTeam', 'onRedTeam', 'redWins']
df_clean = df_clean.drop(cols, axis = 1)

corr_list = df_clean[df_clean.columns[1:]].apply(lambda x: x.corr(df_clean['blueWins']))
cols = []
for col in corr_list.index:
    if (corr_list[col]>0.2 or corr_list[col]<-0.2):
        cols.append(col)
df_clean = df_clean[cols]

X = df_clean
y = df['blueWins']
scaler = MinMaxScaler()
scaler.fit(X)
X = scaler.transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ----- NAIVE BAYES ----- 
clf_nb = GaussianNB()
clf_nb.fit(X_train, y_train)

pred_nb = clf_nb.predict(X_test)

acc_nb = accuracy_score(pred_nb, y_test)

# ----- DECISION TREE ----- 
tree = tree.DecisionTreeClassifier()

# search the best params
grid = {'min_samples_split': [5, 10, 20, 50, 100]},

clf_tree = GridSearchCV(tree, grid, cv=5)
clf_tree.fit(X_train, y_train)

pred_tree = clf_tree.predict(X_test)

# get the accuracy score
acc_tree = accuracy_score(pred_tree, y_test)

# ----- RANDOM FOREST ----- 
rf = RandomForestClassifier()
# search the best params
grid = {'n_estimators':[100,200,300,400,500], 'max_depth': [2, 5, 10]}

clf_rf = GridSearchCV(rf, grid, cv=5)
clf_rf.fit(X_train, y_train)

pred_rf = clf_rf.predict(X_test)
# get the accuracy score
acc_rf = accuracy_score(pred_rf, y_test)

# ----- LOGISTIC REGRESSION ----- 
lr = LogisticRegression()
lr.fit(X_train, y_train)

# get accuracy score
pred_lr = lr.predict(X_test)
acc_lr = accuracy_score(pred_lr, y_test)

# ----- K NEAREST NEIGHBORS -----
knn = KNeighborsClassifier() 

# search the best params
grid = {"n_neighbors":np.arange(1,100)}
clf_knn = GridSearchCV(knn, grid, cv=5)
clf_knn.fit(X_train,y_train) 

# get accuracy score
pred_knn = clf_knn.predict(X_test) 
acc_knn = accuracy_score(pred_knn, y_test)

# Printing of Final Accuracy Scores 
data_dict = {'Naive Bayes': [acc_nb], 'Decision Tree': [acc_tree], 'Random Forest': [acc_rf], 'Logistic Regression': [acc_lr], 'K-Nearest Neighbors': [acc_knn]}
df_c = pd.DataFrame.from_dict(data_dict, orient='index', columns=['Accuracy Score'])
print(df_c)

