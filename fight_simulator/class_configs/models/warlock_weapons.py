from typing import Optional

from pydantic import BaseModel

from fight_simulator.class_configs.models.common_weapons import CommonWeaponStats


class WarlockWeaponStats(CommonWeaponStats):
    mana: int
    self_damage_higher: Optional[int] = None
    self_damage_lower: Optional[int] = None
    self_damage_percent: Optional[int] = None


class WarlockWeapons(BaseModel):
    repeater: WarlockWeaponStats
    void_hex: WarlockWeaponStats
    life_burn: WarlockWeaponStats
    sacrifice: WarlockWeaponStats

    class Config:
        populate_by_name = True
