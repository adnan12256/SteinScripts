from typing import Optional

from pydantic import BaseModel


class ArmorPiece(BaseModel):
    armor: int
    cdr: Optional[int] = None
    cbr: Optional[int] = None
    ccr: Optional[int] = None
    damage: Optional[int] = None
    energy_regen: Optional[float] = None
    mana_regen: Optional[float] = None
    life_regen: Optional[float] = None
    life: Optional[int] = None
    heal: Optional[int] = None
    energy: Optional[int] = None
    mana: Optional[int] = None

    class Config:
        populate_by_name = True


class Armor(BaseModel):
    head: ArmorPiece
    chest: ArmorPiece
    legs: ArmorPiece
    shoulders: ArmorPiece
    gloves: ArmorPiece
    boots: ArmorPiece
