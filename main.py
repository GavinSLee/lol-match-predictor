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
        self.api_key = "RGAPI-647308a9-56a1-4f45-ae05-ddca8c6c6f45"
        
    
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


    def getMatchHistory(self, accountId, beginIndex, endIndex):
        """ Gets a summoner's match history up to the number of recent matches they want, with their account ID passed in. 

        NOTE: The current implementation only gets one match at a time. This is purposefully done such that we can ammend the script incrementally and check for bugs without losing too much progress (i.e. having to loop through all of the matches again). 

        :type account_id: String
        :type beginIndex: int 
        :type endIndex: int 
        :rtype: List[Dict]
        """

        match_history_endpoint = "/lol/match/v4/matchlists/by-account/" # Pass in the account_id as a parameter
        final_url = self.api + match_history_endpoint + accountId 

        params = {'api_key': self.api_key, 'beginIndex': beginIndex, 'endIndex': endIndex}
        curr_match_history = requests.get(final_url, params=params).json()['matches'] 

        return curr_match_history

    def getGameStats(self, matchId):
        """ Gets a game's stats given a matchId; matchId to be passed into the URL.

        :type matchId: String
        :rtype: Dict
        """ 

        match_stats_endpoint = "/lol/match/v4/matches/"
        final_url = self.api + match_stats_endpoint + matchId
        params = {'api_key':self.api_key}
        curr_match_stats = requests.get(final_url, params=params).json() 
        return curr_match_stats 

    def getGameTimeline(self, matchId):
        """ Gets a game's timeline given a matchId; matchId to be passed into the URL.

        :type matchId: String
        :rtype: Dict
        """
        match_timeline_endpoint = "/lol/match/v4/timelines/by-match/"
        final_url = self.api + match_timeline_endpoint + matchId 

        params = {'api_key':self.api_key} 
        curr_match_timeline = requests.get(final_url, params=params).json() 

        return curr_match_timeline 

    def checkMatchValidity(self, curr_match_stats):
        """ Checks whether the game is valid (i.e. the game is CLASSIC and the game duration is at least 15 minutes).

        :type curr_match_stats: Dict
        :rtype: bool
        """

        gameDuration = curr_match_stats["gameDuration"]
        if gameDuration < 900:
            return False 
        elif curr_match_stats["gameMode"] != "CLASSIC":
            return False 
        else:
            return True

    def blueWins(self, curr_match_stats):
        """
        Checks whether blue wins given the current match stats. The output is 1 if the blue team wins, 0 if 
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
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]
            for event in curr_events:             
                # NOTE: We only care about blue wards, yellow wards, and pink wards 
                if event["type"] == "WARD_PLACED":
                    if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                        if event["creatorId"] < 6:
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
        for i in range(16): 
            # This gives us the current frame that we're on (i.e. the ith to ith + 1 minute of the game)
            curr_frame = frames[i] 
            # Gives us an array of the events that took place during this ith minute 
            curr_events = curr_frame["events"]
            for event in curr_events:             
                # NOTE: We only care about blue wards, yellow wards, and pink wards 
                if event["type"] == "WARD_PLACED":
                    if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                        if event["creatorId"] > 5:
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
                # and the particiant is on the red team 
                if event["type"] == "WARD_KILL":
                        if event["wardType"] == "YELLOW_TRINKET" or event["wardType"] == "CONTROL_WARD" or event["wardType"] == "BLUE_TRINKET":
                            if event["killerId"] > 5:
                                numDestroyed += 1
        
        return numDestroyed

    def blueFirstBlood(self, curr_match_stats):
        """ 
        Determines whether the blue team secured first blood given the current match stats.  

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
        Determines whether the red team secured first blood given the current match stats.  

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
        are either dragons or heralds/barons. 

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

        totalLvl = 0 

        frames = curr_match_timeline["frames"]

        curr_frame = frames[15] 
        curr_participants = curr_frame["participantFrames"]

        for i in range(1, 11):
            curr_participant_frame = curr_participants[str(i)]
            participantId = curr_participant_frame["participantId"]
            if participantId > 5:
                totalLvl += curr_participant_frame["level"]
        
        avgLvl = totalLvl / 5

        return avgLvl

    def blueTotalExp(self, curr_match_timeline):
        """ Determines the total experience the blue team had at the 15th minute mark for a given timeline. 

        :type curr_match_timeline: Dict
        :rtype: int
        """

        totalXP = 0 

        frames = curr_match_timeline["frames"]
        curr_frame = frames[15] 
        curr_participants = curr_frame["participantFrames"]

        for i in range(1, 11):
            curr_participant_frame = curr_participants[str(i)]
            participantId = curr_participant_frame["participantId"]
            # Checks that the participant is on the blue team  
            if participantId < 6:
                totalXP += curr_participant_frame["xp"]
        
        return totalXP 

    def redTotalExp(self, curr_match_timeline):
        """ Determines the total experience the red team had at the 15th minute mark for a given timeline. 

        :type curr_match_timeline: Dict
        :rtype: int
        """

        totalXP = 0 

        frames = curr_match_timeline["frames"]
        curr_frame = frames[15] 
        curr_participants = curr_frame["participantFrames"]

        for i in range(1, 11):
            curr_participant_frame = curr_participants[str(i)]
            participantId = curr_participant_frame["participantId"]
            # Checks that the participant is on the red team 
            if participantId > 5:
                totalXP += curr_participant_frame["xp"]
        
        return totalXP
    
    def blueTotalMinionsKilled(self, curr_match_timeline):
        """ Determines the total number of minions the blue team had killed by the 15th minute mark for a given timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int
        """

        totalMinions = 0

        frames = curr_match_timeline["frames"]

        curr_frame = frames[15] 
        curr_participants = curr_frame["participantFrames"]

        for i in range(1, 11):
            curr_participant_frame = curr_participants[str(i)]
            participantId = curr_participant_frame["participantId"]
            # Checks that the participant is on the blue team 
            if participantId < 6:
                totalMinions += curr_participant_frame["minionsKilled"] 
        
        return totalMinions 


    def redTotalMinionsKilled(self, curr_match_timeline):
        """ Determines the total number of minions the red team had killed by the 15th minute mark for a given timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int
        """

        totalMinions = 0

        frames = curr_match_timeline["frames"]

        curr_frame = frames[15] 
        curr_participants = curr_frame["participantFrames"]

        for i in range(1, 11):
            curr_participant_frame = curr_participants[str(i)]
            participantId = curr_participant_frame["participantId"]
            # Checks that the participant is on the red team 
            if participantId > 5:
                totalMinions += curr_participant_frame["minionsKilled"] 
        
        return totalMinions  

    def blueGoldDiff(self, curr_match_timeline):
        """ Finds the gold difference for the blue team given a timeline. 

        :type curr_match_timeline: Dict
        :rtype: int 
        """ 

        blueTotalGold = self.blueTotalGold(curr_match_timeline)
        redTotalGold = self.redTotalGold(curr_match_timeline)

        return blueTotalGold - redTotalGold 

    def redGoldDiff(self, curr_match_timeline):
        """ Finds the gold difference for the red team given a timeline. 

        :type curr_match_timeline: Dict
        :rtype: int 
        """ 

        blueTotalGold = self.blueTotalGold(curr_match_timeline)
        redTotalGold = self.redTotalGold(curr_match_timeline)

        return redTotalGold - blueTotalGold 

    def blueExpDiff(self, curr_match_timeline):
        """ Finds the XP difference for the blue team given a timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int
        """

        blueTotalXP = self.blueTotalExp(curr_match_timeline)
        redTotalXP = self.redTotalExp(curr_match_timeline)

        return blueTotalXP - redTotalXP 

    def redExpDiff(self, curr_match_timeline):
        """ Finds the XP difference for the red team given a timeline. 

        :type curr_match_timeline: Dict 
        :rtype: int
        """

        blueTotalXP = self.blueTotalExp(curr_match_timeline)
        redTotalXP = self.redTotalExp(curr_match_timeline)

        return redTotalXP - blueTotalXP 

    def blueSummonerOnTeam(self, curr_match_stats):
        """ Determines whether the summoner we're training the model for is on the blue team given the current match stats.

        :type curr_match_stats: Dict 
        :rtype: int 
        """

        participantIdentities = curr_match_stats["participantIdentities"]

        for participant in participantIdentities:

            curr_player = participant["player"]
            summoner_name = curr_player["summonerName"]

            if summoner_name == "Leego671" or summoner_name == "ARealFlip":
                id_num = participant["participantId"] 
                if id_num < 6:
                    return 1  
                else:
                    return 0  
    
    def redSummonerOnTeam(self, curr_match_stats):
        """ Determines whether the summoner we're training the model for is on the red team given the current match stats.

        :type curr_match_stats: Dict 
        :rtype: int 
        """

        onBlueTeam = self.blueSummonerOnTeam(curr_match_stats) 
        if onBlueTeam == 1:
            return 0
        else:
            return 1 
        
    

