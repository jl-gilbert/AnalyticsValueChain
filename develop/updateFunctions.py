"""Functions for executing daily update to database.

This module provides several functions that execute the required daily update
to the database reflecting results of any games that were in the database but
without results, then finding the next upcoming game and adding it to the
database without results, or just making sure the opponent's stats are up to
date if no Cavaliers games have occurred since the last update.
"""

import sys
sys.path.append("../")
from app import app, db
from develop import dataPullProcessFunctions as dppf
from app.models import Game
from datetime import datetime, timedelta
import logging


def pull_from_db(season):
    """Function to pull all data from a given season into workspace.

    This function pulls all data from presumably the current season so that
    it can be used to check the type of update needed and/or for aggregating
    new season-long statistics based on new results.

    Args:
        season (str): name of season data to pull in, like '2017-2018-regular'

    Returns:
        games (list): list of app.models.Game objects
    """
    games = Game.query.filter_by(season=season).all()
    logging.debug('Succesfull pull of all game data from db.')
    return games


def find_next_opponent(season, today):
    """Function to find basic details about the next game on the schedule

    This function finds the next game on the schedule that has not been played
    as of 'today'.

    Args:
        today (datetime.date()): date object, if datetime.now().date() is
            passed, the real today will be used.

    Returns:
        next_game_info (dict): dictionary with opponent, date, and home/away
            status for next upcoming game. If there is no regular season game
            within the next 15 days, an empty dictionary is returned.
    """
    next_game_info = {}
    search_date_end = dppf.date_to_api_format(today + timedelta(days=15))
    today_code = dppf.date_to_api_format(today)
    logging.debug('Searching for next game.')
    upcomingjson = dppf.send_request_schedule(
            season,
            'CLE', 'from-' + today_code + '-to-' + search_date_end).json()
    # confirm there are any upcoming games, otherwise return empty dictionary
    if len(upcomingjson['fullgameschedule']) > 1:
        logging.debug('Next game found.')
        nextgame = upcomingjson['fullgameschedule']['gameentry'][0]
        next_game_info['date'] = datetime.strptime(nextgame['date'],
                                                   '%Y-%m-%d').date()
        if nextgame['awayTeam']['Abbreviation'] == 'CLE':
            next_game_info['home/away'] = 'away'
            next_game_info['opponent'] = nextgame['homeTeam']['Abbreviation']
        else:
            next_game_info['home/away'] = 'home'
            next_game_info['opponent'] = nextgame['awayTeam']['Abbreviation']
    return next_game_info


def reverse_engineer_stats(games_played, data):
    """Function for determining season totals based on data in db

    For the purposes of aggregating with data from new game, this function
    reverse engineers what season totals were before that game.

    Args:
        games_played (int): number of games LeBron has played this season, for
            the purpose of calculating totals based on per-game figures stored
            in the db
        data (dict): dictionary with season per-game averages and shooting
            percentages, from which season totals can be derived. Must include
            keys: 'rpg', 'apg', 'plusmin', '2ptm', '3ptm', 'ftm' (all season
            per-game averages), '2pt_pct', '3pt_pct', and 'ft_pct' (season
            percentages).

    Returns:
        statdict (dict): dictionary with season totals for rebounds, assits,
            plus/minus, and 2pt/3pt/ft made and attempted.
        """
    statdict = {
        'season_rebounds': data['rpg'] * games_played,
        'season_assists': data['apg'] * games_played,
        'season_plusminus': data['plusmin'] * games_played,
        'season_2ptm': data['2ptm'] * games_played,
        'season_3ptm': data['3ptm'] * games_played,
        'season_ftm': data['ftm'] * games_played,
        'season_2pta': data['2ptm'] * games_played / data['2pt_pct'],
        'season_3pta': data['3ptm'] * games_played / data['3pt_pct'],
        'season_fta': data['ftm'] * games_played / data['ft_pct']}
    return statdict


