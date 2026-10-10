import time, psycopg, os, pandas as pd
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import leaguegamefinder, playergamelog
from dotenv import load_dotenv
def initializeDB():
    conn = connectDB()
    createTables(conn) #completed
    addPlayers(conn) #completed
    addTeams(conn) #completed
    addLogs(conn) #completed
    addGames(conn) #completed

def connectDB():
    try:
        conn = psycopg.connect(dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"), host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"))
        return conn
    except Exception as e:
        print("Connection failed: ", e)
        return None

def createTables(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE players (player_id INT PRIMARY KEY, first_name TEXT, last_name TEXT)")
        cursor.execute("CREATE TABLE teams (team_id INT PRIMARY KEY, team_name TEXT, abbreviation TEXT)")
        cursor.execute("CREATE TABLE games (game_id INT PRIMARY KEY, game_date DATE, home_id INT, away_id INT, home_score INT, away_score INT)")
        cursor.execute("""CREATE TABLE player_game_stats (player_id INT, game_id INT, min INT, fgm INT, fga INT, 
        fg3m INT, fg3a INT, ftm INT, fta INT, oreb INT, dreb INT, reb INT, ast INT, stl INT, blk INT, tov INT, pf INT, plus_minus INT, PRIMARY KEY (player_id, game_id))""")
        conn.commit()
        print("Table created.")
    except Exception as e:
        conn.rollback() 
        print("Rollback forced: ", e)
    finally:
        cursor.close()
        conn.close()

def addPlayers(conn):
    data = pd.DataFrame(players.get_active_players())
    cursor = conn.cursor()
    try: 
        for i in range(data.shape[0]):
            print(data.iloc[i][["id", "first_name", "last_name"]])
            cursor.execute("INSERT INTO players (player_id, first_name, last_name) VALUES (%s, %s, %s)", (data.iloc[i]["id"], data.iloc[i]["first_name"], data.iloc[i]["last_name"]))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Rollback forced: ", e)
    finally:
        cursor.close()
        conn.close()

def addTeams(conn):
    data = pd.DataFrame(teams.get_teams())
    cursor = conn.cursor()
    try:
        for i in range(data.shape[0]):
            cursor.execute("INSERT INTO teams (team_id, team_name, abbreviation) VALUES (%s, %s, %s)", (data.iloc[i]["id"], data.iloc[i]["full_name"], data.iloc[i]["abbreviation"]))
        conn.commit()
        print("Teams inserted")
    except Exception as e:
        conn.rollback()
        print("Rollback forced: ", e)
    finally:
        cursor.close()
        conn.close()

def addLogs(conn):
    cursor = conn.cursor()
    lastId = -1
    try:
        cursor.execute("SELECT player_id FROM players")
        player_ids = cursor.fetchall()
        for id in player_ids:
            player_data = playergamelog.PlayerGameLog(player_id = id, season = 2025, season_type_all_star = "Regular Season").get_data_frames()[0]
            for row in range(player_data.shape[0]):
                rowData = player_data.iloc[row]
                cursor.execute("""INSERT INTO player_game_stats (player_id, game_id, min, fgm, fga, fg3m, fg3a, ftm, 
                fta, oreb, dreb, reb, ast, stl, blk, tov, pf, plus_minus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                (rowData["Player_ID"], rowData["Game_ID"], rowData["MIN"], rowData["FGM"], rowData["FGA"], rowData["FG3M"], rowData["FG3A"], rowData["FTM"],
                 rowData["FTA"], rowData["OREB"], rowData["DREB"], rowData["REB"], rowData["AST"], rowData["STL"], rowData["BLK"], rowData["TOV"], rowData["PF"], rowData["PLUS_MINUS"]))
            print(id, "done")
            time.sleep(2)
            lastId = id
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Rollback forced: ", e)
        print("Last id was: " + lastId)
        time.sleep(40)
    finally:
        cursor.close()
        conn.close()

def addGames(conn):
    cursor = conn.cursor()
    try:
        data = leaguegamefinder.LeagueGameFinder(season_nullable="2025-26", season_type_nullable="Regular Season").get_data_frames()[0].sort_values(by="GAME_ID").reset_index()
        for i in range(data.shape[0]//2):
            firstLog = data.iloc[2*i]
            secondLog = data.iloc[2*i + 1]
            matchup = firstLog["MATCHUP"]
            vsIndex = matchup.find("vs.")
            if vsIndex is not -1:
                homeTeam = matchup[:vsIndex].strip()
            else:
                atIndex = matchup.find("@")
                homeTeam = matchup[atIndex+1:].strip()
            if(firstLog["TEAM_ABBREVIATION"]==homeTeam):
                homeTeamId = firstLog["TEAM_ID"]
                homeScore = firstLog["PTS"]
                awayTeamId = secondLog["TEAM_ID"]
                awayScore = secondLog["PTS"]
            else:
                homeTeamId = secondLog["TEAM_ID"]
                homeScore = secondLog["PTS"]
                awayTeamId = firstLog["TEAM_ID"]
                awayScore = firstLog["PTS"]  
            cursor.execute("INSERT INTO games (game_id, game_date, home_id, away_id, home_score, away_score) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (firstLog["GAME_ID"], firstLog["GAME_DATE"], homeTeamId, awayTeamId, homeScore, awayScore))
            print(homeTeam, "game added")
        conn.commit()
    except Exception as e:
        print("Had to rollback: ", e)
    finally:
        cursor.close()
        conn.close()


initializeDB()