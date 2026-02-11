import os
from dotenv import load_dotenv

# Carrega o .env apenas se não estivermos em produção
if os.environ.get("FLASK_ENV") != "production":
    load_dotenv()


class Config:
    # Chave secreta
    SECRET_KEY = os.environ.get("SECRET_KEY", "uma-chave-muito-segura")

    # Configurações do SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pega a URL do banco de dados das variáveis de ambiente
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Ajuste para compatibilidade com PostgreSQL do Render
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1)
