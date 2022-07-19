import pytest

from x_wing_squad_builder.model.upgrade import Upgrades
from x_wing_squad_builder.model.xwing import XWing
from x_wing_squad_builder.model.pilot_equip import PilotEquip

from x_wing_squad_builder.model.upgrade_filters import (upgrade_slot_filter, name_filter,
                                                        multiple_name_filter, actions_filter,
                                                        statistics_filter_simple, statistics_filter_adv,
                                                        limit_filter)

from .filter_tests import FILTER_TESTS

UPGRADE_NAME_1 = "pikachu"
UPGRADE_1 = {
    "name": UPGRADE_NAME_1,
    "cost": 1337
}
UPGRADE_NAME_2 = "Geforce"
UPGRADE_2 = {
    "name": UPGRADE_NAME_2,
    "cost": 9999
}


def inject_upgrade_values(fake_upgrades: Upgrades, key: str, vals: list):
    for i, upgrade in enumerate(fake_upgrades):
        upgrade[key] = vals[i]


def inject_upgrade_restrictions(fake_upgrades: Upgrades, restriction: str, vals: list):
    for i, upgrade in enumerate(fake_upgrades):
        upgrade["restrictions"][restriction] = vals[i]


@pytest.fixture(scope="function")
def fake_upgrades():
    return Upgrades([UPGRADE_1, UPGRADE_2])


def test_upgrades_list(upgrades: Upgrades, definition_data):
    assert upgrades.upgrades_list == definition_data['upgrades']


def test_get_upgrade_name(fake_upgrades: Upgrades):
    upgrade = fake_upgrades.get_upgrade(UPGRADE_NAME_1)
    assert fake_upgrades.get_upgrade_name(upgrade) == UPGRADE_NAME_1

    upgrade_name = fake_upgrades.get_upgrade_name({"test": "bogus"})
    assert upgrade_name is None


def test_get_upgrade(fake_upgrades: Upgrades):
    upgrade = fake_upgrades.get_upgrade("snap shot")
    assert upgrade is None

    upgrade = fake_upgrades.get_upgrade(UPGRADE_NAME_1)
    assert upgrade == UPGRADE_1


def test_upgrade_slot_filter():
    upgrade_slots = ["missile", "payload"]
    pilot_slots = ["missile", "missile", "payload", "sensor"]
    assert upgrade_slot_filter(upgrade_slots, pilot_slots) is True

    upgrade_slots = ["missile", "crazy"]
    assert upgrade_slot_filter(upgrade_slots, pilot_slots) is False

    upgrade_slots = ["payload", "payload"]
    assert upgrade_slot_filter(upgrade_slots, pilot_slots) is False


def test_name_filter():
    pilot_faction = "the new world order"
    restriction = []

    assert name_filter(restriction, pilot_faction) is True

    restriction = ["all", "these", "are", "valid"]
    assert name_filter(restriction, pilot_faction) is False

    restriction = ["all", "these", "are", "valid", "the new world order"]
    assert name_filter(restriction, pilot_faction) is True


def test_multiple_name_filter():
    restriction = ["forward", "backward"]
    tests = ["sideways", "around"]

    assert multiple_name_filter(restriction, tests) is False

    tests = ["forward", "around"]
    assert multiple_name_filter(restriction, tests) is True


def test_actions_filter():
    restrictions = [
        {
            'action': 'pelvic_thrust',
            'color': 'mauve',
            'action_link': 'cheer',
            'color_link': None
        },
        {
            'action': 'pelvic_thrust',
            'color': 'tan',
            'action_link': 'cheer',
            'color_link': None
        }
    ]
    pilot_actions = [
        {
            'action': 'dummy test',
            'color': 'dont matta',
            'action_link': None,
            'color_link': None
        },
        {
            'action': 'pelvic_thrust',
            'color': 'tan',
            'action_link': 'cheer',
            'color_link': None
        }
    ]
    assert actions_filter(restrictions, pilot_actions) is True

    pilot_actions = [
        {
            'action': 'dummy test',
            'color': 'dont matta',
            'action_link': None,
            'color_link': None
        }
    ]

    assert actions_filter(restrictions, pilot_actions) is False
    assert actions_filter([], pilot_actions) is True


