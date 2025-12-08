import random
from dataclasses import dataclass, fields

from fight_simulator.class_configs.loader.character_loader import CharacterFactory
from fight_simulator.class_configs.models.character import CharacterEquipment
from fight_simulator.class_configs.models.fighter_weapons import FighterWeaponStats
from fight_simulator.class_configs.models.healer_weapons import HealerWeaponStats
from fight_simulator.class_configs.models.hunter_weapons import HunterWeaponStats
from fight_simulator.class_configs.models.mage_weapons import MageWeaponStats
from fight_simulator.class_configs.models.shaman_weapons import ShamanWeaponStats
from fight_simulator.class_configs.models.tank_weapons import TankWeaponStats
from fight_simulator.class_configs.models.warlock_weapons import WarlockWeaponStats


@dataclass
class PlayerStats:
    armor: int = 0
    cbr: int = 0
    ccr: int = 0
    cdr: int = 0
    damage: int = 0
    energy_regen: float = 2.0
    mana_regen: float = 3.2
    life_regen: float = 4.0
    life: int = 0
    heal: int = 0
    energy: int = 100
    mana: int = 317



@dataclass
class DamageMetrics:
    average_damage: float
    regular_damage: float


class BasicHealDamageCalculation:
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

    @staticmethod
    def _average_heal(player_stats: PlayerStats, base_heal: float, wep_bonus: float, disable_crit: bool = False) -> float:
        wep_bonus /= 100
        # Critical chance formula
        critical_rate = 1 - 0.99 ** (player_stats.ccr / (0.5 * 1.05 ** (30 - 1)))
        critical_bonus = 0.25 + (player_stats.cbr / (0.5 * 1.05 ** (30 - 1))) / 100
        # Base + armor scaling
        effective_heal = base_heal + player_stats.heal * wep_bonus

        if disable_crit:
            return effective_heal

        # Weighted average of crit vs non-crit
        return (effective_heal * (1 + critical_bonus) * critical_rate) + (effective_heal * (1 - critical_rate))

    @staticmethod
    def _calculate_damage(player_stats: PlayerStats, base_damage: float, wep_bonus: float, hit_chance_percent: float) -> float:
        wep_bonus /= 100
        # Critical chance formula
        critical_rate = 1 - 0.99 ** (player_stats.ccr / (0.5 * 1.05 ** (30 - 1)))
        critical_bonus = 0.25 + (player_stats.cbr / (0.5 * 1.05 ** (30 - 1))) / 100

        # Base + armor scaling
        effective_damage = base_damage + player_stats.damage * wep_bonus * round(random.uniform(0.7, 1.3), 3)

        # Checking if weapon hit
        if random.randint(1, 100) <= hit_chance_percent:
            # Crit or non crit hit
            return effective_damage * critical_bonus if random.randint(1, 100) <= critical_rate else effective_damage
        else:
            return 0

    @staticmethod
    def _calculate_heal(player_stats: PlayerStats, base_heal: float, wep_bonus: float, disable_crit: bool = False) -> float:
        wep_bonus /= 100
        # Critical chance formula
        critical_rate = 1 - 0.99 ** (player_stats.ccr / (0.5 * 1.05 ** (30 - 1)))
        critical_bonus = 0.25 + (player_stats.cbr / (0.5 * 1.05 ** (30 - 1))) / 100
        # Base + armor scaling
        effective_heal = base_heal + player_stats.heal * wep_bonus * round(random.uniform(0.7, 1.3), 3)

        if disable_crit:
            return effective_heal

        # Weighted average of crit vs non-crit
        return effective_heal * critical_bonus if random.randint(1, 100) <= critical_rate else effective_heal


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


