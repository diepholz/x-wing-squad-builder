from PySide6 import QtWidgets, QtCore, QtGui
from .ui.definition_form_ui import Ui_DefinitionForm

from .model import XWing, Faction, Ship
from .model.constants import BASE_SIZES, ARC_TYPES_, ACTION_COLORS, ACTIONS_, UPGRADE_SLOTS_, FACTION_NAMES, KEYWORDS, INVALID
from .utils import prettify_definition_form_entry
from .utils_pyside import parse_actions, parse_attacks, arr_to_comma_separated_list, parse_check_box

import logging
import json
from pathlib import Path

from typing import List, Optional, Union


class DefinitionForm(QtWidgets.QDialog):
    update_signal = QtCore.Signal()
    form_closed_signal = QtCore.Signal()

    def __init__(self, data_filepath: Path, parent=None):
        super().__init__()
        self.ui = Ui_DefinitionForm()
        self.ui.setupUi(self)

        self.data_filepath = data_filepath
        self.load_data()

        # This is turned on when editing entries from the viewer, then turned off after the edit is complete
        self.edit_mode = False
        self.edit_pilot_name = None
        self.edit_upgrade_name = None
        self.edit_ship_name = None

        self.ui.faction_name_line_edit.setText("great slayers")
        self.ui.ship_name_line_edit.setText("will-d-beast")
        self.ui.base_size_line_edit.setText("large")
        self.ui.attacks_line_edit.setText("99, 99")
        self.ui.arc_types_line_edit.setText("full rear, full front")
        self.ui.actions_line_edit.setText("focus, evade")
        self.ui.colors_line_edit.setText("red, white")
        self.ui.upgrade_slots_line_edit.setText("astromech")
        self.ui.pilot_name_line_edit.setText("el solverdor")
        self.ui.cost_spinbox.setValue(6969)
        self.ship_check_timer = QtCore.QTimer()
        self.ship_check_timer.timeout.connect(self.check_ship_name)
        self.ship_check_timer.start(500)

        self.accepted.connect(self.handle_ok_pressed)
        self.rejected.connect(self.handle_close_pressed)

    def load_data(self):
        with open(self.data_filepath) as file:
            self.data = json.load(file)

    def check_ship_name(self):
        faction_idx = self.get_faction_index(self.faction_name)
        if faction_idx is not None:
            ship_idx = self.get_ship_index(self.faction_name, self.ship_name)
            if ship_idx is not None:
                self.ui.ship_exists_label.setText(
                    f"Ship {self.ship_name} already exists, continue to pilot entry.")
            else:
                self.ui.ship_exists_label.setText(
                    "Ship does not exist - please continue with new ship entry.")

    @property
    def faction_name(self) -> str:
        """Returns lowercase string of entered faction name"""
        return self.ui.faction_name_line_edit.text().lower()

    @property
    def ship_name(self) -> str:
        """Returns lowercase string of entered ship name"""
        return self.ui.ship_name_line_edit.text().lower()

    @property
    def base_size(self) -> str:
        """Returns lowercase string of entered base name"""
        return self.ui.base_size_line_edit.text().lower()

    @property
    def attacks(self) -> Union[List[str], str]:
        attack_list = prettify_definition_form_entry(
            self.ui.attacks_line_edit.text())
        try:
            attack_list = [int(attack) for attack in attack_list]
        except ValueError:
            return INVALID
        return attack_list

    @property
    def arc_types(self) -> Union[List[str], str]:
        arc_types = prettify_definition_form_entry(
            self.ui.arc_types_line_edit.text())
        for arc_type in arc_types:
            if arc_type not in ARC_TYPES_:
                return INVALID
        if len(arc_types) != len(self.attacks):
            return INVALID
        return arc_types

    @property
    def combined_attacks_arc_types(self) -> List[dict]:
        return [{"attack": attack, "arc_type": arc_type} for attack, arc_type in zip(self.attacks, self.arc_types)]

    @staticmethod
    def parse_actions_and_colors(text: str, restricted_text: List[str]):
        parsed_list = prettify_definition_form_entry(text)
        bases = []
        links = []
        for item in parsed_list:
            if ">" in item:
                base, link = item.split(">")
            else:
                base = item
                link = None
            base = base.strip()
            bases.append(base)
            if base not in restricted_text:
                return INVALID

            if link:
                link = link.strip()
                if link not in restricted_text:
                    return INVALID
            links.append(link)
        return bases, links

    @staticmethod
    def parse_comma_separated_text(text: str, restricted_text: List[str]):
        """Generates a formatted list of entries from a text field separated by commas.  No input must be handled
        outside of this function.


        :param text:
        :type text: str
        :param restricted_text:
        :type restricted_text: List[str]
        :return: A list of formatted values if the input falls within the restricted text, otherwise INVALID string.
        """
        item_list = prettify_definition_form_entry(text)
        for item in item_list:
            if item not in restricted_text:
                return INVALID
        return item_list

    @property
    def actions(self):
        actions_text = self.ui.actions_line_edit.text()
        if actions_text:
            return self.parse_actions_and_colors(actions_text, ACTIONS_)
        return [], []

    @property
    def colors(self):
        colors_text = self.ui.colors_line_edit.text()
        if colors_text:
            colors, color_links = self.parse_actions_and_colors(
                self.ui.colors_line_edit.text(), ACTION_COLORS)
            actions, _ = self.actions
            if len(colors) != len(actions):
                return INVALID
            return colors, color_links
        return [], []

    @property
    def combined_actions_and_colors(self) -> List[dict]:
        actions, action_links = self.actions
        colors, color_links = self.colors
        return [{"action": action, "color": color, "action_link": action_link, "color_link": color_link} for action, color, action_link, color_link in zip(actions, colors, action_links, color_links)]

    @property
    def agility(self) -> int:
        return self.ui.agility_spinbox.value()

    @property
    def hull(self) -> int:
        return self.ui.hull_spinbox.value()

    @property
    def shield(self) -> dict:
        return {"shield": self.ui.shield_spinbox.value(), "recharge": self.ui.shield_recharge_spinbox.value()}

    @property
    def force(self) -> dict:
        return {"force": self.ui.force_spinbox.value(), "recharge": self.ui.force_recharge_spinbox.value()}

    @property
    def energy(self) -> dict:
        return {"energy": self.ui.energy_spinbox.value(), "recharge": self.ui.energy_recharge_spinbox.value()}

    @property
    def charge(self) -> dict:
        return {"charge": self.ui.charge_spinbox.value(), "recharge": self.ui.charge_recharge_spinbox.value()}

    @property
    def upgrade_slots(self) -> Union[List[str], str]:
        upgrade_slot_text = self.ui.upgrade_slots_line_edit.text()
        if upgrade_slot_text:
            return self.parse_comma_separated_text(self.ui.upgrade_slots_line_edit.text(), UPGRADE_SLOTS_)
        return []

    @property
    def pilot_name(self) -> str:
        return self.ui.pilot_name_line_edit.text().lower()

    @property
    def pilot_limit(self) -> int:
        return self.ui.limit_spinbox.value()

    @property
    def pilot_initiative(self) -> int:
        return self.ui.initiative_spinbox.value()

    @property
    def pilot_cost(self) -> int:
        return self.ui.cost_spinbox.value()

    @property
    def pilot_attacks(self) -> Union[List[str], str]:
        attack_text = self.ui.pilot_attacks_line_edit.text()
        if attack_text:
            attack_list = prettify_definition_form_entry(attack_text)
            try:
                attack_list = [int(attack) for attack in attack_list]
            except ValueError:
                return INVALID
        else:
            attack_list = []
        return attack_list

    @property
    def pilot_arc_types(self) -> Union[List[str], str]:
        arc_type_text = self.ui.pilot_arc_types_line_edit.text()
        if arc_type_text:
            arc_types = prettify_definition_form_entry(arc_type_text)
            for arc_type in arc_types:
                if arc_type not in ARC_TYPES_:
                    return INVALID
            if len(arc_types) != len(self.pilot_attacks):
                return INVALID
        else:
            if self.pilot_attacks:
                return INVALID
            else:
                arc_types = []
        return arc_types

    @property
    def pilot_combined_attacks_arc_types(self) -> List[dict]:
        return [{"attack": attack, "arc_type": arc_type} for attack, arc_type in zip(self.pilot_attacks, self.pilot_arc_types)]

    @property
    def pilot_upgrade_slots(self) -> Union[List[str], str]:
        upgrade_slot_text = self.ui.pilot_upgrade_slots_line_edit.text()
        if upgrade_slot_text:
            upgrade_slot_list = self.parse_comma_separated_text(
                upgrade_slot_text, UPGRADE_SLOTS_)
        else:
            upgrade_slot_list = []
        return upgrade_slot_list

    @property
    def pilot_actions(self) -> Union[List[str], str]:
        pilot_actions_text = self.ui.pilot_actions_line_edit.text()
        if pilot_actions_text:
            return self.parse_actions_and_colors(pilot_actions_text, ACTIONS_)
        else:
            return [], []

    @property
    def pilot_colors(self) -> Union[List[str], str]:
        pilot_colors_text = self.ui.pilot_colors_line_edit.text()
        if pilot_colors_text:
            colors, color_links = self.parse_actions_and_colors(
                pilot_colors_text, ACTION_COLORS)
            actions, _ = self.pilot_actions
            if len(colors) != len(actions):
                return INVALID
            return colors, color_links
        else:
            return [], []

    @property
    def pilot_combined_actions_and_colors(self) -> List[dict]:
        actions, action_links = self.pilot_actions
        colors, color_links = self.pilot_colors
        return [{"action": action, "color": color, "action_link": action_link, "color_link": color_link} for action, color, action_link, color_link in zip(actions, colors, action_links, color_links)]

    @property
    def pilot_traits(self) -> List[str]:
        traits_text = self.ui.traits_line_edit.text()
        if traits_text:
            traits = self.parse_comma_separated_text(traits_text, KEYWORDS)
        else:
            traits = []
        return traits

    @staticmethod
    def evaluate_none_spinbox(spinbox: QtWidgets.QSpinBox):
        val = spinbox.value()
        if val == -1:
            return None
        else:
            return val

    @property
    def pilot_agility(self) -> int:
        return self.evaluate_none_spinbox(self.ui.pilot_agility_spinbox)

    @property
    def pilot_hull(self) -> int:
        return self.evaluate_none_spinbox(self.ui.pilot_hull_spinbox)

    def evaluate_attributes(self, name, base_spinbox, recharge_spinbox, decharge_spinbox):
        return {name: self.evaluate_none_spinbox(base_spinbox),
                "recharge": self.evaluate_none_spinbox(recharge_spinbox),
                "decharge": self.evaluate_none_spinbox(decharge_spinbox)}

    @property
    def pilot_shield(self) -> dict:
        return self.evaluate_attributes("shield", self.ui.pilot_shield_spinbox, self.ui.pilot_shield_recharge_spinbox, self.ui.pilot_shield_decharge_spinbox)

    @property
    def pilot_force(self) -> dict:
        return self.evaluate_attributes("force", self.ui.pilot_force_spinbox, self.ui.pilot_force_recharge_spinbox, self.ui.pilot_force_decharge_spinbox)

    @property
    def pilot_energy(self) -> dict:
        return self.evaluate_attributes("energy", self.ui.pilot_energy_spinbox, self.ui.pilot_energy_recharge_spinbox, self.ui.pilot_energy_decharge_spinbox)

    @property
    def pilot_charge(self) -> dict:
        return self.evaluate_attributes("charge", self.ui.pilot_charge_spinbox, self.ui.pilot_charge_recharge_spinbox, self.ui.pilot_charge_decharge_spinbox)

    @property
    def epic(self):
        return str(self.ui.epic_checkbox.isChecked())

    @property
    def valid_entry(self):
        valid = True
        if (not self.faction_name or
            not self.ship_name or
            not self.pilot_name
            ):
            logging.info(
                "Must provide a value for faction name, ship name, and pilot name.")

            valid = False
        if self.faction_name not in FACTION_NAMES:
            logging.info(
                f"Must provide a faction name within the following: {FACTION_NAMES}")
            valid = False
        if self.base_size not in BASE_SIZES:
            logging.info(
                f"Base size invalid.  Please choose from the following: {BASE_SIZES}")
            valid = False
        if self.attacks == INVALID or self.pilot_attacks == INVALID:
            logging.info(
                "Attack entries must be numbers separated by commas.  Please try again.")
            valid = False
        if self.arc_types == INVALID or self.pilot_arc_types == INVALID:
            logging.info(
                f"Arc types must have the same number of attacks.  Arc Types must be be within the following: {ARC_TYPES_}")
            valid = False
        if self.actions == INVALID or self.pilot_actions == INVALID:
            logging.info(
                f"Action entries must be within the following: {ACTIONS_}")
            valid = False
        if self.colors == INVALID or self.pilot_colors == INVALID:
            logging.info(
                f"Colors must have the same number of actions.  Colors must be be within the following: {ACTION_COLORS}")
            valid = False
        if self.upgrade_slots == INVALID or self.pilot_upgrade_slots == INVALID:
            logging.info(
                f"Upgrade slots must be within the following: {UPGRADE_SLOTS_}")
            valid = False
        if self.pilot_traits == INVALID:
            logging.info(
                f"Pilot keywords must either be empty, or one of the following: {KEYWORDS}")
            valid = False

        return valid

    def data_entry_template(self):
        new_entry = {
            "name": self.faction_name,
            "ship":
                {
                    "name": self.ship_name,
                    "base": self.base_size,
                    "statistics": [
                        {
                            "attacks": self.combined_attacks_arc_types
                        },
                        {
                            "agility": self.agility
                        },
                        {
                            "hull": self.hull
                        },
                        {
                            "shield": self.shield
                        },
                        {
                            "force": self.force
                        },
                        {
                            "energy": self.energy
                        },
                        {
                            "charge": self.charge
                        }
                    ],
                    "actions": self.combined_actions_and_colors,
                    "upgrade_slots": self.upgrade_slots,
                    "epic": self.epic,
                    "pilots": []
                },
            "pilot":
                {
                    "name": self.pilot_name,
                    "limit": self.pilot_limit,
                    "initiative": self.pilot_initiative,
                    "cost": self.pilot_cost,
                    "statistics": [
                        {
                            "attacks": self.pilot_combined_attacks_arc_types
                        },
                        {
                            "agility": self.pilot_agility
                        },
                        {
                            "hull": self.pilot_hull
                        },
                        {
                            "shield": self.pilot_shield
                        },
                        {
                            "force": self.pilot_force
                        },
                        {
                            "energy": self.pilot_energy
                        },
                        {
                            "charge": self.pilot_charge
                        }
                    ],
                    "actions": self.pilot_combined_actions_and_colors,
                    "upgrade_slots": self.pilot_upgrade_slots,
                    "keywords": self.pilot_traits
                }
        }
        return new_entry

    @property
    def upgrade_list(self):
        return self.data.get("upgrades")

    @property
    def current_upgrade_names(self):
        upgrade_name_list = [upgrade["name"] for upgrade in self.upgrade_list]
        return upgrade_name_list

    def get_upgrade_idx(self, upgrade_name):
        for i, upgrade in enumerate(self.upgrade_list):
            if upgrade["name"] == upgrade_name:
                return i
        return None

    def insert_new_upgrade_entry(self, upgrade_entry):
        new_upgrade_name = upgrade_entry["name"]
        if new_upgrade_name in self.current_upgrade_names or self.edit_mode:
            title = "Upgrade Exists!"
            msg = "This upgrade exists.  Do you want to overwrite the existing upgrade data?"
            reply = QtWidgets.QMessageBox.warning(
                self, title, msg, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Ok:
                upgrade_idx = self.get_upgrade_idx(self.edit_upgrade_name)
                self.upgrade_list[upgrade_idx] = upgrade_entry
                logging.info(
                    f"Attempting to overwrite data for <{new_upgrade_name}>.")
            else:
                logging.info(
                    f"Upgrade data for <{new_upgrade_name}> not overwritten.")
                # returning true is what we use to open the upgrade form again
                return True
        else:
            self.data["upgrades"].append(upgrade_entry)
            logging.info(
                f"Attempting to insert upgrade data for <{new_upgrade_name}>.")
        self.write_data()
        self.edit_mode = False
        self.edit_upgrade_name = None

    def insert_new_entry(self) -> bool:
        self.xwing = XWing.launch_xwing_data(self.data_filepath)
        entry = self.data_entry_template()
        new_faction_name = entry['name']
        new_ship_name = entry['ship']['name']
        # If the faction already exists...
        if new_faction_name in self.xwing.faction_names:
            if self.edit_mode:
                current_ship_data = self.xwing.get_ship(
                    new_faction_name, self.edit_ship_name)
            else:
                current_ship_data = self.xwing.get_ship(
                    new_faction_name, new_ship_name)
            # If the ship already exists...
            if current_ship_data or self.edit_mode:
                self.insert_ship(new_faction_name, entry['ship'], overwrite=True)
                pilot_data = entry['pilot']
                new_pilot_name = entry['pilot']['name']
                # If the pilot already exists...
                if new_pilot_name in current_ship_data.pilot_names or self.edit_mode:
                    title = "Pilot exists!"
                    msg = "This pilot exists.  Do you want to overwrite the existing pilot data?"
                    reply = QtWidgets.QMessageBox.warning(
                        self, title, msg, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                    if reply == QtWidgets.QMessageBox.Ok:
                        self.insert_pilot(
                            new_faction_name, new_ship_name, pilot_data, overwrite=True)
                    else:
                        # returning true is what we use to open the definition form again
                        return True
                # Otherwise simply append a new pilot
                else:
                    self.insert_pilot(new_faction_name,
                                      new_ship_name, pilot_data)
            # Otherwise simply append a new ship with the pilot
            else:
                self.insert_ship(new_faction_name, entry['ship'])
                self.insert_pilot(new_faction_name,
                                  new_ship_name, entry['pilot'])
        # Otherwise simply append a new faction, ship, and pilot
        else:
            self.insert_faction(new_faction_name)
            self.insert_ship(new_faction_name, entry['ship'])
            self.insert_pilot(new_faction_name, new_ship_name, entry['pilot'])

        self.edit_mode = False
        self.edit_pilot_name = None
        self.edit_ship_name = None

    def get_faction_index(self, faction_name: str) -> Optional[int]:
        for i, faction in enumerate(self.data['factions']):
            if faction['name'] == faction_name:
                return i
        return None

    def get_ship_index(self, faction_name: str, ship_name: str) -> int:
        faction_idx = self.get_faction_index(faction_name)
        for i, ship in enumerate(self.data['factions'][faction_idx]['ships']):
            if ship['name'] == ship_name:
                return i
        return None

    def insert_faction(self, faction_name: str):
        new_faction = {
            'name': faction_name,
            'ships': []
        }
        self.data['factions'].append(new_faction)
        logging.info(f"Attempting to insert new faction <{faction_name}>.")

    def insert_ship(self, faction_name: str, ship_data: dict, overwrite=False):
        faction_idx = self.get_faction_index(faction_name)
        if overwrite:
            for k, ship in enumerate(self.data['factions'][faction_idx]['ships']):
                if ship['name'] == self.edit_ship_name:
                    logging.info(
                        f"Attempting to update ship info for {ship_data['name']}"
                    )
                    # remember to hang on to the pilots
                    pilots = self.data['factions'][faction_idx]['ships'][k]['pilots'].copy()
                    self.data['factions'][faction_idx]['ships'][k] = ship_data
                    self.data['factions'][faction_idx]['ships'][k]['pilots'] = pilots
        else:
            self.data['factions'][faction_idx]['ships'].append(ship_data)
            logging.info(
                f"Attempting to insert new ship <{ship_data['name']}> into faction <{faction_name}>.")

    def insert_pilot(self, faction_name: str, ship_name: str, pilot_data: dict, overwrite=False):
        faction_idx = self.get_faction_index(faction_name)
        ship_idx = self.get_ship_index(faction_name, ship_name)
        if overwrite:
            for k, pilot in enumerate(self.data['factions'][faction_idx]['ships'][ship_idx]['pilots']):
                if pilot['name'] == self.edit_pilot_name:
                    logging.info(
                        f"Attempting to update pilot info for {pilot_data['name']}")
                    self.data['factions'][faction_idx]['ships'][ship_idx]['pilots'][k] = pilot_data
        else:
            self.data['factions'][faction_idx]['ships'][ship_idx]['pilots'].append(
                pilot_data)
            logging.info(
                f"Attempting to insert pilot <{pilot_data['name']}> under ship <{ship_name}> under faction <{faction_name}>.")

    def populate_definition_form(self, ship: Ship, pilot: dict):
        self.ui.faction_name_line_edit.setText(ship.faction_name)
        self.ui.ship_name_line_edit.setText(ship.ship_name)
        self.ui.base_size_line_edit.setText(ship.base)
        parse_attacks(
            self.ui.attacks_line_edit,
            self.ui.arc_types_line_edit,
            ship.statistics
        )
        shallow_ship_stats = [
            (self.ui.agility_spinbox, "agility"),
            (self.ui.hull_spinbox, "hull")
        ]
        for stat in shallow_ship_stats:
            spinbox, attribute = stat
            spinbox.setValue(ship.get_statistic(ship.statistics, attribute))

        deep_ship_stats = [
            (self.ui.shield_spinbox, self.ui.shield_recharge_spinbox, "shield"),
            (self.ui.force_spinbox, self.ui.force_recharge_spinbox, "force"),
            (self.ui.energy_spinbox, self.ui.energy_recharge_spinbox, "energy"),
            (self.ui.charge_spinbox, self.ui.charge_recharge_spinbox, "charge"),
        ]
        for stat in deep_ship_stats:
            att_spinbox, rech_spinbox, attribute = stat
            temp = ship.get_statistic(ship.statistics, attribute)
            att_spinbox.setValue(temp[attribute])
            rech_spinbox.setValue(temp["recharge"])

        parse_actions(
            self.ui.actions_line_edit,
            self.ui.colors_line_edit,
            ship.actions
        )

        self.ui.upgrade_slots_line_edit.setText(
            arr_to_comma_separated_list(ship.upgrade_slots))

        parse_check_box(
            self.ui.epic_checkbox, ship.ship_data.get("epic", "False")
        )

        self.ui.pilot_name_line_edit.setText(pilot.get("name"))

        shallow_pilot_entries = [
            (self.ui.cost_spinbox, "cost"),
            (self.ui.initiative_spinbox, "initiative"),
            (self.ui.limit_spinbox, "limit"),
        ]
        for entry in shallow_pilot_entries:
            spinbox, attribute = entry
            spinbox.setValue(pilot.get(attribute))

        parse_attacks(
            self.ui.pilot_attacks_line_edit,
            self.ui.pilot_arc_types_line_edit,
            pilot.get("statistics")
        )

        shallow_pilot_stats = [
            (self.ui.pilot_agility_spinbox, "agility"),
            (self.ui.pilot_hull_spinbox, "hull"),
        ]
        for stat in shallow_pilot_stats:
            spinbox, attribute = stat
            val = ship.get_statistic(pilot.get("statistics"), attribute)
            if val is None:
                val = -1
            spinbox.setValue(val)

        deep_pilot_stats = [
            (self.ui.pilot_shield_spinbox, self.ui.pilot_shield_recharge_spinbox,
             self.ui.pilot_shield_decharge_spinbox, "shield"),
            (self.ui.pilot_force_spinbox, self.ui.pilot_force_recharge_spinbox,
             self.ui.pilot_force_decharge_spinbox, "force"),
            (self.ui.pilot_energy_spinbox, self.ui.pilot_energy_recharge_spinbox,
             self.ui.pilot_energy_decharge_spinbox, "energy"),
            (self.ui.pilot_charge_spinbox, self.ui.pilot_charge_recharge_spinbox,
             self.ui.pilot_charge_decharge_spinbox, "charge"),
        ]
        for stat in deep_pilot_stats:
            stat_spinbox, recharge_spinbox, decharge_spinbox, attribute = stat
            deep_stat = ship.get_statistic(pilot.get("statistics"), attribute)
            deep_stat = self.parse_deep_stat(deep_stat)
            stat_spinbox.setValue(deep_stat[attribute])
            recharge_spinbox.setValue(deep_stat["recharge"])
            decharge_spinbox.setValue(deep_stat["decharge"])

        parse_actions(
            self.ui.pilot_actions_line_edit,
            self.ui.pilot_colors_line_edit,
            pilot.get("actions")
        )

        self.ui.pilot_upgrade_slots_line_edit.setText(
            arr_to_comma_separated_list(pilot.get("upgrade_slots"))
        )

        self.ui.traits_line_edit.setText(
            arr_to_comma_separated_list(pilot.get("keywords"))
        )

    def parse_deep_stat(self, stat: dict) -> dict:
        """
        this is used for pilot statistics as they have null values.
        Will set any null to -1
        """
        for key in stat.keys():
            val = stat[key]
            if val is None:
                stat[key] = -1
        return stat

    def write_data(self):

        with open(self.data_filepath, "w", encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

        logging.info(f"Data successfully written to {self.data_filepath}")

    def handle_ok_pressed(self):
        if not self.valid_entry:
            self.show()
            return
        insert_flag = self.insert_new_entry()
        if insert_flag:
            self.show()
            return
        self.write_data()
        self.update_signal.emit()

    def handle_close_pressed(self):
        self.form_closed_signal.emit()
