from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

app.secret_key = "crm_saas_segredo"

CAMINHO_BANCO = os.path.join(
    os.path.dirname(__file__),
    "banco.db"
)

# Cria a tabela se não existir
conn = sqlite3.connect(CAMINHO_BANCO)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    observacoes TEXT,
    data_cadastro TEXT
)           
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    senha TEXT
)
""")

conn.commit()
conn.close()

conn = sqlite3.connect(CAMINHO_BANCO)
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE clientes
    ADD COLUMN usuario TEXT
    """)
except:
    pass

conn.commit()
conn.close()


@app.route("/")
def home():

    if "usuario" not in session:
        return redirect("/login")

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    # Total de clientes do usuário logado
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM clientes
        WHERE usuario = ?
        """,
        (session["usuario"],)
    )

    total_clientes = cursor.fetchone()[0]

    # Últimos 5 clientes do usuário logado
    cursor.execute(
        """
        SELECT nome
        FROM clientes
        WHERE usuario = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (session["usuario"],)
    )

    ultimos_clientes = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_clientes=total_clientes,
        ultimos_clientes=ultimos_clientes,
        usuario=session["usuario"]
    )

@app.route("/cadastro")
def cadastro():

    if "usuario" not in session:
        return redirect("/login")

    return render_template("cadastro.html")

@app.route("/cadastrar", methods=["POST"])
def cadastrar():

    nome = request.form["nome"]
    telefone = request.form["telefone"]
    observacoes = request.form["observacoes"]

    telefone = "".join(filter(str.isdigit, telefone))

    if len(telefone) not in [10, 11]:
       flash("Telefone inválido!", "erro")
       return redirect("/cadastro")

    data_cadastro = datetime.now().strftime("%d/%m/%Y")

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    cursor.execute(
    """
    INSERT INTO clientes
    (nome, telefone, observacoes, data_cadastro, usuario)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        nome,
        telefone,
        observacoes,
        data_cadastro,
        session["usuario"]
    )
)
    conn.commit()
    conn.close()

    flash("Cliente cadastrado com sucesso!", "sucesso")
    return redirect("/clientes")

@app.route("/clientes")
def clientes():

    if "usuario" not in session:
        return redirect("/login")

    busca = request.args.get("busca", "")

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM clientes
        WHERE usuario = ?
        AND nome LIKE ?
        ORDER BY id DESC
        """,
        (
            session["usuario"],
            "%" + busca + "%"
        )
    )

    clientes = cursor.fetchall()

    conn.close()

    return render_template(
        "clientes.html",
        clientes=clientes,
        busca=busca
    )


@app.route("/excluir/<int:id>")
def excluir(id):

    if "usuario" not in session:
        return redirect("/login")

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM clientes
        WHERE id = ?
        AND usuario = ?
        """,
        (
            id,
            session["usuario"]
        )
    )

    conn.commit()
    conn.close()

    flash("Cliente excluído com sucesso!", "sucesso")

    return redirect("/clientes")


@app.route("/editar/<int:id>")
def editar(id):

    if "usuario" not in session:
        return redirect("/login")

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM clientes
        WHERE id = ?
        AND usuario = ?
        """,
        (
            id,
            session["usuario"]
        )
    )

    cliente = cursor.fetchone()

    conn.close()

    if not cliente:
        return redirect("/clientes")

    return render_template(
        "editar.html",
        cliente=cliente
    )


@app.route("/atualizar/<int:id>", methods=["POST"])
def atualizar(id):

    nome = request.form["nome"]
    telefone = request.form["telefone"]
    observacoes = request.form["observacoes"]

    telefone = "".join(filter(str.isdigit, telefone))

    if len(telefone) not in [10, 11]:
        flash("Telefone inválido!", "erro")
        return redirect(f"/editar/{id}")

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE clientes
        SET nome = ?, telefone = ?, observacoes = ?
        WHERE id = ?
        """,
        (nome, telefone, observacoes, id)
    )

    conn.commit()
    conn.close()

    flash("Cliente atualizado com sucesso!", "sucesso")
    return redirect("/clientes")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/fazer_login", methods=["POST"])
def fazer_login():

    usuario = request.form["usuario"]
    senha = request.form["senha"]

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM usuarios
        WHERE usuario = ? AND senha = ?
        """,
        (usuario, senha)
    )

    usuario_encontrado = cursor.fetchone()

    conn.close()

    if usuario_encontrado:
        session["usuario"] = usuario
        return redirect("/")

    return "Usuário ou senha incorretos"


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/cadastrar_usuario", methods=["POST"])
def cadastrar_usuario():

    usuario = request.form["usuario"]
    senha = request.form["senha"]

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO usuarios (usuario, senha)
        VALUES (?, ?)
        """,
        (usuario, senha)
    )

    conn.commit()
    conn.close()

    return redirect("/login")

@app.route("/cadastro_usuario")
def cadastro_usuario():
    return render_template("cadastro_usuario.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
