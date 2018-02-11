from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLAlchemy configuration (can update with AWS RDS settings)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/stats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
