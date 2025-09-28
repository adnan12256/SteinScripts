from pydantic import BaseModel

from fight_simulator.class_configs.models.armor import Armor
from fight_simulator.class_configs.models.fighter_weapons import FighterWeapons
from fight_simulator.class_configs.models.mage_weapons import MageWeapons


class CharacterEquipment(BaseModel):
    armor: Armor
    weapons: FighterWeapons | MageWeapons
