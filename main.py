import flet as ft
import sqlite3
import pandas as pd


def main(page: ft.Page):
    page.title = "Manufacturing Tables"
    page.window_width = 1200
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT

    def get_db_connection():
        return sqlite3.connect("manufacturing.db")

    def fetch_table_data(table_name):
        conn = get_db_connection()
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def format_number(nr, digits=3):
        """Convert number to zero-padded string (e.g., 1 → '001' for 3 digits)."""
        if pd.isna(nr):
            return '0' * digits
        return f"{int(nr):0{digits}d}"

    def create_data_table(df, column_names, format_columns=None):
        """Create a Flet DataTable from a DataFrame."""
        if format_columns is None:
            format_columns = {}

        columns = [ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD)) for col in column_names]
        rows = []
        for _, row in df.iterrows():
            cells = []
            for col in column_names:
                value = row[col]
                if col in format_columns:
                    value = format_columns[col](value)
                cells.append(ft.DataCell(ft.Text(str(value))))
            rows.append(ft.DataRow(cells=cells))

        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, ft.Colors.GREY_400),
            heading_row_color=ft.Colors.GREY_200,
            heading_row_height=40,
            data_row_min_height=40,
            column_spacing=10,
        )

    # Fetch data from database
    try:
        auftrag_df = fetch_table_data("Auftrag")
        arbeitsplan_df = fetch_table_data("Arbeitsplan")
        maschine_df = fetch_table_data("Maschine")
    except Exception as e:
        page.add(ft.Text(f"Error loading data: {str(e)}", color=ft.colors.RED))
        return

    # Define column names for each table
    auftrag_columns = ["auftrag_nr", "Anzahl", "Start"]
    arbeitsplan_columns = ["auftrag_nr", "ag_nr", "maschine", "dauer"]
    maschine_columns = ["Nr", "Bezeichnung", "verf_von", "verf_bis", "Kap_Tag"]

    # Define formatting for specific columns
    format_columns = {
        "Nr": lambda x: format_number(x, digits=3),
        "maschine": lambda x: format_number(x, digits=3),
        "ag_nr": lambda x: format_number(x, digits=2)
    }

    # Create DataTables
    auftrag_table = create_data_table(auftrag_df, auftrag_columns, format_columns)
    arbeitsplan_table = create_data_table(arbeitsplan_df, arbeitsplan_columns, format_columns)
    maschine_table = create_data_table(maschine_df, maschine_columns, format_columns)

    # Create scrollable containers
    auftrag_container = ft.Container(
        content=ft.Column([auftrag_table], scroll=ft.ScrollMode.AUTO),
        expand=True,
        padding=10
    )
    arbeitsplan_container = ft.Container(
        content=ft.Column([arbeitsplan_table], scroll=ft.ScrollMode.AUTO),
        expand=True,
        padding=10
    )
    maschine_container = ft.Container(
        content=ft.Column([maschine_table], scroll=ft.ScrollMode.AUTO),
        expand=True,
        padding=10
    )

    # Create tabs
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Auftrag", content=auftrag_container),
            ft.Tab(text="Arbeitsplan", content=arbeitsplan_container),
            ft.Tab(text="Maschine", content=maschine_container),
        ],
        expand=True
    )

    # Add tabs to page
    page.add(tabs)
    page.update()


ft.app(target=main)