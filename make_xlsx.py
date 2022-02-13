import sys,os,re
import fileinput
import urllib.request
import csv
import numpy as np
import pandas as pd
import datetime

from MLDB import MleagueDB

def getTodaysXLSX():
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    return(now.strftime('%Y%m%d') + ".xlsx")
    pass

xlsxfile = getTodaysXLSX()

ml = MleagueDB('','teams.csv','players.csv')
ml.openScoreOffline("score.html")
ml.readScore()
ml.closeScore()

ml_player = ml.getPlayers()
ml_result = ml.getResults()

first_sheet = 1

for i in ml_player.keys():
    i = int(i)
    player_name = ml.getPlayerName(i)

    df_output = ml.analyzeScore(i)

    if (first_sheet == 1):
        with pd.ExcelWriter(xlsxfile, engine="openpyxl", mode="w") as writer:    
            df_output.to_excel(writer, sheet_name=player_name, index=True, header=True)
            first_sheet = 0
    else:
        with pd.ExcelWriter(xlsxfile, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:    
            df_output.to_excel(writer, sheet_name=player_name, index=True, header=True)
