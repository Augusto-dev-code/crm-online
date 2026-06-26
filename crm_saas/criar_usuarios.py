import sqlite3
import os

CAMINHO_BANCO = os.path.join(
    os.path.dirname(__file__),
    "banco.db"
)

conn = sqlite3.connect(CAMINHO_BANCO)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    senha TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO usuarios
(usuario, senha)
VALUES (?, ?)
""", ("admin", "123"))

conn.commit()
conn.close()

print("Usuário admin criado!")