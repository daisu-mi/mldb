import sys,os,re
import fileinput
import urllib.request
import csv
import numpy as np
import pandas as pd

class MleagueDB(object):
    url = 'https://m-league.jp/games/'
    scorefile = 'scores.html'
    fp = ''
    csvfile_teams = "teams.csv"
    csvfile_players = "players.csv"

    # translation from id to name
    players = {}
    teams = {}

    # translation from player_name to player_id / team_id
    players_trans = {}
    teams_trans = {}

    results = {}

    def __init__(self,name,teams,players):
        self.name = name
        if (teams != ''):
            if (os.path.isfile(teams) == False):
                self.downloadTeamsCSV(teams)
        self.readTeamsCSV(teams)

        if (players != ''):
            if (os.path.isfile(players) == False):
                self.downloadPlayersCSV(players)
        self.readPlayersCSV(players)
    
    def getOfficialWebsite(self):
        return self.url

    def setOfficialWebsite(self,buf):
        if(buf != ''):
            self.url = buf

    def downloadScore(self, buf):
        file = self.scorefile
        if (buf != ''):
            file = buf
        with urllib.request.urlopen(self.url) as u:
            with open(file, 'bw') as o:
                o.write(u.read())

    def openScoreOnline(self):
        self.fp = urllib.request.urlopen(self.url)

    def openScoreOffline(self, buf):
        file = self.scorefile
        if (buf != ''):
            file = buf
            if (os.path.isfile(file) == False):
                self.downloadScore(file)
        self.fp = open(file, 'r', encoding="utf-8")

    def closeScore(self):
        self.fp.close()
    
    def getTeams(self):
        return self.teams

    def getTeamsTrans(self):
        return self.teams_trans

    def getPlayers(self):
        return self.players

    def getNumberofPlayers(self):
        return len(self.players)

    def getTeamName(self, id):
        team_id = str(id)
        print(self.teams)
        #return self.teams[team_id]

    def getTeamIDbyPlayer(self, id):
        player_id = str(id)
        player_name = self.players[player_id]
        team_id = self.teams_trans[player_name]
        return team_id

    def getTeamNamebyPlayer(self, id):
        team_id = self.getTeamIDbyPlayer(id)
        team_name = self.teams[team_id]
        return team_name
        
    def getPlayerName(self, id):
        player_id = str(id)
        return self.players[player_id]

    def getPlayersTrans(self):
        return self.players_trans

    def getResults(self):
        return self.results

    def readTeamsCSV(self,buf):
        file = self.csvfile_teams
        if (buf != ""):
            file = buf

        if (buf != ""):
            self.csvfile_teams = buf
        with open(self.csvfile_teams, encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                team_id,team_name = row[:2]
                self.teams[team_id] = team_name

    def readPlayersCSV(self,buf):
        file = self.csvfile_players 
        if (buf != ""):
            file = buf
        with open(self.csvfile_players, encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                player_id,player_name,player_team = row[:3]
                self.players[player_id] = player_name
                self.players_trans[player_name] = player_id
                self.teams_trans[player_name] = player_team

    def downloadTeamsCSV(self,buf):
        url = 'https://drive.google.com/uc?export=download&id=18bcUMfsXitmWhh1DC0-m_2N4q1BwOYXt'
        file = self.csvfile_teams
        if (buf != ''):
            file = buf
        with urllib.request.urlopen(url) as u:
            with open(file, 'bw') as o:
                o.write(u.read())

    def downloadPlayersCSV(self,buf):
        url = 'https://drive.google.com/uc?export=download&id=1qj126RPIQXiafHFkEIusEoQ91HDTm0pa'
        file = self.csvfile_players
        if (buf != ''):
            file = buf
        with urllib.request.urlopen(url) as u:
            with open(file, 'bw') as o:
                o.write(u.read())

    def readScore(self):
        player = ''
        year = 0
        month = 0
        day = 0
        kaisen = 0
        flag_point = 0
        first_data = 1

        for line in self.fp:
            if (type(line) != str):
                line = str(line.decode("utf-8"))

            line = re.sub('\r','',line)
            line = re.sub('\n','',line)

            if flag_point == 1:
                line = line.replace(' ','')
                line = line.replace('\t','')
                line = line.replace('▲','-')
                line = line.replace('pt','')
                line = re.sub('\(.*\)','',line)
                point = line

                if int(year) > 0:
                    player_id = 0
                    team_id = 0
                    if (type(player) == str):
                        player_id = int(self.players_trans[player])
                        team_id = int(self.teams_trans[player])
                    
                    game = "%04d%02d%02d%02d" % (int(year), int(month), int(day), int(kaisen))

                    # save record as dict
                    i = len(self.players)
                    list = [''] * i
                    if game in self.results:
                        list = self.results[game]

                    list[(player_id - 1)] = float(point)
                    self.results[game] = list
 
                flag_point=0
                continue

            line_search=re.search('<div class=\"p-gamesResult__date\">(\d+)\/(\d+)<',line)
            if line_search:
                month = int(line_search.group(1))
                day = int(line_search.group(2))
                if month >= 10:
                    year = 2021
                else:
                    year = 2022
                continue 

            line_search=re.search('<div class=\"p-gamesResult__number\">[^0-9]+([0-9])[^0-9]+',line)
            if line_search:
                kaisen=int(line_search.group(1))
                continue

            line_search=re.search('<div class=\"p-gamesResult__name\">(.+)<\/div>',line)
            if line_search:
                player=line_search.group(1)
                continue 

            if re.search('<div class=\"p-gamesResult__point\">',line):
                flag_point=1
                continue 

    def getScore(self,id):
        npscore = np.empty(0)
        first_data = 1
        for key1 in sorted(self.results.keys()):
            score_list = self.results[key1]
            i = id - 1
            myscore = score_list[i]
            if (type(myscore) == float):
                if (first_data == 1):
                    npscore = [key1,myscore]
                    first_data = 0
                else:
                    npscore = np.append(npscore, [key1,myscore])
            
                score_list_nan = [np.nan if i == '' else i for i in score_list]
                npscore = np.append(npscore,score_list_nan)
 
        # [key1,myscore,allscore] = 1 +  1 + num_of_players = 2 + 32 = 34
        cols = 2 + len(self.players)
        return(npscore.reshape([-1, cols]))

    def analyzeScore(self, id):
        score = self.getScore(id)
        player_name = self.getPlayerName(id)

        dfcol = ['id', 'Name'] + list(self.players.values())
        df = pd.DataFrame(data=(score), columns=dfcol)

        # set gameid (2021040101) as index
        df = df.set_index('id')
        df = df.astype(float)


        # points
        df_point = pd.DataFrame(df.sum(skipna=True,axis=0).round(1),columns=['ポイント']).T

        # diff of points
        df_diff = df.apply(lambda x: x - x['Name'], axis = 1)
        df_diffpoint = pd.DataFrame(df_diff.sum(skipna=True,axis=0).round(1),columns=['ポイント差']).T

        # number of participation
        df_match = pd.DataFrame(df.notnull().sum(axis=0),columns=['出場回数']).T

        df_output = pd.concat([df,df_point,df_diffpoint,df_match])
        df_output = df_output.rename(columns={'Name': player_name})

        return(df_output)
