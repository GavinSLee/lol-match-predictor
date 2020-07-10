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
        self.api_key = "RGAPI-68b5e06e-4a74-4747-bc55-a8394c09dd76"
        
    
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

        curr_match_stats = [] 


        counter = 0 
        for match in match_history: 
            print("Getting Total Game Stats!") 
            print("Counter: " + str(counter) + "\n") 
            matchId = str(match['gameId'])
            curr_game_stats = self.getGameStats(matchId) 
            curr_match_stats.append(curr_game_stats) 
            counter += 1 
            time.sleep(3) 

        return curr_match_stats 

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

    def blueWins(self, curr_match_stats):
        """
        Counts whether blue wins given the current match stats. The output is 1 if the blue team wins, 0 if 
        the blue team loses.

        :type curr_match_stats: Dict
        :rtype: int 
        """


        teams = curr_match_stats["teams"]
        blue_team = teams[0] # Returns a dict of the blue team's basic stats, with winning or losing indicated
        if blue_team["win"] == "Win":
            return 1  
        else:
            return 0   

         

    def redWins(self, curr_match_stats):
        """
        Counts whether red wins given the current match stats. The output is 1 if the red team wins, 0 if 
        the red team loses.

        :type curr_match_stats: Dict
        :rtype: int 
        """


        teams = curr_match_stats["teams"]
        red_team = teams[1] # Returns a dict of the red team's basic stats, with winning or losing indicated
        if red_team["win"] == "Win":
            return 1  
        else:
            return 0   


    def blueWardsPlaced(self, curr_match_timeline):
        """
        Counts the number of wards the blue team had placed down by the 15 minute mark for a given match timeline. 

        :type curr_match_timeline: Dict
        :rtype: int 
        """

        numBlueWards = 0 
        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        if len(frames) > 15:
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
        
        return numBlueWards

    def redWardsPlaced(self, curr_match_timeline):
        """
        Counts the number of wards the red team had placed down by the 15 minute mark for a given match timeline. 

        :type curr_match_timeline: Dict
        :rtype: int 
        """

        numRedWards = 0 
        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        if len(frames) > 15:
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
        
        return numRedWards
    
    def blueWardKills(self, curr_match_timeline):
        """
        Counts the number of wards the blue team had destroyed by the 15 minute mark for a given match timeline. 

        :type curr_match_timeline: Dict
        :rtype: int 
        """


        numDestroyed = 0
        frames = curr_match_timeline["frames"]

        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            for event in curr_events: 
                # Checks that the event type is a ward kill  
                # and the particiant is on the blue team 
                if event["type"] == "WARD_KILL":
                        if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                            if event["killerId"] < 6:
                                numDestroyed += 1
        
        return numDestroyed
    
    def redWardKills(self, curr_match_timeline):
        """
        Counts the number of wards the red team had destroyed by the 15 minute mark for a given match timeline. 

        :type curr_match_timeline: Dict
        :rtype: int 
        """


        numDestroyed = 0
        frames = curr_match_timeline["frames"]

        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            for event in curr_events: 
                # Checks that the event type is a ward kill  
                # and the particiant is on the blue team 
                if event["type"] == "WARD_KILL":
                        if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                            if event["killerId"] > 5:
                                numDestroyed += 1
        
        return numDestroyed

    def blueFirstBlood(self, curr_match_stats):
        """ 
        Determines whether the blue team secured First Blood given the current match stats.  

        :type curr_match_stats: Dict
        :rtype: int 
        """

        teams = curr_match_stats["teams"]
        blue_team = teams[0] # Returns a dict of the blue team's basic stats
        if blue_team["firstBlood"] == True:
            return 1 
        else:
            return 0  

    def redFirstBlood(self, curr_match_stats):
        """ 
        Determines whether the red team secured First Blood given the current match stats.  

        :type curr_match_stats: Dict
        :rtype: int 
        """

        teams = curr_match_stats["teams"]
        red_team = teams[1] # Returns a dict of the red team's basic stats
        if red_team["firstBlood"] == True:
            return 1 
        else:
            return 0  

    def blueKills(self, curr_match_timeline):
        """
        Counts the number of kills the blue team had gotten by the 15 minute mark given a match timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int 
        """

        numKills = 0
        frames = curr_match_timeline["frames"]

        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            for event in curr_events:
                # Checks that the event type is a Champion Kill 
                # and the kiler is on the blue team 
                if event["type"] == "CHAMPION_KILL": 
                    if event["killerId"] < 6:
                        numKills += 1

        return numKills 

    def redKills(self, curr_match_timeline):
        """
        Counts the number of kills the red team had gotten by the 15 minute mark given a match timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int 
        """

        numKills = 0
        frames = curr_match_timeline["frames"]

        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            for event in curr_events:
                # Checks that the event type is a Champion Kill 
                # and the kiler is on the red team 
                if event["type"] == "CHAMPION_KILL": 
                    if event["killerId"] > 5:
                        numKills += 1

        return numKills
        

    def blueDeaths(self, curr_match_timeline):
        """
        Counts the number of deaths the blue team had by the 15 minute mark given a match timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int 
        """

        numBlueDeaths = self.redKills(curr_match_timeline)
        return numBlueDeaths


    def redDeaths(self, curr_match_timeline):
        """
        Counts the number of deaths the red team had gotten by the 15 minute mark given a match timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int 
        """

        numRedDeaths = self.blueKills(curr_match_timeline)
        return numRedDeaths

    def blueAssists(self, curr_match_timeline):
        """
        Counts the number of assists the blue team had gotten by the 15 minute mark given a timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int
        """
    
        numAssists = 0
        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]
            for event in curr_events:
                # Checks that the event type is a champion kill 
                # and the particiant is on the blue team 
                if event["type"] == "CHAMPION_KILL":
                    if event["killerId"] < 6:
                        numAssists += len(event["assistingParticipantIds"])
        return numAssists

    def redAssists(self, curr_match_timeline):
        """
        Counts the number of assists the red team had gotten by the 15 minute mark given a timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int
        """
        numAssists = 0
        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]
            for event in curr_events:
                # Checks that the event type is a champion kill 
                # and the particiant is on the red team 
                if event["type"] == "CHAMPION_KILL":
                    if event["killerId"] > 5:
                        numAssists += len(event["assistingParticipantIds"])
        return numAssists


    def blueEliteMonsterKills(self, curr_match_timeline):
        """
        Determines the number of elite monsters the blue team had killed by the 15 minute mark given a timeline. Elite monsters
        are either dragons or heralds/baron. 

        :type curr_match_timeline: Dict
        :rtype: int
        """ 


        numMonsters = 0
        frames = curr_match_timeline["frames"]

        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            for event in curr_events: 
                # Checks that the event is an elite monster kill and the killer is on the blue team 
                if event["type"] == "ELITE_MONSTER_KILL":
                    if event["killerId"] < 6:
                        numMonsters += 1
    
        return numMonsters

    def redEliteMonsterKills(self, curr_match_timeline):
        """
        Determines the number of elite monsters the red team had killed by the 15 minute mark given a timeline. Elite monsters
        are either dragons or heralds/baron. 

        :type curr_match_timeline: Dict
        :rtype: int
        """ 

        numMonsters = 0
        frames = curr_match_timeline["frames"]

        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            for event in curr_events: 
                # Checks that the event is an elite monster kill and the killer is on the red team 
                if event["type"] == "ELITE_MONSTER_KILL":
                    if event["killerId"] > 5:
                        numMonsters += 1
    
        return numMonsters

    def blueDragonKills(self, curr_match_timeline):
        """ Determines how many dragons the blue team killed in the first 15 minutes given a timeline.  

        :type curr_match_timeline: Dict
        :rtype: int
        """ 
        
        numDragons = 0
        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            # Checks if the current event is a monster dragon kill, and the killer is on the blue team 
            for event in curr_events:
                if event["type"] == "ELITE_MONSTER_KILL":
                    if event["monsterType"] == "DRAGON": 
                        if event["killerId"] < 6:
                            numDragons += 1 

        return numDragons 

    def redDragonKills(self, curr_match_timeline):
        """ Determines how many dragons the red team killed in the first 15 minutes given a timeline.  

        :type curr_match_timeline: Dict
        :rtype: int
        """ 
        
        numDragons = 0
        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            # Checks if the current event is a monster dragon kill, and the killer is on the red team 
            for event in curr_events:
                if event["type"] == "ELITE_MONSTER_KILL":
                    if event["monsterType"] == "DRAGON": 
                        if event["killerId"] > 5:
                            numDragons += 1 

        return numDragons 

    def blueHeraldKills(self, curr_match_timeline):
        """ Determines how many rift heralds the blue team had killed in the first 15 minutes given a timeline.  

        :type curr_match_timeline: Dict
        :rtype: int
        """

        numHeralds = 0
        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            # Checks if the current event is a monster herald kill, and the killer is on the blue team 
            for event in curr_events:
                if event["type"] == "ELITE_MONSTER_KILL":
                    if event["monsterType"] == "RIFTHERALD": 
                        if event["killerId"] < 6:
                            numHeralds += 1  
                
        return numHeralds



    def redHeraldKills(self, curr_match_timeline):
        """ Determines how many rift heralds the red team had killed in the first 15 minutes given a timeline.  

        :type curr_match_timeline: Dict
        :rtype: int
        """

        numHeralds = 0
        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            # Checks if the current event is a monster herald kill, and the killer is on the red team 
            for event in curr_events:
                if event["type"] == "ELITE_MONSTER_KILL":
                    if event["monsterType"] == "RIFTHERALD": 
                        if event["killerId"] > 5:
                            numHeralds += 1  
                
        return numHeralds


    def blueTowerKills(self, curr_match_timeline):
        """
        Counts how many towers the blue team had destroyed by 15 minutes for a given timeline. 

        :type curr_match_timeline: Dict
        :rtype: int
        """

        numTowers = 0

        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            # Checks that the current even is a tower building kill, and the killer is on the blue team 
            for event in curr_events:
                if event["type"] == "BUILDING_KILL":
                    if event["buildingType"] == "TOWER_BUILDING":
                        if event["killerId"] < 6:
                            numTowers += 1

        return numTowers  

    def redTowerKills(self, curr_match_timeline):
        """
        Counts how many towers the red team had destroyed by 15 minutes for a given timeline. 

        :type curr_match_timeline: Dict
        :rtype: int
        """

        numTowers = 0

        frames = curr_match_timeline["frames"]
        # Note that we loop 16 times, as we care only about the first 15 minutes of the game
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]

            # Checks that the current even is a tower building kill, and the killer is on the red team 
            for event in curr_events:
                if event["type"] == "BUILDING_KILL":
                    if event["buildingType"] == "TOWER_BUILDING":
                        if event["killerId"] > 5:
                            numTowers += 1

        return numTowers   

    def blueTotalGold(self, curr_match_timeline):
        """ Determines the total gold of the blue team at the 15th minute mark for a given timeline. 

        :type curr_match_timeline: Dict
        :rtype: int
        """


        totalGold = 0 
        frames = curr_match_timeline["frames"]

        curr_frame = frames[15] # 15th minute mark 
        curr_participants = curr_frame["participantFrames"]

        for i in range(1, 11):
            curr_participant_frame = curr_participants[str(i)]
            participantId = curr_participant_frame["participantId"]
            # Checks that the current participant is on the blue team 
            if participantId < 6:
                totalGold += curr_participant_frame["totalGold"]

        return totalGold 

    def redTotalGold(self, curr_match_timeline):
        """ Determines the total gold of the red team at the 15th minute mark for a given timeline. 

        :type curr_match_timeline: Dict
        :rtype: int
        """


        totalGold = 0 
        frames = curr_match_timeline["frames"]

        curr_frame = frames[15] # 15th minute mark 
        curr_participants = curr_frame["participantFrames"]

        for i in range(1, 11):
            curr_participant_frame = curr_participants[str(i)]
            participantId = curr_participant_frame["participantId"]
            # Checks that the current participant is on the red team 
            if participantId > 5:
                totalGold += curr_participant_frame["totalGold"]

        return totalGold

    def blueAvgLvl(self, curr_match_timeline):
        """ 
        Determines the average level of the blue team at the 15th minute mark for a given timeline. 

        :type curr_match_timeline: Dict
        :rtype: int
        """ 

        totalLvl = 0 

        frames = curr_match_timeline["frames"]

        curr_frame = frames[15] 
        curr_participants = curr_frame["participantFrames"]

        for i in range(1, 11):
            curr_participant_frame = curr_participants[str(i)]
            participantId = curr_participant_frame["participantId"]
            if participantId < 6:
                totalLvl += curr_participant_frame["level"]
        
        avgLvl = totalLvl / 5

        return avgLvl 

    def redAvgLvl(self, curr_match_timeline):
         """ 
        Determines the average level of the red team at the 15th minute mark for a given timeline. 

        :type curr_match_timeline: Dict
        :rtype: int
        """ 

         

    def blueTotalExp(self, curr_match_timeline):
        """ Determines the total experience the blue team has at the 15th minute mark for each timeline in curr_match_timeline. 


        :type curr_match_timeline: List[dict]
        :rtype: List[int]
        """


        blueTotalExp = [] 

        for timeline in curr_match_timeline:
            totalExp = 0 

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 6):
                curr_player = curr_participants[str(i)]
                totalExp += curr_player["xp"] 
            
            blueTotalExp.append(totalExp) 

        return blueTotalExp

    def redTotalExp(self, curr_match_timeline):
        """ Determines the total experience the red team has at the 15th minute mark for each timeline in curr_match_timeline. 


        :type curr_match_timeline: List[dict]
        :rtype: List[int]
        """


        redTotalExp = [] 

        for timeline in curr_match_timeline:
            totalExp = 0 

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(6, 11):
                curr_player = curr_participants[str(i)]
                totalExp += curr_player["xp"] 
            
            redTotalExp.append(totalExp) 

        return redTotalExp
    
    def blueTotalMinionsKilled(self, curr_match_timeline):
        """ Determines the total number of minions the blue team has killed at the 15th minute mark for each timeline in curr_match_timeline. 

        :type curr_match_timeline: List[dict] 
        :rtype: List[int]
        """


        blueTotalMinionsKilled = [] 

        for timeline in curr_match_timeline:
            totalMinions = 0

            frames = timeline["frames"]

            curr_frame = frames[15] 
            curr_participants = curr_frame["participantFrames"]

            for i in range(1, 6):
                curr_player = curr_participants[str(i)]
                totalMinions += curr_player["minionsKilled"] 
            
            blueTotalMinionsKilled.append(totalMinions)

        return blueTotalMinionsKilled 


    def redTotalMinionsKilled(self, curr_match_timeline):
        """ Determines the total number of minions the red team has killed at the 15th minute mark for each timeline in curr_match_timeline. 

        :type curr_match_timeline: List[dict] 
        :rtype: List[int]
        """


        redTotalMinionsKilled = [] 

        for timeline in curr_match_timeline:
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

    def blueSummonerOnTeam(self, curr_match_stats):
        """ Determines whether the summoner we're training the model for is on the blue team for each match in match history.

        :type curr_match_stats: List[dict] 
        :rtype: List[int] 
        """


        onBlueTeam = [] 

        for game in curr_match_stats: 
            
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

    num_matches = 100
    match_history = data.getMatchHistory(accountId, num_matches)
    cleaned_match_history = data.cleanMatchHistory(match_history)

    curr_match_stats = data.getTotalGameStats(cleaned_match_history)
    curr_match_timeline = data.getTotalGameTimeline(cleaned_match_history)

    blueKills = data.blueKills(curr_match_timeline)
    redKills = data.redKills(curr_match_timeline) 

    blueTotalGold = data.blueTotalGold(curr_match_timeline) 
    redTotalGold = data.redTotalGold(curr_match_timeline) 
    blueTotalExp = data.blueTotalExp(curr_match_timeline) 
    redTotalExp = data.redTotalExp(curr_match_timeline) 

    blue_data = {
        "gameId": data.getGameIds(cleaned_match_history), 
        "blueWins": data.blueWins(curr_match_stats), 
        "blueWardsPlaced": data.blueWardsPlaced(curr_match_timeline), 
        "blueWardKills": data.blueWardKills(curr_match_timeline),
        "blueFirstBlood": data.blueFirstBlood(curr_match_stats), 
        "blueKills": data.blueKills(curr_match_timeline),
        "blueDeaths": data.blueDeaths(redKills), 
        "blueAssists": data.blueAssists(curr_match_timeline), 
        "blueEliteMonsterKills": data.blueEliteMonsterKills(curr_match_timeline),
        "blueDragonKills": data.blueDragonKills(curr_match_timeline),
        "blueHeraldKills": data.blueHeraldKills(curr_match_timeline),
        "blueTowerKills": data.blueTowerKills(curr_match_timeline), 
        "blueTotalGold": data.blueTotalGold(curr_match_timeline), 
        "blueAvgLvl": data.blueAvgLvl(curr_match_timeline), 
        "blueTotalExp": data.blueTotalExp(curr_match_timeline),
        "blueTotalMinionsKilled": data.blueTotalMinionsKilled(curr_match_timeline), 
        "blueGoldDiff": data.blueGoldDiff(blueTotalGold, redTotalGold),
        "blueExpDiff": data.blueExpDiff(blueTotalExp, redTotalExp)
    } 

    red_data = {
        "redWins": data.redWins(curr_match_stats), 
        "redWardsPlaced": data.redWardsPlaced(curr_match_timeline),
        "redWardKills": data.redWardKills(curr_match_timeline), 
        "redFirstBlood": data.redFirstBlood(curr_match_stats), 
        "redKills": data.redKills(curr_match_timeline),
        "redDeaths": data.redDeaths(blueKills),
        "redAssists": data.redAssists(curr_match_timeline),
        "redEliteMonsterKills": data.redEliteMonsterKills(curr_match_timeline),
        "redDragonKills": data.redDragonKills(curr_match_timeline),
        "redHeraldKills": data.redHeraldKills(curr_match_timeline), 
        "redTowerKills": data.redTowerKills(curr_match_timeline), 
        "redTotalGold": data.redTotalGold(curr_match_timeline),
        "redAvgLvl": data.redAvgLvl(curr_match_timeline),
        "redTotalExp": data.redTotalExp(curr_match_timeline),
        "redTotalMinionsKilled": data.redTotalMinionsKilled(curr_match_timeline), 
        "redGoldDiff": data.redGoldDiff(blueTotalGold, redTotalGold), 
        "redExpDiff": data.redExpDiff(blueTotalExp, redTotalExp)
    }


    df1 = pd.DataFrame(data = blue_data)
    df2 = pd.DataFrame(data = red_data)
    final_df = pd.concat([df1, df2], axis = 1) 
    final_df.to_csv('league_data.csv')
    print(final_df) 
  
    