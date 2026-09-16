"""
Modulo database: gestisce tutte le operazioni sul database SQLite.
Usiamo SQLite perché è incluso in Python (nessuna installazione extra)
ed è perfetto per validare l'idea prima di eventualmente migrare
a un database condiviso online (es. Supabase) quando servirà
gestire più utenti contemporaneamente da posti diversi.
"""

import sqlite3
import pandas as pd

DB_PATH = "test_atleti.db"

# Tipi di test presenti di default alla prima esecuzione.
# Il cliente potrà aggiungerne altri dalla pagina "Gestisci Tipi di Test".
TIPI_TEST_DI_DEFAULT = [
    ("Salto Verticale", "cm"),
    ("Salto in Lungo", "cm"),
    ("Sprint 20m", "sec"),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea le tabelle se non esistono e inserisce i tipi di test di default."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS atleti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            data_nascita TEXT,
            note TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tipi_test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            unita_misura TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS risultati (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            atleta_id INTEGER NOT NULL,
            tipo_test_id INTEGER NOT NULL,
            valore REAL NOT NULL,
            data TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (atleta_id) REFERENCES atleti (id) ON DELETE CASCADE,
            FOREIGN KEY (tipo_test_id) REFERENCES tipi_test (id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM tipi_test")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO tipi_test (nome, unita_misura) VALUES (?, ?)",
            TIPI_TEST_DI_DEFAULT,
        )
        conn.commit()

    conn.close()


# ---------------------------------------------------------
# ATLETI
# ---------------------------------------------------------

def add_atleta(nome, cognome, data_nascita, note):
    conn = get_connection()
    conn.execute(
        "INSERT INTO atleti (nome, cognome, data_nascita, note) VALUES (?, ?, ?, ?)",
        (nome, cognome, data_nascita, note),
    )
    conn.commit()
    conn.close()


def get_atleti():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM atleti ORDER BY cognome, nome", conn)
    conn.close()
    return df


def delete_atleta(atleta_id):
    conn = get_connection()
    conn.execute("DELETE FROM atleti WHERE id = ?", (atleta_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------
# TIPI DI TEST (la parte "personalizzabile")
# ---------------------------------------------------------

def add_tipo_test(nome, unita_misura):
    conn = get_connection()
    conn.execute(
        "INSERT INTO tipi_test (nome, unita_misura) VALUES (?, ?)",
        (nome, unita_misura),
    )
    conn.commit()
    conn.close()


def get_tipi_test():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM tipi_test ORDER BY nome", conn)
    conn.close()
    return df


def delete_tipo_test(tipo_test_id):
    conn = get_connection()
    conn.execute("DELETE FROM tipi_test WHERE id = ?", (tipo_test_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------
# RISULTATI DEI TEST
# ---------------------------------------------------------

def add_risultato(atleta_id, tipo_test_id, valore, data, note):
    conn = get_connection()
    conn.execute(
        """INSERT INTO risultati (atleta_id, tipo_test_id, valore, data, note)
           VALUES (?, ?, ?, ?, ?)""",
        (atleta_id, tipo_test_id, valore, data, note),
    )
    conn.commit()
    conn.close()


def get_risultati(atleta_id=None):
    conn = get_connection()
    query = """
        SELECT
            r.id,
            a.nome || ' ' || a.cognome AS atleta,
            t.nome AS tipo_test,
            r.valore,
            t.unita_misura,
            r.data,
            r.note
        FROM risultati r
        JOIN atleti a ON a.id = r.atleta_id
        JOIN tipi_test t ON t.id = r.tipo_test_id
    """
    params = ()
    if atleta_id is not None:
        query += " WHERE r.atleta_id = ?"
        params = (atleta_id,)
    query += " ORDER BY r.data DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df
