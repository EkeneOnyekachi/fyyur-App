import os
from os import getenv

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))


from pathlib import Path
from dotenv import load_dotenv

env_path = Path(".", ".env")
load_dotenv(dotenv_path=env_path)


# Enable debug mode.
DEBUG = True


DB_HOST = getenv("db_host")
DB_USER = getenv("db_user")
DB_PASSWORD = getenv("db_pass")
DB_NAME = getenv("db_name")
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
