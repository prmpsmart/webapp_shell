"""The typed arguments of a native function: what a page may send, and what is refused in plain words."""

from dataclasses import dataclass, field

import pytest

from webapp_shell import NativeError
from webapp_shell.native.arguments import Arguments, wire_name


@dataclass(frozen=True)
class Inner:
    first_name: str
    age: int = 0


@dataclass(frozen=True)
class Everything:
    text: str
    count: int = 1
    ratio: float = 0.5
    flag: bool = False
    maybe: str | None = None
    many: list[int] = field(default_factory=list[int])
    pair: tuple[str, ...] = ()
    inner: Inner | None = None


def parse(*values):
    return Arguments(Everything).parse(list(values))


def refused(*values) -> str:
    with pytest.raises(NativeError) as error:
        parse(*values)
    return str(error.value)


def test_positional_values_fill_the_fields_in_order_and_defaults_may_be_left_out():
    assert parse("a") == Everything("a")
    assert parse("a", 2, 3, True, "m", [1, 2], ["x", "y"], {"firstName": "Ada"}) == Everything(
        "a", 2, 3.0, True, "m", [1, 2], ("x", "y"), Inner("Ada")
    )


def test_an_integer_is_a_number_but_a_boolean_is_neither_a_number_nor_text():
    assert parse("a", 1, 2).ratio == 2.0 and isinstance(parse("a", 1, 2).ratio, float)
    assert refused("a", True) == '"count" must be a whole number'
    assert refused("a", 1, True) == '"ratio" must be a number'
    assert refused(True) == '"text" must be text'


def test_nothing_is_converted_silently():
    assert refused(5) == '"text" must be text'
    assert refused("a", "1") == '"count" must be a whole number'
    assert refused("a", 1.5) == '"count" must be a whole number'
    assert refused("a", 1, 1, 1) == '"flag" must be true or false'


def test_none_is_accepted_only_where_the_type_says_so():
    assert parse("a", 1, 1, False, None).maybe is None
    assert refused(None) == '"text" must be text'


def test_lists_are_checked_item_by_item():
    assert refused("a", 1, 1, False, None, [1, "x"]) == '"many[1]" must be a whole number'
    assert refused("a", 1, 1, False, None, "not a list") == '"many" must be a list'


def test_objects_use_camel_case_keys_and_refuse_unknown_or_missing_ones():
    base = ("a", 1, 1, False, None, [], [])
    assert refused(*base, {"first_name": "Ada"}) == '"inner" has no field "first_name"'
    assert refused(*base, {"age": 3}) == '"inner" needs the field "firstName"'
    assert refused(*base, "Ada") == '"inner" must be an object'


def test_too_few_and_too_many_arguments():
    assert refused() == 'missing argument "text"'
    assert refused(*range(10)) == "too many arguments"


def test_a_function_that_cannot_be_declared_is_refused_when_it_is_declared():
    @dataclass(frozen=True)
    class Bad:
        value: dict[str, int]

    @dataclass(frozen=True)
    class AlsoBad:
        value: int | str

    for shape in (Bad, AlsoBad):
        with pytest.raises(TypeError):
            Arguments(shape)
    with pytest.raises(TypeError):
        Arguments(dict)  # not a dataclass


def test_the_wire_name_of_a_field_is_camel_case():
    assert [wire_name(name) for name in ("start", "glow_a", "a_b_c")] == ["start", "glowA", "aBC"]
