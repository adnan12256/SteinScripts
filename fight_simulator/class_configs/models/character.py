from pydantic import BaseModel

from fight_simulator.class_configs.models.armor import Armor
from fight_simulator.class_configs.models.fighter_weapons import FighterWeapons
from fight_simulator.class_configs.models.hunter_weapons import HunterWeapons
from fight_simulator.class_configs.models.mage_weapons import MageWeapons
from fight_simulator.class_configs.models.shaman_weapons import ShamanWeapons
from fight_simulator.class_configs.models.tank_weapons import TankWeapons
from fight_simulator.class_configs.models.warlock_weapons import WarlockWeapons


class CharacterEquipment(BaseModel):
    armor: Armor
    weapons: FighterWeapons | MageWeapons | TankWeapons | WarlockWeapons | ShamanWeapons | HunterWeapons
