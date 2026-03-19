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

# --- ROTA DE LISTA ATUALIZADA COM BUSCA ---
@app.route('/lista')
def lista():
    conn = get_db_connection()
    
    # Pega o que o usuário digitou na barra de pesquisa (se houver)
    busca = request.args.get('busca')
    
    if busca:
        # O '%busca%' faz o banco de dados procurar a palavra em qualquer parte do nome ou email
        clientes = conn.execute(
            'SELECT * FROM clientes WHERE nome LIKE ? OR email LIKE ?', 
            (f'%{busca}%', f'%{busca}%')
        ).fetchall()
    else:
        # Se não tem busca, puxa todos os clientes
        clientes = conn.execute('SELECT * FROM clientes').fetchall()
        
    conn.close()
    
    # Envia os dados e também o termo buscado de volta para a tela
    return render_template('lista.html', clientes=clientes, busca=busca)
# ------------------------------------------

# --- NOVA ROTA DE EXCLUSÃO ADICIONADA AQUI ---
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conn = get_db_connection()
    # Deleta o cliente onde o ID for igual ao que foi clicado
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    # Redireciona de volta para a lista atualizada
    return redirect(url_for('lista'))
# ---------------------------------------------

# --- NOVA ROTA DE EDIÇÃO ADICIONADA AQUI ---
@app.route('/editar/<int:id>', methods=('GET', 'POST'))
def editar(id):
    conn = get_db_connection()
    # Busca o cliente específico pelo ID
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()

    # Se o usuário clicou no botão "Salvar Alterações" do formulário
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']

        if not nome or not email:
            flash('Nome e Email são campos obrigatórios!')
        else:
            # Atualiza os dados no banco
            conn.execute('''
                UPDATE clientes 
                SET nome = ?, email = ?, telefone = ? 
                WHERE id = ?
            ''', (nome, email, telefone, id))
            conn.commit()
            conn.close()
            flash('Cliente atualizado com sucesso!')
            return redirect(url_for('lista')) # Volta para a lista

    conn.close()
    # Se ele só está abrindo a página, mostra o formulário preenchido
    return render_template('editar.html', cliente=cliente)
# ------------------------------------------

if __name__ == '__main__':
    init_db() # Cria o banco de dados e a tabela ao iniciar
    app.run(debug=True)