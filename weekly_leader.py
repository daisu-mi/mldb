import sys,os,re
import fileinput
import urllib.request
import csv
import numpy as np
import pandas as pd
import datetime

from MLDB import MleagueDB

def getToday():
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    return(int(now.strftime('%Y%m%d')))

def getThisMonday():
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)

    wdic = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat':5, 'Sun': 6}
    wday = now.strftime('%a')

    return(int(now.strftime('%Y%m%d'))-wdic[wday])

def getTodaysXLSX():
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    return(now.strftime('%Y%m%d') + ".xlsx")

xlsxfile = getTodaysXLSX()

ml = MleagueDB('','teams.csv','players.csv')
ml.openScoreOffline("score.html")
ml.readScore()
ml.closeScore()

ml_player = ml.getPlayers()
ml_result = ml.getResults()
ml_team = ml.getTeams()

thisMonday = getThisMonday()
today = getToday() + 1

team_score = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

for i in range(20220307, 20220311):
    try:
        key = str(i) + '01'
        score = ml_result[key]
        for j in range(0, len(score)):
            if (score[j] != ''):
                player_id = j + 1
                team_id = int(ml.getTeamIDbyPlayer(player_id)) - 1
                point = round(float(score[j]), 1)
                team_score[team_id] = team_score[team_id] + point
            pass

        key = str(i) + '02'
        score = ml_result[key]
        for j in range(0, len(score)):
            if (score[j] != ''):
                player_id = j + 1
                team_id = int(ml.getTeamIDbyPlayer(player_id)) - 1
                point = round(float(score[j]), 1)
                team_score[team_id] = team_score[team_id] + point
            pass

    except KeyError:
        pass

for i in range(0, len(team_score)):
    team_id = str(i + 1)
    point = round(team_score[i], 1)

    output = "%s,\t\t %.1f" % (ml_team[team_id], point)
    print(output)


