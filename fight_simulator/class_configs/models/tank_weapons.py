from typing import Optional

from pydantic import BaseModel

from fight_simulator.class_configs.models.common_weapons import CommonWeaponStats


class TankWeaponStats(CommonWeaponStats):
    energy: int
    threat_percent: Optional[int] = None


class TankWeapons(BaseModel):
    repeater: TankWeaponStats
    execute: TankWeaponStats
    roar: TankWeaponStats
    distract: TankWeaponStats
    impale: TankWeaponStats
    warstrike_legacy: TankWeaponStats

    class Config:
        populate_by_name = True