class FighterDamage(BasicHealDamageCalculation, CharacterEquipArmor):
    def __init__(self):
        self.fighter_info: CharacterEquipment = CharacterFactory().get_fighter_info()
        self.player_stats: PlayerStats = self._setup_player_stats(self.fighter_info)

    def _weapon_damage_calculation(self, weapon: FighterWeaponStats, multiplier: int = 1, bleed_ticks: int = 0) -> DamageMetrics:
        # Average base damage between lower and higher
        base_damage = (weapon.regular_damage_lower + weapon.regular_damage_higher) / 2

        avg_damage = self._average_damage(self.player_stats, base_damage, weapon.regular_damage_bonus_percent)
        reg_damage = self._calculate_damage(self.player_stats, base_damage, weapon.regular_damage_bonus_percent, weapon.hit_chance_percent)

        # Handle bleed if applicable
        total_bleed_avg_damage = 0
        total_bleed_calc_damage = 0
        if hasattr(weapon, "bleed_damage") and bleed_ticks > 0:
            bleed_avg = self._average_damage(self.player_stats, weapon.bleed_damage, weapon.bleed_bonus)
            total_bleed_avg_damage = bleed_avg * bleed_ticks

            bleed_calc = self._calculate_damage(self.player_stats, weapon.bleed_damage, weapon.bleed_bonus, weapon.hit_chance_percent)
            total_bleed_calc_damage = bleed_calc * bleed_ticks

        average_damage = round(avg_damage * multiplier + total_bleed_avg_damage, 3)
        regular_damage = round(reg_damage * multiplier + total_bleed_calc_damage, 3)

        return DamageMetrics(average_damage=average_damage, regular_damage=regular_damage)

    # Define specific moves using the generic helper
    def repeater_damage(self) -> DamageMetrics:
        return self._weapon_damage_calculation(self.fighter_info.weapons.repeater)

    def cleaving_strike_damage(self) -> DamageMetrics:
        return self._weapon_damage_calculation(self.fighter_info.weapons.cleaving_strike)

    def reckless_slam_damage(self) -> DamageMetrics:
        return self._weapon_damage_calculation(self.fighter_info.weapons.reckless_slam, bleed_ticks=5)

    def breaker_damage(self) -> DamageMetrics:
        return self._weapon_damage_calculation(self.fighter_info.weapons.breaker, multiplier=4)

    def shiver_damage(self) -> DamageMetrics:
        return self._weapon_damage_calculation(self.fighter_info.weapons.shiver)

    def tear_damage(self) -> DamageMetrics:
        return self._weapon_damage_calculation(self.fighter_info.weapons.tear, multiplier=4)


class MageDamage(BasicHealDamageCalculation, CharacterEquipArmor):
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


class TankDamage(BasicHealDamageCalculation, CharacterEquipArmor):
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


class WarlockDamage(BasicHealDamageCalculation, CharacterEquipArmor):
    def __init__(self):
        self._warlock_info: CharacterEquipment = CharacterFactory().get_warlock_info()
        self._player_stats: PlayerStats = self._setup_player_stats(self._warlock_info)

    def _weapon_average_damage(self, weapon: WarlockWeaponStats, multiplier: int = 1) -> float:
        # Average base damage between lower and higher
        base_damage = (weapon.regular_damage_lower + weapon.regular_damage_higher) / 2
        avg_damage = self._average_damage(self._player_stats, base_damage, weapon.regular_damage_bonus_percent)
        return round(avg_damage * multiplier, 3)

    # Define specific moves using the generic helper
    def repeater_average_damage(self) -> float:
        return self._weapon_average_damage(self._warlock_info.weapons.repeater)

    def void_hex_average_damage(self) -> float:
        return self._weapon_average_damage(self._warlock_info.weapons.void_hex, multiplier=5)

    def life_burn_average_damage(self) -> float:
        return self._weapon_average_damage(self._warlock_info.weapons.life_burn)

    def sacrifice_average_damage(self) -> float:
        return self._weapon_average_damage(self._warlock_info.weapons.sacrifice)


