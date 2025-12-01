from typing import Dict, Optional


class Boss:
    def __init__(self, name: str, hp: int):
        self.name = name
        self.hp = hp


class Player:
    def __init__(self, name: str, dps: Optional[int]):
        self.name = name
        self.dps = dps  # None means unknown DPS


class DpsCalculator:
    def __init__(self, bosses: Dict[str, int], players: Dict[str, Optional[int]]):
        self.bosses: list[Boss] = [Boss(name, hp) for name, hp in bosses.items()]
        self.players: list[Player] = [Player(name, dps) for name, dps in players.items()]

    def calculate_for_all_bosses(self, desired_completion_time: int):
        for boss in self.bosses:
            print(f"Boss: {boss.name}")
            self.calculate_single_boss(boss, desired_completion_time)
            print()

    def calculate_single_boss(self, boss: Boss, desired_completion_time: int):
        required_total_dps = boss.hp / desired_completion_time
        print(f"Required total DPS: {required_total_dps:.1f}")

        fixed_dps = sum(players.dps for players in self.players if players.dps is not None)
        unknown_players = [players for players in self.players if players.dps is None]

        remaining_dps = required_total_dps - fixed_dps

        # Edge case handling
        if remaining_dps < 0:
            print("⚠ Fixed DPS already exceeds required amount.")
            return
        if not unknown_players:
            print("⚠ No unknown players left to distribute DPS.")
            return

        share_per_player = remaining_dps / len(unknown_players)

        # Display fixed DPS
        for players in self.players:
            if players.dps is not None:
                print(f"{players.name}: {players.dps} DPS")

        # Display calculated DPS
        for players in unknown_players:
            print(f"{players.name}: {share_per_player:.1f} DPS required")


if __name__ == '__main__':
    boss_name_hp_map = {
        "Garub": 140_000,
        "Inachaus": 170_000,
        "Black'ist": 210_000,
        "Trenun": 260_000,
        "Sedulus Rane": 415_000,
        "Serezith Brakrud": 515_000,
    }

    # None means dps will be calculated and split evenly after the known dps is computed.
    player_dps_dict = {
        "Player1": 0,
        "Player2": 0,
        "Player3": 200,
        "Player4": None,
        "Player5": None,
    }

    desired_time = int(input("Enter desired completion time in seconds: "))

    calculator = DpsCalculator(boss_name_hp_map, player_dps_dict)
    calculator.calculate_for_all_bosses(desired_time)
