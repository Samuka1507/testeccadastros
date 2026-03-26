# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "chave_super_secreta" 

def get_db_connection():
    conn = sqlite3.connect('clientes.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT,
            cpf TEXT,
            senha TEXT NOT NULL /* NOVO CAMPO DE SENHA */
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        # Descobre de qual formulário veio o clique (Cadastro ou Login)
        acao = request.form.get('acao')

        if acao == 'cadastrar':
            nome = request.form['nome']
            email = request.form['email']
            cpf = request.form['cpf']
            telefone = request.form['telefone']
            senha = request.form['senha']

            if not nome or not email or not senha:
                flash('Nome, E-mail e Senha são obrigatórios!', 'erro')
            else:
                conn = get_db_connection()
                email_existente = conn.execute('SELECT * FROM clientes WHERE email = ?', (email,)).fetchone()
                
                if email_existente:
                    flash('Erro: Este e-mail já está cadastrado!', 'erro')
                else:
                    conn.execute('INSERT INTO clientes (nome, email, telefone, cpf, senha) VALUES (?, ?, ?, ?, ?)',
                                 (nome, email, telefone, cpf, senha))
                    conn.commit()
                    flash('Cadastro realizado com sucesso! Faça o login ao lado.', 'sucesso')
                conn.close()
                return redirect(url_for('index'))

        elif acao == 'login':
            email_login = request.form['email_login']
            senha_login = request.form['senha_login']

            conn = get_db_connection()
            # Busca se existe alguém com esse e-mail E essa senha
            usuario = conn.execute('SELECT * FROM clientes WHERE email = ? AND senha = ?', (email_login, senha_login)).fetchone()
            conn.close()

            if usuario:
                # Se achou, manda a mensagem de boas-vindas e vai pra lista!
                flash(f'Bem-vindo(a), {usuario["nome"]}!', 'sucesso')
                return redirect(url_for('lista'))
            else:
                # Se não achou, dá erro e fica na página inicial
                flash('E-mail ou senha incorretos!', 'erro')
                return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/lista')
def lista():
    conn = get_db_connection()
    busca = request.args.get('busca')
    
    if busca:
        clientes = conn.execute(
            'SELECT * FROM clientes WHERE nome LIKE ? OR email LIKE ?', 
            (f'%{busca}%', f'%{busca}%')
        ).fetchall()
    else:
        clientes = conn.execute('SELECT * FROM clientes').fetchall()
        
    conn.close()
    return render_template('lista.html', clientes=clientes, busca=busca)

@app.route('/editar/<int:id>', methods=('GET', 'POST'))
def editar(id):
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cpf = request.form['cpf']

        if not nome or not email:
            flash('Nome e Email são campos obrigatórios!', 'erro')
        else:
            conn.execute('''
                UPDATE clientes 
                SET nome = ?, email = ?, telefone = ?, cpf = ? 
                WHERE id = ?
            ''', (nome, email, telefone, cpf, id))
            conn.commit()
            conn.close()
            flash('Cliente atualizado com sucesso!', 'sucesso')
            return redirect(url_for('lista'))

    conn.close()
    return render_template('editar.html', cliente=cliente)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('lista'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)