class ShamanDamage(BasicHealDamageCalculation, CharacterEquipArmor):
    def __init__(self):
        self._shaman_info: CharacterEquipment = CharacterFactory().get_shaman_info()
        self._player_stats: PlayerStats = self._setup_player_stats(self._shaman_info)

    def _weapon_average_damage(self, weapon: ShamanWeaponStats, multiplier: int = 1) -> float:
        # Average base damage between lower and higher
        base_damage = (weapon.regular_damage_lower + weapon.regular_damage_higher) / 2
        avg_damage = self._average_damage(self._player_stats, base_damage, weapon.regular_damage_bonus_percent)

        backward_damage = 0
        if hasattr(weapon, "backward_damage_lower") and weapon.backward_damage_lower is not None:
            backward_base_damage = (weapon.backward_damage_lower + weapon.backward_damage_higher) / 2
            backward_damage = self._average_damage(self._player_stats, backward_base_damage, weapon.backward_damage_bonus_percent)

        return round(avg_damage * multiplier + backward_damage, 3)

    # Define specific moves using the generic helper
    def repeater_average_damage(self) -> float:
        return self._weapon_average_damage(self._shaman_info.weapons.repeater)

    def frost_bolt_average_damage(self) -> float:
        return self._weapon_average_damage(self._shaman_info.weapons.frost_bolt)

    def waterfall_average_damage(self) -> float:
        return self._weapon_average_damage(self._shaman_info.weapons.waterfall)

    def tide_average_damage(self) -> float:
        return self._weapon_average_damage(self._shaman_info.weapons.tide)

    def ice_totem_average_damage(self) -> float:
        return self._weapon_average_damage(self._shaman_info.weapons.ice_totem, multiplier=4)

    def frost_totem_average_damage(self) -> float:
        return self._weapon_average_damage(self._shaman_info.weapons.frost_totem, multiplier=12)


class HunterDamage(BasicHealDamageCalculation, CharacterEquipArmor):
    def __init__(self):
        self._hunter_info: CharacterEquipment = CharacterFactory().get_hunter_info()
        self._player_stats: PlayerStats = self._setup_player_stats(self._hunter_info)

    def _weapon_average_damage(self, weapon: HunterWeaponStats, multiplier: int = 1, bonus_percent: int = 0) -> float:
        wep_bonus = weapon.regular_damage_bonus_percent
        if bonus_percent > 0:
            wep_bonus = weapon.regular_damage_bonus_percent + bonus_percent

        # Average base damage between lower and higher
        base_damage = (weapon.regular_damage_lower + weapon.regular_damage_higher) / 2
        avg_damage = self._average_damage(self._player_stats, base_damage, wep_bonus)

        return round(avg_damage * multiplier, 3)

    # Define specific moves using the generic helper
    def repeater_average_damage(self) -> float:
        return self._weapon_average_damage(self._hunter_info.weapons.repeater)

    def powerful_shot_average_damage(self) -> float:
        return self._weapon_average_damage(self._hunter_info.weapons.powerful_shot)

    def arrow_hail_average_damage(self) -> float:
        return self._weapon_average_damage(self._hunter_info.weapons.arrow_hail)

    def toxic_shot_average_damage(self) -> float:
        return self._weapon_average_damage(self._hunter_info.weapons.toxic_shot)

    def multi_shot_average_damage(self) -> float:
        return self._weapon_average_damage(self._hunter_info.weapons.multi_shot, bonus_percent=24)