if __name__ == "__main__":
    data = MatchData() 
    summoner_name = "Leego671"
    accountId = data.getAccountID(summoner_name) 

    # Will get stats for up to the last 1000 matches 
    for i in range(1000):
        time.sleep(7) 
        beginIndex = i 
        endIndex = i + 1
        curr_match_history = data.getMatchHistory(accountId, beginIndex, endIndex) 

        if len(curr_match_history) == 0:
            break 

        curr_match = curr_match_history[0] 

        match_id = str(curr_match["gameId"])

        print("Begin Index: " + str(beginIndex)) 
        print("Current Game ID: " + match_id + "\n")
        curr_match_stats = data.getGameStats(match_id)
        curr_match_timeline = data.getGameTimeline(match_id)

        if data.checkMatchValidity(curr_match_stats) == False:
            continue 

        blue_data = {
            "gameId": [match_id], 
            "onBlueTeam": [data.blueSummonerOnTeam(curr_match_stats)],
            "blueWins": [data.blueWins(curr_match_stats)], 
            "blueWardsPlaced": [data.blueWardsPlaced(curr_match_timeline)], 
            "blueWardKills": [data.blueWardKills(curr_match_timeline)],
            "blueFirstBlood": [data.blueFirstBlood(curr_match_stats)], 
            "blueKills": [data.blueKills(curr_match_timeline)],
            "blueDeaths": [data.blueDeaths(curr_match_timeline)], 
            "blueAssists": [data.blueAssists(curr_match_timeline)], 
            "blueEliteMonsterKills": [data.blueEliteMonsterKills(curr_match_timeline)],
            "blueDragonKills": [data.blueDragonKills(curr_match_timeline)],
            "blueHeraldKills": [data.blueHeraldKills(curr_match_timeline)],
            "blueTowerKills": [data.blueTowerKills(curr_match_timeline)], 
            "blueTotalGold": [data.blueTotalGold(curr_match_timeline)], 
            "blueAvgLvl": [data.blueAvgLvl(curr_match_timeline)], 
            "blueTotalExp": [data.blueTotalExp(curr_match_timeline)],
            "blueTotalMinionsKilled": [data.blueTotalMinionsKilled(curr_match_timeline)], 
            "blueGoldDiff": [data.blueGoldDiff(curr_match_timeline)],
            "blueExpDiff": [data.blueExpDiff(curr_match_timeline)]
        } 

        red_data = {
            "onRedTeam": [data.redSummonerOnTeam(curr_match_stats)],
            "redWins": [data.redWins(curr_match_stats)], 
            "redWardsPlaced": [data.redWardsPlaced(curr_match_timeline)],
            "redWardKills": [data.redWardKills(curr_match_timeline)], 
            "redFirstBlood": [data.redFirstBlood(curr_match_stats)], 
            "redKills": [data.redKills(curr_match_timeline)],
            "redDeaths": [data.redDeaths(curr_match_timeline)],
            "redAssists": [data.redAssists(curr_match_timeline)],
            "redEliteMonsterKills": [data.redEliteMonsterKills(curr_match_timeline)],
            "redDragonKills": [data.redDragonKills(curr_match_timeline)],
            "redHeraldKills": [data.redHeraldKills(curr_match_timeline)], 
            "redTowerKills": [data.redTowerKills(curr_match_timeline)], 
            "redTotalGold": [data.redTotalGold(curr_match_timeline)],
            "redAvgLvl": [data.redAvgLvl(curr_match_timeline)],
            "redTotalExp": [data.redTotalExp(curr_match_timeline)],
            "redTotalMinionsKilled": [data.redTotalMinionsKilled(curr_match_timeline)], 
            "redGoldDiff": [data.redGoldDiff(curr_match_timeline)], 
            "redExpDiff": [data.redExpDiff(curr_match_timeline)]
        }


        df1 = pd.DataFrame(data = blue_data)
        df2 = pd.DataFrame(data = red_data)
        final_df = pd.concat([df1, df2], axis = 1) 

        if i == 0: 
            final_df.to_csv('league_data.csv', mode = 'a', header=True)
        else:
            final_df.to_csv('league_data.csv', mode = 'a', header=False)

  
    