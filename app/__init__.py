# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# Instancia SQLAlchemy normalmente
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    db.init_app(app)

    # Registra filtro de template
    from .utils import format_brl
    app.add_template_filter(format_brl, 'brl')

    # Importa e registra o blueprint
    from .routes import main
    app.register_blueprint(main)

    # Cria todas as tabelas
    with app.app_context():
        db.create_all()

    return app
