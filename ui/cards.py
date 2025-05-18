

import flet as ft

def RecordCard(title: str, record: dict, on_edit=None, on_delete=None):
    rows = [
        ft.Text(f"{key}: {value}", size=13)
        for key, value in record.items()
    ]

    return ft.Card(
        content=ft.Container(
            padding=10,
            content=ft.Column([
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Bearbeiten",
                                icon_color=ft.Colors.BLUE,
                                on_click=lambda e: on_edit(record) if on_edit else None,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Löschen",
                                icon_color=ft.Colors.RED,
                                on_click=lambda e: on_delete(record) if on_delete else None,
                            ),
                        ])
                    ]
                ),
                ft.Column(rows, spacing=3),
            ],
            spacing=8)
        )
    )

