"""The range of the page zoom, for every shell (no toolkit is imported here, so a Qt-only build can read it)."""

MIN_ZOOM = 0.5
MAX_ZOOM = 3.0


def clamp(value: float) -> float:
    """A usable zoom factor: the value, kept between the smallest and the largest the shells allow."""
    return min(MAX_ZOOM, max(MIN_ZOOM, value))