def opp_stat_update(season, season_start_date, today, opponent):
    """Function that provides up-to-date stats for opponent.

    This function will find an opponent's wins, losses, offensive efficiency
    rating, and defensive efficiency rating through the season up to the value
    of 'today' provided.

    Args:
        season (str): season of the date on which we are updating, like
            '2017-2018-regular'
        season_start_date (datetime.date()): date of the first game of this
            season
        today (datetime.date()): date of 'today', or day we are doing update
            for
        opponent (str): 3 letter abbreviation for opponent whose stats we are
            updating, like 'BOS'

    Returns:
        upcoming_opp_stats (dict): dictionary with up-to-date wins, losses,
            defensive efficiency rating, and offensive efficiency rating for
            opponent
    """
    print("Updating opponent stats.")
    starting_values = {
        'FGAttAgainst': 0,
        'FTAttAgainst': 0,
        'OffRbsAgainst': 0,
        'PtsAgainst': 0,
        'TOVAgainst': 0,
        'FGAtt': 0,
        'FTAtt': 0,
        'OffRbs': 0,
        'Pts': 0,
        'TOV': 0,
        'OppWins': 0,
        'OppLosses': 0}
    opponent_stats = dppf.find_opponent_stats(
            season, season_start_date, today - timedelta(days=1),
            starting_values, opponent)
    upcoming_opp_stats = {
        'opp_def_eff': (opponent_stats['PtsAgainst']/(
            opponent_stats[
                    'FGAttAgainst'] - opponent_stats[
                            'OffRbsAgainst'] + opponent_stats[
                'TOVAgainst'] + 0.4*opponent_stats['FTAttAgainst']))*100,
        'opp_off_eff': (opponent_stats['Pts']/(
            opponent_stats[
                    'FGAtt'] - opponent_stats['OffRbs'] + opponent_stats[
                'TOV'] + 0.4*opponent_stats['FTAtt']))*100,
        'OPPW': opponent_stats['OppWins'],
        'OPPL': opponent_stats['OppLosses']}
    return upcoming_opp_stats


