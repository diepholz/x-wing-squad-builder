import json

from typing import List, Optional

from .faction import Faction
from .ship import Ship

from ..utils import prettify_name

from collections import defaultdict


class XWing:

    def __init__(self, data):
        self.data = data

    @property
    def faction_names(self) -> List[str]:
        return [faction["name"] for faction in self.data["factions"]]

    @property
    def upgrades(self):
        return self.data["upgrades"]

    def get_faction(self, faction_name: str) -> Optional[Faction]:
        for i, test_faction in enumerate(self.data["factions"]):
            if faction_name == test_faction["name"]:
                return Faction(test_faction)
        return None

    def get_ship(self, faction_name: str, ship_name: str) -> Optional[Ship]:
        faction = self.get_faction(faction_name)
        ship = faction.get_ship(ship_name)
        return ship

    @classmethod
    def launch_xwing_data(cls, data_path: str):
        with open(data_path) as file:
            data = json.load(file)
        return cls(data)

    def get_pilot(self, faction_name: str, ship_name: str, pilot_name: str):
        faction = self.get_faction(faction_name)
        ship = faction.get_ship(ship_name)
        return ship.get_pilot_data(pilot_name)

    @property
    def faction_ship_pilot_dict(self):
        d = defaultdict(lambda: defaultdict(list))
        for faction_name in self.faction_names:
            faction = self.get_faction(faction_name)
            for ship in faction.faction_ships:
                for pilot_name in ship.pilot_names_for_gui:
                    d[faction_name][ship.ship_name].append(pilot_name)
        return d
