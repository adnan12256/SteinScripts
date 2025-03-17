from dataclasses import dataclass
from dataclasses import asdict
from typing import Coroutine, Any
from bs4 import BeautifulSoup
from playwright.async_api import Page
from playwright.sync_api import sync_playwright

import re
import json

# Sample commands
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# div_information = page.locator("div#stein-inventory-head-item").inner_text()
# image_asset_name = page.locator("div#stein-inventory-head-item").get_attribute("style")
# tool_tip_info = page.locator("div#stein-tooltip").inner_text()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

json_file_name = 'inventory_data.json'


@dataclass
class ArmorItem:
    item_name: str = None
    item_type: str = None
    item_armor: str = None
    item_life: str = None
    item_damage: str = None
    item_heal: str = None
    item_cbr: str = None
    item_ccr: str = None
    item_mana: str = None
    item_mana_regen: str = None
    item_life_regen: str = None
    item_energy_regen: str = None


@dataclass
class WeaponItem:
    item_name: Coroutine[Any, Any, str]
    item_type: Coroutine[Any, Any, str]
    item_description: Coroutine[Any, Any, str] | str
    item_activation_cost: Coroutine[Any, Any, str] | None
    item_cast_time: Coroutine[Any, Any, str]
    item_cooldown_time: Coroutine[Any, Any, str]


