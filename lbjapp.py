from flask import render_template
from app import app


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
    return render_template('index.html', predicted_stats=[25, 10, 9])
