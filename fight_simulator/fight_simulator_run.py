from __future__ import annotations
import dataclasses
from decimal import Decimal
from typing import Dict, List, Optional, Callable, Any

# External dependency
from fight_simulator.class_configs.models.fighter_weapons import FighterWeaponStats
from fight_simulator.class_configs.weapon_damage_calulator import FighterDamage


# =====================================================
# ===============   Status Effects   ==================
# =====================================================

@dataclasses.dataclass
class StatusEffect:
    name: str
    start_time: Decimal
    end_time: Decimal

    def is_active(self, now: Decimal) -> bool:
        return self.start_time <= now <= self.end_time


# =====================================================
# ==================   Actions   ======================
# =====================================================

class BaseAction:
    """Abstract parent for weapons, abilities, potions."""
    name: str
    cooldown: float
    cast_time: float

    def __init__(self, name: str, cooldown: float, cast_time: float):
        self.name = name
        self.cooldown = cooldown
        self.cast_time = cast_time

    def can_use(self, player: "Player", now: Decimal, cooldown_remaining: float) -> bool:
        return cooldown_remaining <= 0

    def on_use(self, player: "Player", sim: "RotationSimulator", now: Decimal) -> float:
        """Return damage dealt by this action."""
        raise NotImplementedError


class PotionAction(BaseAction):
    def __init__(self, name: str, resource: int, cooldown: float, cast_time: float):
        super().__init__(name, cooldown, cast_time)
        self.resource = resource

    def on_use(self, player: "Player", sim: "RotationSimulator", now: Decimal) -> float:
        if self.name == "energy":
            player.energy = min(player.max_energy, player.energy + self.resource)
        elif self.name == "mana":
            player.mana = min(player.max_mana, player.mana + self.resource)

        player.energy = round(player.energy, 3)
        player.mana = round(player.mana, 3)
        return 0.0  # potions do no damage


class WeaponAction(BaseAction):
    """
    Wrapper for real FighterWeaponStats abilities.
    Delegates damage calculation to FighterDamage methods.
    """
    def __init__(
        self,
        name: str,
        weapon_stats: FighterWeaponStats,
        damage_fn: Callable[[], Any],
        bleed_bonus_fn: Optional[Callable[[bool], Any]] = None,
    ):
        super().__init__(name, weapon_stats.cooldown_s, weapon_stats.casttime_s)
        self.stats = weapon_stats
        self.damage_fn = damage_fn
        self.bleed_fn = bleed_bonus_fn

    def can_use(self, player: "Player", now: Decimal, cooldown_remaining: float):
        if cooldown_remaining > 0:
            return False

        # Check mana/energy
        if self.stats.energy and player.energy < self.stats.energy:
            return False
        if self.stats.mana and player.mana < self.stats.mana:
            return False
        return True

    def on_use(self, player: "Player", sim: "RotationSimulator", now: Decimal) -> float:
        # Spend resources
        if self.stats.energy:
            player.energy = max(0, round(player.energy - self.stats.energy, 3))
        if self.stats.mana:
            player.mana = max(0, round(player.mana - self.stats.mana, 3))

        # Damage logic
        if self.name == "breaker":
            has_bleed = sim.has_status("bleed", now)
            dmg = (
                self.bleed_fn(has_bleed).regular_damage
                if self.bleed_fn else self.damage_fn().regular_damage
            )
        else:
            dmg = self.damage_fn().regular_damage

        # Apply special effects
        if self.name == "reckless_slam":
            sim.add_status("bleed", now, now + 5)

        return dmg


# =====================================================
# ===================   Player   ======================
# =====================================================

class Player:
    def __init__(self, fighter_handle: FighterDamage):
        stats = fighter_handle.player_stats
        self.energy = stats.energy
        self.mana = stats.mana
        self.max_energy = stats.energy
        self.max_mana = stats.mana
        self.energy_regen = stats.energy_regen
        self.mana_regen = stats.mana_regen

    def regen(self):
        self.energy = round(min(self.max_energy, self.energy + self.energy_regen), 3)
        self.mana = round(min(self.max_mana, self.mana + self.mana_regen), 3)


# =====================================================
# ==============   Rotation Simulator   ===============
# =====================================================

