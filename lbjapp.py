from flask import render_template
from app import app
from app.models import Game, Predictions


@app.route('/')
def index():
    return render_template('index.html', next_game=Game.query.order_by(
            Game.date.desc()).first(), predictions=Predictions.query.order_by(
                    Predictions.predict_date.desc()).first())


if __name__ == "__main__":
    app.run(host='0.0.0.0')
