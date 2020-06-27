import pandas as pd 
import numpy as np 
import requests 
import pprint
import time 

class MatchData:

    def __init__(self):
        # Change the API endpoint according to your game region. 
        self.api = "https://na1.api.riotgames.com"
        # Generate your personal API key on the Riot Games API website. 
        self.api_key = "RGAPI-42c1f889-a2e8-4283-a1a1-58952bd15882"
        
    
    def getAccountID(self, summoner_name):
        
        """ Gets the account ID to use as a parameter when getting match history, takes in a summoner name to pass as a 
        parameter to the API endpoint. 

        :type summoner_name: String
        :rtype: String 
        """

        summoner_endpoint = "/lol/summoner/v4/summoners/by-name/" # Pass in the summoner name as a parameter
        final_url = self.api + summoner_endpoint + summoner_name

        params = {'api_key': self.api_key}
        account_data = requests.get(final_url, params=params).json()
        accountId = account_data['accountId']
        
        return accountId


    def getTotalMatchHistory(self, accountId):
        """ Gets a summoner's total match history, with their account ID passed in. 

        :type account_id: String
        :rtype: List[Dict]
        """


        match_history_endpoint = "/lol/match/v4/matchlists/by-account/" # Pass in the account_id as a parameter
        final_url = self.api + match_history_endpoint + accountId 
        total_match_history = [] 

        # Note that we can only get 100 matches person API request; we assume that the player has at most 1000 matches played 
        for i in range(0, 1000, 100):

            beginIndex = i 
            endIndex = i + 100
            params = {'api_key': self.api_key, 'beginIndex': beginIndex, 'endIndex': endIndex}
            curr_match_history = requests.get(final_url, params=params).json()['matches']
            total_match_history += curr_match_history 

        return total_match_history

    def cleanMatchHistory(self, match_history):
        """ Cleans match history by removing all games that are not on Summoner's Rift (i.e. removing games that are all ARAM).

        :type match_history: List[Dict]
        :rtype: List[Dict] 
        """  

        cleaned_match_history = [] 
        counter = 0
        for match in match_history:
            matchId = str(match['gameId'])
            curr_match_stats = self.getGameStats(matchId)  
            curr_game_mode = curr_match_stats['gameMode']

            print(matchId) 
            print(curr_game_mode)
            print("Counter: " + str(counter) + "\n")
            counter += 1
            time.sleep(1) 

            if curr_game_mode != "CLASSIC":
                continue 
            else: 
                cleaned_match_history.append(match)

            if counter == 5:
                break  

        return cleaned_match_history 

    def getGameStats(self, matchId):
        """ Gets a game's stats given a matchId; matchId to be passed into the URL 

        :type matchId: String
        :rtype: Dict
        """ 


        match_stats_endpoint = "/lol/match/v4/matches/"
        final_url = self.api + match_stats_endpoint + matchId
        params = {'api_key':self.api_key}
        curr_match_stats = requests.get(final_url, params=params).json() 
        return curr_match_stats

    def getTotalGameStats(self, match_history):
        """ Returns the total game stats for each match in match_history. 

        :type match_history: List[dict] 
        :rtype: List[dict]
        """

        total_game_stats = [] 


        for match in match_history: 
            matchId = str(match['gameId'])
            curr_game_stats = self.getGameStats(matchId) 
            total_game_stats.append(curr_game_stats) 

        return total_game_stats 

    def getGameTimeline(self, matchId):
        """ Gets a game's timeline given a matchId; matchId to be passed into the URL 

        :type matchId: String
        :rtype: Dict
        """
        match_timeline_endpoint = "/lol/match/v4/timelines/by-match/"
        final_url = self.api + match_timeline_endpoint + matchId 

        params = {'api_key':self.api_key} 
        curr_match_timeline = requests.get(final_url, params=params).json() 

        return curr_match_timeline 

    def getTotalGameTimeline(self, match_history):
        """ Returns a total timeline for each match played in match_history. 

        :type match_history: List[dict] 
        :rtype: List[dict] 
        """

        total_timeline = [] 

        for match in match_history: 
            matchId = str(match['gameId'])
            curr_timeline = self.getGameTimeline(matchId) 
            total_timeline.append(curr_timeline)
            
        return total_timeline 

    def blueWins(self, total_game_stats):
        """
        Counts the occurrences at which blue wins given a list of game stats for each game. The output is 1 if the blue team wins, 0 if 
        the blue team loses.

        :type total_game_stats: List[dict]
        :rtype: List[bool]
        """

        blueWins = [] 

        for game in total_game_stats:
            teams = game["teams"]
            blue_team = teams[0] # Returns a dict of the blue team's basic stats, with winning or losing indicated
            if blue_team["win"] == "Win":
                blueWins.append(1) 
            else:
                blueWins.append(0)  

        return blueWins 

    def redWins(self, total_game_stats):
        """
        Counts the occurrences at which the red team wins given a list of game stats for each game. The output is 1 if the red team wins, 0 if the red team loses.

        :type total_game_stats: List[dict]
        :rtype: List[bool]
        """

        redWins = [] 

        for game in total_game_stats :
            teams = game["teams"]
            red_team = teams[1] # Returns a dict of the red team's basic stats, with winning or losing indicated
            if red_team["win"] == "Win":
                redWins.append(1) 
            else:
                redWins.append(0) 

        return redWins 


    def blueWardsPlaced(self, total_game_timeline):
        """
        Counts the number of wards the blue team had placed down by the 15 minute mark for each match in the total game timeline. 


        :type total_game_timeline: List[dict]
        :rtype: List[int] 
        """

        blueWardsPlaced = [] 

        for timeline in total_game_timeline:
            numBlueWards = 0 

            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:             
                    # NOTE: We only care about blue wards, yellow wards, and pink wards 
                    if event["type"] == "WARD_PLACED" and event["creatorId"] < 6:
                        if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                            numBlueWards += 1

            blueWardsPlaced.append(numBlueWards)

        return blueWardsPlaced

    def redWardsPlaced(self, total_game_timeline):
        """
        Counts the number of wards the red team had placed down by the 15 minute mark for each match in match history. 


        :type match_history: List[dict]
        :rtype: List[int] 
        """

        redWardsPlaced = [] 

        for timeline in total_game_timeline:
            numRedWards = 0 

            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # NOTE: We only care about blue wards, yellow wards, and pink wards 
                    if event["type"] == "WARD_PLACED" and event["creatorId"] > 5:
                        if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                            numRedWards += 1

            redWardsPlaced.append(numRedWards)

        return redWardsPlaced
    
    def blueWardsDestroyed(self, total_game_timeline):
        """
        Counts the number of wards the blue team had destroyed by the 15 minute mark for each match in total_game_timeline. 

        :type total_game_timeline: List[dict]
        :rtype: List[int] 
        """

        blueWardsDestroyed = []

        for timeline in total_game_timeline:
            numDestroyed = 0
            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events: 
                    # Checks that the event type is a ward placement 
                    # and the particiant is on the red team 
                    if event["type"] == "WARD_KILL" and event["killerId"] < 6:
                        if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                            numDestroyed += 1
           
            blueWardsDestroyed.append(numDestroyed) 
        return blueWardsDestroyed
    
    def redWardsDestroyed(self, total_game_timeline):
        """ 
        Counts the number of wards the red team had destroyed by the 15 minute mark for each match in total_game_timeline. 

        :type total_game_timeline: List[dict]
        :rtype: List[int] 
        """

        redWardsDestroyed = []

        for timeline in total_game_timeline:
            numDestroyed = 0
            
            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # Checks that the event type is a ward placement 
                    # and the particiant is on the red team 
                    if event["type"] == "WARD_KILL" and event["killerId"] > 5:
                        if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                            numDestroyed += 1

            redWardsDestroyed.append(numDestroyed) 
        return redWardsDestroyed

    def blueFirstBlood(self, total_game_stats):
        """ 
        Determines whether the blue team secured First Blood in each match in total_game_stats.  

        :type total_game_stats: List[dict]
        :rtype: List[int] 
        """


        blueFirstBlood = [] 

        for match in total_game_stats:
            teams = match["teams"]
            blue_team = teams[0] # Returns a dict of the blue team's basic stats
            if blue_team["firstBlood"] == True:
                blueFirstBlood.append(1) 
            else:
                blueFirstBlood.append(0) 

        return blueFirstBlood

    
    def redFirstBlood(self, blueFirstBlood):
        """
        Determines whether the red team secured First Blood in each match (if blue team does not get first blood, then red team gets first flood and vice versa).

        :type blueFirstBlood: List[int]
        :rtype: List[int]
        """

        redFirstBlood = [] 

        for i in range(len(blueFirstBlood)):
            if blueFirstBlood[i] == 1:
                redFirstBlood.append(0) 
            else:
                redFirstBlood.append(1) 

        return redFirstBlood 

    def blueKills(self, total_game_timeline):
        """
        Counts the number of kills the blue team had gotten by the 15 minute mark. 

        :type total_game_timeline: List[dict] 
        :rtype: List[int] 
        """

        blueKills = [] 

        for timeline in total_game_timeline:
            numKills = 0
            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # Checks that the event type is a Champion Kill 
                    # and the kiler is on the blue team 
                    if event["type"] == "CHAMPION_KILL" and event["killerId"] < 6:
                        numKills += 1

            blueKills.append(numKills)  
        return blueKills 

    def redKills(self, total_game_timeline):
        """
        Counts the number of kills the red team had gotten by the 15 minute mark. 

        :type total_game_timeline: List[dict] 
        :rtype: List[int] 
        """

        redKills = [] 

        for timeline in total_game_timeline:
            numKills = 0
            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # Checks that the event type is a Champion Kill 
                    # and the kiler is on the blue team 
                    if event["type"] == "CHAMPION_KILL" and event["killerId"] > 5:
                        numKills += 1

            redKills.append(numKills)  
        return redKills

    def blueDeaths(self, redKills):
        """
        Counts the number of deaths the blue team had gotten by the 15 minute mark. 

        :type redKills: List[int]
        :rtype: List[int]
        """ 

        return redKills 


    def redDeaths(self, blueKills):
        """
        Counts the numbr of deaths the red team had gotten by the 15 minute mark. 

        :type blueKills: List[int]
        :rtype: List[int]
        """

        return blueKills 

    def blueAssists(self, total_game_timeline):
        """
        Counts the number of assists the blue team had gotten by the 15 minute mark. 

        :type total_game_timeline: List[dict] 
        :rtype: List[int]
        """

        blueAssists = [] 

        for timeline in total_game_timeline:
            numAssists = 0
            
            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    
                    # Checks that the event type is a champion kill 
                    # and the particiant is on the blue team 
                    if event["type"] == "CHAMPION_KILL" and event["killerId"] < 6:
                        numAssists += len(event["assistingParticipantIds"])
            blueAssists.append(numAssists)

        return blueAssists

    def redAssists(self, total_game_timeline):
        """
        Counts the number of assists the red team had gotten by the 15 minute mark. 

        :type total_game_timeline: List[dict] 
        :rtype: List[int]
        """

        redAssists = [] 

        for timeline in total_game_timeline:
            numAssists = 0
            
            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    
                    # Checks that the event type is a champion kill 
                    # and the particiant is on the red team 
                    if event["type"] == "CHAMPION_KILL" and event["killerId"] > 5:
                        numAssists += len(event["assistingParticipantIds"])
            redAssists.append(numAssists)

        return redAssists


    def blueEliteMonsterKills(self, total_game_timeline):
        """
        Determines the number of elite monsters the blue team has killed by the 15 minute mark. Elite monsters
        are either dragons or heralds/baron. 

        :type total_game_timeline: List[dict] 
        :rtype: List[int]

        """ 

        blueEliteMonsters = [] 

        for timeline in total_game_timeline:
            numMonsters = 0
            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events: 
                    # Checks that the event is an elite monster kill 
                    if event["type"] == "ELITE_MONSTER_KILL" and event["killerId"] < 6:
                        numMonsters += 1
            blueEliteMonsters.append(numMonsters)

        return blueEliteMonsters

    def redEliteMonsterKills(self, total_game_timeline):
        """
        Determines the number of elite monsters the red team has killed by the 15 minute mark. Elite monsters
        are either dragons or heralds/baron. 

        :type total_game_timeline: List[dict] 
        :rtype: List[int]

        """ 

        redEliteMonsters = [] 

        for timeline in total_game_timeline:
            numMonsters = 0
            frames = timeline["frames"]

            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # Checks that the event is an elite monster kill 
                    if event["type"] == "ELITE_MONSTER_KILL" and event["killerId"] > 5:
                        numMonsters += 1
            redEliteMonsters.append(numMonsters)

        return redEliteMonsters

    def blueDragonKills(self, total_game_timeline):
        """ Determines how many dragons the blue team killed in the first 15 minutes 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """

        blueDragonKills = [] 

        for timeline in total_game_timeline:
            numDragons = 0
            frames = timeline["frames"]
            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # Checks that the event is an elite monster kill
                    if "monsterType" in event: 
                        if event["monsterType"] == "DRAGON" and event["killerId"] < 6:
                            numDragons += 1
            blueDragonKills.append(numDragons) 

        return blueDragonKills

    def redDragonKills(self, total_game_timeline):
        """ Determines how many dragons the red team killed in the first 15 minutes 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """

        redDragonKills = [] 

        for timeline in total_game_timeline:
            numDragons = 0
            frames = timeline["frames"]
            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # Checks that the event is an elite monster kill 
                    if "monsterType" in event:
                        if event["monsterType"] == "DRAGON" and event["killerId"] > 5:
                            numDragons += 1
            redDragonKills.append(numDragons) 

        return redDragonKills

    def blueHeraldKills(self, total_game_timeline):
        """ Determines how many Heralds the blue team has killed in the first 15 minutes 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """

        blueHeraldKills = [] 

        for timeline in total_game_timeline:
            numHeralds = 0
            frames = timeline["frames"]
            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # Checks that the event is an elite monster kill 
                    if "monsterType" in event:
                        if event["monsterType"] == "RIFTHERALD" and event["killerId"] < 6:
                            numHeralds += 1
            blueHeraldKills.append(numHeralds)  

        return blueHeraldKills



    def redHeraldKills(self, total_game_timeline):
        """ Determines how many Heralds the red team has killed in the first 15 minutes 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """

        redHeraldKills = [] 

        for timeline in total_game_timeline:
            numHeralds = 0
            frames = timeline["frames"]
            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # Checks that the event is an elite monster kill 
                    if "monsterType" in event:
                        if event["monsterType"] == "RIFTHERALD" and event["killerId"] > 5:
                            numHeralds += 1
            redHeraldKills.append(numHeralds)  

        return redHeraldKills


    def blueTowerKills(self, total_game_timeline):
        """
        Counts how many towers the blue team has destroyed by the 15th minute mark for
        each timeline in total_game_timeline. 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """


        blueTowerKills = [] 

        for timeline in total_game_timeline: 
            numTowers = 0

            frames = timeline["frames"]
            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    if event["type"] == "BUILDING_KILL" and event["killerId"] < 6:
                        if event["buildingType"] == "TOWER_BUILDING":
                            numTowers += 1
            blueTowerKills.append(numTowers) 

        return blueTowerKills  

    def redTowerKills(self, total_game_timeline):
        """
        Counts how many towers the red team has destroyed by the 15th minute mark for each
        timeline in total_game_timeline. 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """


        redTowerKills = [] 

        for timeline in total_game_timeline: 
            numTowers = 0

            frames = timeline["frames"]
            # Note that we loop 15 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 

                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    if event["type"] == "BUILDING_KILL" and event["killerId"] > 5:
                        if event["buildingType"] == "TOWER_BUILDING":
                            numTowers += 1
            redTowerKills.append(numTowers) 

        return redTowerKills 

    def blueTotalGold(self, total_game_timeline):
        """ Determines the total gold of the blue team at the 15th minute mark for each
        timeline in total_game_timeline. 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """

        blueTotalGold = [] 

        for timeline in total_game_timeline:
            totalGold = 0 
            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 6):
                curr_player = curr_participants[str(i)]
                totalGold += curr_player["totalGold"]

            blueTotalGold.append(totalGold)

        return blueTotalGold

    def redTotalGold(self, total_game_timeline):
        """ Determines the total gold of the red team at the 15th minute mark for each
        timeline in total_game_timeline. 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """

        redTotalGold = [] 

        for timeline in total_game_timeline:
            totalGold = 0 
            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(6, 11):
                curr_player = curr_participants[str(i)]
                totalGold += curr_player["totalGold"]

            redTotalGold.append(totalGold)

        return redTotalGold

    def blueAvgLvl(self, total_game_timeline):
        """ 
        Determines the average level of the blue team at the 15th minute mark for each timeline in total_game_timeline. 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """


        blueAvgLvl = [] 

        for timeline in total_game_timeline:
            totalLvl = 0 

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 6):
                curr_player = curr_participants[str(i)]
                totalLvl += curr_player["level"]
            
            avgLvl = totalLvl / 5

            blueAvgLvl.append(avgLvl) 

        return blueAvgLvl 

    def redAvgLvl(self, total_game_timeline):
        """ 
        Determines the average level of the red team at the 15th minute mark for each timeline in total_game_timeline. 

        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """


        redAvgLvl = [] 

        for timeline in total_game_timeline:
            totalLvl = 0 

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(6, 11):
                curr_player = curr_participants[str(i)]
                totalLvl += curr_player["level"]
            
            avgLvl = totalLvl / 5

            redAvgLvl.append(avgLvl) 

        return redAvgLvl 

    def blueTotalExp(self, total_game_timeline):
        """ Determines the total experience the blue team has at the 15th minute mark for each timeline in total_game_timeline. 


        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """


        blueTotalExp = [] 

        for timeline in total_game_timeline:
            totalExp = 0 

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 6):
                curr_player = curr_participants[str(i)]
                totalExp += curr_player["xp"] 
            
            blueTotalExp.append(totalExp) 

        return blueTotalExp

    def redTotalExp(self, total_game_timeline):
        """ Determines the total experience the red team has at the 15th minute mark for each timeline in total_game_timeline. 


        :type total_game_timeline: List[dict]
        :rtype: List[int]
        """


        redTotalExp = [] 

        for timeline in total_game_timeline:
            totalExp = 0 

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(6, 11):
                curr_player = curr_participants[str(i)]
                totalExp += curr_player["xp"] 
            
            redTotalExp.append(totalExp) 

        return redTotalExp
    
    def blueTotalMinionsKilled(self, total_game_timeline):
        """ Determines the total number of minions the blue team has killed at the 15th minute mark for each timeline in total_game_timeline. 

        :type total_game_timeline: List[dict] 
        :rtype: List[int]
        """


        blueTotalMinionsKilled = [] 

        for timeline in total_game_timeline:
            totalMinions = 0

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 6):
                curr_player = curr_participants[str(i)]
                totalMinions += curr_player["minionsKilled"] 
            
            blueTotalMinionsKilled.append(totalMinions)

        return blueTotalMinionsKilled 


    def redTotalMinionsKilled(self, total_game_timeline):
        """ Determines the total number of minions the red team has killed at the 15th minute mark for each timeline in total_game_timeline. 

        :type total_game_timeline: List[dict] 
        :rtype: List[int]
        """


        redTotalMinionsKilled = [] 

        for timeline in total_game_timeline:
            totalMinions = 0

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(6, 11):
                curr_player = curr_participants[str(i)]
                totalMinions += curr_player["minionsKilled"] 
            
            redTotalMinionsKilled.append(totalMinions)

        return redTotalMinionsKilled 


    def blueSummonerOnTeam(self, total_game_stats):
        """ Determines whether the summoner we're training the model for is on the blue team for each match in match history.

        :type total_game_stats: List[dict] 
        :rtype: List[int] 
        """


        onBlueTeam = [] 

        for game in total_game_stats: 
            
            # Returns an array of participants 
            participantIdentities = game["participantIdentities"]

            for participant in participantIdentities:

                curr_player = participant["player"]
                summoner_name = curr_player["summonerName"]

                if summoner_name == "Leego671" or summoner_name == "ARealFlip":
                    id_num = participant["participantId"] 

                    if id_num < 6:
                        onBlueTeam.append(1) 
                    else:
                        onBlueTeam.append(0) 

        return onBlueTeam 
    
    def redSummonerOnTeam(self, onBlueTeam):
        """ Given a list of bools of whether or not the summoner is on the blue team, flips every number in the list and returns if the summoner is on the red team. 

        :type onBlueTeam: List[int] 
        :rtype: List[int]
        """

        onRedTeam = []
        for i in range(len(onBlueTeam)):
            if onBlueTeam[i] == 0:
                onRedTeam.append(1)
            else:
                onRedTeam.append(0) 

        return onRedTeam 
        
    

if __name__ == "__main__":
    data = MatchData() 
    summoner_name = "Leego671"
    accountId = data.getAccountID(summoner_name) 
    match_history = data.getTotalMatchHistory(accountId)
    cleaned_match_history = data.cleanMatchHistory(match_history)

    total_game_stats = data.getTotalGameStats(cleaned_match_history)
    total_game_timeline = data.getTotalGameTimeline(cleaned_match_history)

    redTotalMinionsKilled = data.redTotalMinionsKilled(total_game_timeline) 
    print(redTotalMinionsKilled)      
