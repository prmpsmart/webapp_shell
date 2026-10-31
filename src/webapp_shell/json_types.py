"""What JSON can carry. Everything that crosses between the page and Python is one of these, never a bare `dict`."""

type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]
