import logging
from collections import namedtuple

from .ship import Ship
from .upgrade_filters import upgrade_slot_filter
from .definition import Action

from ..settings import Settings
from ..utils import prettify_name

from typing import List, Dict


Upgrade = namedtuple('Upgrade', ['slots', 'name', 'cost', 'attributes'])


class PilotEquip:
    """
    This class is used for managing equipped pilot data.

    Note that filtered upgrades are intended to be updated from the Upgrades class.
    """
    settings = Settings()

    def __init__(self, ship: Ship, pilot: dict):
        self.ship = ship
        self.pilot = pilot
        self.__filtered_upgrades = []
        self.__equipped_upgrades = []

        self.data = self.__synthesize_ship_and_pilot()

    def __synthesize_ship_and_pilot(self):
        d = {}
        d["faction_name"] = self.ship.faction_name
        d["ship_name"] = self.ship.ship_name
        d["base"] = self.ship.base
        d["statistics"] = self.__combine_statistics()
        d["actions"] = self.__combine_actions()
        d["upgrade_slots"] = self.__combine_upgrade_slots()
        d["pilot_name"] = self.pilot["name"]
        d["limit"] = self.pilot["limit"]
        d["initiative"] = self.pilot["initiative"]
        d["cost"] = self.pilot["cost"]
        d["keywords"] = self.pilot["keywords"]
        d["hardpoint"] = self.ship.ship_data.get("hardpoint", [])

        return d

    @property
    def filtered_upgrades(self):
        """
        These are calculated when a pilot is equipped.
        """
        return self.__filtered_upgrades

    @filtered_upgrades.setter
    def filtered_upgrades(self, val: List[Dict]):
        self.__filtered_upgrades = val

    @property
    def base_size(self):
        return self.data.get("base")

    @property
    def hardpoint(self):
        return self.data.get("hardpoint")

    @property
    def limit(self):
        temp = self.data.get("limit")
        val = None
        if temp is None or temp == 0:
            val = 99
        else:
            val = temp
        return val

    @property
    def initiative(self):
        return self.data.get("initiative")

    @property
    def faction_name(self):
        return self.data.get("faction_name")

    @property
    def ship_name(self):
        return self.data.get("ship_name")

    @property
    def pilot_name(self):
        return self.data.get("pilot_name")

    @property
    def statistics(self):
        return self.data.get("statistics")

    @property
    def default_pilot_actions(self) -> List[Action]:
        """
        returns a list of pilot action dictionaries (regardless of what the pilot has equipped) of the form:
        [
            ...
            {
                'action': <action>,
                'color': <color>,
                'action_link': <action_link>,
                'color_link': <color_link>
            }
            ...
        ]
        """
        return [Action(**action) for action in self.data.get("actions").copy()]

    @property
    def actions(self) -> List[Action]:
        """
        returns a pilot's available actions based on equipped upgrades.
        this needs the upgrades list in order to evaluate the equipped
        returns a list of pilot action dictionaries of the form:
        [
            ...
            {
                'action': <action>,
                'color': <color>,
                'action_link': <action_link>,
                'color_link': <color_link>
            }
            ...
        ]
        """
        additional_actions = []
        for upgrade in self.equipped_upgrades:

            upgrade_actions = upgrade.attributes.get("modifications", {}).get("actions", [])
            upgrade_actions = [Action(**action) for action in upgrade_actions]
            additional_actions.extend(upgrade_actions)

        return self.default_pilot_actions + additional_actions

    @property
    def keywords(self):
        return self.data.get("keywords")

    @property
    def arc_types(self) -> list:
        return [attack.get("arc_type") for attack in self.attacks]

    @property
    def attacks(self):
        attacks = self.get_statistic(self.statistics, "attacks")
        return attacks.get("attacks")

    @property
    def max_attack(self):
        return max([attack.get("attack") for attack in self.attacks])

    @staticmethod
    def get_statistic(statistics_list, statistic_name):
        for statistic in statistics_list:
            name = list(statistic.keys())[0]
            if name == statistic_name:
                return statistic
        return None

    def get_attribute(self, attribute):
        """
        This function is used to assess attributes that impact variable cost.
        """
        if (attribute == "base") or (attribute == "initiative"):
            return self.data.get(attribute)
        elif attribute == "agility":
            statistic = self.get_statistic(self.statistics, attribute)
            return statistic.get(attribute)
        else:
            return self.max_attack

    def __combine_statistics(self):
        ship_statistics = self.ship.statistics.copy()
        pilot_statistics = self.pilot["statistics"]
        combined = []
        for statistic in pilot_statistics:
            stat_key = list(statistic.keys())[0]
            value = statistic.get(stat_key)
            # use the pilot value if it exists
            updated = False
            if type(value) is list:
                if value:
                    updated = True
            elif type(value) is dict:
                for _, v in value.items():
                    if v is not None:
                        updated = True
            else:
                if value is not None:
                    updated = True
            if updated:
                combined.append(statistic)
            else:
                combined.append(self.get_statistic(ship_statistics, stat_key))

        return combined

    def __combine_actions(self):
        """For actions, we take all the ship actions, and see if any additional pilot actions are specified."""
        combined = self.ship.actions.copy()
        pilot_actions = self.pilot.get("actions")
        for action in pilot_actions:
            combined.append(action)
        return combined

    def __combine_upgrade_slots(self):
        combined = self.ship.upgrade_slots.copy()
        pilot_slots = self.pilot.get("upgrade_slots")
        for slot in pilot_slots:
            combined.append(slot)
        return combined

    @property
    def default_upgrade_slots(self) -> List[str]:
        """
        returns upgrade slots default to the pilot
        """
        return self.data.get("upgrade_slots").copy()

    @property
    def upgrade_slots(self):
        """
        returns upgrade slots, adds additional slots based on equipped upgrades and weapon hardpoints
        adds a command slot if the mode is epic
        """
        additional_slots = []
        if self.settings.mode == Settings.Mode.EPIC and self.base_size != "huge":
            additional_slots.append("command")
        added = []
        removed = []
        for upgrade in self.equipped_upgrades:
            upgrade_modifiers = upgrade.attributes.get("modifications", {}).get("upgrade_slots", {})
            added.extend(upgrade_modifiers.get("added", []))
            removed.extend(upgrade_modifiers.get("removed", []))
            for slot in upgrade.slots:
                if slot in self.hardpoint:
                    removed.extend([hp_slot for hp_slot in self.hardpoint if hp_slot != slot])

        additional_slots.extend(added)

        final_slots = additional_slots + self.default_upgrade_slots + self.hardpoint
        final_slots = [slot for slot in final_slots if slot not in removed]
        return final_slots

    @property
    def cost(self):
        return self.data.get("cost")

    @property
    def cost_with_upgrades(self):
        upgrade_cost = sum([upgrade.cost for upgrade in self.equipped_upgrades])
        return self.data.get("cost") + upgrade_cost

    @property
    def equipped_upgrades(self) -> List[Upgrade]:
        return self.__equipped_upgrades

    @property
    def total_equipped_upgrade_cost(self) -> int:
        return sum([upgrade.cost for upgrade in self.equipped_upgrades])

    @property
    def available_upgrade_slots(self) -> List[str]:
        """Returns all remaining upgrade slots available for an equipped pilot."""
        upgrade_slots = self.upgrade_slots.copy()
        for upgrade in self.equipped_upgrades:
            for slot in upgrade.slots:
                upgrade_slots.pop(upgrade_slots.index(slot))
        return upgrade_slots

    def equip_upgrade(self, upgrade_slots: List[str], upgrade_name: str, upgrade_cost: int, upgrade_dict: dict) -> bool:
        """adds upgrade to the equipped upgrades
        returns true if upgrade equipped
        """
        # Test that slots are available for every slot the upgrade needs
        if not upgrade_slot_filter(upgrade_slots, self.available_upgrade_slots):
            logging.info(
                f"Insufficient upgrade slots to equip {prettify_name(upgrade_name)} to {prettify_name(self.pilot_name)}")
            return False
        removed = upgrade_dict.get("modifications", {}).get("upgrade_slots", {}).get("removed", [])
        for removed_upgrade_slot in removed:
            if removed_upgrade_slot not in self.available_upgrade_slots:
                logging.info(f"An upgrade is equipped in the to-be removed <{removed_upgrade_slot}> slot.  Please unequip this upgrade first.")
                return False
        for upgrade in self.equipped_upgrades:
            if upgrade.name == upgrade_name:
                logging.info("Unable to equip more than one of an upgrade to the same pilot instance.")
                return False
        self.__equipped_upgrades.append(Upgrade(upgrade_slots, upgrade_name, upgrade_cost, upgrade_dict))
        return True

    def unequip_upgrade(self, upgrade_name):
        """removes an equipped upgrade.
        returns true if upgrade successfully unequipped"""
        unequipped = False
        for upgrade in self.equipped_upgrades:
            if upgrade.name == upgrade_name:
                upgrade_modifiers = upgrade.attributes.get("modifications", {}).get("upgrade_slots", {})
                added = upgrade_modifiers.get("added", [])
                for added_upgrade_slot in added:
                    if added_upgrade_slot not in self.available_upgrade_slots:
                        logging.info(f"An upgrade is equipped in the added <{added_upgrade_slot}> slot.  Please unequip this upgrade first.")
                        return False
                self.__equipped_upgrades.pop(self.__equipped_upgrades.index(upgrade))
                unequipped = True
                break
        return unequipped