def full_daily_update(today, datapull, database):
    """Function to write results of last game and return info on upcoming game

    This function is used when a game has been completed since the last time
    the database updated. It will edit the bottom row in the database to
    include the stats from said completed game. It will then return a
    dictionary of all available info for the next upcoming game so that can
    be written to the database (though this function does not perform that
    write). If there is no game upcoming in the next 15 days to return the info
    for, the function will return a string saying so and also print that string
    to the console.

    Args:
        today (datetime.date()): date of 'today', or day we are doing update
            for
        datapull (list): the list of app.models.Game objects returned by pull
            from db for full season.
        db (flask_sqlalchemy.SQLAlchemy): database to write the edit to

    Returns:
        next_game (dict): dictionary with date, opponent, and home/away status
            for next game on the schedule that is not yet in the database. This
            is only returned if there is a new game within the next 15 days
        error_string (str): string returned if there is not a new game
    """
    # datapull is result of Game.query.filter_by(season).all()
    # db is database to write updates to
    # first find stats from just-completed game
    logging.info('Making full daily update')
    last_game = datapull[len(datapull) - 1]
    logging.debug('last_game object is of type %s', type(last_game))
    logging.debug('last game was on %s against %s',
                  last_game.date, last_game.opponent)
    this_season = last_game.season
    lastgamejson = dppf.send_request_lbj(this_season,
                                         dppf.date_to_api_format(
                                                 last_game.date.date())).json()
    lastgamestats = dppf.extract_lbj_stats(
            lastgamejson['playergamelogs']['gamelogs'][0])
    last_game.pts = lastgamestats['Pts']
    last_game.rbs = lastgamestats['Rbs']
    last_game.ast = lastgamestats['Ast']
    if lastgamestats['MinutesPlayed'] == 0:
        last_game.lbj_DNP = True
    else:
        last_game.lbj_DNP = False
    # add in game stats to bottom row of database-most recently completed game
    database.session.commit()
    logging.info('Last game stats added.')
    # now move on to upcoming game
    next_game = find_next_opponent(this_season, today)
    # confirm that we were able to find an upcoming game
    if len(next_game) > 0:
        delta = next_game['date'] - last_game.date.date()
        next_game['days_rest'] = delta.days - 1
        next_game['lbj_games_missed'] = last_game.lbj_games_missed + last_game.lbj_DNP
        games_played = len(datapull) - next_game['lbj_games_missed']
        last_game_season_stats = {
            'rpg': last_game.lbj_rbs_pgm,
            'apg': last_game.lbj_ast_pgm,
            'plusmin': last_game.lbj_plusminpg,
            '2ptm': last_game.lbj_2pt_mpg,
            '3ptm': last_game.lbj_3pt_mpg,
            'ftm': last_game.lbj_ft_mpg,
            '2pt_pct': last_game.lbj_2pt_pct,
            '3pt_pct': last_game.lbj_3pt_pct,
            'ft_pct': last_game.lbj_ft_pct}
        # find out season totals at start of last game in db
        season_stats = reverse_engineer_stats(games_played - (
                1 - last_game.lbj_DNP), last_game_season_stats)
        # add results of last game to totals to find
        # season stats at start of upcoming game
        next_game['season_rpg'] = (season_stats[
                'season_rebounds'] + lastgamestats['Rbs']) / games_played
        next_game['season_apg'] = (season_stats[
                'season_assists'] + lastgamestats['Ast']) / games_played
        next_game['season_plusminpg'] = (season_stats[
                'season_plusminus'] + lastgamestats[
                        'PlusMinus']) / games_played
        next_game['season_2ptpg'] = (season_stats[
                'season_2ptm'] + lastgamestats['2ptMade']) / games_played
        next_game['season_3ptpg'] = (season_stats[
                'season_3ptm'] + lastgamestats['3ptMade']) / games_played
        next_game['season_ftpg'] = (season_stats[
                'season_ftm'] + lastgamestats['FtMade']) / games_played
        next_game['season_2pt_pct'] = (season_stats[
                'season_2ptm'] + lastgamestats['2ptMade']) / (
            season_stats['season_2pta'] + lastgamestats['2ptAtt'])
        next_game['season_3pt_pct'] = (season_stats[
                'season_3ptm'] + lastgamestats['3ptMade']) / (
            season_stats['season_3pta'] + lastgamestats['3ptAtt'])
        next_game['season_ft_pct'] = (season_stats[
                'season_ftm'] + lastgamestats['FtMade']) / (
            season_stats['season_fta'] + lastgamestats['FtAtt'])
        # find out if Cavs won last game
        last_game_date = dppf.date_to_api_format(last_game.date.date())
        last_game_json = dppf.send_request_cavsgame(
                        last_game.season, last_game_date).json()
        if last_game_json['scoreboard']['gameScore'][0][
                        'game']['homeTeam']['Abbreviation'] == "CLE":
            last_game_cavs = int(last_game_json['scoreboard'][
                            'gameScore'][0]['homeScore'])
            last_game_opp = int(last_game_json['scoreboard'][
                            'gameScore'][0]['awayScore'])
        else:
            last_game_cavs = int(last_game_json['scoreboard'][
                            'gameScore'][0]['awayScore'])
            last_game_opp = int(last_game_json['scoreboard'][
                            'gameScore'][0]['homeScore'])
        if last_game_cavs > last_game_opp:
            next_game['cavsWins'] = last_game.cavsWins + 1
            next_game['cavsLosses'] = last_game.cavsLosses
        else:
            next_game['cavsWins'] = last_game.cavsWins
            next_game['cavsLosses'] = last_game.cavsLosses + 1
        # find opponent cumulative season stats
        season_firstgame_date = datapull[0].date.date()
        upcoming_opp_stats = opp_stat_update(
                last_game.season, season_firstgame_date, today, next_game[
                        'opponent'])
        next_game['opp_def_eff'] = upcoming_opp_stats['opp_def_eff']
        next_game['opp_off_eff'] = upcoming_opp_stats['opp_off_eff']
        next_game['OPPW'] = upcoming_opp_stats['OPPW']
        next_game['OPPL'] = upcoming_opp_stats['OPPL']
        return next_game
    # if empty dict was returned by find_next_opponent, return str
    else:
        error_string = "No new game"
        return error_string
        logging.warning("No upcoming games on regular season schedule.")


