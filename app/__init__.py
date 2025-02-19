from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object("config")

login = LoginManager(app)
login.login_view = "/login"

from app import routes