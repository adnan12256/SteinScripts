# TODO LIST
# Overheal mapping
# Duration tank was fully healed
# Make dps graph

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
        self.player_hps_in_combat: dict[str, float] = {}
        self.player_dps_in_combat: dict[str, float] = {}
        self.player_overheal_in_combat: dict[str, float] = {}

        self._fight_metadata: Metadata = fight_log.metadata
        self._fight_events: list[Event] = fight_log.events
        self._setup_metrics()

    def _setup_metrics(self):
        for event in self._fight_events:
            self._set_highest_damage_in_combat(event)
            self._set_highest_heal_in_combat(event)
            self._set_total_damage_in_combat(event)
            self._set_total_heal_in_combat(event)
            self._set_overheal_in_combat(event)

        self._set_dps_in_combat()
        self._set_hps_in_combat()

    def _set_highest_damage_in_combat(self, event: Event):
        if event.effectType == "Damage":
            if event.attacker not in self.player_highest_damage_in_combat:
                self.player_highest_damage_in_combat[event.attacker] = event.value
            if self.player_highest_damage_in_combat[event.attacker] < event.value:
                self.player_highest_damage_in_combat[event.attacker] = event.value

        self.player_highest_damage_in_combat = dict(sorted(self.player_highest_damage_in_combat.items(), key=lambda item: item[1], reverse=True))

    def _set_highest_heal_in_combat(self, event: Event):
        if event.effectType == "Heal":
            if event.attacker not in self.player_highest_heal_in_combat:
                self.player_highest_heal_in_combat[event.attacker] = event.value

            if self.player_highest_heal_in_combat[event.attacker] < event.value:
                self.player_highest_heal_in_combat[event.attacker] = event.value

        self.player_highest_heal_in_combat = dict(sorted(self.player_highest_heal_in_combat.items(), key=lambda item: item[1], reverse=True))

    def _set_total_damage_in_combat(self, event: Event):
        if event.effectType == "Damage":
            if event.attacker not in self.player_total_damage_in_combat:
                self.player_total_damage_in_combat[event.attacker] = event.value
            else:
                self.player_total_damage_in_combat[event.attacker] += event.value

        self.player_total_damage_in_combat = dict(sorted(self.player_total_damage_in_combat.items(), key=lambda item: item[1], reverse=True))

    def _set_total_heal_in_combat(self, event: Event):
        if event.effectType == "Heal":
            if event.attacker not in self.player_total_heal_in_combat:
                self.player_total_heal_in_combat[event.attacker] = event.value
            else:
                self.player_total_heal_in_combat[event.attacker] += event.value

        self.player_total_heal_in_combat = dict(sorted(self.player_total_heal_in_combat.items(), key=lambda item: item[1], reverse=True))

    def _set_dps_in_combat(self):
        if self.player_total_damage_in_combat:
            self.player_dps_in_combat = {name: total_damage / self._fight_metadata.durationSec for name, total_damage in self.player_total_damage_in_combat.items()}

        self.player_dps_in_combat = dict(sorted(self.player_dps_in_combat.items(), key=lambda item: item[1], reverse=True))

    def _set_hps_in_combat(self):
        if self.player_total_heal_in_combat:
            self.player_hps_in_combat = {name: total_heal / self._fight_metadata.durationSec for name, total_heal in self.player_total_heal_in_combat.items()}

        self.player_hps_in_combat = dict(sorted(self.player_hps_in_combat.items(), key=lambda item: item[1], reverse=True))

    def _set_overheal_in_combat(self, event: Event):
        # TODO: Not correct logic. current HP is not acquired from event.resources.HP
        if event.effectType == "Heal":
            if event.attacker not in self.player_overheal_in_combat:
                if (over_heal := event.value - (event.resources.HPmax - event.resources.HP)) > 0:
                    self.player_overheal_in_combat[event.attacker] = over_heal
            else:
                if (over_heal := event.value - (event.resources.HPmax - event.resources.HP)) > 0:
                    self.player_overheal_in_combat[event.attacker] += over_heal

        self.player_overheal_in_combat = dict(sorted(self.player_overheal_in_combat.items(), key=lambda item: item[1], reverse=True))


if __name__ == '__main__':
    report = CombatReporter()
    print("COMBAT REPORT")
    print("```````````````````````````````````````````````````````````````````````````````````````````````````````````")
    print("Damage Metrics")
    print(f"Highest Damage Map = {report.player_highest_damage_in_combat}")
    print(f"Total Damage Map = {report.player_total_damage_in_combat}")
    print(f"DPS Map = {report.player_dps_in_combat}")

    print("\n")
    print("```````````````````````````````````````````````````````````````````````````````````````````````````````````")
    print("Heal Metrics")
    print(f"Highest Heal Map = {report.player_highest_heal_in_combat}")
    print(f"Total Heal Map = {report.player_total_heal_in_combat}")
    print(f"HPS Map = {report.player_hps_in_combat}")
    print(f"Over Heal Map = {report.player_overheal_in_combat}")
