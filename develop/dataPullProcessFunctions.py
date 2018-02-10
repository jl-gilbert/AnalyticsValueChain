import requests
import base64
from datetime import datetime,timedelta
import time

from develop import config

def date_to_api_format(date):
    convert = str(date).replace('-','')
    return(convert)

def send_request_schedule(season,team,daterange):
    try:
        response = requests.get(
        url = 'https://api.mysportsfeeds.com/v1.2/pull/nba/'+season+'/full_game_schedule.json',
            params = {
            "team": team,
            "date": daterange
        },
        headers = {
            "Authorization": "Basic " + base64.b64encode('{}:{}'.format(config.username,config.password).encode('utf-8')).decode('ascii')
        }
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        #print('Response HTTP Response Body: {content}'.format(
            #content=response.content))
        time.sleep(3)
        return response
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        

def send_request_lbj(season,daterange):
    try:
        response = requests.get(
        url = 'https://api.mysportsfeeds.com/v1.2/pull/nba/'+season+'/player_gamelogs.json',
        params = {
            "player":['lebron-james'],
            "date": daterange
        },
        headers = {
            "Authorization": "Basic " + base64.b64encode('{}:{}'.format(config.username,config.password).encode('utf-8')).decode('ascii')
        }
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        #print('Response HTTP Response Body: {content}'.format(
            #content=response.content))
        time.sleep(3)
        return response
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        
        
def request_opponent_stats(season,gameID):
    try:
        response = requests.get(
        url = 'https://api.mysportsfeeds.com/v1.2/pull/nba/' + season + '/game_boxscore.json?gameid=' + gameID,
        params = {
            #"teamstats":['FGA','FTA','OREB','PTS','TOV'],
            "playerstats":'none'
        },
        headers = {
            "Authorization": "Basic " + base64.b64encode('{}:{}'.format(config.username,config.password).encode('utf-8')).decode('ascii')
        }
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        #print('Response HTTP Response Body: {content}'.format(
            #content=response.content))
        time.sleep(3)
        return response
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        
        
def extract_lbj_stats(json_game):
    stats = json_game['stats']
    stats_dict = {}
    stats_dict['Pts'] = int(stats['Pts']['#text'])
    stats_dict['Rbs'] = int(stats['Reb']['#text'])
    stats_dict['Ast'] = int(stats['Ast']['#text'])
    stats_dict['2ptAtt'] = int(stats['Fg2PtAtt']['#text'])
    stats_dict['2ptMade'] = int(stats['Fg2PtMade']['#text'])
    stats_dict['3ptAtt'] = int(stats['Fg3PtAtt']['#text'])
    stats_dict['3ptMade'] = int(stats['Fg3PtMade']['#text'])
    stats_dict['FtAtt'] = int(stats['FtAtt']['#text'])
    stats_dict['FtMade'] = int(stats['FtMade']['#text'])
    stats_dict['PlusMinus'] = int(stats['PlusMinus']['#text'])
    return(stats_dict)

class schedule:
    def __init__(self,season,until_date):
        #set until_date = None for entire season, otherwise use format 'until-yesterday',etc.
        self.season = season
        game_list = []
        #call API for Cavs' season schedule
        data = send_request_schedule(season,'cleveland-cavaliers',until_date).json()
        #add each game to game list
        for game in data['fullgameschedule']['gameentry']:
            if game['homeTeam']['Abbreviation'] == 'CLE':
                game_list.append({'date':datetime.strptime(game['date'],'%Y-%m-%d').date(),
                                  'opponent':game['awayTeam']['Abbreviation'], 'home/away':'home'})
            else:
                game_list.append({'date':datetime.strptime(game['date'],'%Y-%m-%d').date(),
                                  'opponent':game['homeTeam']['Abbreviation'], 'home/away':'away'})
        self.games = game_list
        self.find_lebron_stats_all_games()
        self.sum_lebron_season_stats()
        self.find_days_rest()
        self.find_last_game_per_opponent()
        self.find_stats_since_last_meeting()
        self.calc_opp_efficiency()
        
        
    def find_lebron_stats_all_games(self):
        firstgamedate = self.games[0]['date']
        lastgamedate = self.games[len(self.games)-1]['date']
        #request games logs for lebron james for all games this season
        all_games_json = send_request_lbj(self.season,'from-'+date_to_api_format(firstgamedate)+'-to-'+date_to_api_format(lastgamedate)).json()
        json_game_list = all_games_json['playergamelogs']['gamelogs']
        for game in json_game_list:
            this_game_stats = extract_lbj_stats(game)
            self.games[json_game_list.index(game)]['lbj_pts'] = this_game_stats['Pts']
            self.games[json_game_list.index(game)]['lbj_rbs'] = this_game_stats['Rbs']
            self.games[json_game_list.index(game)]['lbj_ast'] = this_game_stats['Ast']
            self.games[json_game_list.index(game)]['lbj_2pta'] = this_game_stats['2ptAtt'] 
            self.games[json_game_list.index(game)]['lbj_2ptm'] = this_game_stats['2ptMade'] 
            self.games[json_game_list.index(game)]['lbj_3pta'] = this_game_stats['3ptAtt']
            self.games[json_game_list.index(game)]['lbj_3ptm'] = this_game_stats['3ptMade']
            self.games[json_game_list.index(game)]['lbj_fta'] = this_game_stats['FtAtt']
            self.games[json_game_list.index(game)]['lbj_ftm'] = this_game_stats['FtMade']
            self.games[json_game_list.index(game)]['lbj_plusminus'] = this_game_stats['PlusMinus']
            
    def sum_lebron_season_stats(self):
        for game in self.games:
            game_index = self.games.index(game)
            if game_index == 0:
                game['season_2pta'] = 0
                game['season_2ptm'] = 0
                game['season_3pta'] = 0
                game['season_3ptm'] = 0
                game['season_fta'] = 0
                game['season_ftm'] = 0
                game['season_plusminus'] = 0
                game['season_rbs'] = 0
                game['season_ast'] = 0
                game['season_2pt_pct'] = 0
                game['season_3pt_pct'] = 0
                game['season_ft_pct'] = 0
                game['season_2ptpg'] = 0
                game['season_3ptpg'] = 0
                game['season_ftpg'] = 0
                game['season_rpg'] = 0
                game['season_apg'] = 0
                game['season_plusminpg'] = 0
            else:
                last_game = self.games[game_index -1]
                game['season_2pta'] = last_game['lbj_2pta'] + last_game['season_2pta']
                game['season_2ptm'] = last_game['lbj_2ptm'] + last_game['season_2ptm']
                game['season_3pta'] = last_game['lbj_3pta'] + last_game['season_3pta']
                game['season_3ptm'] = last_game['lbj_3ptm'] + last_game['season_3ptm']
                game['season_fta'] = last_game['lbj_fta'] + last_game['season_fta']
                game['season_ftm'] = last_game['lbj_ftm'] + last_game['season_ftm']
                game['season_plusminus'] = last_game['lbj_plusminus'] + last_game['season_plusminus']
                game['season_rbs'] = last_game['lbj_rbs'] + last_game['season_rbs']
                game['season_ast'] = last_game['lbj_ast'] + last_game['season_ast']
                game['season_2pt_pct'] = game['season_2ptm'] / game['season_2pta']
                game['season_3pt_pct'] = game['season_3ptm'] / game['season_3pta']
                game['season_ft_pct'] = game['season_ftm'] / game['season_fta']
                game['season_2ptpg'] = game['season_2ptm'] / game_index
                game['season_3ptpg'] = game['season_3ptm'] / game_index
                game['season_ftpg'] = game['season_ftm'] / game_index
                game['season_rpg'] = game['season_rbs'] / game_index
                game['season_apg'] = game['season_ast'] / game_index
                game['season_plusminpg'] = game['season_plusminus'] / game_index
                
    def find_days_rest(self):
        for game in self.games:
            game_index = self.games.index(game)
            if game_index == 0:
                game['days_rest'] = 0
            else:
                last_game = self.games[game_index -1]
                delta = game['date'] - last_game['date']
                game['days_rest'] = delta.days - 1 
                
        
            
            
        
    def find_last_game_per_opponent(self):
        for game in self.games:
            prev_game_date = None
            #iterate through Cavs' schedule to find last date these 2 teams played
            for prev_game_index in range(1,self.games.index(game)-1):
                if self.games[prev_game_index]['opponent'] == game['opponent']:
                    prev_game_date = self.games[prev_game_index]['date']
            if prev_game_date == None:
                #if teams haven't played before this season, use first day of season as last time they played
                prev_game_date = self.games[0]['date']
            game['last_meeting_date'] = prev_game_date
            

    def find_stats_since_last_meeting(self):
        for game in self.games:
            opponent = game['opponent']
            lastgame = next((oldgame for oldgame in self.games if oldgame['date'] == game['last_meeting_date']),None)
            #get starting values based on what we had last time Cavs played this team
            game_index = self.games.index(game)
            if game_index == 0:
                FGAttAgainst = 0
                FTAttAgainst = 0
                OffRbsAgainst = 0
                PtsAgainst = 0
                TOVAgainst = 0
                FGAtt = 0
                FTAtt = 0
                OffRbs = 0
                Pts = 0
                TOV = 0
            else:
                FGAttAgainst = lastgame['FGAA']
                FTAttAgainst = lastgame['FTAA']
                OffRbsAgainst = lastgame['OREBA']
                PtsAgainst = lastgame['PTSA']
                TOVAgainst = lastgame['TOVA']
                FGAtt = lastgame['FGA']
                FTAtt = lastgame['FTA']
                OffRbs = lastgame['OREB']
                Pts = lastgame['PTS']
                TOV = lastgame['TOV']
                #get range of dates between last meeting with Cavs and now
                daterange = 'from-' + date_to_api_format(game['last_meeting_date']) + '-to-' + date_to_api_format(game['date']-timedelta(days=1))
                #call API for opponent's schedule since last meeting
                opponent_games_json = send_request_schedule(self.season,opponent,daterange).json()
                #make sure opponent has played at least 1 game, otherwise there will only be 'last_updated_on' key
                if len(opponent_games_json['fullgameschedule'].keys()) > 1:
                    opponent_game_list = opponent_games_json['fullgameschedule']['gameentry']
                    opponent_games = []
                    #get game IDs to send in API call for box scores
                    for opp_game in opponent_game_list:
                        opponent_games.append(opp_game['date'].replace('-','') + '-' + 
                                              opp_game['awayTeam']['Abbreviation'] +  '-' + 
                                              opp_game['homeTeam']['Abbreviation'])
                    for opp_game_ID in opponent_games:
                        #call API for each box score of every game the opponent had since last meeting with Cavs
                        print(opp_game_ID)
                        box_score_json = request_opponent_stats(self.season,opp_game_ID).json()
                        #record stats
                        hometeamstats = {"FGA":box_score_json['gameboxscore']['homeTeam']['homeTeamStats']['FgAtt']['#text'],
                                         "FTA":box_score_json['gameboxscore']['homeTeam']['homeTeamStats']['FtAtt']['#text'],
                                         "OREB":box_score_json['gameboxscore']['homeTeam']['homeTeamStats']['OffReb']['#text'],
                                         "TOV":box_score_json['gameboxscore']['homeTeam']['homeTeamStats']['Tov']['#text'],
                                         "PTS":box_score_json['gameboxscore']['homeTeam']['homeTeamStats']['Pts']['#text']}
                        awayteamstats = {"FGA":box_score_json['gameboxscore']['awayTeam']['awayTeamStats']['FgAtt']['#text'],
                                         "FTA":box_score_json['gameboxscore']['awayTeam']['awayTeamStats']['FtAtt']['#text'],
                                         "OREB":box_score_json['gameboxscore']['awayTeam']['awayTeamStats']['OffReb']['#text'],
                                         "TOV":box_score_json['gameboxscore']['awayTeam']['awayTeamStats']['Tov']['#text'],
                                         "PTS":box_score_json['gameboxscore']['awayTeam']['awayTeamStats']['Pts']['#text']}
                        #concatenate this game with aggregating season total
                        if box_score_json['gameboxscore']['game']['homeTeam']['Abbreviation'] == opponent:
                            FGAttAgainst += int(awayteamstats['FGA'])
                            FTAttAgainst += int(awayteamstats['FTA'])
                            OffRbsAgainst += int(awayteamstats['OREB'])
                            PtsAgainst += int(awayteamstats['PTS'])
                            TOVAgainst += int(awayteamstats['TOV'])
                            FGAtt += int(hometeamstats['FGA'])
                            FTAtt += int(hometeamstats['FTA'])
                            OffRbs += int(hometeamstats['OREB'])
                            Pts += int(hometeamstats['PTS'])
                            TOV += int(hometeamstats['TOV'])
                        else:
                            FGAttAgainst += int(hometeamstats['FGA'])
                            FTAttAgainst += int(hometeamstats['FTA'])
                            OffRbsAgainst += int(hometeamstats['OREB'])
                            PtsAgainst += int(hometeamstats['PTS'])
                            TOVAgainst += int(hometeamstats['TOV'])
                            FGAtt += int(awayteamstats['FGA'])
                            FTAtt += int(awayteamstats['FTA'])
                            OffRbs += int(awayteamstats['OREB'])
                            Pts += int(awayteamstats['PTS'])
                            TOV += int(awayteamstats['TOV'])
            #now we have season totals for each stat at the time of this game - add back into main table
            game['FGAA'] = FGAttAgainst
            game['FTAA'] = FTAttAgainst
            game['OREBA'] = OffRbsAgainst
            game['PTSA'] = PtsAgainst
            game['TOVA'] = TOVAgainst
            game['FGA'] = FGAtt
            game['FTA'] = FTAtt
            game['OREB'] = OffRbs
            game['PTS'] = Pts
            game['TOV'] = TOV
            
        
    def calc_opp_efficiency(self):
        for game in self.games:
            game_index = self.games.index(game)
            if game_index == 0:
                game['opp_def_eff'] = 0
                game['opp_off_eff'] = 0
            else:    
                if game['PTSA'] == 0:
                    game['opp_def_eff'] = 0
                    game['opp_off_eff'] = 0
                else:
                    game['opp_def_eff'] = (game['PTSA']/(game['FGAA'] - game['OREBA'] + game['TOVA'] + 0.4*game['FTAA']))*100
                    game['opp_off_eff'] = (game['PTS']/(game['FGA'] - game['OREB'] + game['TOV'] + 0.4*game['FTA']))*100
        
        
