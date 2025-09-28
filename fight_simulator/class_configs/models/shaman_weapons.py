from typing import Optional

from pydantic import BaseModel, Field

from fight_simulator.class_configs.models.common_weapons import CommonWeaponStats


class ShamanWeaponStats(CommonWeaponStats):
    backward_damage_lower: Optional[int] = None
    backward_damage_higher: Optional[int] = None
    backward_damage_bonus_percent: Optional[int] = None
    mana: int


class ShamanWeapons(BaseModel):
    repeater: ShamanWeaponStats
    frost_bolt: ShamanWeaponStats
    waterfall: ShamanWeaponStats
    tide: ShamanWeaponStats
    ice_totem: ShamanWeaponStats
    frost_totem: ShamanWeaponStats

    class Config:
        populate_by_name = True
