import os

# To generate a new secret key:
# >>> import random, string
# >>> "".join([random.choice(string.printable) for _ in range(24)])
SECRET_KEY = "#d#JCqTTW\nilK\\7m\x0bp#\tj~#H"

PERMANENT_SESSION_LIFETIME = 3600*24*30

DATABASE = "musico.sqlite3"
SOURCE = "app/static/musique"
USER_DATA = "app/static/user_data"

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "manuel.touchefeu@gmail.com"
MAIL_PASSWORD = "Kerdrien882"