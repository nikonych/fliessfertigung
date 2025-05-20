# db_utils.py
import sqlite3

from flet.core.snack_bar import SnackBar
from flet.core.text import Text

from data.transfer_to_sqlite import create_database_and_tables, insert_data


def create_empty_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Maschine (
            Nr TEXT PRIMARY KEY,
            Bezeichnung TEXT,
            verf_von INTEGER,
            verf_bis INTEGER,
            Kap_Tag INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Auftrag (
            auftrag_nr TEXT PRIMARY KEY,
            Anzahl INTEGER,
            Start INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Arbeitsplan (
            auftrag_nr TEXT,
            ag_nr TEXT,
            maschine TEXT,
            dauer INTEGER,
            PRIMARY KEY (auftrag_nr, ag_nr),
            FOREIGN KEY (auftrag_nr) REFERENCES Auftrag(auftrag_nr),
            FOREIGN KEY (maschine) REFERENCES Maschine(Nr)
        )
    ''')
    conn.commit()
    conn.close()


def import_excel_to_db(excel_file, db_path, page):
    try:
        conn = sqlite3.connect(db_path)
        create_database_and_tables(db_path)  # Создаём таблицы если надо
        insert_data(conn, excel_file)
        conn.close()
        page.snack_bar = SnackBar(Text("Import erfolgreich!"))
        page.snack_bar.open = True
        page.update()
    except Exception as e:
        page.snack_bar = SnackBar(Text(f"Fehler beim Import: {e}"))
        page.snack_bar.open = True
        page.update()
