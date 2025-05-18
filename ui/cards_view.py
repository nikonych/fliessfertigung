
import flet as ft
import sqlite3
from ui.cards import RecordCard

def create_card_tab(db_path, table_name):
    grid = ft.GridView(
        expand=True,
        runs_count=0,  # auto
        max_extent=400,  # 4 карточки на 1400px ширины
        child_aspect_ratio=1.4,
        spacing=10,
        run_spacing=10,
    )
    debug = ft.Text()

    def load_data():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            grid.controls = [
                RecordCard(
                    title=f"{table_name} #{i+1}",
                    record=dict(row),
                    on_edit=lambda r: print("EDIT", r),
                    on_delete=lambda r: print("DELETE", r)
                )
                for i, row in enumerate(rows)
            ]
            debug.value = f"{len(rows)} Zeilen geladen"
        except Exception as e:
            debug.value = f"Fehler: {e}"
        finally:
            conn.close()

    load_button = ft.ElevatedButton("Neu laden", on_click=lambda e: load_data())
    load_data()

    return ft.Container(
        expand=True,
        padding=10,
        content=ft.Column([
            ft.Row([ft.Text(f"Tabelle: {table_name}", size=20), load_button]),
            debug,
            ft.Divider(),
            grid  # 👈 теперь сетка карточек
        ],
        expand=True)
    )


