import flet as ft
from core.simulation import Simulation
from ui.components import create_machine_widget, create_control_panel, create_stats_panel
import threading
import time

from datetime import datetime


def main(page: ft.Page):
    page.title = "Fließfertigung Simulation"
    page.window_width = 1400
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT

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
    # Create UI elements
    time_display = ft.Text("Simulationszeit: ", size=16)
    machine_panel = ft.Row(scroll=ft.ScrollMode.AUTO)
    control_panel = create_control_panel(handle_sim_control)
    stats_panel, update_stats = create_stats_panel(simulation)

    def update_ui():
        with update_lock:
            state = simulation.get_state()
            time_display.value = f"Simulationszeit: {state['sim_time'].strftime('%Y-%m-%d %H:%M')}"

            # Update machines
            machine_panel.controls = [
                create_machine_widget(m)
                for m in state['maschinen']
            ]

            # Update stats
            update_stats()

            page.update()

    def sim_thread():
        simulation.start()



    # Setup layout
    page.add(
        ft.Column([
            time_display,
            control_panel,
            ft.Divider(),
            machine_panel,
            ft.Divider(),
            stats_panel
        ])
    )

    # Start UI update loop
    def ui_update_loop():
        while True:
            update_ui()
            time.sleep(0.5)

    threading.Thread(target=ui_update_loop, daemon=True).start()


if __name__ == "__main__":
    ft.app(target=main)