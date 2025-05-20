import pandas as pd
import sqlite3
from datetime import datetime


def create_database_and_tables(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Maschine
                   (
                       Nr
                       TEXT
                       PRIMARY
                       KEY,
                       Bezeichnung
                       TEXT,
                       verf_von
                       INTEGER,
                       verf_bis
                       INTEGER,
                       Kap_Tag
                       INTEGER
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Auftrag
                   (
                       auftrag_nr
                       TEXT
                       PRIMARY
                       KEY,
                       Anzahl
                       INTEGER,
                       Start
                       INTEGER
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Arbeitsplan
                   (
                       auftrag_nr
                       TEXT,
                       ag_nr
                       TEXT,
                       maschine
                       TEXT,
                       dauer
                       INTEGER,
                       PRIMARY
                       KEY
                   (
                       auftrag_nr,
                       ag_nr
                   ),
                       FOREIGN KEY
                   (
                       auftrag_nr
                   ) REFERENCES Auftrag
                   (
                       auftrag_nr
                   ),
                       FOREIGN KEY
                   (
                       maschine
                   ) REFERENCES Maschine
                   (
                       Nr
                   )
                       )
                   ''')

    conn.commit()
    return conn


def date_to_excel_serial(date):
    """Convert a date or Timestamp to Excel serial date (integer)."""
    if pd.isna(date):
        return 0
    if isinstance(date, pd.Timestamp):
        date = date.to_pydatetime()
    excel_epoch = datetime(1899, 12, 30)  # Excel's epoch
    delta = date - excel_epoch
    return delta.days


def format_number(nr, digits=3):
    """Convert number to zero-padded string (e.g., 1.0 → '001' for 3 digits)."""
    if pd.isna(nr):
        return '0' * digits
    return f"{int(float(nr)):0{digits}d}"


def process_auftrag_sheet(df, cursor):
    if df.empty:
        print("Auftrag sheet is empty")
        return
    expected_columns = ['auftrag_nr', 'Anzahl', 'Start']
    if not all(col in df.columns for col in expected_columns):
        print(f"Auftrag sheet missing required columns. Found: {df.columns.tolist()}")
        return
    auftrag_data = df[df['auftrag_nr'].notna() & df['Anzahl'].notna() & df['Start'].notna()][expected_columns]
    print("Auftrag data shape:", auftrag_data.shape)
    for _, row in auftrag_data.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO Auftrag (auftrag_nr, Anzahl, Start)
            VALUES (?, ?, ?)
        ''', (
            str(row['auftrag_nr']),
            int(row['Anzahl']) if pd.notna(row['Anzahl']) else 0,
            int(row['Start']) if pd.notna(row['Start']) else 0
        ))


def process_arbeitsplan_sheet(df, cursor):
    if df.empty:
        print("Arbeitsplan sheet is empty")
        return
    expected_columns = ['auftrag_nr', 'ag_nr', 'maschine', 'dauer']
    if not all(col in df.columns for col in expected_columns):
        print(f"Arbeitsplan sheet missing required columns. Found: {df.columns.tolist()}")
        return
    arbeitsplan_data = \
    df[df['auftrag_nr'].notna() & df['ag_nr'].notna() & df['maschine'].notna() & df['dauer'].notna()][expected_columns]
    print("Arbeitsplan data shape:", arbeitsplan_data.shape)
    for _, row in arbeitsplan_data.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO Arbeitsplan (auftrag_nr, ag_nr, maschine, dauer)
            VALUES (?, ?, ?, ?)
        ''', (
            str(row['auftrag_nr']),
            format_number(row['ag_nr'], digits=2),  # Zero-pad ag_nr to 2 digits
            format_number(row['maschine'], digits=3),  # Zero-pad maschine to 3 digits
            int(row['dauer']) if pd.notna(row['dauer']) else 0
        ))


def process_maschine_sheet(df, cursor):
    if df.empty:
        print("Maschine sheet is empty")
        return
    expected_columns = ['Nr', 'Bezeichnung', 'verf_von', 'verf_bis', 'Kap_Tag']
    if not all(col in df.columns for col in expected_columns):
        print(f"Maschine sheet missing required columns. Found: {df.columns.tolist()}")
        return
    maschine_data = df[df['Nr'].notna() & df['Bezeichnung'].notna()][expected_columns]
    print("Maschine data shape:", maschine_data.shape)
    for _, row in maschine_data.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO Maschine (Nr, Bezeichnung, verf_von, verf_bis, Kap_Tag)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            format_number(row['Nr'], digits=3),  # Zero-pad Nr to 3 digits
            str(row['Bezeichnung']),
            date_to_excel_serial(row['verf_von']) if pd.notna(row['verf_von']) else 0,
            date_to_excel_serial(row['verf_bis']) if pd.notna(row['verf_bis']) else 0,
            int(row['Kap_Tag']) if pd.notna(row['Kap_Tag']) else 0
        ))


def insert_data(conn, excel_file):
    xls = pd.ExcelFile(excel_file)
    cursor = conn.cursor()

    print("Available sheets:", xls.sheet_names)

    for sheet_name in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name, na_values=['', 'NaN'])
            df = df.dropna(how='all')  # Drop rows where all values are NaN
            print(f"\nProcessing sheet: {sheet_name}")
            print("Columns:", df.columns.tolist())
            print("First few rows:\n", df.head().to_string())
            print("Shape:", df.shape)

            if df.empty:
                print(f"Sheet {sheet_name} is empty after cleaning")
                continue

            if sheet_name.lower() == 'auftrag':
                process_auftrag_sheet(df, cursor)
            elif sheet_name.lower() == 'arbeitsplan':
                process_arbeitsplan_sheet(df, cursor)
            elif sheet_name.lower() == 'maschine':
                process_maschine_sheet(df, cursor)
            else:
                print(f"Skipping sheet {sheet_name} (unrecognized)")

        except Exception as e:
            print(f"Error processing sheet {sheet_name}: {str(e)}")
            continue

    conn.commit()
    if cursor.rowcount == 0:
        print("Warning: No data was inserted from any sheet")


def main():
    excel_file = "../21_Simulation_Fliessfertigung (2).xlsx"
    db_name = "manufacturing.db"

    conn = create_database_and_tables(db_name)

    try:
        insert_data(conn, excel_file)
        print("Data successfully transferred to SQLite database")

    except Exception as e:
        print(f"Error occurred: {str(e)}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()