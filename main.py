import flet as ft
from database import fetch_table_data
from components import create_data_table, format_number

def main(page: ft.Page):
    page.title = "Manufacturing Tables"
    page.window_width = 1200
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT

    try:
        auftrag_df = fetch_table_data("Auftrag")
        arbeitsplan_df = fetch_table_data("Arbeitsplan")
        maschine_df = fetch_table_data("Maschine")
    except Exception as e:
        page.add(ft.Text(f"Error loading data: {str(e)}", color=ft.colors.RED))
        return

    auftrag_columns = ["auftrag_nr", "Anzahl", "Start"]
    arbeitsplan_columns = ["auftrag_nr", "ag_nr", "maschine", "dauer"]
    maschine_columns = ["Nr", "Bezeichnung", "verf_von", "verf_bis", "Kap_Tag"]

    format_columns = {
        "Nr": lambda x: format_number(x, digits=3),
        "maschine": lambda x: format_number(x, digits=3),
        "ag_nr": lambda x: format_number(x, digits=2)
    }

    auftrag_table = create_data_table(auftrag_df, auftrag_columns, format_columns)
    arbeitsplan_table = create_data_table(arbeitsplan_df, arbeitsplan_columns, format_columns)
    maschine_table = create_data_table(maschine_df, maschine_columns, format_columns)

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Auftrag",
                content=ft.Container(
                    ft.Column([auftrag_table], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    padding=10
                )
            ),
            ft.Tab(
                text="Arbeitsplan",
                content=ft.Container(
                    ft.Column([arbeitsplan_table], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    padding=10
                )
            ),
            ft.Tab(
                text="Maschine",
                content=ft.Container(
                    ft.Column([maschine_table], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    padding=10
                )
            ),
        ],
        expand=True
    )

    page.add(tabs)
    page.update()

ft.app(target=main)