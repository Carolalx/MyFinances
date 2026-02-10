import os
from dotenv import load_dotenv  # Adicione esta linha

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "uma-chave-muito-segura"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
