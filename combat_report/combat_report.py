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
    Mana: Optional[int]
    Energy: Optional[int]


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
    def __init__(self, fight_log_json: Path):
        # Opens and reads json
        with open(fight_log_json) as f:
            data = json.load(f)

        # Puts json data info pydantic base model schema
        fight_log = FightLog(**data)

        # Holds metric info
        self.player_total_heal_in_combat: dict[str, float] = {}
        self.player_total_damage_in_combat: dict[str, float] = {}
        self.player_highest_heal_in_combat: dict[str, float] = {}
        self.player_highest_damage_in_combat: dict[str, float] = {}
        self.player_hps_in_combat: dict[str, float] = {}
        self.player_dps_in_combat: dict[str, float] = {}
        self.player_overheal_in_combat: dict[str, float] = {}
        self.player_total_damage_taken_in_combat: dict[str, float] = {}
        self.player_time_below_20_in_combat: dict[str, float] = {}

        # Used to calculate some metrics
        self.last_hp_below_critical_threshold: dict[str, float] = {}
        self.player_current_hp_in_combat: dict[str, float] = {}

        # Constants
        self.critical_hp_threshold: float = 1100

        # Holds json data
        self._fight_metadata: Metadata = fight_log.metadata
        self._fight_events: list[Event] = fight_log.events

        # Setting up events df and adding Time (s) col
        self._events_df = pd.DataFrame(data["events"])
        start_time = self._fight_metadata.startTime
        self._events_df["Time (s)"] = (self._events_df["timestamp"] - start_time) / 1000

        # Gets all the metrics
        self._setup_metrics()

    def _setup_metrics(self):
        for event in self._fight_events:
            self._set_highest_damage_in_combat(event)
            self._set_highest_heal_in_combat(event)
            self._set_total_damage_in_combat(event)
            self._set_total_damage_taken_in_combat(event)
            self._set_total_heal_in_combat(event)
            self._set_overheal_in_combat(event)
            self._set_time_below_critical_hp_in_combat(event)

        self._set_dps_in_combat()
        self._set_hps_in_combat()
        # self._plot_hp_over_time_in_combat()
        # self._plot_damage_over_time_in_combat()

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

    def _set_time_below_critical_hp_in_combat(self, event: Event):
        """
            Will not work if players starts with critical hp. Can only work after an event logs the player at critical hp

        """
        defender: str = event.defender
        hp: float = event.resources.HP
        hpmax: float = event.resources.HPmax
        time_s: float = (event.timestamp - self._fight_metadata.startTime) / 1000

        if hpmax == 0:
            return

        # If player drops below threshold and wasn't already tracked
        if hp < self.critical_hp_threshold and defender not in self.last_hp_below_critical_threshold:
            self.last_hp_below_critical_threshold[defender] = time_s

        # If player recovers above 20% and was tracked
        elif defender in self.last_hp_below_critical_threshold and (hp >= self.critical_hp_threshold or hp == 0):
            duration = time_s - self.last_hp_below_critical_threshold[defender]
            self.player_time_below_20_in_combat[defender] = self.player_time_below_20_in_combat.get(defender, 0) + duration
            del self.last_hp_below_critical_threshold[defender]

        if event == self._fight_events[-1] and self.last_hp_below_critical_threshold:
            # If someone ended the fight still below 20% → close out with fight end time
            for defender, start_time in self.last_hp_below_critical_threshold.items():
                duration = self._fight_metadata.durationSec - start_time
                self.player_time_below_20_in_combat[defender] = self.player_time_below_20_in_combat.get(defender, 0) + duration

        # Sort by longest survival under critical threshold%
        self.player_time_below_20_in_combat = dict(
            sorted(self.player_time_below_20_in_combat.items(), key=lambda x: x[1], reverse=True)
        )

    def _plot_hp_over_time_in_combat(self):
        fig = px.line(self._events_df, x="Time (s)", y=[event.resources.HP for event in self._fight_events], color="defender", title="HP Over Time in Combat", labels={"y": "HP"})
        fig.show()

    def _plot_damage_over_time_in_combat(self):
        self._events_df["Damage"] = [event.value if event.effectType == "Damage" else 0 for event in self._fight_events]
        self._events_df["Running Total Damage"] = self._events_df.groupby("attacker")["Damage"].cumsum()
        fig = px.line(self._events_df, x="Time (s)", y="Running Total Damage", color="attacker", title="Running Total Damage in Combat")
        fig.show()


if __name__ == '__main__':
    json_file_location: str | Path = input("Enter Path to the fight-log.json file or press ENTER to use default path: ")
    if not json_file_location:
        json_file_location: Path = Path(__file__).parent / "fight-log-1758484168170.json"

    if not Path(json_file_location).is_file() or not Path(json_file_location).suffix == ".json":
        print(f"Invalid file: {json_file_location}")
        exit()

    report = CombatReporter(Path(json_file_location))
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
    print(f"Duration player HP below {report.critical_hp_threshold} = {report.player_time_below_20_in_combat}")
    print(f"Over Heal Map (Broken) = {report.player_overheal_in_combat}")
    print(f"HP At Fight End Map (Only players that were attacked or healed)= {report.player_current_hp_in_combat}")
