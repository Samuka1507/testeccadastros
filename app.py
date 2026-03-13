# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
# Chave secreta necessária para usar as mensagens (flash messages)
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
            telefone TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']

        if not nome or not email:
            flash('Nome e Email são campos obrigatórios!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)',
                         (nome, email, telefone))
            conn.commit()
            conn.close()
            flash('Cliente cadastrado com sucesso!')
            return redirect(url_for('index'))

    return render_template('index.html')

# --- NOVA ROTA ADICIONADA AQUI ---
@app.route('/lista')
def lista():
    # Conecta no banco de dados
    conn = get_db_connection()
    # Puxa todos os clientes cadastrados
    clientes = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    
    # Envia os dados para a página lista.html
    return render_template('lista.html', clientes=clientes)
# ---------------------------------

if __name__ == '__main__':
    init_db() # Cria o banco de dados e a tabela ao iniciar
    app.run(debug=True)