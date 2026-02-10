import os


class Config:
    SECRET_KEY = "sua_chave_secreta_aqui"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Caminho absoluto para a pasta 'instance' na raiz do projeto
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    INSTANCE_PATH = os.path.join(BASE_DIR, "instance")

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_PATH, 'site.db')}"
