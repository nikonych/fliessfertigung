import flet as ft
from core.simulation import Simulation
from ui.cards_view import create_card_tab
from ui.components import create_machine_widget, create_control_panel, create_stats_panel
import threading
import time

import os

db_path = os.path.join("data", "manufacturing.db")


def build_ui(page: ft.Page):
    simulation = Simulation()
    update_lock = threading.Lock()

    def handle_sim_control(command):
        if command == 'start':
            if not simulation.running:
                simulation.running = True
                threading.Thread(target=sim_thread, daemon=True).start()
        elif command == 'pause':
            simulation.running = False
        elif command == 'reset':
            simulation.__init__()
            update_ui()
        elif isinstance(command, tuple) and command[0] == 'speed':
            simulation.speed = command[1]

    time_display = ft.Text("Simulationszeit: ", size=16)
    machine_panel = ft.Row(scroll=ft.ScrollMode.AUTO)
    control_panel = create_control_panel(handle_sim_control)
    stats_panel, update_stats = create_stats_panel(simulation)

    def update_ui():
        with update_lock:
            state = simulation.get_state()
            time_display.value = f"Simulationszeit: {state['sim_time'].strftime('%Y-%m-%d %H:%M')}"
            machine_panel.controls = [create_machine_widget(m) for m in state['maschinen']]
            update_stats()
            page.update()

    def sim_thread():
        simulation.start()

    sim_layout = ft.Column([
        time_display,
        control_panel,
        ft.Divider(),
        machine_panel,
        ft.Divider(),
        stats_panel
    ])

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Simulation", content=sim_layout),
            ft.Tab(text="Maschine", content=create_card_tab(db_path, "Maschine")),
            ft.Tab(text="Auftrag", content=create_card_tab(db_path, "Auftrag")),
            ft.Tab(text="Arbeitsplan", content=create_card_tab(db_path, "Arbeitsplan"))
        ],
        expand=True
    )

    page.add(tabs)  # ✅ только один раз добавляем всё

    def ui_update_loop():
        while True:
            update_ui()
            time.sleep(0.5)

    threading.Thread(target=ui_update_loop, daemon=True).start()

