import sqlite3
import tempfile

import flet as ft
from flet.core.file_picker import FilePickerResultEvent
from flet.core.snack_bar import SnackBar
from flet.core.text import Text

from core.simulation import Simulation
from data.transfer_to_sqlite import create_database_and_tables, insert_data
from ui.cards_view import create_card_tab
import threading
import time

import os
import sys
import shutil


def resource_path(relative_path):
    """ PyInstaller compatibility (flet pack аналогично работает) """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def get_user_db_path():
    return os.path.join(tempfile.gettempdir(), "manufacturing.db")


def ensure_db_exists():
    db_dst = get_user_db_path()
    if not os.path.exists(db_dst):
        # Попытаться скопировать образец
        db_src = resource_path(os.path.join(tempfile.gettempdir(), "manufacturing.db"))
        if os.path.exists(db_src):
            shutil.copy(db_src, db_dst)
        else:
            create_empty_database(db_dst)  # Если образца нет — создаём пустую БД
    return db_dst


from data.db_utils import create_empty_database, import_excel_to_db

db_path = ensure_db_exists()  # Твоя функция, определяющая путь к базе
create_empty_database(db_path)  # <-- Гарантирует наличие таблиц




def build_ui(page: ft.Page):
    print(f"Используется база: {db_path}")
    simulation = Simulation(db_path)
    update_lock = threading.Lock()

    time_display = ft.Text("Simulationszeit: ", size=16)
    excel_picker = ft.FilePicker()

    def on_excel_picked(e: FilePickerResultEvent):
        if not e.files:
            return
        file_path = e.files[0].path
        import_excel_to_db(file_path, db_path, page)
        page.controls.clear()
        build_ui(page)
        page.update()

    excel_picker.on_result = on_excel_picked

    import_button = ft.ElevatedButton(
        "Excel importieren",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: excel_picker.pick_files(
            dialog_title="Excel-Datei wählen",
            allowed_extensions=["xlsx"],
            allow_multiple=False
        )
    )

    sim_layout = ft.Column([time_display])

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Maschine", content=create_card_tab(db_path, "Maschine")),
            ft.Tab(text="Auftrag", content=create_card_tab(db_path, "Auftrag")),
            ft.Tab(text="Arbeitsplan", content=create_card_tab(db_path, "Arbeitsplan")),
            ft.Tab(text="Simulation", content=ft.Column([time_display])),
        ],
        expand=True  # <— чтобы занять всё доступное пространство по высоте
    )


    # --- Вот ключевой кусок: оборачиваем tabs и кнопку в один Row ---
    main_layout = ft.Column([
        ft.Row(
            [
                tabs,  # сам Tabs уже «expand=True»
            ],
            expand=True,  # <-- Row растягивается и по ширине, и по высоте
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
    ])

    page.add(main_layout)

    def ui_update_loop():
        while True:
            time.sleep(0.5)

    threading.Thread(target=ui_update_loop, daemon=True).start()


