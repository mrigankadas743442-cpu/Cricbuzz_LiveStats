"""Input validation for player data."""
from datetime import date, datetime

from models.player import Player
from utils.exceptions import ValidationError

ROLES = {"Batsman", "Bowler", "All-rounder", "Wicket-keeper"}


def validate_player(p: Player) -> Player:
    """Clean and validate a Player; raise ValidationError if invalid."""
    p.full_name = (p.full_name or "").strip()
    p.country = (p.country or "").strip()

    if not 2 <= len(p.full_name) <= 100:
        raise ValidationError("Name must be 2-100 characters.")
    if not p.country:
        raise ValidationError("Country is required.")
    if p.playing_role and p.playing_role not in ROLES:
        raise ValidationError(f"Role must be one of: {', '.join(sorted(ROLES))}.")
    if p.date_of_birth:
        try:
            dob = datetime.strptime(p.date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Date of birth must be YYYY-MM-DD.")
        if dob >= date.today():
            raise ValidationError("Date of birth must be in the past.")
    return p