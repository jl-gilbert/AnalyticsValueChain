# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 16:14:53 2018

@author: jgilbert
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


def pandas_from_db(date):
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    sql = "select * from game where date < " + date
    data = pd.read_sql_query(sql, con=engine)
    return data


def convert_home_away(df):
    cleanup_cats = {'home_away': {'home': 1, 'away': 0}}
    df.replace(cleanup_cats, inplace=True)


def extract_predictors(df):
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


def create_training_data(date):
    data = pandas_from_db(date)
    convert_home_away(data)
    good_rows = data.loc[data.opp_def_eff != 0]
    good_rows = good_rows.loc[good_rows.lbj_DNP == 0]
    return good_rows


class trained_linear_models:
    def __init__(self, date):
        train_data = create_training_data()
        train_predictors = extract_predictors(train_data)
        response_pts = train_data.loc[:, ['pts']]
        response_rbs = train_data.loc[:, ['rbs']]
        response_ast = train_data.loc[:, ['ast']]
        self.pts_model = linear_model.LinearRegression().fit(train_predictors,response_pts)
        self.rbs_model = linear_model.LinearRegression().fit(train_predictors,response_rbs)
        self.ast_model = linear_model.LinearRegression().fit(train_predictors,response_ast)
