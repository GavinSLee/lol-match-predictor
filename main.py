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
        self.api_key = "RGAPI-0ac392f7-36fa-4d01-aa62-a5e2b6c15e62"
        
    
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


    def getMatchHistory(self, accountId, num_matches):
        """ Gets a summoner's match history up to the number of recent matches they want, with their account ID passed in. 

        :type account_id: String
        :rtype: List[Dict]
        """


        match_history_endpoint = "/lol/match/v4/matchlists/by-account/" # Pass in the account_id as a parameter
        final_url = self.api + match_history_endpoint + accountId 
        total_match_history = [] 

        
        for i in range(0, num_matches, 100):
            beginIndex = i 
            if num_matches - beginIndex < 100:
                endIndex = num_matches 
            else:
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

            print("Cleaning Match History!") 
            print("Counter: " + str(counter) + "\n")
            counter += 1
            time.sleep(4) 

            if curr_game_mode != "CLASSIC":
                continue 
            else: 
                cleaned_match_history.append(match)

        return cleaned_match_history 

    def getGameIds(self, match_history):
        """ Gets the gameId for each match in match history. 

        :type match_history: List[Dict]
        :rtype: List[String]
        """

        matchIds = [] 

        for match in match_history:
            matchId = str(match['gameId']) 
            matchIds.append(matchId) 
        return matchIds 

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

        match_history_stats = [] 


        counter = 0 
        for match in match_history: 
            print("Getting Total Game Stats!") 
            print("Counter: " + str(counter) + "\n") 
            matchId = str(match['gameId'])
            curr_game_stats = self.getGameStats(matchId) 
            match_history_stats.append(curr_game_stats) 
            counter += 1 
            time.sleep(3) 

        return match_history_stats 

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

        counter = 0 
        for match in match_history: 
            print("Getting Total Game Timeline!") 
            print("Counter: " + str(counter) + "\n") 
            matchId = str(match['gameId'])
            curr_timeline = self.getGameTimeline(matchId) 
            total_timeline.append(curr_timeline) 
            counter += 1
            time.sleep(3) 
            
        return total_timeline 

    def blueWins(self, match_history_stats):
        """
        Counts the occurrences at which blue wins given a list of game stats for each game. The output is 1 if the blue team wins, 0 if 
        the blue team loses.

        :type match_history_stats: List[dict]
        :rtype: List[bool]
        """

        blueWins = [] 

        for game in match_history_stats:
            teams = game["teams"]
            blue_team = teams[0] # Returns a dict of the blue team's basic stats, with winning or losing indicated
            if blue_team["win"] == "Win":
                blueWins.append(1) 
            else:
                blueWins.append(0)  

        return blueWins 

    def redWins(self, match_history_stats):
        """
        Counts the occurrences at which the red team wins given a list of game stats for each game. The output is 1 if the red team wins, 0 if the red team loses.

        :type match_history_stats: List[dict]
        :rtype: List[bool]
        """

        redWins = [] 

        for game in match_history_stats :
            teams = game["teams"]
            red_team = teams[1] # Returns a dict of the red team's basic stats, with winning or losing indicated
            if red_team["win"] == "Win":
                redWins.append(1) 
            else:
                redWins.append(0) 

        return redWins 


    def blueWardsPlaced(self, match_history_timelines):
        """
        Counts the number of wards the blue team had placed down by the 15 minute mark for each timeline in match_history_timelines. 


        :type match_history_timelines: List[dict]
        :rtype: List[int] 
        """

        blueWardsPlaced = [] 

        for timeline in match_history_timelines:
            numBlueWards = 0 

            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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

    def redWardsPlaced(self, match_history_timelines):
        """
        Counts the number of wards the red team had placed down by the 15 minute mark for each timeline in match_history_timelines. 


        :type match_history: List[dict]
        :rtype: List[int] 
        """

        redWardsPlaced = [] 

        for timeline in match_history_timelines:
            numRedWards = 0 

            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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
    
    def blueWardKills(self, match_history_timelines):
        """
        Counts the number of wards the blue team had destroyed by the 15 minute mark for each timeline in match_history_timelines. 

        :type match_history_timelines: List[dict]
        :rtype: List[int] 
        """

        blueWardKills = []

        for timeline in match_history_timelines:
            numDestroyed = 0
            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events: 
                    # Checks that the event type is a ward kill  
                    # and the particiant is on the blue team 
                    if event["type"] == "WARD_KILL" and event["killerId"] < 6:
                        if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                            numDestroyed += 1
           
            blueWardKills.append(numDestroyed) 
        return blueWardKills
    
    def redWardKills(self, match_history_timelines):
        """ 
        Counts the number of wards the red team had destroyed by the 15 minute mark for each match in match_history_timelines. 

        :type match_history_timelines: List[dict]
        :rtype: List[int] 
        """

        redWardKills = []

        for timeline in match_history_timelines:
            numDestroyed = 0
            
            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
            for i in range(16): 
                # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
                curr_frame = frames[i] 
                # Gives us an array of the events that took place during this ith minute 
                curr_events = curr_frame["events"]

                for event in curr_events:
                    # Checks that the event type is a ward kill 
                    # and the particiant is on the red team 
                    if event["type"] == "WARD_KILL" and event["killerId"] > 5:
                        if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                            numDestroyed += 1

            redWardKills.append(numDestroyed) 
        return redWardKills

    def blueFirstBlood(self, match_history_stats):
        """ 
        Determines whether the blue team secured First Blood in each match in match_history_stats.  

        :type match_history_stats: List[dict]
        :rtype: List[int] 
        """


        blueFirstBlood = [] 

        for match in match_history_stats:
            teams = match["teams"]
            blue_team = teams[0] # Returns a dict of the blue team's basic stats
            if blue_team["firstBlood"] == True:
                blueFirstBlood.append(1) 
            else:
                blueFirstBlood.append(0) 

        return blueFirstBlood

    
    def redFirstBlood(self, match_history_stats):
        """
        Determines whether the red team secured First Blood in each match in match_history_stats.  

        :type match_history_stats: List[dict]
        :rtype: List[int]
        """

        redFirstBlood = [] 

        for match in match_history_stats:
            teams = match["teams"]
            red_team = teams[1] # Returns a dict of the blue team's basic stats
            if red_team["firstBlood"] == True:
                redFirstBlood.append(1) 
            else:
                redFirstBlood.append(0) 

        return redFirstBlood 

    def blueKills(self, match_history_timelines):
        """
        Counts the number of kills the blue team had gotten by the 15 minute mark. 

        :type match_history_timelines: List[dict] 
        :rtype: List[int] 
        """

        blueKills = [] 

        for timeline in match_history_timelines:
            numKills = 0
            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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

    def redKills(self, match_history_timelines):
        """
        Counts the number of kills the red team had gotten by the 15 minute mark. 

        :type match_history_timelines: List[dict] 
        :rtype: List[int] 
        """

        redKills = [] 

        for timeline in match_history_timelines:
            numKills = 0
            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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
        Counts the number of deaths the red team had gotten by the 15 minute mark. 

        :type blueKills: List[int]
        :rtype: List[int]
        """

        return blueKills 

    def blueAssists(self, match_history_timelines):
        """
        Counts the number of assists the blue team had gotten by the 15 minute mark. 

        :type match_history_timelines: List[dict] 
        :rtype: List[int]
        """

        blueAssists = [] 

        for timeline in match_history_timelines:
            numAssists = 0
            
            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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

    def redAssists(self, match_history_timelines):
        """
        Counts the number of assists the red team had gotten by the 15 minute mark. 

        :type match_history_timelines: List[dict] 
        :rtype: List[int]
        """

        redAssists = [] 

        for timeline in match_history_timelines:
            numAssists = 0
            
            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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


    def blueEliteMonsterKills(self, match_history_timelines):
        """
        Determines the number of elite monsters the blue team had killed by the 15 minute mark. Elite monsters
        are either dragons or heralds/baron. 

        :type match_history_timelines: List[dict] 
        :rtype: List[int]

        """ 

        blueEliteMonsters = [] 

        for timeline in match_history_timelines:
            numMonsters = 0
            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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

    def redEliteMonsterKills(self, match_history_timelines):
        """
        Determines the number of elite monsters the red team had killed by the 15 minute mark. Elite monsters
        are either dragons or heralds/baron. 

        :type match_history_timelines: List[dict] 
        :rtype: List[int]

        """ 

        redEliteMonsters = [] 

        for timeline in match_history_timelines:
            numMonsters = 0
            frames = timeline["frames"]

            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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

    def blueDragonKills(self, match_history_timelines):
        """ Determines how many dragons the blue team killed in the first 15 minutes 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """

        blueDragonKills = [] 

        for timeline in match_history_timelines:
            numDragons = 0
            frames = timeline["frames"]
            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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

    def redDragonKills(self, match_history_timelines):
        """ Determines how many dragons the red team killed in the first 15 minutes 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """

        redDragonKills = [] 

        for timeline in match_history_timelines:
            numDragons = 0
            frames = timeline["frames"]
            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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

    def blueHeraldKills(self, match_history_timelines):
        """ Determines how many Heralds the blue team has killed in the first 15 minutes 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """

        blueHeraldKills = [] 

        for timeline in match_history_timelines:
            numHeralds = 0
            frames = timeline["frames"]
            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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



    def redHeraldKills(self, match_history_timelines):
        """ Determines how many Heralds the red team has killed in the first 15 minutes 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """

        redHeraldKills = [] 

        for timeline in match_history_timelines:
            numHeralds = 0
            frames = timeline["frames"]
            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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


    def blueTowerKills(self, match_history_timelines):
        """
        Counts how many towers the blue team has destroyed by the 15th minute mark for
        each timeline in match_history_timelines. 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """


        blueTowerKills = [] 

        for timeline in match_history_timelines: 
            numTowers = 0

            frames = timeline["frames"]
            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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

    def redTowerKills(self, match_history_timelines):
        """
        Counts how many towers the red team has destroyed by the 15th minute mark for each
        timeline in match_history_timelines. 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """


        redTowerKills = [] 

        for timeline in match_history_timelines: 
            numTowers = 0

            frames = timeline["frames"]
            # Note that we loop 16 times, as we care only about the first 15 minutes of the game
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

    def blueTotalGold(self, match_history_timelines):
        """ Determines the total gold of the blue team at the 15th minute mark for each
        timeline in match_history_timelines. 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """

        blueTotalGold = [] 

        for timeline in match_history_timelines:
            totalGold = 0 
            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 11):
                curr_participant_frame = curr_participants[str(i)]
                participantId = curr_participant_frame["participantId"]
                if participantId < 6:
                    totalGold += curr_participant_frame["totalGold"]
            blueTotalGold.append(totalGold)

        return blueTotalGold

    def redTotalGold(self, match_history_timelines):
        """ Determines the total gold of the red team at the 15th minute mark for each
        timeline in match_history_timelines. 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """

        redTotalGold = [] 

        for timeline in match_history_timelines:
            totalGold = 0 
            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 11):
                curr_participant_frame = curr_participants[str(i)]
                participantId = curr_participant_frame["participantId"]
                if participantId > 5:
                    totalGold += curr_participant_frame["totalGold"]

            redTotalGold.append(totalGold)

        return redTotalGold

    def blueAvgLvl(self, match_history_timelines):
        """ 
        Determines the average level of the blue team at the 15th minute mark for each timeline in match_history_timelines. 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """


        blueAvgLvl = [] 

        for timeline in match_history_timelines:
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

    def redAvgLvl(self, match_history_timelines):
        """ 
        Determines the average level of the red team at the 15th minute mark for each timeline in match_history_timelines. 

        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """


        redAvgLvl = [] 

        for timeline in match_history_timelines:
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

    def blueTotalExp(self, match_history_timelines):
        """ Determines the total experience the blue team has at the 15th minute mark for each timeline in match_history_timelines. 


        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """


        blueTotalExp = [] 

        for timeline in match_history_timelines:
            totalExp = 0 

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 6):
                curr_player = curr_participants[str(i)]
                totalExp += curr_player["xp"] 
            
            blueTotalExp.append(totalExp) 

        return blueTotalExp

    def redTotalExp(self, match_history_timelines):
        """ Determines the total experience the red team has at the 15th minute mark for each timeline in match_history_timelines. 


        :type match_history_timelines: List[dict]
        :rtype: List[int]
        """


        redTotalExp = [] 

        for timeline in match_history_timelines:
            totalExp = 0 

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(6, 11):
                curr_player = curr_participants[str(i)]
                totalExp += curr_player["xp"] 
            
            redTotalExp.append(totalExp) 

        return redTotalExp
    
    def blueTotalMinionsKilled(self, match_history_timelines):
        """ Determines the total number of minions the blue team has killed at the 15th minute mark for each timeline in match_history_timelines. 

        :type match_history_timelines: List[dict] 
        :rtype: List[int]
        """


        blueTotalMinionsKilled = [] 

        for timeline in match_history_timelines:
            totalMinions = 0

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 6):
                curr_player = curr_participants[str(i)]
                totalMinions += curr_player["minionsKilled"] 
            
            blueTotalMinionsKilled.append(totalMinions)

        return blueTotalMinionsKilled 


    def redTotalMinionsKilled(self, match_history_timelines):
        """ Determines the total number of minions the red team has killed at the 15th minute mark for each timeline in match_history_timelines. 

        :type match_history_timelines: List[dict] 
        :rtype: List[int]
        """


        redTotalMinionsKilled = [] 

        for timeline in match_history_timelines:
            totalMinions = 0

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(6, 11):
                curr_player = curr_participants[str(i)]
                totalMinions += curr_player["minionsKilled"] 
            
            redTotalMinionsKilled.append(totalMinions)

        return redTotalMinionsKilled 

    def blueGoldDiff(self, blueTotalGold, redTotalGold):
        """ Finds the difference per match of the gold difference between the blue team and the red team at 15 minutes. 

        :type blueTotalGold: List[int] 
        :type redTotalGold: List[int]
        :rtype: List[int]
        """ 

        blueGoldDiff = [] 

        for i in range(len(blueTotalGold)):

            diff = blueTotalGold[i] - redTotalGold[i] 
            blueGoldDiff.append(diff) 

        return blueGoldDiff

    def redGoldDiff(self, blueTotalGold, redTotalGold):
        """ Finds the difference per match of the gold difference between the red team and the blue team at 15 minutes. 

        :type blueTotalGold: List[int] 
        :type redTotalGold: List[int]
        :rtype: List[int]
        """ 

        redGoldDiff = [] 

        for i in range(len(blueTotalGold)):

            diff = redTotalGold[i] - blueTotalGold[i] 
            redGoldDiff.append(diff) 

        return redGoldDiff

    def blueExpDiff(self, blueTotalExp, redTotalExp):
        """ Finds the differnce per match of the exp difference between the blue team and the red team at 15 minutes. 

        :type blueTotalExp, redTotalExp: List[int] 

        :rtype: List[int]
        """

        blueExpDiff = [] 

        for i in range(len(blueTotalExp)):
            diff = blueTotalExp[i] - redTotalExp[i] 
            blueExpDiff.append(diff) 

        return blueExpDiff

    def redExpDiff(self, blueTotalExp, redTotalExp):
        """ Finds the differnce per match of the exp difference between the red team and the blue team at 15 minutes. 

        :type blueTotalExp, redTotalExp: List[int] 

        :rtype: List[int]
        """

        redExpDiff = [] 

        for i in range(len(blueTotalExp)):
            diff = redTotalExp[i] - blueTotalExp[i] 
            redExpDiff.append(diff) 

        return redExpDiff

    def blueSummonerOnTeam(self, match_history_stats):
        """ Determines whether the summoner we're training the model for is on the blue team for each match in match history.

        :type match_history_stats: List[dict] 
        :rtype: List[int] 
        """


        onBlueTeam = [] 

        for game in match_history_stats: 
            
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

    num_matches = 1000
    match_history = data.getMatchHistory(accountId, num_matches)
    cleaned_match_history = data.cleanMatchHistory(match_history)

    match_history_stats = data.getTotalGameStats(cleaned_match_history)
    match_history_timelines = data.getTotalGameTimeline(cleaned_match_history)

    blueKills = data.blueKills(match_history_timelines)
    redKills = data.redKills(match_history_timelines) 

    blueTotalGold = data.blueTotalGold(match_history_timelines) 
    redTotalGold = data.redTotalGold(match_history_timelines) 
    blueTotalExp = data.blueTotalExp(match_history_timelines) 
    redTotalExp = data.redTotalExp(match_history_timelines) 

    blue_data = {
        "gameId": data.getGameIds(cleaned_match_history), 
        "blueWins": data.blueWins(match_history_stats), 
        "blueWardsPlaced": data.blueWardsPlaced(match_history_timelines), 
        "blueWardKills": data.blueWardKills(match_history_timelines),
        "blueFirstBlood": data.blueFirstBlood(match_history_stats), 
        "blueKills": data.blueKills(match_history_timelines),
        "blueDeaths": data.blueDeaths(redKills), 
        "blueAssists": data.blueAssists(match_history_timelines), 
        "blueEliteMonsterKills": data.blueEliteMonsterKills(match_history_timelines),
        "blueDragonKills": data.blueDragonKills(match_history_timelines),
        "blueHeraldKills": data.blueHeraldKills(match_history_timelines),
        "blueTowerKills": data.blueTowerKills(match_history_timelines), 
        "blueTotalGold": data.blueTotalGold(match_history_timelines), 
        "blueAvgLvl": data.blueAvgLvl(match_history_timelines), 
        "blueTotalExp": data.blueTotalExp(match_history_timelines),
        "blueTotalMinionsKilled": data.blueTotalMinionsKilled(match_history_timelines), 
        "blueGoldDiff": data.blueGoldDiff(blueTotalGold, redTotalGold),
        "blueExpDiff": data.blueExpDiff(blueTotalExp, redTotalExp)
    } 

    red_data = {
        "redWins": data.redWins(match_history_stats), 
        "redWardsPlaced": data.redWardsPlaced(match_history_timelines),
        "redWardKills": data.redWardKills(match_history_timelines), 
        "redFirstBlood": data.redFirstBlood(match_history_stats), 
        "redKills": data.redKills(match_history_timelines),
        "redDeaths": data.redDeaths(blueKills),
        "redAssists": data.redAssists(match_history_timelines),
        "redEliteMonsterKills": data.redEliteMonsterKills(match_history_timelines),
        "redDragonKills": data.redDragonKills(match_history_timelines),
        "redHeraldKills": data.redHeraldKills(match_history_timelines), 
        "redTowerKills": data.redTowerKills(match_history_timelines), 
        "redTotalGold": data.redTotalGold(match_history_timelines),
        "redAvgLvl": data.redAvgLvl(match_history_timelines),
        "redTotalExp": data.redTotalExp(match_history_timelines),
        "redTotalMinionsKilled": data.redTotalMinionsKilled(match_history_timelines), 
        "redGoldDiff": data.redGoldDiff(blueTotalGold, redTotalGold), 
        "redExpDiff": data.redExpDiff(blueTotalExp, redTotalExp)
    }


    df1 = pd.DataFrame(data = blue_data)
    df2 = pd.DataFrame(data = red_data)
    final_df = pd.concat([df1, df2], axis = 1) 
    final_df.to_csv('league_data.csv')
    print(final_df) 
  
    