from flask import Blueprint, app, request, render_template, redirect, url_for, flash, jsonify, session
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime
from .models import User, Account, TransactionType, Expense, Revenue, SavingGoal

main = Blueprint('main', __name__)

# -------------------------------
# TIPOS PADRÃO
# -------------------------------

DEFAULT_EXPENSE_TYPES = [
    'Alimentação',
    'Transporte/Combustível',
    'Diversão/Lazer',
    'Saúde',
    'Moradia',
    'Educação',
    'Cartão de Crédito',
    'Saneamento (Água/Esgoto)',
    'Energia Elétrica',
    'Investimentos',
    'Internet',
    'Telefonia'
]

DEFAULT_REVENUE_TYPES = [
    'Salário',
    '13º Salário',
    '1/3 de férias',
    'Bônus / Hora extra',
    'Freelance',
    'Renda de Aluguel',
    'Renda de Investimentos'
]


# -------------------------------
# INDEX
# -------------------------------

@main.route('/')
def index():
    return redirect(url_for('main.login'))


# -------------------------------
# REGISTRO
# -------------------------------

@main.route('/add_account', methods=['POST'])
def add_account():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    account_name = request.form.get('account_name')
    if not account_name:
        flash('O nome da conta não pode ser vazio.', 'error')
        return redirect(url_for('main.config'))

    account = Account(
        account_name=account_name,
        user_id=session['user_id']
    )
    db.session.add(account)
    db.session.commit()

    flash('Conta adicionada com sucesso!', 'success')
    return redirect(url_for('main.config'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('Preencha todos os campos obrigatórios.', 'error')
            return render_template('register.html')

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash('Usuário ou e-mail já cadastrado.', 'error')
            return render_template('register.html')

        user = User(fullname=fullname, username=username, email=email)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()

            db.session.add(Account(account_name='Carteira', user_id=user.id))

            for name in DEFAULT_EXPENSE_TYPES:
                db.session.add(TransactionType(
                    name=name,
                    transaction_category='expense',
                    user_id=user.id
                ))

            for name in DEFAULT_REVENUE_TYPES:
                db.session.add(TransactionType(
                    name=name,
                    transaction_category='revenue',
                    user_id=user.id
                ))

            db.session.commit()
            flash('Usuário registrado com sucesso!', 'success')
            return redirect(url_for('main.login'))

        except Exception as e:
            db.session.rollback()
            flash(str(e), 'error')

    return render_template('register.html')


@main.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    if check_password_hash(user.password, request.form.get('current_password')):
        if request.form.get('new_password') == request.form.get('confirm_new_password'):
            user.password = generate_password_hash(
                request.form.get('new_password'),
                method='pbkdf2:sha256'
            )
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
        else:
            flash('As novas senhas não coincidem!', 'error')
    else:
        flash('Senha atual incorreta!', 'error')

    return redirect(url_for('main.config'))


# -------------------------------
# LOGIN / LOGOUT
# -------------------------------

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form.get('username')
        ).first()

        if user and user.check_password(request.form.get('password')):
            session['user_id'] = user.id
            return redirect(url_for('main.dashboard'))

        flash('Usuário ou senha incorretos.', 'error')

    return render_template('login.html')


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


# -------------------------------
# DASHBOARD
# -------------------------------

@main.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login'))

    accounts = Account.query.filter_by(user_id=user_id).all()
    expense_types = TransactionType.query.filter_by(
        user_id=user_id, transaction_category='expense'
    ).all()
    revenue_types = TransactionType.query.filter_by(
        user_id=user_id, transaction_category='revenue'
    ).all()

    expenses = Expense.query.join(Account).filter(
        Account.user_id == user_id
    ).all()

    revenues = Revenue.query.join(Account).filter(
        Account.user_id == user_id
    ).all()

    total_revenue = sum(r.amount for r in revenues)
    total_expense = sum(e.amount for e in expenses)

    # --- Geração do gráfico (somente tipos com despesas) ---
    expense_sums = {}
    for e in expenses:
        name = e.transaction_type.name
        expense_sums[name] = expense_sums.get(name, 0) + e.amount

    labels = list(expense_sums.keys())
    data = list(expense_sums.values()) + \
        [total_revenue - sum(expense_sums.values())]

    labels_json = json.dumps(labels)
    data_json = json.dumps(data)

    return render_template(
        'dashboard.html',
        accounts=accounts,
        expense_types=expense_types,
        revenue_types=revenue_types,
        expenses=expenses,
        revenues=revenues,
        total_revenue=total_revenue,
        total_expense=total_expense,
        balance=total_revenue - total_expense,
        labels_json=labels_json,
        data_json=data_json
    )


# -------------------------------
# ADICIONAR DESPESA
# -------------------------------

@main.route('/add_expense', methods=['POST'])
def add_expense():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login'))

    # Pega os valores do formulário
    transaction_type_id = request.form.get('transaction_type_id')
    amount = request.form.get('amount')
    date_str = request.form.get('date')
    account_id = request.form.get('account_id')
    description = request.form.get('description')

    # Validação simples
    if not transaction_type_id:
        flash('Tipo da despesa é obrigatório.', 'error')
        return redirect(url_for('main.dashboard'))

    if not amount or not date_str or not account_id:
        flash('Preencha todos os campos obrigatórios.', 'error')
        return redirect(url_for('main.dashboard'))

    # Converte os valores
    try:
        transaction_type_id = int(transaction_type_id)
        amount = float(amount)
        account_id = int(account_id)
        expense_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        flash('Dados do formulário inválidos.', 'error')
        return redirect(url_for('main.dashboard'))

    # Busca o TransactionType e a Account
    transaction_type = TransactionType.query.filter_by(
        id=transaction_type_id,
        user_id=user_id,
        transaction_category='expense'
    ).first()
    if not transaction_type:
        flash('Tipo de despesa inválido.', 'error')
        return redirect(url_for('main.dashboard'))

    account = Account.query.filter_by(
        id=account_id,
        user_id=user_id
    ).first()
    if not account:
        flash('Conta inválida.', 'error')
        return redirect(url_for('main.dashboard'))

    # Cria e salva a despesa
    expense = Expense(
        amount=amount,
        expense_date=expense_date,
        account_id=account.id,
        transaction_type_id=transaction_type.id,
        description=description
    )

    db.session.add(expense)
    db.session.commit()

    flash('Despesa adicionada com sucesso!', 'success')
    return redirect(url_for('main.dashboard'))


# -------------------------------
# ADICIONAR RECEITA
# -------------------------------

@main.route('/add_revenue', methods=['POST'])
def add_revenue():
    print(request.form)
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login'))

    # Pega o ID do tipo de receita do formulário
    transaction_type_id = request.form.get('transaction_type_id')
    if not transaction_type_id:
        flash('Tipo da receita é obrigatório.', 'error')
        return redirect(url_for('main.dashboard'))

    # Converte para inteiro e busca o objeto TransactionType
    transaction_type = TransactionType.query.get(int(transaction_type_id))
    if not transaction_type:
        flash('Tipo de receita inválido.', 'error')
        return redirect(url_for('main.dashboard'))

    # Pega os demais campos do formulário
    try:
        amount = float(request.form.get('amount'))
        account_id = int(request.form.get('account_id'))
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        description = request.form.get('description')
    except Exception as e:
        flash('Erro nos dados enviados. Verifique os valores.', 'error')
        return redirect(url_for('main.dashboard'))

    # Cria a receita
    new_rev = Revenue(
        amount=amount,
        transaction_type_id=transaction_type.id,
        account_id=account_id,
        revenue_date=date,
        description=description
    )

    db.session.add(new_rev)
    db.session.commit()
    flash('Receita adicionada com sucesso!', 'success')
    return redirect(url_for('main.dashboard'))


@main.route('/transaction_management', methods=['GET', 'POST'])
def transaction_management():
    from .models import TransactionType, User
    user_id = session.get('user_id')
    if not user_id:
        flash('Por favor, faça login para acessar essa página.', 'warning')
        return redirect(url_for('main.login'))

    # --- Inserir tipos padrão para todos os usuários, caso ainda não existam ---
    DEFAULT_EXPENSE_TYPES = [
        'Alimentação',
        'Transporte/Combustível',
        'Diversão/Lazer',
        'Saúde',
        'Moradia',
        'Educação',
        'Cartão de Crédito',
        'Saneamento (Água/Esgoto)',
        'Energia Elétrica',
        'Investimentos',
        'Internet',
        'Telefonia'
    ]

    DEFAULT_REVENUE_TYPES = [
        'Salário',
        '13º Salário',
        '1/3 de férias',
        'Bônus / Hora extra',
        'Freelance',
        'Renda de Aluguel',
        'Renda de Investimentos'
    ]

    # Atualizar tipos padrão para o usuário logado, sem duplicar
    for name in DEFAULT_EXPENSE_TYPES:
        if not TransactionType.query.filter_by(
            name=name, user_id=user_id, transaction_category='expense'
        ).first():
            db.session.add(TransactionType(
                name=name,
                user_id=user_id,
                transaction_category='expense'
            ))

    for name in DEFAULT_REVENUE_TYPES:
        if not TransactionType.query.filter_by(
            name=name, user_id=user_id, transaction_category='revenue'
        ).first():
            db.session.add(TransactionType(
                name=name,
                user_id=user_id,
                transaction_category='revenue'
            ))

    db.session.commit()

    # --- Processar envio do formulário ---
    if request.method == 'POST':
        # Novo tipo de despesa
        expense_name = request.form.get('expense_type', '').strip()
        if expense_name:
            exists = TransactionType.query.filter_by(
                name=expense_name,
                user_id=user_id,
                transaction_category='expense'
            ).first()
            if not exists:
                db.session.add(TransactionType(
                    name=expense_name,
                    user_id=user_id,
                    transaction_category='expense'
                ))
                db.session.commit()
                flash('Novo tipo de despesa adicionado com sucesso.', 'success')
            else:
                flash('Esse tipo de despesa já existe.', 'warning')

        # Novo tipo de receita
        revenue_name = request.form.get('revenue_type', '').strip()
        if revenue_name:
            exists = TransactionType.query.filter_by(
                name=revenue_name,
                user_id=user_id,
                transaction_category='revenue'
            ).first()
            if not exists:
                db.session.add(TransactionType(
                    name=revenue_name,
                    user_id=user_id,
                    transaction_category='revenue'
                ))
                db.session.commit()
                flash('Novo tipo de receita adicionado com sucesso.', 'success')
            else:
                flash('Esse tipo de receita já existe.', 'warning')

    # --- Listar tipos existentes ---
    expense_types = TransactionType.query.filter_by(
        user_id=user_id, transaction_category='expense'
    ).all()
    revenue_types = TransactionType.query.filter_by(
        user_id=user_id, transaction_category='revenue'
    ).all()

    return render_template(
        'transaction_management.html',
        expense_types=expense_types,
        revenue_types=revenue_types
    )


@main.route('/transaction_history')
def transaction_history():
    from .models import Expense, Revenue, TransactionType, Account
    user_id = session.get('user_id')
    if not user_id:
        flash('Por favor, faça login para acessar essa página.', 'warning')
        return redirect(url_for('main.login'))

    expenses = db.session.query(Expense, TransactionType, Account).join(TransactionType, Expense.transaction_type_id == TransactionType.id).join(
        Account, Expense.account_id == Account.id).filter(Account.user_id == user_id).all()
    revenues = db.session.query(Revenue, TransactionType, Account).join(TransactionType, Revenue.transaction_type_id == TransactionType.id).join(
        Account, Revenue.account_id == Account.id).filter(Account.user_id == user_id).all()

    expense_data = [{'expense': expense, 'transaction_type': transaction_type,
                     'account': account} for expense, transaction_type, account in expenses]
    revenue_data = [{'revenue': revenue, 'transaction_type': transaction_type,
                     'account': account} for revenue, transaction_type, account in revenues]

    return render_template('transaction_history.html', expenses=expense_data, revenues=revenue_data)


@main.route('/simulador_invest')
def simulador_invest():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar essa página.', 'warning')
        return redirect(url_for('main.login'))
    return render_template('simulador_invest.html')

# 👇 CADASTRO DE METAS


@main.route('/saving_goal', methods=['GET', 'POST'])
def saving_goal():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        goal = SavingGoal(
            user_id=user_id,
            goal_name=request.form['goal_name'],
            target_amount=float(request.form['target_amount']),
            current_amount=0.0,
            target_date=datetime.strptime(
                request.form['target_date'], '%Y-%m-%d')
        )
        db.session.add(goal)
        db.session.commit()
        return redirect(url_for('main.saving_goal'))

    # Buscar metas: ativas primeiro, concluídas por último
    goals = SavingGoal.query.filter_by(user_id=user_id)\
        .order_by(SavingGoal.completed.asc(), SavingGoal.target_date.asc())\
        .all()

    return render_template('saving_goal.html', goals=goals)


# Adicionar valor à meta
@main.route('/saving_goal/add/<int:goal_id>', methods=['POST'])
def add_to_goal(goal_id):
    user_id = session.get('user_id')
    goal = SavingGoal.query.filter_by(
        id=goal_id, user_id=user_id).first_or_404()
    value = float(request.form['amount'])
    goal.current_amount += value
    db.session.commit()
    return redirect(url_for('main.saving_goal'))


# Marcar meta como concluída
@main.route('/saving_goal/complete/<int:goal_id>', methods=['POST'])
def complete_goal(goal_id):
    user_id = session.get('user_id')
    goal = SavingGoal.query.filter_by(
        id=goal_id, user_id=user_id).first_or_404()
    goal.completed = True
    db.session.commit()
    return redirect(url_for('main.saving_goal'))

# Excluir meta


@main.route('/saving_goal/delete/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    user_id = session.get('user_id')
    goal = SavingGoal.query.filter_by(
        id=goal_id, user_id=user_id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    return redirect(url_for('main.saving_goal'))


@main.route('/calendar')
def calendar():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar essa página.', 'warning')
        return redirect(url_for('main.login'))
    return render_template('calendar.html')


@main.route('/api/events')
def api_events():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])

    events = []

    # despesas
    for expense in Expense.query.join(Account).filter(Account.user_id == user_id).all():
        events.append({
            'title': f"R$ {expense.amount} ({expense.description[:10]}...)",
            'start': expense.expense_date.strftime('%Y-%m-%d'),
            'color': 'red'
        })

    # receitas
    for revenue in Revenue.query.join(Account).filter(Account.user_id == user_id).all():
        events.append({
            'title': f"R$ {revenue.amount} ({revenue.description[:10]}...)",
            'start': revenue.revenue_date.strftime('%Y-%m-%d'),
            'color': 'green'
        })

    # metas de economia
    for goal in SavingGoal.query.filter_by(user_id=user_id).all():
        events.append({
            'title': f"{goal.goal_name} ({goal.current_amount:.2f}/{goal.target_amount:.2f})",
            'start': goal.target_date.strftime('%Y-%m-%d'),
            'color': 'blue'  # cor diferente para metas
        })

    return jsonify(events)


def get_events():
    goals = SavingGoal.query.all()
    events = []

    for goal in goals:
        events.append({
            'title': goal.goal_name,
            'start': goal.target_date.isoformat(),  # FullCalendar aceita ISO
            'allDay': True,
        })

    return jsonify(events)


@main.route('/config', methods=['GET', 'POST'])
def config():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        try:
            user.fullname = request.form.get('fullname')
            user.email = request.form.get('email')
            db.session.commit()
            flash('Dados atualizados com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'error')

    return render_template('config.html', user=user)


@main.route('/delete_expense_type/<int:id>')
def delete_expense_type(id):
    from .models import TransactionType, Expense
    if 'user_id' not in session:
        flash('Por favor, faça login para excluir um tipo de despesa.', 'warning')
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    expense_type = TransactionType.query.get(id)

    if not expense_type or expense_type.user_id != user_id or expense_type.transaction_category != 'expense':
        flash('Você não tem permissão para excluir esse tipo de despesa.', 'danger')
        return redirect(url_for('main.transaction_management'))

    associated_expenses = Expense.query.filter_by(
        transaction_type_id=id).count()
    if associated_expenses > 0:
        flash('Não é possível excluir este tipo de despesa, pois existem despesas associadas a ele.', 'danger')
        return redirect(url_for('main.transaction_management'))

    db.session.delete(expense_type)
    db.session.commit()
    flash('Tipo de despesa excluído com sucesso!', 'success')
    return redirect(url_for('main.transaction_management'))


@main.route('/delete_revenue_type/<int:id>')
def delete_revenue_type(id):
    from .models import TransactionType, Revenue
    if 'user_id' not in session:
        flash('Por favor, faça login para excluir um tipo de receita.', 'warning')
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    revenue_type = TransactionType.query.get(id)

    if not revenue_type or revenue_type.user_id != user_id or revenue_type.transaction_category != 'revenue':
        flash('Você não tem permissão para excluir esse tipo de receita.', 'danger')
        return redirect(url_for('main.transaction_management'))

    associated_revenues = Revenue.query.filter_by(
        transaction_type_id=id).count()
    if associated_revenues > 0:
        flash('Não é possível excluir este tipo de receita, pois existem receitas associadas a ele.', 'danger')
        return redirect(url_for('main.transaction_management'))

    db.session.delete(revenue_type)
    db.session.commit()
    flash('Tipo de receita excluído com sucesso!', 'success')
    return redirect(url_for('main.transaction_management'))


@main.route('/delete_expense/<int:id>')
def delete_expense(id):
    from .models import Expense, Account
    if 'user_id' not in session:
        flash('Por favor, faça login para excluir uma despesa.', 'warning')
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    expense = Expense.query.get(id)

    account = Account.query.get(expense.account_id)
    if not expense or account.user_id != user_id:
        flash('Você não tem permissão para excluir essa despesa.', 'danger')
        return redirect(url_for('main.dashboard'))

    db.session.delete(expense)
    db.session.commit()
    flash('Despesa excluída com sucesso!', 'success')
    return redirect(url_for('main.transaction_history'))


@main.route('/delete_revenue/<int:id>')
def delete_revenue(id):
    from .models import Revenue, Account
    if 'user_id' not in session:
        flash('Por favor, faça login para excluir uma receita.', 'warning')
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    revenue = Revenue.query.get(id)

    account = Account.query.get(revenue.account_id)
    if not revenue or account.user_id != user_id:
        flash('Você não tem permissão para excluir essa receita.', 'danger')
        return redirect(url_for('main.transaction_history'))

    db.session.delete(revenue)
    db.session.commit()
    flash('Receita excluída com sucesso!', 'success')
    return redirect(url_for('main.transaction_history'))
