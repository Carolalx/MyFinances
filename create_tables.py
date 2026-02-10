# create_tables.py

from app import create_app, db
from app.models import User, Account, TransactionType, Expense, Revenue, SavingGoal

# Cria a instância da aplicação Flask com PostgreSQL
app = create_app()

with app.app_context():
    db.create_all()  # cria todas as tabelas no PostgreSQL
    print("Tabelas criadas com sucesso!")
