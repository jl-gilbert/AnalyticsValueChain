from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLAlchemy configuration (can update with AWS RDS settings)
app.config.from_pyfile('awsdbconfig.py')
db = SQLAlchemy(app)
