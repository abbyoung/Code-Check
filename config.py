import os

# Config file, put all your keys and passwords and whatnot in here
DEBUG = True
DB_URI = os.environ.get("DATABASE_URL", "sqlite:///my_app.db")
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///my_app.db")
SECRET_KEY = "this should be a secret"

