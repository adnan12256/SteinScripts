import json
from pathlib import Path
from typing import Optional, Dict, Annotated, Union
from pydantic import BaseModel, Field

from fight_simulator.class_configs.parse_common_info import Armor


class Weapon(BaseModel):
    regular_damage_lower: int
    regular_damage_higher: int
    regular_damage_bonus_percent: int
    casttime_s: float
    cooldown_s: float


class FighterWeapon(Weapon):
    bleed_damage: Optional[int] = None
    bleed_bonus: Optional[int] = None
    energy: int


class MageWeapon(Weapon):
    mana: int


class FighterWeapons(BaseModel):
    repeater: FighterWeapon
    cleaving_strike: FighterWeapon = Field(..., alias="cleaving strike")
    reckless_slam: FighterWeapon = Field(..., alias="reckless slam")
    breaker: FighterWeapon
    shiver: FighterWeapon
    tear: FighterWeapon

    class Config:
        populate_by_name = True


class MageWeapons(BaseModel):
    repeater: MageWeapon
    fireball: MageWeapon
    flamestrike: MageWeapon
    fire_bomb: MageWeapon
    sunfire: MageWeapon
    flame_rush: MageWeapon
    flame_rush_legacy: MageWeapon

    class Config:
        populate_by_name = True


class CharacterEquipment(BaseModel):
    armor: Armor
    weapons: FighterWeapons | MageWeapons


def get_fighter_info() -> CharacterEquipment:
    json_file = Path(__file__).parent / "fighter.json"
    with open(json_file) as f:
        data = json.load(f)

    return CharacterEquipment(**data)


def get_mage_info() -> CharacterEquipment:
    json_file = Path(__file__).parent / "mage.json"
    with open(json_file) as f:
        data = json.load(f)

    return CharacterEquipment(**data)


if __name__ == '__main__':
    a = get_fighter_info()
    b = get_mage_info()
