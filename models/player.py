"""Player data model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Player:
    full_name: str
    country: str
    playing_role: Optional[str] = None
    batting_style: Optional[str] = None
    bowling_style: Optional[str] = None
    date_of_birth: Optional[str] = None  # ISO: YYYY-MM-DD
    team_id: Optional[int] = None
    player_id: Optional[int] = None