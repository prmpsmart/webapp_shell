"""Turns the list of JSON values a page sent into the typed arguments of a native function.

A function declares its arguments as a dataclass; the page's positional arguments fill the fields in order, and a
field with a default may be left out. Supported field types: `str`, `int`, `float` (an integer is accepted),
`bool`, `X | None`, `list[X]`, `tuple[X, ...]` and another dataclass (sent as an object with camelCase keys, so the
field `glow_a` is `glowA` on the wire). Nothing is converted silently: a number where text is expected is refused.
"""

import dataclasses
import types
from collections.abc import Callable
from typing import Union, get_args, get_origin, get_type_hints

from ..json_types import JsonValue
from .errors import NativeError


def wire_name(field_name: str) -> str:
    """`glow_a` -> `glowA`: the name a field has on the wire."""
    head, *rest = field_name.split("_")
    return head + "".join(part.capitalize() for part in rest)


def _has_default(field: dataclasses.Field[object]) -> bool:
    return field.default is not dataclasses.MISSING or field.default_factory is not dataclasses.MISSING


def _is_union(hint: object) -> bool:
    return get_origin(hint) in (Union, types.UnionType)


def _check_supported(hint: object, where: str) -> None:
    """Fails when a function is declared, not when a page first calls it."""
    if hint is str or hint is int or hint is float or hint is bool:
        return
    if _is_union(hint):
        members = [member for member in get_args(hint) if member is not type(None)]
        if len(members) != 1:
            raise TypeError(f"{where}: only `X | None` unions are supported")
        return _check_supported(members[0], where)
    origin = get_origin(hint)
    if origin is list:
        return _check_supported(get_args(hint)[0], where)
    if origin is tuple:
        item, ellipsis = get_args(hint)
        if ellipsis is not Ellipsis:
            raise TypeError(f"{where}: only `tuple[X, ...]` is supported")
        return _check_supported(item, where)
    if isinstance(hint, type) and dataclasses.is_dataclass(hint):
        for field_name, field_hint in get_type_hints(hint).items():
            _check_supported(field_hint, f"{where}.{field_name}")
        return
    raise TypeError(f"{where}: the type {hint!r} cannot be an argument of a native function")


def _convert(value: JsonValue, hint: object, label: str) -> object:
    if _is_union(hint):
        if value is None:
            return None
        (member,) = (member for member in get_args(hint) if member is not type(None))
        return _convert(value, member, label)
    if hint is str:
        if isinstance(value, str):
            return value
        raise NativeError(f'"{label}" must be text')
    if hint is bool:
        if isinstance(value, bool):
            return value
        raise NativeError(f'"{label}" must be true or false')
    if hint is int:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        raise NativeError(f'"{label}" must be a whole number')
    if hint is float:
        if isinstance(value, int | float) and not isinstance(value, bool):
            return float(value)
        raise NativeError(f'"{label}" must be a number')
    origin = get_origin(hint)
    if origin in (list, tuple):
        if not isinstance(value, list):
            raise NativeError(f'"{label}" must be a list')
        item = get_args(hint)[0]
        items = [_convert(entry, item, f"{label}[{index}]") for index, entry in enumerate(value)]
        return items if origin is list else tuple(items)
    if isinstance(hint, type) and dataclasses.is_dataclass(hint):
        return _convert_object(value, hint, label)
    raise AssertionError(f"unsupported type {hint!r}")  # _check_supported refused it at declaration


def _convert_object(value: JsonValue, shape: type, label: str) -> object:
    if not isinstance(value, dict):
        raise NativeError(f'"{label}" must be an object')
    hints = get_type_hints(shape)
    fields = {wire_name(field.name): field for field in dataclasses.fields(shape)}
    unknown = sorted(set(value) - set(fields))
    if unknown:
        raise NativeError(f'"{label}" has no field "{unknown[0]}"')
    values: dict[str, object] = {}
    for name, field in fields.items():
        if name in value:
            values[field.name] = _convert(value[name], hints[field.name], f"{label}.{name}")
        elif not _has_default(field):
            raise NativeError(f'"{label}" needs the field "{name}"')
    build: Callable[..., object] = shape
    return build(**values)


class Arguments[A]:
    """The arguments of one native function, declared as a dataclass."""

    def __init__(self, shape: type[A]):
        if not dataclasses.is_dataclass(shape):
            raise TypeError(f"the arguments of a native function are a dataclass, not {shape!r}")
        self._shape = shape
        self._hints = get_type_hints(shape)
        self._fields = dataclasses.fields(shape)
        for field in self._fields:
            _check_supported(self._hints[field.name], f"{shape.__name__}.{field.name}")

    def parse(self, values: list[JsonValue]) -> A:
        if len(values) > len(self._fields):
            raise NativeError("too many arguments")
        parsed: dict[str, object] = {}
        for index, field in enumerate(self._fields):
            label = wire_name(field.name)
            if index < len(values):
                parsed[field.name] = _convert(values[index], self._hints[field.name], label)
            elif not _has_default(field):
                raise NativeError(f'missing argument "{label}"')
        build: Callable[..., A] = self._shape
        return build(**parsed)
