from pydantic import BaseModel

from fight_simulator.class_configs.models.common_weapons import CommonWeaponStats


class HunterWeaponStats(CommonWeaponStats):
    energy: int


class HunterWeapons(BaseModel):
    repeater: HunterWeaponStats
    powerful_shot: HunterWeaponStats
    arrow_hail: HunterWeaponStats
    toxic_shot: HunterWeaponStats
    multi_shot: HunterWeaponStats

    class Config:
        populate_by_name = True
