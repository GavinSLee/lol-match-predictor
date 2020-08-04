import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 

df = pd.read_csv('league_data.csv')
df_clean = df.copy() 
df_clean = df_clean.drop(['gameId'], axis = 1)

g = sns.PairGrid(data=df_clean, vars=['blueKills', 'blueAssists', 'blueWardsPlaced', 'blueTotalGold'], hue='blueWins', height=3, palette='Set1')
g.map_diag(plt.hist)
g.map_offdiag(plt.scatter)
g.add_legend();
plt.figure(figsize=(16, 12))
sns.heatmap(df_clean.drop('blueWins', axis = 1).corr(), cmap="YlGnBu", annot = True, fmt = '.2f', vmin = 0)

plt.show() 