@pytest.mark.parametrize(
    "stat_low, stat_high, test_val, expected", [
        pytest.param(1, 6, 5, True, id="hull test in defined range"),
        pytest.param(None, None, 5, True, id="hull test in undefined range"),
        pytest.param(None, None, None, True, id="no restriction and no defined stat"),
        pytest.param(None, 6, 5, True, id="stat low is None, stat high has val"),
        pytest.param(None, 6, 7, False, id="stat low is None, stat high has val"),
        pytest.param(6, None, 5, False, id="hull test not in defined range"),
    ]
)
def test_simple_statistics_filter(stat_low, stat_high, test_val, expected):
    restriction = {
        'low': stat_low,
        'high': stat_high
    }
    statistic = {
        'hull': test_val
    }
    assert statistics_filter_simple(restriction, statistic) is expected


@pytest.mark.parametrize(
    "stat_low, stat_high, recharge_low, recharge_high, decharge_low, decharge_high, test_stat, test_recharge, test_decharge, expected", [
        pytest.param(1, 6, None, None, None, None, 5, None, None, True),
        pytest.param(None, None, None, 6, 2, 5, 5, 2, 3, True),
        pytest.param(1, 6, None, None, None, None, None, None, None, False),
        pytest.param(None, None, None, None, 2, 5, None, None, None, False),
        pytest.param(None, None, None, 6, 2, 5, None, 7, 3, False),
    ]
)
def test_adv_statistics_filter(stat_low, stat_high, recharge_low, recharge_high, decharge_low, decharge_high, test_stat, test_recharge, test_decharge, expected):
    stats = ['super_stat', 'recharge', 'decharge']
    restriction = {
        stats[0]: {
            'low': stat_low,
            'high': stat_high
        },
        stats[1]: {
            'low': recharge_low,
            'high': recharge_high
        },
        stats[2]: {
            'low': decharge_low,
            'high': decharge_high
        }
    }
    test_statistic = {
        stats[0]: test_stat,
        stats[1]: test_recharge,
        stats[2]: test_decharge
    }
    assert statistics_filter_adv(restriction, test_statistic) is expected


@pytest.mark.parametrize(
    "limit_name, limit, arr, expected", [
        pytest.param('heyo', 0, ['heyo', 'nice', 'heyo'], True),
        pytest.param('heyo', 1, ['heyo', 'nice', 'heyo'], False),
        pytest.param('heyo', 2, ['heyo', 'nice', 'heyo'], False),
        pytest.param('nice', 2, ['heyo', 'nice', 'heyo'], True),
        pytest.param('nice', 2, [], True),
    ]
)
def test_limit_filter(limit_name, limit, arr, expected):
    restriction = {limit_name: limit}
    assert limit_filter(restriction, arr) is expected


@pytest.mark.parametrize(
    "faction_name, ship_name, pilot_name", [
        pytest.param("galactic empire", "lambda-class t-4a shuttle", "omicron group pilot"),
    ]
)
def test_filtered_upgrades_by_pilot(xwing: XWing, upgrades: Upgrades, faction_name, ship_name, pilot_name):
    expected = FILTER_TESTS[faction_name][ship_name][pilot_name]
    ship = xwing.get_ship(faction_name, ship_name)
    pilot = ship.get_pilot_data(pilot_name)
    pilot_equip = PilotEquip(ship, pilot)
    pilot_equip.filtered_upgrades = upgrades.filtered_upgrades_by_pilot(pilot_equip)
    for upgrade in pilot_equip.filtered_upgrades:
        assert upgrade['name'] in expected
        expected.pop(expected.index(upgrade['name']))
    assert len(expected) == 0