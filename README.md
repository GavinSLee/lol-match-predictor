# League of Legends Match Predictor

I've been playing League of Legends (LoL) for the last 8 years. Recently, I took Brown's Machine Learning course (CSCI 1420) my sophomore spring. I decided that it would be a little fun to see if I could combine what I had learned in ML with some game stats that I've accumulated over the years.

Thus, I wanted to answer the question: Given a LoL's game stats at the 15 minute mark, can we determine which side will win? 

## Yours Truly (Leego671)

Here's a look at my current League account, which has the username Leego671. As of 8/24/2020, my account is Silver II for solo/duo ratings; however, I don't really play too much solo queue, as I tend to play with friends in larger parties (3+ more people). 

<p align = "center">
 
 <img src = "https://user-images.githubusercontent.com/46236119/91107939-6888cf00-e62b-11ea-9533-f6bbe28265a5.PNG" alt = "https://user-images.githubusercontent.com/46236119/91107939-6888cf00-e62b-11ea-9533-f6bbe28265a5.PNG" />
  
</p>

I'm not the best player, and I would say that my rank is fairly indicative of my skill level. In other words, I would say my skill is around high silver/low gold, maybe high gold on a good day. 

We'll be grabbing data from my account, Leego671, to train several ML models and see what kind of accuracies we can get. :) 

## Grabbing the Data

Riot Games has a nifty API to which we can send HTTP requests to in order to grab our data. Note that there are a couple of nuances with this API:

1. There's a request limit for users who are building some project solely for personal use (i.e. using their API for a non-enterprise related product); we can only make 20 requests per second, and 50 requests per minute. 

2. Their API doesn't allow for live game data, at least without extended use of their API. 

<p align = "center">
 <img src = "https://user-images.githubusercontent.com/46236119/91111174-ae966080-e634-11ea-8085-2831c060dca8.PNG" alt = "https://user-images.githubusercontent.com/46236119/91111174-ae966080-e634-11ea-8085-2831c060dca8.PNG" />  
</p>

Their API requires a developer key, with which you can generate if you have a valid Riot Games account. 

With their API, we can pass in a summoner name (in this case, Leego671), get a ton of matches from this summoner's match history, get match specific details per match (first blood, who's on which team, etc), and a timeline of the match. 

When grabbing the data, we only care about games that take place on summoner's rift; I play a lot of ARAM, but we're not gathering any statistics for those games. 

With their API, I was able to grab my last 300 games from the past 2-3 years that took place on summoner's rift, that lasted at least 15 minutes. I wasn't able to grab any matches later than the past 2-3 years, but that's okay because the game changes so much, so those statistics wouldn't be as useful as recent matches. 

From each match, we gathered the following statistics at the 15 minute mark: 

<ul>
 <li> gameId </li>
 <li> win </li>
 <li> wardsPlaced </li>
 <li> wardsDestroyed </li>
 <li> firstBlood </li>
 <li> kills </li>
 <li> deaths </li>
 <li> assists </li>
 <li> eliteMonsterKills </li>
 <li> dragons </li>
 <li> heralds </li>
 <li> towerKills </li>
 <li> totalGold </li>
 <li> avgLvl </li>
 <li> totalExp </li>
 <li> totalMinionsKilled </li>
 <li> goldDiff </li>
 <li> expDiff </li>
</ul>

These statistics were gathered for both the blue and the red team. 
## Cleaning the Data
Notice that we grabbed a ton of statistics for both the blueside and the red side. Some of the statistics are a little repetitive/not super relevant to what we're trying to achieve, at least from personal experience. I figured it would be better if we grabbed more data than necessary, as it's always easier to remove features than it is to make GET requests to grab more data. 

Thus, we use Pandas, Numpy, SKLearn, and Seaborn to analyze our data, remove unecessary features, and create machine learning models. Also, I reframed my question to answer: "Can we predict whether the blue team will win at the 15 minute mark?" As league is a zero-sum game, and so if the blue team wins, then the red team loses, and vice-versa. 

First, we analyze the correlation between blueKills, blueAssists, blueWardsPlaced, and blueTotalGold: 

<p align = "center">
 <img src = "https://user-images.githubusercontent.com/46236119/91112490-1ac69380-e638-11ea-85bc-bd1f9765d75a.png" alt = "https://user-images.githubusercontent.com/46236119/91112490-1ac69380-e638-11ea-85bc-bd1f9765d75a.png" />  
</p>

We can see that we have some pretty good lineararity between these some of these variables. Let's look at which variables are well correlated with a heatmap using seaborn: 

<p align = "center">
 <img src = "https://user-images.githubusercontent.com/46236119/91112659-91639100-e638-11ea-981d-190ae3129a05.png" alt = "https://user-images.githubusercontent.com/46236119/91112659-91639100-e638-11ea-981d-190ae3129a05.png" />  
</p>

As personally expected, some decent correlation with blue winning with variables: blue kills, blue total gold, and blue experience. 


## Model Training and Accuracy 

For training and testing purposes, I split the data into a training set and testing set, where the testing set was about 20% of the data, and training was the majority portion. For each ML model, I used the same training/testing data for each algorithm. 

With our cleaned data, I decided to implement the following 5 ML methods:

<ul>
 <li> Naive Bayes </li>
 <li> Decision Tree </li>
 <li> Random Forest </li>
 <li> Logistic Regression </li>
 <li> K-Nearest Neighbors </li>
</ul>

There's definitely some room here to take this data and train more ML models with it using other techniques.

To see how I implemented the models, take a look at models.py; it's decently commented and should be self-explanatory if one has sufficient ML knowledge. 

With these 5 models, I obtained the following results: 

<p align = "center">
 <img src = "https://user-images.githubusercontent.com/46236119/91113081-8ceba800-e639-11ea-91e6-16bd513943e0.PNG" alt = "https://user-images.githubusercontent.com/46236119/91113081-8ceba800-e639-11ea-91e6-16bd513943e0.PNG" />  
</p>

Not too shabby, if you ask me. :)

## Conclusion and Interesting Takeaways

This was a pretty fun little data science/ml project; it was fun gathering data for myself using the Riot Games API, as all of the data in Brown's ML course was supplied to us by the course staff. There's definitely some room for expansion to this project, and I'd personally like to come back to it when my knowledge of ML betters. 

Some interesting takeaways:

1. Rift Herald seems to be not that important of a feature, with its little correlation on both the blue side and the red side impacting a win. I assume this is the case because most players at lower elos don't know how to use it properly. 


2. Surprisingly, wards placed down by the 15 minute mark doesn't seem to impact the outcome of a game all that much either. I assume this is because lower elo players don't know how to ward properly, or really just don't ward at all. 

3. The most important things that impact the outcome of a game are kills and dragons (to a certain extent). Kills doesn't particularly surprise me, as players tilt when they get killed, and kills impact the gold difference. It seems like dragons are rather important, because dragons can be used to snowball the game at later stages, when either team is at soul-point. 

Thanks for reading; if you have any questions, please email me at: gavin_lee@brown.edu. 