class HealerHeal(BasicHealDamageCalculation, CharacterEquipArmor):
    def __init__(self):
        self._healer_info: CharacterEquipment = CharacterFactory().get_healer_info()
        self._player_stats: PlayerStats = self._setup_player_stats(self._healer_info)

    def _weapon_average_heal(self, weapon: HealerWeaponStats, multiplier: int = 1, disable_crit: bool = False) -> float:
        # Average base damage between lower and higher
        base_heal = (weapon.regular_damage_lower + weapon.regular_damage_higher) / 2
        avg_damage = self._average_heal(self._player_stats, base_heal, weapon.regular_damage_bonus_percent, disable_crit=disable_crit)
        return round(avg_damage * multiplier, 3)

    # Define specific moves using the generic helper
    def repeater_average_heal(self) -> float:
        return self._weapon_average_heal(self._healer_info.weapons.repeater)

    def restoration_average_heal(self) -> float:
        return self._weapon_average_heal(self._healer_info.weapons.restoration)

    def blessing_legacy_average_heal(self) -> float:
        return self._weapon_average_heal(self._healer_info.weapons.blessing_legacy, multiplier=5)

    def blessing_average_heal(self) -> float:
        return self._weapon_average_heal(self._healer_info.weapons.blessing, multiplier=4)

    def holy_barrage_legacy_average_heal(self) -> float:
        return self._weapon_average_heal(self._healer_info.weapons.holy_barrage_legacy, multiplier=5)

    def eviction_average_heal(self) -> float:
        return self._weapon_average_heal(self._healer_info.weapons.eviction, disable_crit=True)

    def life_burst_average_heal(self) -> float:
        return self._weapon_average_heal(self._healer_info.weapons.life_burst, multiplier=5)


if __name__ == "__main__":
    fighter_damage = FighterDamage()
    print("Fighter:")
    print(f"Repeater Average Damage: {fighter_damage.repeater_damage().average_damage}")
    print(f"Cleaving Strike Average Damage: {fighter_damage.cleaving_strike_damage().average_damage}")
    print(f"Reckless Slam Average Damage: {fighter_damage.reckless_slam_damage().average_damage}")
    print(f"Breaker Average Damage: {fighter_damage.breaker_damage().average_damage}")
    print(f"Shiver Average Damage: {fighter_damage.shiver_damage().average_damage}")
    print(f"Tear Average Damage: {fighter_damage.tear_damage().average_damage}")

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

    warlock_damage = WarlockDamage()
    print("\nWarlock:")
    print(f"Repeater Average Damage: {warlock_damage.repeater_average_damage()}")
    print(f"Void hex Average Damage: {warlock_damage.void_hex_average_damage()}")
    print(f"Life burn Average Damage: {warlock_damage.life_burn_average_damage()}")
    print(f"Sacrifice Average Damage: {warlock_damage.sacrifice_average_damage()}")

    shaman_damage = ShamanDamage()
    print("\nShaman:")
    print(f"Repeater Average Damage: {shaman_damage.repeater_average_damage()}")
    print(f"Frost Bolt Average Damage: {shaman_damage.frost_bolt_average_damage()}")
    print(f"Waterfall Average Damage: {shaman_damage.waterfall_average_damage()}")
    print(f"Tide Average Damage: {shaman_damage.tide_average_damage()}")
    print(f"Ice Totem Average Damage: {shaman_damage.ice_totem_average_damage()}")
    print(f"Frost Totem Average Damage: {shaman_damage.frost_totem_average_damage()}")

    hunter_damage = HunterDamage()
    print("\nShaman:")
    print(f"Repeater Average Damage: {hunter_damage.repeater_average_damage()}")
    print(f"Powerful Shot Average Damage: {hunter_damage.powerful_shot_average_damage()}")
    print(f"Arrow Hail Average Damage: {hunter_damage.arrow_hail_average_damage()}")
    print(f"Toxic Shot Average Damage: {hunter_damage.toxic_shot_average_damage()}")
    print(f"Multi Shot Average Damage: {hunter_damage.multi_shot_average_damage()}")

    healer_damage = HealerHeal()
    print("\nHealer:")
    print(f"Repeater Average Heal: {healer_damage.repeater_average_heal()}")
    print(f"Restoration Average Heal: {healer_damage.restoration_average_heal()}")
    print(f"Blessings Legacy Average Heal: {healer_damage.blessing_legacy_average_heal()}")
    print(f"Blessings Average Heal: {healer_damage.blessing_average_heal()}")
    print(f"Holy Barrage Average Heal: {healer_damage.holy_barrage_legacy_average_heal()}")
    print(f"Eviction Average Heal: {healer_damage.eviction_average_heal()}")
    print(f"Life Burst Legacy Average Heal: {healer_damage.life_burst_average_heal()}")
