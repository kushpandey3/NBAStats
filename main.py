import pandas as pd
import json
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
data = {}
def loadData():
    try: 
        with open("NBA_Data") as f:
            all_data = json.load(f)
        for k, v in all_data.items():
            data[k] = pd.DataFrame(v)
    except FileNotFoundError:
        pass

def fetchPlayerData(playerName, season):
    playerName = playerName.strip().title()
    for k in data:
            if playerName in k:
                return data[k]
    print("Accessing API")
    id = players.find_players_by_full_name(playerName)[0]['id']
    data[playerName] = playergamelog.PlayerGameLog(player_id = id, season = season, season_type_all_star = "Regular Season").get_data_frames()[0]
    with open("NBA_Data", "w") as f:
            json.dump(({k: v.to_dict(orient='records') for k, v in data.items()}), f, indent=4)
    return data[playerName]
    
def viewGameLog(playerName, season):
    playerName = playerName.strip().title()
    gameLog = fetchPlayerData(playerName, season)
    gameStats = ["MIN", "PTS", "REB", "AST", "STL", "BLK", "PLUS_MINUS", "TOV", "PF", "OREB", "DREB"]
    efficiencySingles = ["FG_PCT", "FG3_PCT", "FT_PCT"]
    efficiencyPairs = [["FGM", "FGA"], ["FG3M", "FG3A"], ["FTM", "FTA"]]
    print("#\tMATCHUP\t\tMIN\tPTS\tREB\tAST\tSTL\tBLK\t+/-\tTOV\tPF\tOREB\tDREB\tFG%\t3P%\tFT%\tFGM/A\t3PM/A\tFTM/A")
    for i in range(gameLog.shape[0]):
        print(f"{i+1}\t{gameLog.iloc[i]["MATCHUP"]}", end = "\t")
        for stat in gameStats:
            print(gameLog.iloc[i][stat], end = "\t")
        for single in efficiencySingles: 
            print(f"{gameLog.iloc[i][single]*100:.0f}%", end = "\t")
        for shotPair in efficiencyPairs:
            print(f"{gameLog.iloc[i][shotPair[0]]}/{gameLog.iloc[i][shotPair[1]]}", end="\t")
        print()

def viewSummary(playerName, season):
    playerName = playerName.strip().title()
    gameLog = fetchPlayerData(playerName, season)
    commonAvgs = gameLog[["MIN", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS", "PLUS_MINUS"]].mean()
    print(f"{playerName}'s {season} Season Summary\n{commonAvgs["PTS"]:.2f} | {commonAvgs["REB"]:.2f} | {commonAvgs["AST"]:.2f} | {commonAvgs["BLK"]:.2f}b | {commonAvgs["STL"]:.2f}s")
    print(f"Shooting Splits: {commonAvgs["FG_PCT"]*100:.2f} / {commonAvgs["FG3_PCT"]*100:.2f} / {commonAvgs["FT_PCT"]*100:.2f}")
    gameStats = ["MIN", "PTS", "REB", "AST", "STL", "BLK", "PLUS_MINUS", "TOV", "PF", "OREB", "DREB"]
    efficiencySingles = ["FG_PCT", "FG3_PCT", "FT_PCT"]
    efficiencyPairs = [["FGM", "FGA"], ["FG3M", "FG3A"], ["FTM", "FTA"]]
    print("Last 5 Games:\n#\tMATCHUP\t\tMIN\tPTS\tREB\tAST\tSTL\tBLK\t+/-\tTOV\tPF\tOREB\tDREB\tFG%\t3P%\tFT%\tFGM/A\t3PM/A\tFTM/A")
    for i in range(1, 6):
        print(f"{i}\t{gameLog.iloc[i]["MATCHUP"]}", end = "\t")
        for stat in gameStats:
            print(gameLog.iloc[i][stat], end = "\t")
        for single in efficiencySingles: 
                    print(f"{gameLog.iloc[i][single]*100:.0f}%", end = "\t")
        for shotPair in efficiencyPairs:
             print(f"{gameLog.iloc[i][shotPair[0]]}/{gameLog.iloc[i][shotPair[1]]}", end="\t")
        print()
    changeInPerformance = gameLog.head().mean(numeric_only=True) - gameLog.drop(columns = ["SEASON_ID", "Player_ID", "VIDEO_AVAILABLE", "Game_ID"]).mean(numeric_only=True)
    print("RECENT TRENDS\t\t", end="")
    for stat in gameStats:
         print(f"{changeInPerformance[stat] :+.2f}", end = "\t")
    for single in efficiencySingles:
        print(f"{changeInPerformance[single]*100 :+.2f}%", end = "\t")


loadData()
#viewGameLog("Stephen curry", 2023)
#viewSummary("Stephen Curry", 2025)
#viewSummary("Al Horford", 2010)

