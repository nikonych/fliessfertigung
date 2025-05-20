import flet as ft
import sqlite3
from ui.cards import RecordCard


def create_card_tab(db_path, table_name):
    grid = ft.GridView(
        expand=True,
        runs_count=0,
        max_extent=400,
        child_aspect_ratio=1.4,
        spacing=10,
        run_spacing=10,
    )
    debug = ft.Text()

    # ----------------------
    # ДИАЛОГ ДЛЯ MASCHINE
    # ----------------------
    dlg = ft.AlertDialog(modal=True,
                         title=ft.Text(""),  # <- пустой заголовок, можно и content=ft.Text("") добавить
                         content=ft.Text(""),
                         actions=[])
    nr = ft.TextField(label="Nr", autofocus=True)
    bezeichnung = ft.TextField(label="Bezeichnung")
    verf_von = ft.TextField(label="verf_von (Excel Datum, z.B. 45252)")
    verf_bis = ft.TextField(label="verf_bis (Excel Datum, z.B. 45260)")
    kap_tag = ft.TextField(label="Kapazität pro Tag", keyboard_type=ft.KeyboardType.NUMBER)
    dialog_fields = [nr, bezeichnung, verf_von, verf_bis, kap_tag]

    def show_add_dialog(e):
        for field in dialog_fields:
            field.value = ""
        dlg.title = ft.Text("Neue Maschine anlegen")
        dlg.content = ft.Column(dialog_fields, tight=True)
        dlg.actions = [
            ft.TextButton("Abbrechen", on_click=lambda e: setattr(dlg, "open", False)),
            ft.ElevatedButton("Erstellen", on_click=add_new_machine)
        ]
        dlg.open = True
        dlg.update()

    def add_new_machine(e):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Maschine (Nr, Bezeichnung, verf_von, verf_bis, Kap_Tag) VALUES (?, ?, ?, ?, ?)",
                (nr.value, bezeichnung.value, int(verf_von.value), int(verf_bis.value), int(kap_tag.value))
            )
            conn.commit()
            dlg.open = False
            dlg.update()
            load_data(do_update=True)  # обновить таблицу и вызвать update
        except Exception as ex:
            debug.value = f"Fehler beim Hinzufügen: {ex}"
            debug.update()
        finally:
            if conn:
                conn.close()

    # ------------------------
    # ГЛАВНАЯ ФУНКЦИЯ ЗАГРУЗКИ
    # ------------------------
    def load_data(do_update=False):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            grid.controls = [
                RecordCard(
                    title=f"{table_name} #{i + 1}",
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
        if do_update:
            grid.update()
            debug.update()

    # -------------------
    # КНОПКИ
    # -------------------
    add_button = None
    if table_name == "Maschine":
        add_button = ft.ElevatedButton("Neue Maschine", icon=ft.Icons.ADD, on_click=show_add_dialog)

    # начальная загрузка (без update!)
    load_data(do_update=False)
    controls_row = [ft.Text(f"Tabelle: {table_name}", size=20)]

    if add_button:
        controls_row.append(add_button)

    # on_mount для первой отрисовки (с update) — опционально, но удобно:
    def on_mount(e):
        load_data(do_update=True)

    return ft.Container(
        expand=True,
        padding=10,
        content=ft.Column([
            ft.Row(controls_row),
            debug,
            ft.Divider(),
            grid,
            dlg
        ], expand=True),
    )
