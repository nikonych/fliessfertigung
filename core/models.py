from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class Teil:
    id: int
    startzeit: datetime
    bearbeitungszeiten: dict[int, float]  # {maschine_id: dauer}
    current_maschine: int = 0
    endzeit: datetime = None
    position: str = 'waiting'  # 'processing'|'waiting'|'done'

    @property
    def durchlaufzeit(self):
        return (self.endzeit - self.startzeit).total_seconds() if self.endzeit else 0

    @property
    def liegezeit(self):
        return self.durchlaufzeit - sum(self.bearbeitungszeiten.values())


@dataclass
class Maschine:
    Nr: str
    Bezeichnung: str  # Используем оригинальное название из БД
    verf_von: pd.Timestamp
    verf_bis: pd.Timestamp
    Kap_Tag: int

    def __post_init__(self):
        self.warteschlange = []
        self.in_bearbeitung = []
        self.stillstandzeit = 0.0
        self.kapazität = self.Kap_Tag
        self.id = self.Nr  # Добавляем алиас для совместимости
