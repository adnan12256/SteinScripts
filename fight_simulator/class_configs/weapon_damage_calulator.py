from dataclasses import dataclass, fields
from fight_simulator.class_configs.parse_fighter import get_fighter_info, CharacterEquipment, Weapon


@dataclass
class PlayerStats:
    armor: int = 0
    cbr: int = 0
    ccr: int = 0
    damage: int = 0
    energy_regen: float = 2.0
    mana_regen: float = 3.2
    life: int = 0
    life_regen: float = 4.0


class BasicDamageCalculation:
    @staticmethod
    def _average_damage(player_stats: PlayerStats, base_damage: float, wep_bonus: float) -> float:
        wep_bonus /= 100
        # Critical chance formula
        critical_rate = 1 - 0.99 ** (player_stats.ccr / (0.5 * 1.05 ** (30 - 1)))
        critical_bonus = 0.25 + (player_stats.cbr / (0.5 * 1.05 ** (30 - 1))) / 100
        # Base + armor scaling
        effective_damage = base_damage + player_stats.damage * wep_bonus
        # Weighted average of crit vs non-crit
        return (effective_damage * (1 + critical_bonus) * critical_rate) + (effective_damage * (1 - critical_rate))


class FighterDamage(BasicDamageCalculation):
    def __init__(self):
        self._fighter_info: CharacterEquipment = get_fighter_info()
        self._player_stats: PlayerStats = self._setup_player_stats()

    def _setup_player_stats(self) -> PlayerStats:
        player_stats = PlayerStats()

        # Loop over all defined stats in PlayerStats instead of hardcoding
        for _, armor_piece_stats in self._fighter_info.armor:
            for field in fields(PlayerStats):
                name = field.name
                # getattr with default 0 if the attribute doesn't exist on armor_piece_stats
                value = getattr(armor_piece_stats, name, 0)
                setattr(player_stats, name, getattr(player_stats, name) + (value or 0))

        return player_stats

    def _weapon_average_damage(self, weapon: Weapon, multiplier: int = 1, bleed_ticks: int = 0) -> float:
        # Average base damage between lower and higher
        base_damage = (weapon.regular_damage_lower + weapon.regular_damage_higher) / 2
        avg_damage = self._average_damage(self._player_stats, base_damage, weapon.regular_damage_bonus_percent)

        # Handle bleed if applicable
        total_bleed_damage = 0
        if hasattr(weapon, "bleed_damage") and bleed_ticks > 0:
            bleed_avg = self._average_damage(self._player_stats, weapon.bleed_damage, weapon.bleed_bonus)
            total_bleed_damage = bleed_avg * bleed_ticks

        return round(avg_damage * multiplier + total_bleed_damage, 3)

    # Define specific moves using the generic helper
    def repeater_average_damage(self) -> float:
        return self._weapon_average_damage(self._fighter_info.weapons.repeater)

    def cleaving_strike_average_damage(self) -> float:
        return self._weapon_average_damage(self._fighter_info.weapons.cleaving_strike)

    def reckless_slam_average_damage(self) -> float:
        return self._weapon_average_damage(self._fighter_info.weapons.reckless_slam, bleed_ticks=5)

    def breaker_average_damage(self) -> float:
        return self._weapon_average_damage(self._fighter_info.weapons.breaker, multiplier=4)

    def shiver_average_damage(self) -> float:
        return self._weapon_average_damage(self._fighter_info.weapons.shiver)

    def tear_average_damage(self) -> float:
        return self._weapon_average_damage(self._fighter_info.weapons.tear, multiplier=4)


if __name__ == "__main__":
    a = FighterDamage()
    print(f"Repeater Average Damage: {a.repeater_average_damage()}")
    print(f"Cleaving Strike Average Damage: {a.cleaving_strike_average_damage()}")
    print(f"Reckless Slam Average Damage: {a.reckless_slam_average_damage()}")
    print(f"Breaker Average Damage: {a.breaker_average_damage()}")
    print(f"Shiver Average Damage: {a.shiver_average_damage()}")
    print(f"Tear Average Damage: {a.tear_average_damage()}")
