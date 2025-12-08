from pydantic import BaseModel


class CommonWeaponStats(BaseModel):
    regular_damage_lower: int
    regular_damage_higher: int
    regular_damage_bonus_percent: int
    casttime_s: float
    cooldown_s: float
    hit_chance_percent: float = 100
