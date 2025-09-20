# TODO LIST
# Duration tank was fully healed
# How many times players had near death events (Defined by %HP drops)

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
import json
import pandas as pd
import plotly.express as px


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
        self.player_current_hp_in_combat: dict[str, float] = {}
        self.player_total_damage_taken_in_combat: dict[str, float] = {}

        self._fight_metadata: Metadata = fight_log.metadata
        self._fight_events: list[Event] = fight_log.events

        # Setting up events df and adding time_sec col
        self._events_df = pd.DataFrame(data["events"])
        start_time = self._fight_metadata.startTime
        self._events_df["time_sec"] = (self._events_df["timestamp"] - start_time) / 1000

        self._setup_metrics()

    def _setup_metrics(self):
        for event in self._fight_events:
            self._set_highest_damage_in_combat(event)
            self._set_highest_heal_in_combat(event)
            self._set_total_damage_in_combat(event)
            self._set_total_damage_taken_in_combat(event)
            self._set_total_heal_in_combat(event)
            self._set_overheal_in_combat(event)

        self._set_dps_in_combat()
        self._set_hps_in_combat()
        self._plot_hp_over_time_in_combat()
        self._plot_damage_over_time_in_combat()

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

    def _set_total_damage_taken_in_combat(self, event: Event):
        if event.effectType == "Damage":
            if event.defender not in self.player_total_damage_taken_in_combat:
                self.player_total_damage_taken_in_combat[event.defender] = event.value
            else:
                self.player_total_damage_taken_in_combat[event.defender] += event.value

        self.player_total_damage_taken_in_combat = dict(sorted(self.player_total_damage_taken_in_combat.items(), key=lambda item: item[1], reverse=True))

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
        if event.effectType == "Heal":
            # First heal in combat
            if event.defender not in self.player_current_hp_in_combat:
                self.player_current_hp_in_combat[event.defender] = event.resources.HPmax
                self.player_overheal_in_combat[event.attacker] = event.value
                return
            # Any heal done on player after they already have their initial hp in the current hp map
            if (over_heal := event.value - (event.resources.HPmax - self.player_current_hp_in_combat[event.defender])) > 0:
                self.player_overheal_in_combat[event.attacker] = over_heal

            # Updates current hp value after heal incase it wasnt overhealed
            self.player_current_hp_in_combat[event.defender] = event.resources.HP

        if event.effectType == "Damage":
            # Updates player hp whenever its attacked
            self.player_current_hp_in_combat[event.defender] = event.resources.HP

        self.player_current_hp_in_combat = dict(sorted(self.player_current_hp_in_combat.items(), key=lambda item: item[1], reverse=True))
        self.player_overheal_in_combat = dict(sorted(self.player_overheal_in_combat.items(), key=lambda item: item[1], reverse=True))

    def _plot_hp_over_time_in_combat(self):
        fig = px.line(self._events_df, x="time_sec", y=[event.resources.HP for event in self._fight_events], color="defender", title="HP Over Time")
        fig.show()

    def _plot_damage_over_time_in_combat(self):
        self._events_df["Damage"] = [event.value if event.effectType == "Damage" else 0 for event in self._fight_events]
        self._events_df["Running Total Damage"] = self._events_df.groupby("attacker")["Damage"].cumsum()
        fig = px.line(self._events_df, x="time_sec", y="Running Total Damage", color="attacker", title="Running Total Damage in Combat")
        fig.show()


if __name__ == '__main__':
    report = CombatReporter()
    print("COMBAT REPORT")
    print("```````````````````````````````````````````````````````````````````````````````````````````````````````````")
    print("Damage Metrics")
    print(f"Highest Damage Map = {report.player_highest_damage_in_combat}")
    print(f"Total Damage Map = {report.player_total_damage_in_combat}")
    print(f"Total Damage Taken Map = {report.player_total_damage_taken_in_combat}")
    print(f"DPS Map = {report.player_dps_in_combat}")

    print("\n")
    print("```````````````````````````````````````````````````````````````````````````````````````````````````````````")
    print("Heal Metrics")
    print(f"Highest Heal Map = {report.player_highest_heal_in_combat}")
    print(f"Total Heal Map = {report.player_total_heal_in_combat}")
    print(f"HPS Map = {report.player_hps_in_combat}")
    print(f"Over Heal Map = {report.player_overheal_in_combat}")
    print(f"HP At Fight End Map (Only players that were attacked or healed)= {report.player_current_hp_in_combat}")
