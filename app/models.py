from datetime import datetime
from . import db
import pytz
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fullname = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)

    accounts = db.relationship('Account', backref='user', lazy=True)
    saving_goals = db.relationship('SavingGoal', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    revenues = db.relationship('Revenue', backref='account', lazy=True)
    expenses = db.relationship('Expense', backref='account', lazy=True)


class TransactionType(db.Model):
    __tablename__ = 'transaction_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    transaction_category = db.Column(
        db.String(20), nullable=False)  # 'revenue' ou 'expense'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    expenses = db.relationship(
        'Expense', backref='transaction_type', lazy=True)
    revenues = db.relationship(
        'Revenue', backref='transaction_type', lazy=True)


class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type_id = db.Column(
        db.Integer, db.ForeignKey('transaction_types.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    expense_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    description = db.Column(db.String(50))  # adiciona o campo


class Revenue (db.Model):
    __tablename__ = 'revenue'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    revenue_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    transaction_type_id = db.Column(db.Integer, db.ForeignKey(
        'transaction_types.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey(
        'account.id'), nullable=False)


class SavingGoal(db.Model):
    __tablename__ = 'saving_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, nullable=False, default=0.00)
    target_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.utc))
    completed = db.Column(db.Boolean, default=False)


class Investment(db.Model):
    __tablename__ = 'investments'
    id = db.Column(db.Integer, primary_key=True)  # id do investimento
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False)  # id do usuário
    starting_capital = db.Column(db.Float, nullable=False)  # Capital inicial
    contribution = db.Column(db.Float, nullable=False)  # Aporte mensal
    # Taxa anual aumento de aporte
    contribution_tax = db.Column(db.Float, nullable=False, default=0.00)
    annual_tax = db.Column(db.Float, nullable=False,
                           default=0.00)  # Taxa de juros anual
    target_time = db.Column(db.Float, nullable=False,
                            default=0.00)  # Tempo investimento (anos)
