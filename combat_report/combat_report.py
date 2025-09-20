# For each player show hps and dps

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
import json


class Metadata(BaseModel):
    startTime: int
    endTime: int
    durationSec: int
    totalDamageDone: int
    totalDamageTaken: int
    eventCount: int


class Resources(BaseModel):
    HP: int
    HPmax: int
    Shield: float
    Mana: int
    Energy: int


class Event(BaseModel):
    timestamp: int
    direction: str
    attacker: str
    defender: str
    attack: Optional[str]  # sometimes null
    value: int
    effectType: str
    result: str
    crit: bool
    resources: Resources


class FightLog(BaseModel):
    metadata: Metadata
    events: List[Event]


class CombatReporter:
    def __init__(self, fight_log_json: Path = Path("fight-log.json")):
        with open(fight_log_json) as f:
            data = json.load(f)

        fight_log = FightLog(**data)

        self.player_total_heal_in_combat: dict[str, float] = {}
        self.player_total_damage_in_combat: dict[str, float] = {}
        self.player_highest_heal_in_combat: dict[str, float] = {}
        self.player_highest_damage_in_combat: dict[str, float] = {}

        self._fight_metadata: Metadata = fight_log.metadata
        self._fight_events: list[Event] = fight_log.events
        self._setup_metrics()

    def _setup_metrics(self):
        for event in self._fight_events:
            self._set_highest_damage_in_combat(event)
            self._set_highest_heal_in_combat(event)
            self._set_total_damage_in_combat(event)
            self._set_total_heal_in_combat(event)

    def _set_highest_damage_in_combat(self, event: Event):
        if event.effectType == "Damage":
            if event.attacker not in self.player_highest_damage_in_combat:
                self.player_highest_damage_in_combat[event.attacker] = event.value
            if self.player_highest_damage_in_combat[event.attacker] < event.value:
                self.player_highest_damage_in_combat[event.attacker] = event.value

    def _set_highest_heal_in_combat(self, event: Event):
        if event.effectType == "Heal":
            if event.attacker not in self.player_highest_heal_in_combat:
                self.player_highest_heal_in_combat[event.attacker] = event.value

            if self.player_highest_heal_in_combat[event.attacker] < event.value:
                self.player_highest_heal_in_combat[event.attacker] = event.value

    def _set_total_damage_in_combat(self, event: Event):
        if event.effectType == "Damage":
            if event.attacker not in self.player_total_damage_in_combat:
                self.player_total_damage_in_combat[event.attacker] = event.value

            self.player_total_damage_in_combat[event.attacker] += event.value

    def _set_total_heal_in_combat(self, event: Event):
        if event.effectType == "Heal":
            if event.attacker not in self.player_total_heal_in_combat:
                self.player_total_heal_in_combat[event.attacker] = event.value

            self.player_total_heal_in_combat[event.attacker] += event.value


if __name__ == '__main__':
    report = CombatReporter()
    a = 1
