import flet as ft
from datetime import datetime

import pandas as pd


def create_machine_widget(maschine):
    return ft.Container(
        width=300,
        height=150,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=5,
        padding=10,
        content=ft.Column([
            ft.Text(maschine.Bezeichnung, weight=ft.FontWeight.BOLD),  # Исправлено на Bezeichnung
            ft.ProgressBar(
                value=len(maschine.in_bearbeitung)/maschine.kapazität,
                color=ft.Colors.BLUE_300,
                bgcolor=ft.Colors.GREY_300
            ),
            ft.Text(f"Kapazität: {maschine.kapazität}"),
            ft.Divider(),
            ft.Row([
                ft.Column([
                    ft.Text("In Bearbeitung:"),
                    *[ft.Container(
                        width=20,
                        height=20,
                        border_radius=10,
                        bgcolor=ft.Colors.RED_300 if teil.position == 'processing' else ft.Colors.ORANGE_300,
                        tooltip=f"Teil {teil.id}\nBearbeitungszeit: {sum(teil.bearbeitungszeiten.values())} min"
                    ) for teil in maschine.in_bearbeitung]
                ]),
                ft.VerticalDivider(),
                ft.Column([
                    ft.Text("Warteschlange:"),
                    *[ft.Container(
                        width=20,
                        height=20,
                        border_radius=10,
                        bgcolor=ft.Colors.RED_300 if teil.position == 'processing' else ft.Colors.ORANGE_300,
                        tooltip=f"Teil {teil.id}\nBearbeitungszeit: {sum(teil.bearbeitungszeiten.values())} min"
                    ) for teil in maschine.warteschlange]
                ])
            ])
        ])
    )


def create_control_panel(on_control_callback):
    return ft.Row([
        ft.ElevatedButton(
            "Start",
            icon=ft.Icons.PLAY_ARROW,
            on_click=lambda e: on_control_callback('start')
        ),
        ft.ElevatedButton(
            "Pause",
            icon=ft.Icons.PAUSE,
            on_click=lambda e: on_control_callback('pause')
        ),
        ft.ElevatedButton(
            "Reset",
            icon=ft.Icons.REPLAY,
            on_click=lambda e: on_control_callback('reset')
        ),
        ft.Slider(
            min=0.1,
            max=10,
            divisions=10,
            label="{value}x",
            on_change=lambda e: on_control_callback(('speed', e.control.value))
        )
    ])


def create_stats_panel(simulation):
    stats_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Maschine")),
            ft.DataColumn(ft.Text("Auslastung")),
            ft.DataColumn(ft.Text("Stillstand")),
            ft.DataColumn(ft.Text("Warteschlange"))
        ],
        rows=[]
    )

    def update_stats():
        stats_table.rows.clear()
        for maschine in simulation.maschinen:
            try:
                # Используем текущее время симуляции вместо datetime.min
                if simulation.sim_time > pd.Timestamp('1970-01-01'):
                    total_time = (simulation.sim_time - pd.Timestamp('1970-01-01')).total_seconds() / 60
                else:
                    total_time = 1  # Защита от деления на ноль

                busy_time = sum(t.bearbeitungszeiten.get(maschine.Nr, 0) for t in simulation.teile)

                stats_table.rows.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(maschine.Bezeichnung)),
                        ft.DataCell(ft.Text(f"{(busy_time / total_time * 100):.1f}%" if total_time > 0 else "N/A")),
                        ft.DataCell(ft.Text(f"{maschine.stillstandzeit:.1f} min")),
                        ft.DataCell(ft.Text(str(len(maschine.warteschlange))))
                    ]
                ))
            except Exception as e:
                print(f"Ошибка в статистике: {str(e)}")

        stats_table.update()

    return ft.Column([
        ft.Text("Statistiken", size=18, weight=ft.FontWeight.BOLD),
        stats_table
    ]), update_stats