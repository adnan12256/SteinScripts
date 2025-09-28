import json
from pathlib import Path

from fight_simulator.class_configs.models.character import CharacterEquipment


class CharacterFactory:
    @staticmethod
    def _parse_character_info(json_ile_path: Path) -> CharacterEquipment:
        with open(json_ile_path) as f:
            data = json.load(f)
        return CharacterEquipment(**data)

    def get_fighter_info(self) -> CharacterEquipment:
        return self._parse_character_info(Path(__file__).parent.parent / "data" / "fighter.json")

    def get_mage_info(self) -> CharacterEquipment:
        return self._parse_character_info(Path(__file__).parent.parent / "data" / "mage.json")


if __name__ == '__main__':
    equipment_info = CharacterFactory()
    a = equipment_info.get_mage_info()
    b = equipment_info.get_fighter_info()
    print(1)
