import os
import re
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "uma-chave-muito-segura"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pega a URL do banco das variáveis de ambiente
    uri = os.environ.get("DATABASE_URL")

    # Ajuste crucial para compatibilidade do SQLAlchemy com o PostgreSQL do Render
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri
