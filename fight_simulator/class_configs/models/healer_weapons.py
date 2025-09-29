from pydantic import BaseModel

from fight_simulator.class_configs.models.common_weapons import CommonWeaponStats


class HealerWeaponStats(CommonWeaponStats):
    mana: int


class HealerWeapons(BaseModel):
    repeater: HealerWeaponStats
    restoration: HealerWeaponStats
    blessing_legacy: HealerWeaponStats
    blessing: HealerWeaponStats
    holy_barrage_legacy: HealerWeaponStats
    eviction: HealerWeaponStats
    life_burst: HealerWeaponStats

    class Config:
        populate_by_name = True
