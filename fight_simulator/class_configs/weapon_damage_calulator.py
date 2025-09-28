from fight_simulator.class_configs.parse_fighter import get_fighter_info, CharacterEquipment


class PlayerStats:
    armor: int = 0
    cbr: int = 0
    ccr: int = 0
    damage: int = 0
    energy_regen: float = 2.0
    mana_regen: float = 3.2
    life: int = 0
    life_regen: int = 4.0


class BasicDamageCalculation:
    @staticmethod
    def _average_damage(player_stats: PlayerStats, base_damage: float, wep_bonus: float) -> float:
        wep_bonus = wep_bonus / 100
        critical_rate = 1 - 0.99**(player_stats.ccr/(0.5*1.05**(30-1)))
        critical_bonus = 0.25 + (player_stats.cbr / (0.5 * 1.05**(30-1))) / 100
        armor_damage = player_stats.damage
        average_damage = ((base_damage + armor_damage * wep_bonus) * (1 + critical_bonus) * critical_rate) + ((base_damage + armor_damage * wep_bonus) * (1 - critical_rate))
        return average_damage


class FighterDamage(BasicDamageCalculation):
    def __init__(self):
        super().__init__()
        self._fighter_info: CharacterEquipment = get_fighter_info()
        self._player_stats: PlayerStats = self.setup_player_stats()

    def setup_player_stats(self) -> PlayerStats:
        player_stats = PlayerStats()
        for field, armor_piece_stats in self._fighter_info.armor:
            player_stats.armor += armor_piece_stats.armor if armor_piece_stats.armor else 0
            player_stats.cbr += armor_piece_stats.cbr if armor_piece_stats.cbr else 0
            player_stats.ccr += armor_piece_stats.ccr if armor_piece_stats.ccr else 0
            player_stats.damage += armor_piece_stats.damage if armor_piece_stats.damage else 0
            player_stats.energy_regen += armor_piece_stats.energy_regen if armor_piece_stats.energy_regen else 0
            player_stats.mana_regen += armor_piece_stats.mana_regen if armor_piece_stats.mana_regen else 0
            player_stats.life_regen += armor_piece_stats.life_regen if armor_piece_stats.life_regen else 0
            player_stats.life += armor_piece_stats.life if armor_piece_stats.life else 0

        return player_stats

    def repeater_average_damage(self) -> float:
        base_damage = self._fighter_info.weapons.repeater.regular_damage_lower + self._fighter_info.weapons.repeater.regular_damage_higher / 2
        average_damage = self._average_damage(self._player_stats, base_damage, self._fighter_info.weapons.repeater.regular_damage_bonus_percent)
        return average_damage

    def cleaving_strike_average_damage(self) -> float:
        base_damage = self._fighter_info.weapons.cleaving_strike.regular_damage_lower + self._fighter_info.weapons.cleaving_strike.regular_damage_higher / 2
        average_damage = self._average_damage(self._player_stats, base_damage, self._fighter_info.weapons.cleaving_strike.regular_damage_bonus_percent)
        return average_damage

    def reckless_slam_average_damage(self) -> float:
        base_damage = self._fighter_info.weapons.reckless_slam.regular_damage_lower + self._fighter_info.weapons.reckless_slam.regular_damage_higher / 2
        average_damage = self._average_damage(self._player_stats, base_damage, self._fighter_info.weapons.reckless_slam.regular_damage_bonus_percent)

        bleed_base_damage = self._fighter_info.weapons.reckless_slam.bleed_damage
        bleed_wep_bonus = self._fighter_info.weapons.reckless_slam.bleed_bonus
        bleed_average_damage = self._average_damage(self._player_stats, bleed_base_damage, bleed_wep_bonus)
        total_bleed_average_damage = bleed_average_damage * 5

        return average_damage + total_bleed_average_damage

    def breaker_average_damage(self) -> float:
        base_damage = self._fighter_info.weapons.breaker.regular_damage_lower + self._fighter_info.weapons.breaker.regular_damage_higher / 2
        average_damage = self._average_damage(self._player_stats, base_damage, self._fighter_info.weapons.breaker.regular_damage_bonus_percent)
        total_average_damage = average_damage * 4
        return total_average_damage

    def shiver_average_damage(self) -> float:
        base_damage = self._fighter_info.weapons.shiver.regular_damage_lower + self._fighter_info.weapons.shiver.regular_damage_higher / 2
        average_damage = self._average_damage(self._player_stats, base_damage, self._fighter_info.weapons.shiver.regular_damage_bonus_percent)
        return average_damage

    def tear_average_damage(self) -> float:
        base_damage = self._fighter_info.weapons.tear.regular_damage_lower + self._fighter_info.weapons.tear.regular_damage_higher / 2
        average_damage = self._average_damage(self._player_stats, base_damage, self._fighter_info.weapons.tear.regular_damage_bonus_percent)
        total_average_damage = average_damage * 4
        return total_average_damage


if __name__ == '__main__':
    a = FighterDamage()
    print(f"Repeater Average Damage: {a.repeater_average_damage()}")
    print(f"Cleaving Strike Average Damage: {a.cleaving_strike_average_damage()}")
    print(f"Reckless Slam Average Damage: {a.reckless_slam_average_damage()}")
    print(f"Breaker Average Damage: {a.breaker_average_damage()}")
    print(f"Shiver Average Damage: {a.shiver_average_damage()}")
    print(f"Tear Average Damage: {a.tear_average_damage()}")
