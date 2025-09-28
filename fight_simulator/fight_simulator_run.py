from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict


@dataclass
class Weapon:
    name: str
    dmg_low: int
    dmg_high: int
    bonus_percent: int
    bonus_percent: int
    casttime: float
    cooldown: float
    energy_cost: int
    bleed_damage: Optional[int] = None
    bleed_bonus: Optional[int] = None


# Example weapons (from your JSON)
weapons = {
    "cleaving strike": Weapon("cleaving strike", 114, 211, 80, 0.3, 6, 6),
    "reckless slam": Weapon("reckless slam", 65, 120, 65, 0.3, 6, 10, bleed_damage=19, bleed_bonus=13),
    "breaker": Weapon("breaker", 40, 75, 15, 0.6, 0.6, 15),
    "shiver": Weapon("shiver", 226, 419, 15, 0.6, 0.6, 6),
    "tear": Weapon("shiver", 88, 165, 15, 0.6, 0.6, 6),
    "repeater": Weapon("repeater", 22, 41, 15, 0.6, 0.6, 0),
}

# Simulation settings
energy_regen_per_sec = 4.9  # e.g. from armor
max_energy = 100
duration = 300.0  # simulate 20 seconds
tick = 0.1  # tick resolution (0.1s)

# Runtime state
energy = 100
cooldowns: Dict[str, float] = {w: 0.0 for w in weapons}
time = Decimal("0.0")

print("=== Combat Simulation Start ===")

while time < duration:
    if time % 1 == 0:
        energy = min([max_energy, energy + energy_regen_per_sec])
        print(f"New energy {energy}")

    # try to attack (priority order)
    for w in weapons.values():
        if cooldowns[w.name] <= 0 and energy >= w.energy_cost:
            energy -= w.energy_cost
            cooldowns[w.name] = w.cooldown
            dmg = (w.dmg_low + w.dmg_high) // 2
            print(f"{time:4.1f}s: Used {w.name}, dealt {dmg}, energy left {energy:.1f}")
            break

    # tick down cooldowns
    for k in cooldowns:
        cooldowns[k] = max([0, cooldowns[k] - 0.1])

    time += Decimal(str(tick))
