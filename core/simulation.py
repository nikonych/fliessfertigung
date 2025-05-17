import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from queue import PriorityQueue
from core.models import Teil, Maschine
import threading
import time


class Simulation:
    def __init__(self, db_path='manufacturing.db'):
        self.sim_time = pd.Timestamp('2020-01-01')
        self.db_conn = sqlite3.connect(db_path)
        self.events = PriorityQueue()
        self.maschinen = self._load_maschinen()
        self.teile = self._load_auftraege()
        self.sim_time = datetime.min
        self.running = False
        self.speed = 1.0  # 1x real-time
        self.lock = threading.Lock()

    def _load_maschinen(self):
        df = pd.read_sql("SELECT * FROM Maschine", self.db_conn)

        # Конвертация с обработкой переполнения
        def convert_excel_date(day_num):
            try:
                return pd.Timestamp('1899-12-30') + pd.DateOffset(days=int(day_num))
            except:
                return pd.NaT

        df['verf_von'] = df['verf_von'].apply(convert_excel_date)
        df['verf_bis'] = df['verf_bis'].apply(convert_excel_date)

        print("Проверка конвертации дат Maschine:")
        print(df[['Nr', 'verf_von', 'verf_bis']].head(3))

        return [Maschine(**row) for row in df.to_dict('records')]

    def _load_auftraege(self):
        df = pd.read_sql("""
                         SELECT a.auftrag_nr AS id,
                                a.Start      AS startzeit,
                                ag.maschine  AS maschine_id,
                                ag.dauer     AS dauer
                         FROM Auftrag a
                                  JOIN Arbeitsplan ag ON a.auftrag_nr = ag.auftrag_nr
                         ORDER BY a.auftrag_nr, ag.ag_nr
                         """, self.db_conn)

        # Конвертация даты с проверкой
        try:
            df['startzeit'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df['startzeit'], unit='D')
        except Exception as e:
            print(f"Ошибка конвертации даты: {str(e)}")
            df['startzeit'] = pd.NaT

        print("\nПример данных Auftrag:")
        print(df[['id', 'startzeit', 'maschine_id', 'dauer']].head(3))

        auftraege = []
        for auftrag_nr, group in df.groupby('id'):
            startzeit = group.iloc[0]['startzeit']
            bearbeitungszeiten = {
                row['maschine_id']: row['dauer']
                for _, row in group.iterrows()
            }
            teil = Teil(auftrag_nr, startzeit, bearbeitungszeiten)
            self.events.put((startzeit, 'teil_start', teil))
            auftraege.append(teil)
        return auftraege

    def _process_teil_start(self, teil: Teil):
        first_maschine = next(iter(teil.bearbeitungszeiten))
        maschine = next(m for m in self.maschinen if m.id == first_maschine)
        maschine.warteschlange.append(teil)
        teil.current_maschine = first_maschine

    def _process_maschine(self, maschine: Maschine):
        # Freie Kapazität berechnen
        free_slots = maschine.kapazität - len(maschine.in_bearbeitung)

        # Teile aus der Warteschlange holen
        for _ in range(free_slots):
            if maschine.warteschlange:
                teil = maschine.warteschlange.pop(0)
                dauer = teil.bearbeitungszeiten[maschine.id]
                end_time = self.sim_time + timedelta(minutes=dauer)
                self.events.put((end_time, 'teil_fertig', (teil, maschine.id)))
                maschine.in_bearbeitung.append(teil)
                teil.position = 'processing'

    def _process_teil_fertig(self, teil: Teil, maschine_id: int):
        # Nächste Maschine finden
        current_idx = list(teil.bearbeitungszeiten.keys()).index(maschine_id)
        next_maschine_id = list(teil.bearbeitungszeiten.keys())[current_idx + 1] if current_idx + 1 < len(
            teil.bearbeitungszeiten) else None

        if next_maschine_id:
            next_maschine = next(m for m in self.maschinen if m.id == next_maschine_id)
            next_maschine.warteschlange.append(teil)
            teil.current_maschine = next_maschine_id
            teil.position = 'waiting'
        else:
            teil.endzeit = self.sim_time
            teil.position = 'done'

    def run_step(self):
        with self.lock:
            if self.events.empty():
                return False

            event_time, event_type, event_data = self.events.get()
            self.sim_time = event_time

            if event_type == 'teil_start':
                self._process_teil_start(event_data)
            elif event_type == 'teil_fertig':
                self._process_teil_fertig(*event_data)

            # Maschinen verarbeiten
            for maschine in self.maschinen:
                self._process_maschine(maschine)

            return True

    def start(self):
        self.running = True
        while self.running:
            if not self.run_step():
                break
            time.sleep(0.1 / self.speed)

    def get_state(self):
        with self.lock:
            return {
                'sim_time': self.sim_time,
                'maschinen': self.maschinen,
                'teile': self.teile,
                'running': self.running
            }
