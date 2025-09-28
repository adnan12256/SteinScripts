from pydantic import BaseModel

from fight_simulator.class_configs.models.common_weapons import CommonWeaponStats


class MageWeaponStats(CommonWeaponStats):
    mana: int


class MageWeapons(BaseModel):
    repeater: MageWeaponStats
    fireball: MageWeaponStats
    flamestrike: MageWeaponStats
    fire_bomb: MageWeaponStats
    sunfire: MageWeaponStats
    flame_rush: MageWeaponStats
    flame_rush_legacy: MageWeaponStats

    class Config:
        populate_by_name = True
