# -*- coding: utf-8 -*-
import collections
import dateutil.parser
import re


RE_ISO8601_DATETIME = re.compile(
    r"(^\d{4}-\d{2}-\d{2})?((^|T)\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[\+|-]\d{2}:\d{2})?)?$"
)
RE_PREFIX_UNDERSCORES = re.compile(r"^(_+)")
RE_SUFFIX_UNDERSCORES = re.compile(r"(_+)$")
RE_SNAKECASE_FIRST_CAP = re.compile(r"(.)([A-Z][a-z]+)")
RE_SNAKECASE_ALL_CAP = re.compile(r"([a-z0-9])([A-Z])")


def is_iso8601_datetime(value):
    """Returns whether a string matches a datetime in ISO 8601 format."""
    return isinstance(value, basestring) and value != "" and RE_ISO8601_DATETIME.match(value)


def dict_walk(data, key_callbacks=None, value_callbacks=None):
    """Walks recursively through a dictionary and apply callbacks on keys and/or values."""
    key_callbacks = key_callbacks or []
    value_callbacks = value_callbacks or []

    def exec_callbacks(value, key=None):
        """Loop over callbacks and execute them."""
        for callback in value_callbacks:
            value = callback(value)

        if key is not None:
            for callback in key_callbacks:
                key = callback(key)
            return key, value

        return value

    # Dictionary.
    if isinstance(data, collections.Mapping):
        new_data = {}
        for key, value in data.items():
            key, value = exec_callbacks(value, key)
            new_data[key] = dict_walk(value, key_callbacks, value_callbacks)

    # Iterable and not string.
    elif hasattr(data, "__iter__") and not isinstance(data, str):
        new_data = []
        for value in data:
            new_data.append(dict_walk(value, key_callbacks, value_callbacks))

    # Other cases.
    else:
        new_data = exec_callbacks(data)

    return new_data


def dict_walk_python_to_json(data):
    """Converts a dictionary from Python to JSON conventions."""
    key_callbacks = [to_camel_case]
    value_callbacks = [datetime_to_isoformat]
    return dict_walk(data, key_callbacks=key_callbacks, value_callbacks=value_callbacks)


def dict_walk_json_to_python(data):
    """Converts a dictionary from JSON to Python conventions."""
    key_callbacks = [to_snake_case]
    value_callbacks = [isoformat_to_datetime]
    return dict_walk(data, key_callbacks=key_callbacks, value_callbacks=value_callbacks)


def isoformat_to_datetime(value):
    """Converts a string representing a date (and/or) time to a Python datetime."""
    if not is_iso8601_datetime(value):
        return value

    new_value = dateutil.parser.parse(value)
    return new_value


def datetime_to_isoformat(value):
    """Converts Python date/time objects to ISO 8601 format."""
    if hasattr(value, "isoformat") and callable(value.isoformat):
        return value.isoformat()
    return value


def to_camel_case(value, upper=False):
    """Converts a value to camelCase (UpperCamelCase) format."""
    def pre_suf_fix(regex):
        v = re.search(regex, value)
        return v.group(0) if v else u""

    new_value = u"".join(s for s in value.replace(u"_", u" ").title() if not s.isspace())
    if not upper:
        new_value = new_value[0].lower() + new_value[1:]
    return pre_suf_fix(RE_PREFIX_UNDERSCORES) + new_value + pre_suf_fix(RE_SUFFIX_UNDERSCORES)


def to_upper_camel_case(value):
    """Converts a value to UpperCamelCase format."""
    return to_camel_case(value, upper=True)


def to_snake_case(value):
    """Converts a value to snake_case format."""
    if not value:
        return value

    new_value = RE_SNAKECASE_FIRST_CAP.sub(r"\1_\2", value)
    new_value = RE_SNAKECASE_ALL_CAP.sub(r"\1_\2", new_value).lower()
    return new_value
