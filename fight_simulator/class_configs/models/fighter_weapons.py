from typing import Optional

from pydantic import BaseModel, Field

from fight_simulator.class_configs.models.common_weapons import CommonWeaponStats


class FighterWeaponStats(CommonWeaponStats):
    bleed_damage: Optional[int] = None
    bleed_bonus: Optional[int] = None
    energy: Optional[int] = None
    mana: Optional[int] = None


class FighterWeapons(BaseModel):
    repeater: FighterWeaponStats
    cleaving_strike: FighterWeaponStats = Field(..., alias="cleaving strike")
    reckless_slam: FighterWeaponStats = Field(..., alias="reckless slam")
    breaker: FighterWeaponStats
    shiver: FighterWeaponStats
    tear: FighterWeaponStats
    cata_staff: FighterWeaponStats

    class Config:
        populate_by_name = True