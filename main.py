import flet as ft
from ui.views import build_ui

def main(page: ft.Page):
    page.title = "Fließfertigung Simulation"
    page.window_width = 1400
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.MainAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 0

    build_ui(page)

if __name__ == "__main__":
    ft.app(target=main)
