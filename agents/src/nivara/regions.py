"""NIVARA market focus — Bangalore only (expandable later)."""

DEFAULT_REGION = "Bangalore"
DEFAULT_STATE = "Karnataka"

# Priority micro-markets and corridors
BANGALORE_CORRIDORS = [
    "Whitefield",
    "Sarjapur Road",
    "Electronic City",
    "HSR Layout",
    "Koramangala",
    "Hebbal",
    "Yelahanka",
    "Devanahalli / North Bangalore",
    "Bannerghatta Road",
    "Marathahalli",
]

CORRIDORS: dict[str, list[str]] = {
    DEFAULT_REGION: BANGALORE_CORRIDORS,
}


def market_scope(region: str | None = None) -> str:
    """Human-readable market scope for prompts."""
    r = region or DEFAULT_REGION
    return f"{r}, {DEFAULT_STATE}"
