# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_migrate import Migrate
from .utils import price_format  # importa a função diretamente


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Inicializa banco e migrações
    db.init_app(app)
    migrate.init_app(app, db)

    # ✅ Registra filtro do Jinja
    from .utils import price_format
    app.add_template_filter(price_format, 'brl')  # 'brl' será o nome do filtro

    # Blueprint
    from .routes import main
    app.register_blueprint(main)

    # Cria tabelas
    with app.app_context():
        db.create_all()

    return app
