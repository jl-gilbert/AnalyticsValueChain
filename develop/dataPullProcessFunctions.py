"""Functions and classes for pulling data from API and processing for database

This module provides functions and a class that can be used for pulling from
the MySportsFeeds.com API. It has several functions to make API calls for
various types of responses, as well as some functions for altering Python
objects into a format suitable for a component of an API call or into a format
suitable for storage in a database, depending on the case.
"""

import requests
import base64
from datetime import datetime, timedelta
import time

from develop import config


def date_to_api_format(date):
    """Function to convert date to string as needed by API call

    Args:
        date (datetime.date()): Date to be converted

    Returns:
        convert (str): String in format needeed for API call
    """
    convert = str(date).replace('-', '')
    return(convert)


def send_request_schedule(season, team, daterange):
    """Function to call API for a schedule

    Args:
        season (str): Season for the schedule. Convention is the format as in
            the following example: '2015-2016-regular'
        team (str): Team for the schedule. Convention is the 3 letter all caps
            abbreviation, such as 'CLE'
        daterange (str): Dates for which the schedule is requested. Given date
            must be in form such as '20151027' for Oct 27, 2015. 'today' also
            works. For range, use 'from-20151027-to-20160401'. 'until-today'
            also works. If None object is passed, full season is requested.

    Returns:
        response (requests.models.Response): Response from API call
    """
    try:
        response = requests.get(
            url='https://api.mysportsfeeds.com/v1.2/pull/nba/' + season +
            '/full_game_schedule.json',
            params={
                    "team": team,
                    "date": daterange
                    },
            headers={
                    "Authorization": "Basic " +
                    base64.b64encode('{}:{}'.format(
                            config.username,
                            config.password
                            ).encode('utf-8')).decode('ascii')
                    }
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        time.sleep(3)
        return response
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def send_request_lbj(season, daterange):
    """Function to call API for LeBron James game statistics

    Args:
        season (str): Season for the stats. Convention is the format as in
            the following example: '2015-2016-regular'
        daterange (str): Dates for which the stats are requested. Given date
            must be in form such as '20151027' for Oct 27, 2015. 'today' also
            works. For range, use 'from-20151027-to-20160401'. 'until-today'
            also works. If None object is passed, stats for each game in the
            season are requested.

    Returns:
        response (requests.models.Response): Response from API call
    """
    try:
        response = requests.get(
                url='https://api.mysportsfeeds.com/v1.2/pull/nba/' +
                season + '/player_gamelogs.json',
                params={
                        "player": ['lebron-james'],
                        "date": daterange
                        },
                headers={
                        "Authorization": "Basic " +
                        base64.b64encode('{}:{}'.format(
                                config.username,
                                config.password
                                ).encode('utf-8')).decode('ascii')
                        }
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        time.sleep(3)
        return response
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def request_opponent_stats(season, gameID):
    """Function to call API for a given game. Used to get opponent stats

    Args:
        season (str): Season for the stats. Convention is the format as in
        the following example: '2015-2016-regular'
        gameID (str): Game for which the stats are requested. Must in format
        'date-awayteam-hometeam' such as '20151027-CLE-CHI'.

    Returns:
        response (requests.models.Response): Response from API call
    """

    try:
        response = requests.get(
                url='https://api.mysportsfeeds.com/v1.2/pull/nba/' +
                season + '/game_boxscore.json?gameid=' + gameID,
                params={
                        # "teamstats":['FGA','FTA','OREB','PTS','TOV'],
                        "playerstats": 'none'
                        },
                headers={
                        "Authorization": "Basic " +
                        base64.b64encode('{}:{}'.format(
                                config.username,
                                config.password
                                ).encode('utf-8')).decode('ascii')
                        }
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        time.sleep(3)
        return response
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def extract_lbj_stats(json_game):
    """Function to extract relevant LeBron James stats.

    The dictionary passed to this function is part of the output of the .json()
    method applied to the response object returned by the send_request_lbj()
    function. Before passing to this, that json must be parsed to represent a
    single game, if necessary.

    Args:
        json_game (dict): dictionary that is an element of the list associated
            with the key 'gamelogs' of the dict associated with the key
            'playergamelogs' of the root json dict obtain by calling the
            .json() method on the output of send_request_lbj

    Returns:
        stats_dict (dict): Dictionary with all required individual stats for
            LeBron James for the given game.
    """
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
    stats_dict['MinutesPlayed'] = int(stats['MinSeconds']['#text']) / 60
    return(stats_dict)


def send_request_cavsgame(season, date):
    """Function to call API for Cleveland Cavs game scores.

    This function is used to determine the winner of a Cavs game.

    Args:
        season (str): Season for the game results.
        daterange (str): Date of the game for which the results are requested.
            Given date must be in form such as '20151027' for Oct 27, 2015.
            'today' also works.

    Returns:
        response (requests.models.Response): Response from API call
    """
    try:
        response = requests.get(
                url='https://api.mysportsfeeds.com/v1.2/pull/nba/' +
                season + '/scoreboard.json?fordate=' + date,
                params={
                        "team": ['CLE'],
                        },
                headers={
                        "Authorization": "Basic " +
                        base64.b64encode('{}:{}'.format(
                                config.username,
                                config.password
                                ).encode('utf-8')).decode('ascii')
                        }
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        time.sleep(3)
        return response
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def find_opponent_stats(season, from_date, to_date, starting_values, opponent):
    """Function to find cumulative stats for an opponent between 2 dates.

    This function is used to...

    Args:
        season (str): specifies season of dates, needed for API call.
        from_date (datetime.date()): gives beginning date of period, presumably
            the date of the last game between opponent and Cavs.
        to_date (datetime.date()): gives ending date of period, presumably the
            day before the game against the Cavs in question.
        starting_values (dict): dictionary with stats for opponent at start of
            period so the function can add onto them.
        opponent (str): 3 letter abbreviation for opponent, such as 'BOS'.

    Returns:
        starting_values (dict) : the starting values for stats modified by
            concatenating stats that happened during the specified period. If
            no games occured for the opponent during the specified timeframe
            the inputed values will be returned to reflect so. This is useful
            for the daily updates that will occur when the app is live.
    """
    daterange = 'from-' + date_to_api_format(
            from_date) + '-to-' + date_to_api_format(
                to_date)
    # call API for opponent's schedule since last meeting
    opponent_games_json = send_request_schedule(
            season, opponent, daterange).json()
    # make sure opponent has played at least 1 game,
    # otherwise there will only be 'last_updated_on' key
    if len(opponent_games_json['fullgameschedule'].keys()) > 1:
        opponent_game_list = opponent_games_json[
                'fullgameschedule']['gameentry']
        opponent_games = []
        # get game IDs to send in API call for box scores
        for opp_game in opponent_game_list:
            opponent_games.append(
                    opp_game['date'].replace('-', '') + '-' +
                    opp_game['awayTeam']['Abbreviation'] + '-' +
                    opp_game['homeTeam']['Abbreviation'])
        for opp_game_ID in opponent_games:
            # call API for each box score of every game the
            # opponent had between the two dates specified (inclusive)
            print(opp_game_ID)
            box_score_json = request_opponent_stats(
                    season, opp_game_ID).json()
            # record stats
            hometeamstats = {
                     "FGA": box_score_json[
                             'gameboxscore'][
                             'homeTeam'][
                             'homeTeamStats']['FgAtt']['#text'],
                     "FTA": box_score_json[
                             'gameboxscore'][
                             'homeTeam'][
                             'homeTeamStats']['FtAtt']['#text'],
                     "OREB": box_score_json[
                             'gameboxscore'][
                             'homeTeam'][
                             'homeTeamStats']['OffReb']['#text'],
                     "TOV": box_score_json[
                             'gameboxscore'][
                             'homeTeam'][
                             'homeTeamStats']['Tov']['#text'],
                     "PTS": box_score_json[
                             'gameboxscore'][
                             'homeTeam'][
                             'homeTeamStats']['Pts']['#text']}
            awayteamstats = {
                     "FGA": box_score_json[
                             'gameboxscore'][
                             'awayTeam'][
                             'awayTeamStats']['FgAtt']['#text'],
                     "FTA": box_score_json[
                             'gameboxscore'][
                             'awayTeam'][
                             'awayTeamStats']['FtAtt']['#text'],
                     "OREB": box_score_json[
                             'gameboxscore'][
                             'awayTeam'][
                             'awayTeamStats']['OffReb']['#text'],
                     "TOV": box_score_json[
                             'gameboxscore'][
                             'awayTeam'][
                             'awayTeamStats']['Tov']['#text'],
                     "PTS": box_score_json[
                             'gameboxscore'][
                             'awayTeam'][
                             'awayTeamStats']['Pts']['#text']}
            # concatenate this game with aggregating period total
            if box_score_json['gameboxscore']['game']['homeTeam'][
                    'Abbreviation'] == opponent:
                starting_values['FGAttAgainst'] += int(awayteamstats['FGA'])
                starting_values['FTAttAgainst'] += int(awayteamstats['FTA'])
                starting_values['OffRbsAgainst'] += int(awayteamstats['OREB'])
                starting_values['PtsAgainst'] += int(awayteamstats['PTS'])
                starting_values['TOVAgainst'] += int(awayteamstats['TOV'])
                starting_values['FGAtt'] += int(hometeamstats['FGA'])
                starting_values['FTAtt'] += int(hometeamstats['FTA'])
                starting_values['OffRbs'] += int(hometeamstats['OREB'])
                starting_values['Pts'] += int(hometeamstats['PTS'])
                starting_values['TOV'] += int(hometeamstats['TOV'])
                if int(hometeamstats['PTS']) > int(
                        awayteamstats['PTS']):
                    starting_values['OppWins'] += 1
                else:
                    starting_values['OppLosses'] += 1
            else:
                starting_values['FGAttAgainst'] += int(hometeamstats['FGA'])
                starting_values['FTAttAgainst'] += int(hometeamstats['FTA'])
                starting_values['OffRbsAgainst'] += int(hometeamstats['OREB'])
                starting_values['PtsAgainst'] += int(hometeamstats['PTS'])
                starting_values['TOVAgainst'] += int(hometeamstats['TOV'])
                starting_values['FGAtt'] += int(awayteamstats['FGA'])
                starting_values['FTAtt'] += int(awayteamstats['FTA'])
                starting_values['OffRbs'] += int(awayteamstats['OREB'])
                starting_values['Pts'] += int(awayteamstats['PTS'])
                starting_values['TOV'] += int(awayteamstats['TOV'])
                if int(awayteamstats['PTS']) > int(
                        hometeamstats['PTS']):
                    starting_values['OppWins'] += 1
                else:
                    starting_values['OppLosses'] += 1
    return starting_values


class schedule:
    """Class containing all needed data for a given season.

    Attributes:
        season (str): string representing the season for which this object
            contains data.
        games (list): list of dictionaries, each dictionary is for a particular
            game.
    """

    def __init__(self, season, until_date):
        """Constructor for a schedule object.

        Args:
            season (str): string representing season for this schedule object.
                Must be in format as is required for send_request_schedule()
                function.
            until_date (str): string representing dates for the object to be
                built around. Can build a partial season for testing purposes.
                Must be in format as is required for send_request_schedule()
                function. If a None object is passed, the full season of data
                will be assembled.
        """

        # set until_date = None for entire season,
        # otherwise use format 'until-yesterday',etc.
        self.season = season
        game_list = []
        # call API for Cavs' season schedule
        data = send_request_schedule(season,
                                     'cleveland-cavaliers',
                                     until_date).json()
        # add each game to game list
        for game in data['fullgameschedule']['gameentry']:
            if game['homeTeam']['Abbreviation'] == 'CLE':
                game_list.append({'date': datetime.strptime(
                        game['date'], '%Y-%m-%d').date(),
                        'opponent': game['awayTeam']['Abbreviation'],
                        'home/away': 'home'})
            else:
                game_list.append({'date': datetime.strptime(
                        game['date'], '%Y-%m-%d').date(),
                        'opponent': game['homeTeam']['Abbreviation'],
                        'home/away': 'away'})
        self.games = game_list
        self.find_lebron_stats_all_games()
        self.sum_lebron_season_stats()
        self.find_days_rest()
        self.find_last_game_per_opponent()
        self.find_stats_since_last_meeting()
        self.calc_opp_efficiency()

    def find_lebron_stats_all_games(self):
        """Adds LeBron James individual game stats to data.

        Modifies dicts inside games attribute so that they include LeBron James
        stats for each individual game.

        Args:
            None

        Returns:
            None
        """
        firstgamedate = self.games[0]['date']
        lastgamedate = self.games[len(self.games)-1]['date']
        # request games logs for lebron james for all games this season
        all_games_json = send_request_lbj(
                self.season, 'from-' + date_to_api_format(firstgamedate) +
                '-to-' + date_to_api_format(lastgamedate)).json()
        json_game_list = all_games_json['playergamelogs']['gamelogs']
        for game in json_game_list:
            this_game_stats = extract_lbj_stats(game)
            self.games[json_game_list.index(game)][
                    'lbj_pts'] = this_game_stats['Pts']
            self.games[json_game_list.index(game)][
                    'lbj_rbs'] = this_game_stats['Rbs']
            self.games[json_game_list.index(game)][
                    'lbj_ast'] = this_game_stats['Ast']
            self.games[json_game_list.index(game)][
                    'lbj_2pta'] = this_game_stats['2ptAtt']
            self.games[json_game_list.index(game)][
                    'lbj_2ptm'] = this_game_stats['2ptMade']
            self.games[json_game_list.index(game)][
                    'lbj_3pta'] = this_game_stats['3ptAtt']
            self.games[json_game_list.index(game)][
                    'lbj_3ptm'] = this_game_stats['3ptMade']
            self.games[json_game_list.index(game)][
                    'lbj_fta'] = this_game_stats['FtAtt']
            self.games[json_game_list.index(game)][
                    'lbj_ftm'] = this_game_stats['FtMade']
            self.games[json_game_list.index(game)][
                    'lbj_plusminus'] = this_game_stats['PlusMinus']
            if this_game_stats['MinutesPlayed'] == 0:
                self.games[json_game_list.index(game)]['DNP'] = True
            else:
                self.games[json_game_list.index(game)]['DNP'] = False

    def sum_lebron_season_stats(self):
        """Adds LeBron James cumulative stats to data.

        Modifies dicts inside games attribute so that they include LeBron James
        cumulative stats for the season at the point of the beginning of each
        particular game.

        Args:
            None

        Returns:
            None
        """
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
                game['cavsWins'] = 0
                game['cavsLosses'] = 0
                game['gamesMissed'] = 0
            else:
                last_game = self.games[game_index - 1]
                game['season_2pta'] = last_game[
                        'lbj_2pta'] + last_game['season_2pta']
                game['season_2ptm'] = last_game[
                        'lbj_2ptm'] + last_game['season_2ptm']
                game['season_3pta'] = last_game[
                        'lbj_3pta'] + last_game['season_3pta']
                game['season_3ptm'] = last_game[
                        'lbj_3ptm'] + last_game['season_3ptm']
                game['season_fta'] = last_game[
                        'lbj_fta'] + last_game['season_fta']
                game['season_ftm'] = last_game[
                        'lbj_ftm'] + last_game['season_ftm']
                game['season_plusminus'] = last_game[
                        'lbj_plusminus'] + last_game['season_plusminus']
                game['season_rbs'] = last_game[
                        'lbj_rbs'] + last_game['season_rbs']
                game['season_ast'] = last_game[
                        'lbj_ast'] + last_game['season_ast']
                game['season_2pt_pct'] = game[
                        'season_2ptm'] / game['season_2pta']
                game['season_3pt_pct'] = game[
                        'season_3ptm'] / game['season_3pta']
                game['season_ft_pct'] = game[
                        'season_ftm'] / game['season_fta']
                game['gamesMissed'] = last_game[
                        'gamesMissed'] + last_game['DNP']
                game['season_2ptpg'] = game['season_2ptm'] / game_index - game[
                        'gamesMissed']
                game['season_3ptpg'] = game['season_3ptm'] / game_index - game[
                        'gamesMissed']
                game['season_ftpg'] = game['season_ftm'] / game_index - game[
                        'gamesMissed']
                game['season_rpg'] = game['season_rbs'] / game_index - game[
                        'gamesMissed']
                game['season_apg'] = game['season_ast'] / game_index - game[
                        'gamesMissed']
                game['season_plusminpg'] = game[
                        'season_plusminus'] / game_index
                last_game_date = date_to_api_format(last_game['date'])
                last_game_json = send_request_cavsgame(
                        self.season, last_game_date).json()
                if last_game_json['scoreboard']['gameScore'][0][
                        'game']['homeTeam']['Abbreviation'] == "CLE":
                    last_game_cavs = int(last_game_json[
                            'scoreboard']['gameScore'][0]['homeScore'])
                    last_game_opp = int(last_game_json[
                            'scoreboard']['gameScore'][0]['awayScore'])
                else:
                    last_game_cavs = int(last_game_json['scoreboard'][
                            'gameScore'][0]['awayScore'])
                    last_game_opp = int(last_game_json['scoreboard'][
                            'gameScore'][0]['homeScore'])
                if last_game_cavs > last_game_opp:
                    game['cavsWins'] = last_game['cavsWins'] + 1
                    game['cavsLosses'] = last_game['cavsLosses']
                else:
                    game['cavsWins'] = last_game['cavsWins']
                    game['cavsLosses'] = last_game['cavsLosses'] + 1

    def find_days_rest(self):
        """Adds days of rest to data.

        Modifies dicts inside games attribute so that they include the number
        of days of rest the Cavaliers had before each game. The first game uses
        0 for this value, which will be irrelevant because that game will not
        be used in model training or validation.

        Args:
            None

        Returns:
            None
        """
        for game in self.games:
            game_index = self.games.index(game)
            if game_index == 0:
                game['days_rest'] = 0
            else:
                last_game = self.games[game_index - 1]
                delta = game['date'] - last_game['date']
                game['days_rest'] = delta.days - 1

    def find_last_game_per_opponent(self):
        """Adds date the Cavs last played each opponent to the data.

        Modifies dicts inside games attribute so that they include the date of
        the Cavs' last meeting with the opponent of each game. If the teams
        have not yet met in the given season, the first day of the season is
        used.

        Args:
            None

        Returns:
            None
        """
        for game in self.games:
            prev_game_date = None
            # iterate through Cavs' schedule to find last date
            # these 2 teams played
            for prev_game_index in range(1, self.games.index(game) - 1):
                if self.games[prev_game_index]['opponent'] == game['opponent']:
                    prev_game_date = self.games[prev_game_index]['date']
            if prev_game_date is None:
                # if teams haven't played before this season,
                # use first day of season as last time they played
                prev_game_date = self.games[0]['date']
            game['last_meeting_date'] = prev_game_date

    def find_stats_since_last_meeting(self):
        """Adds opponent team cumulative stats to the data.

        Modifies dicts inside games attribute so that they include each
        opponent team's cumulative stats at the point of the beginning of the
        particular game.

        Args:
            None

        Returns:
            None
        """
        for game in self.games:
            opponent = game['opponent']
            lastgame = next((oldgame for oldgame in self.games if oldgame[
                    'date'] == game['last_meeting_date']), None)
            # get starting values based on what we had last time Cavs played
            # this team
            game_index = self.games.index(game)
            last_stats = {}
            if game_index == 0:
                last_stats['FGAttAgainst'] = 0
                last_stats['FTAttAgainst'] = 0
                last_stats['OffRbsAgainst'] = 0
                last_stats['PtsAgainst'] = 0
                last_stats['TOVAgainst'] = 0
                last_stats['FGAtt'] = 0
                last_stats['FTAtt'] = 0
                last_stats['OffRbs'] = 0
                last_stats['Pts'] = 0
                last_stats['TOV'] = 0
                last_stats['OppWins'] = 0
                last_stats['OppLosses'] = 0
                stat_update = last_stats
            else:
                last_stats['FGAttAgainst'] = lastgame['FGAA']
                last_stats['FTAttAgainst'] = lastgame['FTAA']
                last_stats['OffRbsAgainst'] = lastgame['OREBA']
                last_stats['PtsAgainst'] = lastgame['PTSA']
                last_stats['TOVAgainst'] = lastgame['TOVA']
                last_stats['FGAtt'] = lastgame['FGA']
                last_stats['FTAtt'] = lastgame['FTA']
                last_stats['OffRbs'] = lastgame['OREB']
                last_stats['Pts'] = lastgame['PTS']
                last_stats['TOV'] = lastgame['TOV']
                last_stats['OppWins'] = lastgame['OPPW']
                last_stats['OppLosses'] = lastgame['OPPL']
                # get range of dates between last meeting with Cavs and now
                stat_update = find_opponent_stats(
                        self.season,
                        game['last_meeting_date'],
                        game['date'] - timedelta(days=1),
                        last_stats,
                        opponent)
            # now we have season totals for each stat at the time of this game
            # add back into main table
            game['FGAA'] = stat_update['FGAttAgainst']
            game['FTAA'] = stat_update['FTAttAgainst']
            game['OREBA'] = stat_update['OffRbsAgainst']
            game['PTSA'] = stat_update['PtsAgainst']
            game['TOVA'] = stat_update['TOVAgainst']
            game['FGA'] = stat_update['FGAtt']
            game['FTA'] = stat_update['FTAtt']
            game['OREB'] = stat_update['OffRbs']
            game['PTS'] = stat_update['Pts']
            game['TOV'] = stat_update['TOV']
            game['OPPW'] = stat_update['OppWins']
            game['OPPL'] = stat_update['OppLosses']

    def calc_opp_efficiency(self):
        """Adds opponents' defensive and offensive efficiency ratings to data.

        Modifies dicts inside games attribute so that they include each
        opponent's season offensive and defensive efficieny ratings at the
        beginning of the particular game, based on the opponent's cumulative
        statistics as added by find_stats_since_last_meeting method.

        Args:
            None

        Returns:
            None
        """
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
                    game['opp_def_eff'] = (
                            game['PTSA']/(
                                    game['FGAA'] - game[
                                            'OREBA'] + game[
                                            'TOVA'] + 0.4*game['FTAA']))*100
                    game['opp_off_eff'] = (
                            game['PTS']/(
                                    game['FGA'] - game[
                                            'OREB'] + game[
                                            'TOV'] + 0.4*game['FTA']))*100
