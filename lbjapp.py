from flask import render_template
from app import app
from app.models import Game, Predictions


@app.route('/')
def index():
    """Renders landing page for web app.

    This page will be the only page of the app, as it will be updated daily to
    reflect predictions for the upcoming game.

    Args:
        None

    Returns:
        rendering (render_template): rendering of web page to display with
            Flask.
    """
    return render_template('index.html', next_game=Game.query.order_by(
            Game.date.desc()).first(), predictions=Predictions.query.order_by(
                    Predictions.predict_date.desc()).first())


if __name__ == "__main__":
    app.run(host='0.0.0.0')
