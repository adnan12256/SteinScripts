from pydantic import BaseModel

from fight_simulator.class_configs.models.common_weapons import CommonWeaponStats


class HealerWeaponStats(CommonWeaponStats):
    mana: int


class HealerWeapons(BaseModel):
    repeater: HealerWeaponStats
    fireball: HealerWeaponStats
    flamestrike: HealerWeaponStats
    fire_bomb: HealerWeaponStats
    sunfire: HealerWeaponStats
    flame_rush: HealerWeaponStats
    flame_rush_legacy: HealerWeaponStats

    class Config:
        populate_by_name = True
