import json
from pathlib import Path
from typing import Optional, Dict
from pydantic import BaseModel, Field


class ArmorPiece(BaseModel):
    armor: int
    cbr: Optional[int] = None
    ccr: Optional[int] = None
    death_damage: Optional[int] = Field(None, alias="death damage")
    energy_regen: Optional[float] = Field(None, alias="energy regen")
    life: Optional[int] = None

    class Config:
        populate_by_name = True


class Armor(BaseModel):
    head: ArmorPiece
    chest: ArmorPiece
    legs: ArmorPiece
    shoulders: ArmorPiece
    gloves: ArmorPiece
    boots: ArmorPiece


class Weapon(BaseModel):
    regular_damage_lower: int
    regular_damage_higher: int
    regular_damage_bonus_percent: int
    bleed_damage: Optional[int] = None
    bleed_bonus: Optional[int] = None
    casttime_s: float
    cooldown_s: float
    energy: int


class Weapons(BaseModel):
    repeater: Weapon
    cleaving_strike: Weapon = Field(..., alias="cleaving strike")
    reckless_slam: Weapon = Field(..., alias="reckless slam")
    breaker: Weapon
    shiver: Weapon
    tear: Weapon

    class Config:
        populate_by_name = True


class CharacterEquipment(BaseModel):
    armor: Armor
    weapons: Weapons


def get_fighter_info() -> CharacterEquipment:
    json_file = Path(__file__).parent / "fighter.json"
    with open(json_file) as f:
        data = json.load(f)

    return CharacterEquipment(**data)
