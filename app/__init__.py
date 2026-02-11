# app/__init__.py

import types
from typing import TypingOnly
import sqlalchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# =============================
# 🛠️ PATCH AUTOMÁTICO PARA PYTHON 3.12 + SQLALCHEMY 2.x
# =============================


def fix_typingonly_attrs(module):
    """
    Remove atributos extras de todas as classes que herdam TypingOnly
    dentro de um módulo (recursivo).
    """
    for name in dir(module):
        try:
            obj = getattr(module, name)
        except AttributeError:
            continue

        if isinstance(obj, type) and TypingOnly in obj.__bases__:
            # Remove atributos extras
            for attr in list(vars(obj)):
                if attr not in ('__module__', '__qualname__'):
                    delattr(obj, attr)
        elif isinstance(obj, types.ModuleType) and obj.__name__.startswith(module.__name__):
            fix_typingonly_attrs(obj)


# Aplica patch no módulo sqlalchemy.sql antes de instanciar SQLAlchemy
fix_typingonly_attrs(sqlalchemy.sql)

# =============================

# Instancia o SQLAlchemy depois do patch
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    db.init_app(app)

    # ✅ Registra o filtro de template
    from .utils import format_brl
    app.add_template_filter(format_brl, 'brl')

    # ✅ Importa e registra o blueprint
    from .routes import main
    app.register_blueprint(main)

    # ✅ Cria todas as tabelas dentro do app context
    with app.app_context():
        db.create_all()

    return app
