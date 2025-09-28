from dataclasses import dataclass, fields

from fight_simulator.class_configs.loader.character_loader import CharacterFactory
from fight_simulator.class_configs.models.character import CharacterEquipment
from fight_simulator.class_configs.models.fighter_weapons import FighterWeaponStats
from fight_simulator.class_configs.models.mage_weapons import MageWeaponStats
from fight_simulator.class_configs.models.tank_weapons import TankWeaponStats


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


class CharacterEquipArmor:
    @staticmethod
    def _setup_player_stats(character_equipment: CharacterEquipment) -> PlayerStats:
        player_stats = PlayerStats()

        # Loop over all defined stats in PlayerStats instead of hardcoding
        for _, armor_piece_stats in character_equipment.armor:
            for field in fields(PlayerStats):
                name = field.name
                # getattr with default 0 if the attribute doesn't exist on armor_piece_stats
                value = getattr(armor_piece_stats, name, 0)
                setattr(player_stats, name, getattr(player_stats, name) + (value or 0))
        return player_stats


class FighterDamage(BasicDamageCalculation, CharacterEquipArmor):
    def __init__(self):
        self._fighter_info: CharacterEquipment = CharacterFactory().get_fighter_info()
        self._player_stats: PlayerStats = self._setup_player_stats(self._fighter_info)

    def _weapon_average_damage(self, weapon: FighterWeaponStats, multiplier: int = 1, bleed_ticks: int = 0) -> float:
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


class MageDamage(BasicDamageCalculation, CharacterEquipArmor):
    def __init__(self):
        self._mage_info: CharacterEquipment = CharacterFactory().get_mage_info()
        self._player_stats: PlayerStats = self._setup_player_stats(self._mage_info)

    def _weapon_average_damage(self, weapon: MageWeaponStats, multiplier: int = 1) -> float:
        # Average base damage between lower and higher
        base_damage = (weapon.regular_damage_lower + weapon.regular_damage_higher) / 2
        avg_damage = self._average_damage(self._player_stats, base_damage, weapon.regular_damage_bonus_percent)
        return round(avg_damage * multiplier, 3)

    # Define specific moves using the generic helper
    def repeater_average_damage(self) -> float:
        return self._weapon_average_damage(self._mage_info.weapons.repeater)

    def fireball_average_damage(self) -> float:
        return self._weapon_average_damage(self._mage_info.weapons.fireball)

    def flamestrike_average_damage(self) -> float:
        return self._weapon_average_damage(self._mage_info.weapons.flamestrike)

    def firebomb_average_damage(self) -> float:
        return self._weapon_average_damage(self._mage_info.weapons.fire_bomb)

    def sunfire_average_damage(self) -> float:
        return self._weapon_average_damage(self._mage_info.weapons.sunfire, multiplier=5)

    def flamerush_average_damage(self) -> float:
        return self._weapon_average_damage(self._mage_info.weapons.flame_rush)

    def flamerush_legacy_average_damage(self) -> float:
        return self._weapon_average_damage(self._mage_info.weapons.flame_rush_legacy, multiplier=10)


class TankDamage(BasicDamageCalculation, CharacterEquipArmor):
    def __init__(self):
        self._tank_info: CharacterEquipment = CharacterFactory().get_tank_info()
        self._player_stats: PlayerStats = self._setup_player_stats(self._tank_info)

    def _weapon_average_damage(self, weapon: TankWeaponStats, multiplier: int = 1) -> float:
        # Average base damage between lower and higher
        base_damage = (weapon.regular_damage_lower + weapon.regular_damage_higher) / 2
        avg_damage = self._average_damage(self._player_stats, base_damage, weapon.regular_damage_bonus_percent)
        return round(avg_damage * multiplier, 3)

    # Define specific moves using the generic helper
    def repeater_average_damage(self) -> float:
        return self._weapon_average_damage(self._tank_info.weapons.repeater)

    def execute_average_damage(self) -> float:
        return self._weapon_average_damage(self._tank_info.weapons.execute)

    def roar_average_damage(self) -> float:
        return self._weapon_average_damage(self._tank_info.weapons.roar)

    def distract_average_damage(self) -> float:
        return self._weapon_average_damage(self._tank_info.weapons.distract)

    def impale_average_damage(self) -> float:
        return self._weapon_average_damage(self._tank_info.weapons.impale)

    def warstrike_average_damage(self) -> float:
        return self._weapon_average_damage(self._tank_info.weapons.warstrike_legacy)


if __name__ == "__main__":
    fighter_damage = FighterDamage()
    print("Fighter:")
    print(f"Repeater Average Damage: {fighter_damage.repeater_average_damage()}")
    print(f"Cleaving Strike Average Damage: {fighter_damage.cleaving_strike_average_damage()}")
    print(f"Reckless Slam Average Damage: {fighter_damage.reckless_slam_average_damage()}")
    print(f"Breaker Average Damage: {fighter_damage.breaker_average_damage()}")
    print(f"Shiver Average Damage: {fighter_damage.shiver_average_damage()}")
    print(f"Tear Average Damage: {fighter_damage.tear_average_damage()}")

    mage_damage = MageDamage()
    print("\nMage:")
    print(f"Repeater Average Damage: {mage_damage.repeater_average_damage()}")
    print(f"Fireball Average Damage: {mage_damage.fireball_average_damage()}")
    print(f"Flamestrike Average Damage: {mage_damage.flamestrike_average_damage()}")
    print(f"Firebomb Average Damage: {mage_damage.firebomb_average_damage()}")
    print(f"Sunfire Average Damage: {mage_damage.sunfire_average_damage()}")
    print(f"Flamerush Average Damage: {mage_damage.flamerush_average_damage()}")
    print(f"Flamerush Legacy Average Damage: {mage_damage.flamerush_legacy_average_damage()}")

    tank_damage = TankDamage()
    print("\nTank:")
    print(f"Repeater Average Damage: {tank_damage.repeater_average_damage()}")
    print(f"Execute Average Damage: {tank_damage.execute_average_damage()}")
    print(f"Roar Average Damage: {tank_damage.roar_average_damage()}")
    print(f"Distract Average Damage: {tank_damage.distract_average_damage()}")
    print(f"Impale Average Damage: {tank_damage.impale_average_damage()}")
    print(f"Warstrike Average Damage: {tank_damage.warstrike_average_damage()}")