class RotationSimulator:
    def __init__(
        self,
        player: Player,
        actions: Dict[str, BaseAction],
        fight_duration: float = 120,
        tick: float = 0.1,
    ):
        self.player = player
        self.actions = actions
        self.fight_duration = fight_duration
        self.tick = tick

        self.time = Decimal("0")
        self.cooldowns: Dict[str, float] = {a: 0.0 for a in actions}
        self.status_effects: List[StatusEffect] = []

        # tracking
        self.damage_by_action = {a: 0.0 for a in actions}
        self.count_by_action = {a: 0 for a in actions}

    # ----- Status Effect Helpers -----

    def add_status(self, name: str, start: Decimal, end: Decimal):
        self.status_effects.append(StatusEffect(name, start, end))

    def has_status(self, name: str, now: Decimal) -> bool:
        return any(s.name == name and s.is_active(now) for s in self.status_effects)

    # ----- Simulation Core -----

    def run(self):
        print("=== Combat Simulation Start (OOP) ===")
        while self.time < self.fight_duration:
            now = self.time

            # regen per 1 second
            if now % 1 == 0:
                self.player.regen()

            # Remove expired effects
            self.status_effects = [
                s for s in self.status_effects if s.is_active(now)
            ]

            # Priority-based action loop
            for name, action in self.actions.items():
                if not action.can_use(self.player, now, self.cooldowns[name]):
                    continue

                dmg = action.on_use(self.player, self, now)

                # Set cooldown
                self.cooldowns[name] = action.cooldown + action.cast_time

                # Track damage + count
                self.damage_by_action[name] += dmg
                self.count_by_action[name] += 1

                break  # Only one action per tick

            # Tick down cooldowns
            for a in self.cooldowns:
                self.cooldowns[a] = max(0, self.cooldowns[a] - self.tick)

            # Advance time
            self.time += Decimal(str(self.tick))

        return self.build_report()

    # ----- Report -----

    def build_report(self):
        total_dps = 0
        report = {
            "duration": self.fight_duration,
            "actions": {},
            "total_dps": 0
        }

        for name, dmg in self.damage_by_action.items():
            dps = dmg / self.fight_duration
            total_dps += dps

            report["actions"][name] = {
                "damage": dmg,
                "dps": dps,
                "count": self.count_by_action[name],
            }

        report["total_dps"] = total_dps
        return report


if __name__ == '__main__':
    fighter_handle = FighterDamage()
    player = Player(fighter_handle)

    actions = {
        "repeater": WeaponAction(
            "repeater",
            fighter_handle.fighter_info.weapons.repeater,
            damage_fn=lambda: fighter_handle.repeater_damage(),
        ),
        "cleaving_strike": WeaponAction(
            "cleaving_strike",
            fighter_handle.fighter_info.weapons.cleaving_strike,
            damage_fn=lambda: fighter_handle.cleaving_strike_damage(),
        ),
        "reckless_slam": WeaponAction(
            "reckless_slam",
            fighter_handle.fighter_info.weapons.reckless_slam,
            damage_fn=lambda: fighter_handle.reckless_slam_damage(),
        ),
        "breaker": WeaponAction(
            "breaker",
            fighter_handle.fighter_info.weapons.breaker,
            damage_fn=lambda: None,
            bleed_bonus_fn=lambda bleed: fighter_handle.breaker_damage(bleed_bonus=bleed),
        ),
        "tear": WeaponAction(
            "tear",
            fighter_handle.fighter_info.weapons.tear,
            damage_fn=lambda: fighter_handle.tear_damage(),
        ),
        "shiver": WeaponAction(
            "shiver",
            fighter_handle.fighter_info.weapons.shiver,
            damage_fn=lambda: fighter_handle.shiver_damage(),
        ),
        "cata_staff": WeaponAction(
            "cata_staff",
            fighter_handle.fighter_info.weapons.cata_staff,
            damage_fn=lambda: fighter_handle.cata_staff_damage(),
        ),
        "energy_pot": PotionAction("energy", resource=20, cooldown=60, cast_time=0.5),
    }

    sim = RotationSimulator(player, actions, fight_duration=125)
    result = sim.run()

    print(result)
