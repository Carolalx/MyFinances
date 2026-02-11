# app/__init__.py

from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import sys
import types
from typing import TypingOnly
import sqlalchemy

# =============================
# 🛠️ PATCH AUTOMÁTICO PARA PYTHON 3.12 + SQLALCHEMY 2.x
# =============================


def fix_typingonly_attrs(module):
    """
    Remove atributos extras de todas as classes que herdam TypingOnly
    dentro de um módulo (recursivo).
    """
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type):
            # Se herda TypingOnly
            if TypingOnly in obj.__bases__:
                # Remove atributos extras
                for attr in list(vars(obj)):
                    if attr not in ('__module__', '__qualname__'):
                        delattr(obj, attr)
        # Se é submódulo, aplica recursivamente
        elif isinstance(obj, types.ModuleType) and obj.__name__.startswith(module.__name__):
            fix_typingonly_attrs(obj)


# Aplica patch no módulo sqlalchemy.sql
fix_typingonly_attrs(sqlalchemy.sql)

# =============================


db = SQLAlchemy()  # instanciando depois do patch


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    db.init_app(app)

    # ✅ REGISTRA O FILTRO DE TEMPLATE
    from .utils import format_brl
    app.add_template_filter(format_brl, 'brl')

    # Importa e registra o blueprint
    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()  # cria as tabelas

    return app
