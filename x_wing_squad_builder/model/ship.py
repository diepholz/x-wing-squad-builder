from typing import List, Tuple, Optional, Union, Dict
from ..utils import prettify_name, gui_text_encode



class Ship:
    def __init__(self, faction_name: str, ship_data: dict):
        self.__faction_name = faction_name
        self.__ship_data = ship_data

    def __repr__(self):
        return f"Ship(ship_name = {self.ship_name}, faction_name = {self.faction_name})"

    @property
    def ship_name(self) -> str:
        return self.__ship_data['name']

    @property
    def ship_name_encoded(self) -> str:
        return gui_text_encode(self.ship_name)

    @property
    def faction_name(self) -> str:
        return self.__faction_name

    @property
    def base(self) -> str:
        return self.ship_data.get('base')

    @property
    def pilots(self):
        return self.ship_data.get('pilots')

    @property
    def pilot_names(self) -> List[str]:
        return [pilot["name"] for pilot in self.pilots]

    @property
    def pilot_names_cost_initiative(self):
        arr_generics = []
        arr_aces = []
        for pilot in self.pilots:
            pilot_tuple = (pilot["initiative"], pilot["cost"], pilot["name"])
            if pilot.get("unique", False):
                arr_aces.append(pilot_tuple)
            else:
                arr_generics.append(pilot_tuple)
        arr_generics = sorted(arr_generics, key=lambda x: (x[0], x[1], x[2]))
        arr_aces = sorted(arr_aces, key=lambda x: (x[0], x[1], x[2]))
        arr = arr_generics + arr_aces
        return arr

    @property
    def pilot_names_for_gui(self):
        return [f"({init}) {prettify_name(name)} ({cost})" for init, cost, name in self.pilot_names_cost_initiative]

    @property
    def initiative_list(self) -> List[int]:
        return list(sorted((int(pilot["initiative"]) for pilot in self.pilots)))

    @property
    def point_list(self) -> List[int]:
        return [int(pilot["cost"]) for pilot in self.pilots]

    @property
    def point_range(self) -> Tuple[int]:
        points = self.point_list
        return (min(points), max(points))

    @property
    def statistics(self):
        return self.ship_data['statistics']

    @property
    def actions(self):
        return self.ship_data['actions']

    @property
    def upgrade_slots(self) -> List[str]:
        return self.ship_data['upgrade_slots']

    @property
    def ship_data(self):
        return self.__ship_data

    @staticmethod
    def get_statistic(statistics: dict, attribute: str) -> Union[List, Dict, int, None]:
        """Returns the value for the given statistic attribute from the flat statistics dict."""
        return statistics.get(attribute)

    def get_pilot_data(self, pilot_name: str) -> Optional[dict]:
        for pilot in self.pilots:
            if pilot["name"] == pilot_name:
                return pilot
        return None

    def get_pilot_actions(self, pilot_name: str):
        pilot = self.get_pilot_data(pilot_name)
        return pilot["actions"]
