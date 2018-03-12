"""Functions for making the daily update to the database.

This module provides functions for updating the database on a daily basis. If
run as main it will update the games table in the database containing
information on all completed games as well as the next one upcoming, and then
proceed to update the predictions table in the database with the latest
prediction for the upcoming game. This should be executed daily via the
crontab.
"""

from app import db
from app.models import Predictions
from develop import updateFunctions as uf
from develop import modelTrainingFunctions as mTF
from datetime import datetime
import pickle
import logging


def update_db():
    """Function to run daily to update db with latest info.

    This function will run functions from updateFunctions.py to add a new row
    to the database if appropriate, or otherwise just update the bottom row. It
    is intended to be executed once per day.

    Args:
        None

    Returns:
        update status (str): string describing the type of update that was made
             to the database. Possible values are 'newgameupdate',
             'updatedstats', and 'nogame'.
    """
    update_status = uf.make_update(datetime.now().date(),
                                   "2017-2018-regular", db)
    return update_status


def update_model():
    """Function to run when needed to create new model with latest data.

    This function will run when new game results are available to retrain the
    model.

    Args:
        None

    Returns:
        models (mTF.trained_linear_models): returns object of custom class
            trained_linear_models which has attributes of models to predict
            points, assists, and rebounds
    """
    logging.info('Training new model.')
    models = mTF.trained_linear_models(datetime.now().date())
    return models


def make_new_predictions(models):
    """Using the supplied trained_linear_models object, makes predictions.

    This function uses the custom class trained_linear_models' predict method
    to add or modify the attributes of that class that contain the predictions
    of points, rebounds, and assists for the upcoming game, as well as the date
    of the upcoming game.

    Args:
        models (mTF.trained_linear_models): takes object of custom class
            trained_linear_models to make predictions. After this function
            executes, this object will have attributes containing these
            predictions.

    Returns:
        None
    """
    upcoming_predictors = mTF.create_upcoming_game()
    logging.info('Making new predictions')
    models.predict(upcoming_predictors)


def update_predictions_db(update_status):
    """Updates table in database containing predictions.

    Based on what type of update was made to the database table containing info
    on games, this function will take the proper steps in updating the table
    containing predictions. If new game results were added to the former table
    the model will be retrained and predictions will be made. Otherwise, the
    most recent model will be recalled and used to make new predictions based
    on any updated info pertaining to the upcoming game.

    Args:
        update_status (str): the return of uf.make_update, and in turn the
            return of update_db(). Describes the type of update made to the
            games table and informs what process should be used for making new
            predictions (build new model and predict, predict using most recent
            model, or do nothing because there are no upcoming games).

    Returns:
        None
    """
    if update_status == "newgameupdate":
        models = update_model()
        with open('models.pickle', 'wb') as f:
            pickle.dump(models, f)
        make_new_predictions(models)
        new_row_predict = Predictions(
                game_date=models.predicted_game_date,
                predict_date=datetime.now().date(),
                predicted_pts=models.predicted_pts,
                predicted_rbs=models.predicted_rbs,
                predicted_ast=models.predicted_ast)
    elif update_status == "updatedstats":
        with open('models.pickle', 'rb') as f:
            models = pickle.load(f)
        make_new_predictions(models)
        new_row_predict = Predictions(
                game_date=models.predicted_game_date,
                predict_date=datetime.now().date(),
                predicted_pts=models.predicted_pts,
                predicted_rbs=models.predicted_rbs,
                predicted_ast=models.predicted_ast)
    else:
        new_row_predict = Predictions(
                game_date=datetime.now().date(),
                predict_date=datetime.now().date(),
                predicted_pts=0,
                predicted_rbs=0,
                predicted_ast=0)
    db.session.add(new_row_predict)
    db.session.commit()
    db.session.close()


if __name__ == "__main__":
    logging.basicConfig(filename="logs/daily_update.log",
                        level=logging.DEBUG)
    logging.info('Logging for %s', str(datetime.now().date()))
    update_status = update_db()
    update_predictions_db(update_status)
