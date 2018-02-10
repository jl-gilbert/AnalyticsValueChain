"""Runs flask web app."""

from flask import render_template
from app import app

@app.route('/')
def index():
    return render_template('index.html', predicted_stats=[25,10,9])