def make_update(today, season, database):
    """Function to make required daily update to db.

    This function will, depending on the contents of the bottom row of the
    database, make the type of update needed. If the bottom row contains a
    game that has occurred in the past, this function will fill in the stats
    from that game and add a new row onto the bottom of the database with
    the incomplete stats from the next game on the schedule (those stats will
    be completed when this function is run again after that game happens). If
    there is no upcoming game, this function will still write in the results
    of the last game in the database and commit that change, but do nothing
    else.

    Args:
        today (datetime.date()): date of 'today', or day we are doing update
            for
        season (str): string representing current season, like '2017-2018-
            regular'
        db (flask_sqlalchemy.SQLAlchemy): database to pull from and write to

    Returns:
        status (str): string describing type of update made, either
        "newgameupdate", "updatedstats", or "nogame".
    """
    # pass datetime.now().date() to use today as argument
    # db is database to write to
    datapull = pull_from_db(season)
    # check if most recent game in database has occurred
    # if so, we fill in its stats and add the next upcoming game as the bottom
    # row of the database
    if datapull[len(datapull) - 1].date.date() < today:
        new_row = full_daily_update(today, datapull, db)
        # if there are no upcoming games, full_daily_update returns str
        # if there is an upcoming game, full_daily_update returns a dict of
        # stats for that game
        if isinstance(new_row, dict):
            new_row_model = Game(date=new_row['date'],
                                 season=season,
                                 opponent=new_row['opponent'],
                                 home_away=new_row['home/away'],
                                 lbj_days_rest=new_row['days_rest'],
                                 lbj_2pt_pct=new_row['season_2pt_pct'],
                                 lbj_3pt_pct=new_row['season_3pt_pct'],
                                 lbj_ft_pct=new_row['season_ft_pct'],
                                 lbj_2pt_mpg=new_row['season_2ptpg'],
                                 lbj_3pt_mpg=new_row['season_3ptpg'],
                                 lbj_ft_mpg=new_row['season_ftpg'],
                                 lbj_rbs_pgm=new_row['season_rpg'],
                                 lbj_ast_pgm=new_row['season_apg'],
                                 lbj_plusminpg=new_row['season_plusminpg'],
                                 opp_def_eff=new_row['opp_def_eff'],
                                 opp_off_eff=new_row['opp_off_eff'],
                                 cavsWins=new_row['cavsWins'],
                                 cavsLosses=new_row['cavsLosses'],
                                 oppWins=new_row['OPPW'],
                                 oppLosses=new_row['OPPL'],
                                 lbj_games_missed=new_row['lbj_games_missed'])
            database.session.add(new_row_model)
            database.session.commit()
            status = "newgameupdate"
        else:
            status = "nogame"
        # if the most recent game in the database hasn't occurred yet,
        # we don't need to update Cavs stats,
        # instead we just pull opponent stats again to make sure they are
        # updated to reflect any games
        # the opponent played in the interim
    else:
        this_season = datapull[0].season
        this_season_start = datapull[0].date.date()
        upcoming_game = datapull[len(datapull) - 1]
        opponent = upcoming_game.opponent
        bottom_row_update = opp_stat_update(this_season, this_season_start,
                                            today, opponent)
        upcoming_game.opp_def_eff = bottom_row_update['opp_def_eff']
        upcoming_game.opp_off_eff = bottom_row_update['opp_off_eff']
        upcoming_game.oppWins = bottom_row_update['OPPW']
        upcoming_game.oppLosses = bottom_row_update['OPPL']
        db.session.commit()
        status = "updatedstats"
    return status
