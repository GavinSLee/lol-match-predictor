import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

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

# Checks the relationship between parameters of blue team features (cleaned)
# g = sns.PairGrid(data=df_clean, vars=['blueKills', 'blueAssists', 'blueWardsPlaced', 'blueTotalGold'], hue='blueWins', size=3, palette='Set1')
# g.map_diag(plt.hist)
# g.map_offdiag(plt.scatter)
# g.add_legend()

# Histogram of cleaned data correlation
df_clean.hist(alpha = 0.7, figsize=(12,10), bins=5)


# Creates a heatmap of the correlation between variables (cleaned)
# plt.figure(figsize=(16, 12))
# sns.heatmap(df_clean.corr(), cmap='YlGnBu', annot=True, fmt='.2f', vmin=0)
plt.show() 