class SteinLootAppraiser:
    # "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_profile"
    #  ^|^ Always run chrome with this command in the command line for this script to work ^|^

    def __init__(self, chromium_context_manager):
        self.browser = chromium_context_manager.chromium.connect_over_cdp("http://localhost:9222")
        self.page: Page = self.browser.contexts[0].pages[0]  # Get first open tab

    def main_application(self):
        user_input = input(
            "Press 1 to grab inventory data from inventory. Press anything else to get it from the json.")

        if user_input == "1":
            inventory_info: dict = self.get_item_info_from_inventory()

        else:
            inventory_info: dict = self.read_inventory_info_from_json()

        drop_item_info: dict = self.get_loot_information_list()

        self.compare_loot_with_inventory(inventory_info, drop_item_info)

    def get_item_info_from_inventory(self) -> dict:
        # get all item in the inventory
        inventory_slots = self.page.locator("div#stein-inventory-slots div.stein-item-inventory-slot")
        slot_count: int | Coroutine[Any, Any, int] = inventory_slots.count()
        inventory_info = {}
        for i in range(slot_count):
            slot = inventory_slots.nth(i)
            slot.click()
            tool_tip_info: WeaponItem | ArmorItem | None = self.parse_item_info()

            if tool_tip_info is None:
                continue

            if tool_tip_info == 'No item in slot':
                continue

            if tool_tip_info.item_name not in inventory_info.keys():
                inventory_info[tool_tip_info.item_name] = tool_tip_info

            elif tool_tip_info.item_name in inventory_info.keys():
                count = list(inventory_info.keys()).count(tool_tip_info.item_name)
                inventory_info[f"{tool_tip_info.item_name}_{count + 1}"] = tool_tip_info

        self.write_inventory_info_to_json(inventory_info)

        return inventory_info

    def parse_item_info(self) -> WeaponItem | ArmorItem | None:
        if self.page.locator("div#stein-tooltip").inner_text() == 'No item in slot':
            return None

        if self.page.locator("div#stein-tooltip div.stein-tooltip-item-name").count() > 1:  # Skipping skill books. They have two item names in them because of book name and skill name
            return None

        item_name = self.page.locator("div#stein-tooltip div.stein-tooltip-item-name").inner_text()
        item_type = self.page.locator("div#stein-tooltip div.stein-tooltip-item-type").inner_text()

        if item_type in ["Head", "Chest", "Legs", "Shoulders", "Hands", "Feet"]:
            # Armor Items
            html_data = self.page.locator("div#stein-tooltip ul.stein-tooltip-item-properties").inner_html()
            soup = BeautifulSoup(html_data, "html.parser")
            armor_properties = [li.get_text() for li in soup.find_all("li")]
            item_data = ArmorItem()
            item_data.item_name = item_name

            for stat in armor_properties:
                match stat.casefold():
                    case x if "armor" in x:
                        item_data.item_armor = stat
                    case x if "damage" in x:
                        item_data.item_damage = stat
                    case x if "life" in x:
                        item_data.item_life = stat
                    case x if "critical bonus rating" in x:
                        item_data.item_cbr = stat
                    case x if "critical chance rating" in x:
                        item_data.item_ccr = stat
                    case x if "heal" in x:
                        item_data.item_heal = stat
                    case x if "mana regeneration" in x:
                        item_data.item_mana_regen = stat
                    case x if "mana" in x:
                        item_data.item_mana = stat

        elif item_type in ["Resource", "Trash", "Key", "Consumable", "Lumbering", "Herbalism", "Mining", "Energy Potion", "Healing Potion", "Mana Potion", "Skill book", "No item in slot"]:
            # Skip parsing these items
            item_data = None

        else:
            # Weapons Items
            # Setting Description
            text_count = self.page.locator("div#stein-tooltip div.stein-tooltip-item-effect").count()
            description = []
            for text_num in range(text_count):
                description.append(self.page.locator("div#stein-tooltip div.stein-tooltip-item-effect").nth(text_num).inner_text())
            full_description = ". ".join(description)

            if item_type in ["Tool", "Vision of Darkness"]:
                item_data = WeaponItem(item_name=item_name,
                                       item_type=item_type,
                                       item_description=full_description,
                                       item_activation_cost=None,
                                       item_cast_time=self.page.locator("div#stein-tooltip div.stein-tooltip-item-casttime").inner_text(),
                                       item_cooldown_time=self.page.locator("div#stein-tooltip div.stein-tooltip-item-cooldown").inner_text())
            else:
                item_data = WeaponItem(item_name=item_name,
                                       item_type=item_type,
                                       item_description=full_description,
                                       item_activation_cost=self.page.locator("div#stein-tooltip div.stein-tooltip-item-activation-cost").inner_text(),
                                       item_cast_time=self.page.locator("div#stein-tooltip div.stein-tooltip-item-casttime").inner_text(),
                                       item_cooldown_time=self.page.locator("div#stein-tooltip div.stein-tooltip-item-cooldown").inner_text())

        return item_data

    @staticmethod
    def write_inventory_info_to_json(inventory_info: dict):
        serializable_data = {key: asdict(value) for key, value in inventory_info.items()}
        with open('inventory_data.json', 'w') as fp:
            json.dump(serializable_data, fp, indent=4)

    @staticmethod
    def read_inventory_info_from_json() -> dict:
        def deserialize_item(item_data: dict):
            if "item_description" in item_data:  # If description exists, it's a WeaponItem
                return WeaponItem(**item_data)
            else:  # Otherwise, it's an ArmorItem
                return ArmorItem(**item_data)

        with open(json_file_name) as json_file:
            inventory_info = json.load(json_file)
            parsed_data = {key: deserialize_item(value) for key, value in inventory_info.items()}
            return parsed_data

    def get_loot_information_list(self) -> dict:
        dropped_item = self.page.locator("div#stein-dialog-window-container div.stein-need-or-greed")
        dropped_item_count = dropped_item.count()

        if dropped_item_count > 0:
            print("There are some item drops!")
        else:
            print("There are no item drops!")

        drop_item_info = {}
        for i in range(dropped_item_count):
            slot = dropped_item.nth(i).locator(
                "div.stein-need-or-greed-window.stein-window div.stein-item-inventory-slot.need-or-greed-item")
            slot.click()
            tool_tip_info = self.parse_item_info()

            if tool_tip_info is None:
                continue

            if tool_tip_info == 'No item in slot':
                continue

            if tool_tip_info.item_name not in drop_item_info.keys():
                drop_item_info[tool_tip_info.item_name] = tool_tip_info

            elif tool_tip_info.item_name in drop_item_info.keys():
                count = list(drop_item_info.keys()).count(tool_tip_info.item_name)
                drop_item_info[f"{tool_tip_info.item_name}_{count + 1}"] = tool_tip_info

        return drop_item_info

    def compare_loot_with_inventory(self, inventory_info: dict[str, WeaponItem | ArmorItem], dropped_items_dict: dict):
        # dropped_items_dict = {'Risato': WeaponItem(item_name='Risato', item_type='Fireball', item_description='Throws a large fireball that deals 259-482 damage (+80% Bonus) to enemies', item_activation_cost=' 36 Mana', item_cast_time='Casttime: 1.50 sec', item_cooldown_time='Cooldown: 5.00 sec')}
        for item_name, stats in dropped_items_dict.items():
            inventory_item_match = [key for key in inventory_info.keys() if key.startswith(item_name)]
            if len(inventory_item_match) > 0:
                print("Item exists in the inventory")
                for inventory_item in inventory_item_match:
                    inv_description = inventory_info[inventory_item].item_description
                    drop_description = stats.item_description

                    try:
                        inv_get_match = re.search(r"(\d+)-(\d+) (?:\w+ )?damage", inv_description)
                        if inv_get_match is None:
                            continue
                        inv_lower_damage = int(inv_get_match.group(1))
                        inv_higher_damage = int(inv_get_match.group(2))

                        drop_get_match = re.search(r"(\d+)-(\d+) (?:\w+ )?damage", drop_description)
                        if drop_get_match is None:
                            continue
                        drop_lower_damage = int(drop_get_match.group(1))
                        drop_higher_damage = int(drop_get_match.group(2))

                        if ((drop_lower_damage + drop_higher_damage) / 2) > ((inv_lower_damage + inv_higher_damage) / 2):
                            print("This is an upgrade")
                        else:
                            print("This is not an upgrade")

                    except Exception as err:
                        print(str(err))

            else:
                print("This is a new Item!")


if __name__ == '__main__':
    with sync_playwright() as p:
        appraiser = SteinLootAppraiser(p)
        appraiser.main_application()
