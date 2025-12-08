from decimal import Decimal
from typing import Dict

from fight_simulator.class_configs.models.fighter_weapons import FighterWeaponStats
from fight_simulator.class_configs.weapon_damage_calulator import FighterDamage

fighter_handle = FighterDamage()

# Simulation settings
energy_regen_per_sec = fighter_handle.player_stats.energy_regen
mana_regen_per_sec = fighter_handle.player_stats.mana_regen
max_energy = fighter_handle.player_stats.energy
max_mana = fighter_handle.player_stats.mana
duration = 130  # simulate 20 seconds
tick = 0.1  # tick resolution (0.1s)

# Runtime state
player_energy = max_energy
player_mana = max_mana
weapons_in_use: dict[str, FighterWeaponStats] = {
    "repeater": fighter_handle.fighter_info.weapons.repeater,
    "cleaving_strike": fighter_handle.fighter_info.weapons.cleaving_strike,
    "reckless_slam": fighter_handle.fighter_info.weapons.reckless_slam,
    "breaker": fighter_handle.fighter_info.weapons.breaker,
    "tear": fighter_handle.fighter_info.weapons.tear,
    "shiver": fighter_handle.fighter_info.weapons.shiver
}

weapons_damage: dict[str, float] = {
    "repeater": 0,
    "cleaving_strike": 0,
    "reckless_slam": 0,
    "breaker": 0,
    "tear": 0,
    "shiver": 0
}


cooldowns: Dict[str, float] = {w: 0.0 for w in weapons_in_use}
time = Decimal("0.0")

print("=== Combat Simulation Start ===")

while time < duration:
    if time % 1 == 0:
        player_energy = min([max_energy, player_energy + energy_regen_per_sec])
        player_mana = min([max_mana, player_mana + mana_regen_per_sec])
        print(f"New energy {player_energy}")
        print(f"New mana {player_mana}")

    # try to attack (priority order)
    for wep_name, weapon in weapons_in_use.items():
        if cooldowns[wep_name] <= 0:
            # Controlling mana/energy
            enough_resource_to_use_skill = False
            if hasattr(weapon, "energy") and player_energy >= weapon.energy:
                player_energy -= weapon.energy
                player_energy = max(0, player_energy)
                enough_resource_to_use_skill = True
            if hasattr(weapon, "mana") and player_mana >= weapon.mana:
                player_mana -= weapon.mana
                player_mana = max(0, player_mana)
                enough_resource_to_use_skill = True

            if enough_resource_to_use_skill:
                # Updating weapon cooldowns
                cooldowns[wep_name] = weapon.cooldown_s + weapon.casttime_s

                # Updating weapon damage
                match wep_name:
                    case "repeater":
                        dmg = fighter_handle.repeater_damage().regular_damage
                    case "cleaving_strike":
                        dmg = fighter_handle.cleaving_strike_damage().regular_damage
                    case "reckless_slam":
                        dmg = fighter_handle.reckless_slam_damage().regular_damage
                    case "breaker":
                        dmg = fighter_handle.breaker_damage().regular_damage
                    case "tear":
                        dmg = fighter_handle.tear_damage().regular_damage
                    case "shiver":
                        dmg = fighter_handle.shiver_damage().regular_damage
                    case _:
                        raise ValueError("Unknown Wep Name")
                weapons_damage[wep_name] += dmg

                print(f"{time:4.1f}s: Used {wep_name}, dealt {dmg}, energy left {player_energy:.1f}")

    # tick down cooldowns
    for k in cooldowns:
        cooldowns[k] = max([0, cooldowns[k] - 0.1])

    time += Decimal(str(tick))

print("\n=== COMBAT REPORT ===")
total_dps = 0
print(f"Fight Duration in seconds: {duration}")
for wep, wep_damage in weapons_damage.items():
    print(f"Weapon: {wep}")
    dps = wep_damage / duration
    total_dps += dps
    print(f"DPS: {dps}\n")

print(f"TOTAL DPS: {total_dps}")
