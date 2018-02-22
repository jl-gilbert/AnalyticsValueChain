from app import db
from develop import updateFunctions as uf
from datetime import datetime


def update_db():
    """Function to run daily to update db with latest info.

    This function will run functions from updateFunctions.py to add a new row
    to the database if appropriate, or otherwise just update the bottom row. It
    is intended to be executed once per day.

    Args:
        None

    Returns:
        None
    """
    uf.make_update(datetime.now().date(),
                   "2017-2018-regular", db)

if __name__ == "__main__":
    update_db()
