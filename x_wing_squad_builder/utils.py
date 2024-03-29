import json
import re
from _ctypes import PyObj_FromPtr
import argparse

from typing import List

from PIL import Image
import numpy as np

from PySide6.QtGui import QImage


def change_action_image_color(image_path, color) -> QImage:
    im = Image.open(image_path)
    im_arr = np.array(im).astype('uint8')
    if color == "red":
        im_arr[im_arr[:, :, 0] > 0, 1] = 0
        im_arr[im_arr[:, :, 0] > 0, 2] = 0
    elif color == "purple":
        im_arr[im_arr[:, :, 0] > 0, 1] = 0
    elif color == "green":
        im_arr[im_arr[:, :, 0] > 0, 0] = 0
        im_arr[im_arr[:, :, 0] > 0, 2] = 0
    return Image.fromarray(im_arr).toqimage()


def contains_number(text):
    return any([char.isnumeric() for char in text])


def process_part(part: str, symbol: str):
    sub_parts = part.split(symbol)
    sub_processed = []
    for sub_part in sub_parts:
        if contains_number(sub_part):
            sub_part = sub_part.upper()
        elif len(sub_part) <= 3:
            sub_part = sub_part.lower()
            if sub_part in ["odd", "obi", "wan", "axe", "red", "zeb", "bo", "mag"]:
                sub_part = sub_part.capitalize()
            else:
                sub_part = sub_part.upper()
        elif len(sub_part) > 3:
            sub_part = sub_part.capitalize()
        sub_processed.append(sub_part)
    part = symbol.join(sub_processed)
    return part


def prettify_name(name: str) -> str:
    """Takes a lowercase string of a name and capitalizes it."""
    text = gui_text_decode(name)
    parts = text.split()
    processed = []
    for part in parts:
        if "-" in part:
            part = process_part(part, "-")
        elif "(" in part:
            part = process_part(part, "(")
        elif "/" in part:
            part = process_part(part, "/")
        elif "\"" in part:
            part = process_part(part, "\"")
        else:
            part = part.capitalize()
        processed.append(part)
    return " ".join(processed)


def gui_text_encode(text: str):
    """In order to work with the Windows File System, we cannot have certain characters in file names.  This is the workaround."""
    text = text.lower().replace("/", "%").replace("\"", "^")
    return text


def gui_text_decode(text: str):
    text = text.lower().replace("%", "/").replace("^", "\"")
    return text


def get_pilot_name_from_list_item_text(text: str):
    """returns encoded version of highlighted pilot name"""
    pilot_name = gui_text_encode(" ".join(text.lower().split()[1:-1]))
    return pilot_name


def get_upgrade_slot_from_list_item_text(text: str):
    """returns lowercase version of the text selected"""
    upgrade_name = text.lower()
    return upgrade_name


def get_upgrade_name_from_list_item_text(text: str):
    """returns encoded version of selected upgrade name"""
    upgrade_name = gui_text_encode(" ".join(text.lower().split()[:-1]))
    return upgrade_name


def prettify_definition_form_entry(values: str) -> List[str]:
    """Takes a list of values separated by a comma, and returns a list of the values
    in lowercase with white space stripped from each side.

    :param values: string of values from the definition form
    :type values: str
    :return: list of values cleaned up.
    :rtype: List[str]
    """
    val_split = values.split(',')
    return [val.lower().strip() for val in val_split]


def create_log_level_parser():
    class NoAction(argparse.Action):
        def __init__(self, **kwargs):
            kwargs.setdefault('nargs', 0)
            super(NoAction, self).__init__(**kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            pass
    choices = {
        'debug': 'Detailed information, typically of interest only when diagnosing problems.',
        'info': 'Confirmation that things are working as expected.',
        'warning': 'An indication that something unexpected happened.  The software is still working as expected.',
        'error': 'Due to a more serious problem, the software has not been able to perform some function.',
        'critical': 'A serious error, indicating that the program itself may be unable to continue running.'
    }
    parser = argparse.ArgumentParser()
    parser.register('action', 'none', NoAction)
    parser.add_argument(
        '-log',
        '--log',
        choices=list(choices.keys()),
        default='info',
        help=(
            'Provide logging level. \n'
            'Example: --log debug \n'
        )
    )
    group = parser.add_argument_group(title='valid log level options')
    for key, value in choices.items():
        group.add_argument(key, help=value, action='none')

    return parser


class NoIndent(object):
    """ Value wrapper. """

    def __init__(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError('Only lists and tuples can be wrapped')
        self.value = value


class PrettyJSONEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'  # Unique string pattern of NoIndent object ids.
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))  # compile(r'@@(\d+)@@')

    def __init__(self, **kwargs):
        # Keyword arguments to ignore when encoding NoIndent wrapped values.
        ignore = {'cls', 'indent'}

        # Save copy of any keyword argument values needed for use here.
        self._kwargs = {k: v for k, v in kwargs.items() if k not in ignore}
        super(PrettyJSONEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, NoIndent)
                else super(PrettyJSONEncoder, self).default(obj))

    def iterencode(self, obj, **kwargs):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.

        # Replace any marked-up NoIndent wrapped values in the JSON repr
        # with the json.dumps() of the corresponding wrapped Python object.
        for encoded in super(PrettyJSONEncoder, self).iterencode(obj, **kwargs):
            match = self.regex.search(encoded)
            if match:
                id = int(match.group(1))
                no_indent = PyObj_FromPtr(id)
                json_repr = json.dumps(no_indent.value, **self._kwargs)
                # Replace the matched id string with json formatted representation
                # of the corresponding Python object.
                encoded = encoded.replace(
                    '"{}"'.format(format_spec.format(id)), json_repr)

            yield encoded
