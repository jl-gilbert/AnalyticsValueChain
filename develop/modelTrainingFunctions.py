# -*- coding: utf-8 -*-
"""Functions for pulling data from database and using it to train and predict.

This module provides functions and classes for pulling data from the database
into a pandas dataframe, organizing the data into relevant training data
and data to be used as predictors for the upcoming game, and finally for
training the model and using it to make predictions.
"""

import sys
sys.path.append("../")
from app import app, db
from app.models import Game
from app.awsdbconfig import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
from sklearn import linear_model
from datetime import datetime


def pandas_from_db():
    """Function for putting the entire games table into a pandas dataframe.

    This function queries the game table in the database for all rows and
    places the return into a pandas dataframe.

    Args:
        None

    Returns:
        data (pd.DataFrame): pandas dataframe containing full contents of game
            table from database
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    sql = "select * from game"
    data = pd.read_sql_query(sql, con=engine)
    return data


def convert_home_away(df):
    """Converts categorical variable into binary numeric.

    This function will replace the "home/away" attribute of the dataframe,
    stored in the database as strings, into a binary numeric variable so that
    it can easily be used by the scikit-learn model in model training and
    outcome prediction.

    Args:
        df (pd.DataFrame): pandas dataframe containing the column to be
            converted.

    Returns:
        None
    """
    cleanup_cats = {'home_away': {'home': 1, 'away': 0}}
    df.replace(cleanup_cats, inplace=True)


def extract_predictors(df):
    """Extracts the columns needed as predictor variables in the model.

    This function will return a new dataframe that is a slice of the inputed
    dataframe but only containing the columns relevant to prediction of the
    responses.

    Args:
        df (pd.DataFrame): pandas dataframe to be sliced

    Returns:
        predictors (pd.DataFrame): pandas dataframe with only the predictor
            columns
    """
    predictors = df.loc[:, ['home_away',
                            'lbj_days_rest',
                            'lbj_2pt_pct',
                            'lbj_3pt_pct',
                            'lbj_ft_pct',
                            'lbj_2pt_mpg',
                            'lbj_3pt_mpg',
                            'lbj_ft_mpg',
                            'lbj_rbs_pgm',
                            'lbj_ast_pgm',
                            'lbj_plusminpg',
                            'opp_def_eff',
                            'opp_off_eff']]
    return predictors


def create_training_data(date=datetime.now().date()):
    """Extracts the rows that will be useful in training a model.

    The function will extract only the games in which the following conditions
    are met: the opponent had played previous games in the season and thus had
    establish offensive and defensive efficiency ratings to be used as
    predictors, the game has already been completed, and Lebron James played in
    the game.

    Args:
        date (datetime.date()): Gives the date up to which we want to use data.
            This defaults to the current day, as we assume we will be making
            a model using all available data to predict the next game. However,
            it can be specified as an earlier date if the user wants to
            reproduce an earlier model.

    Returns:
        good_rows (pd.DataFrame): pandas dataframe containing only the rows
            suitable for use in model training.
    """
    data = pandas_from_db()
    convert_home_away(data)
    good_rows = data.loc[data.opp_def_eff != 0]
    good_rows = good_rows.loc[data.date < date]
    good_rows = good_rows.loc[good_rows.lbj_DNP == 0]
    return good_rows


def create_upcoming_game():
    """Creates single-row dataframe containing info on the next future game.

    This function will query the games database and return the last row,
    which is the next upcoming game, as a pandas dataframe.

    Args:
        None

    Returns:
        predict_row (pd.DataFrame): single-row dataframe containing info on the
            next upcoming game
    """
    data = pandas_from_db()
    convert_home_away(data)
    predict_row = data.tail(1)
    return predict_row


class trained_linear_models:
    """Class containing predictive models and the predictions they yield.

    By default, this class will build models using all past data, but a user
    can also use it to reproduce models made in the past.  To do so, the user
    would pass the date of the game for which reproduced predictions are
    desired into the constructor, then when executing the predict method, pass
    the row from the games table in the database of that game.

    Attributes:
        pts_model (sklearn.linear_model): scikit-learn trained linear model
            for predicting points.
        rbs_model (sklearn.linear_model): scikit-learn trained linear model
            for predicting rebounds.
        ast_model (sklearn.linear_model): scikit-learn trained linear model
            for predicting assists.
        predicted_pts (float): predicted number of points for specified game
        predicted_rbs (float): predicted number of rebounds for specified game
        predicted_ast (float): predicted number of assists for specified game
        predicted_game_date (datetime.date()): date of game for which
            predictions are made.
    """

    def __init__(self, date=datetime.now().date()):
        """Constructor for a trained_linear_models object.

        Args:
            date (datetime.date()): date specifying what data will be allowed
                for use in model training. Defaults to current date, which will
                use all available data for model training, but can be specified
                as a previous date to reproduce an earlier version of the model
        """
        train_data = create_training_data(date)
        train_predictors = extract_predictors(train_data)
        response_pts = train_data.loc[:, ['pts']]
        response_rbs = train_data.loc[:, ['rbs']]
        response_ast = train_data.loc[:, ['ast']]
        self.pts_model = linear_model.LinearRegression().fit(
                train_predictors, response_pts)
        self.rbs_model = linear_model.LinearRegression().fit(
                train_predictors, response_rbs)
        self.ast_model = linear_model.LinearRegression().fit(
                train_predictors, response_ast)

    def predict(self, predict_game):
        """Method to make predictions with supplied game information.

        This method will define the attributes of the trained_linear_models
        object that describe the predictions it makes for a game and the date
        of that game.

        Args:
            predict_game (pd.DataFrame): single-row pandas dataframe containing
                all columns from the games database in regard to a single game.
                It is this game for which predictions will be made.

        Returns:
            None
        """
        predictor_values = extract_predictors(predict_game)
        self.predicted_pts = np.asscalar(self.pts_model.predict(
                predictor_values)[0])
        self.predicted_rbs = np.asscalar(self.rbs_model.predict(
                predictor_values)[0])
        self.predicted_ast = np.asscalar(self.ast_model.predict(
                predictor_values)[0])
        self.predicted_game_date = datetime.strptime(
                predict_game.date.values[0].astype(str)[:10], '%Y-%m-%d').date(
                        )
