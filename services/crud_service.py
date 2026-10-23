"""Business rules for player CRUD."""
import sqlite3

from database.repositories import player_repo
from models.player import Player
from utils.exceptions import (AppError, DuplicateError, InUseError,
                              NotFoundError, ValidationError)
from utils.logger import get_logger
from utils.validators import validate_player
from database.repositories import team_repo

log = get_logger(__name__)


def create_player(p: Player) -> int:
    p = validate_player(p)
    if player_repo.find_duplicate(p.full_name, p.country):
        raise DuplicateError(f"{p.full_name} ({p.country}) already exists.")
    try:
        return player_repo.insert(p)
    except sqlite3.IntegrityError as exc:  # e.g. bad team_id FK
        log.error("Insert failed: %s", exc)
        raise ValidationError("Invalid team or data conflict.") from exc


def get_player(player_id: int) -> Player:
    p = player_repo.get_by_id(player_id)
    if p is None:
        raise NotFoundError(f"Player {player_id} not found.")
    return p


def list_players(search: str = "", country: str = "", page: int = 1,
                 page_size: int = 50) -> list[Player]:
    return player_repo.list_players(search, country, page_size,
                                    (max(page, 1) - 1) * page_size)


def update_player(player_id: int, changes: dict) -> None:
    current = get_player(player_id)  # raises NotFoundError
    merged = Player(**{**current.__dict__, **changes})
    validate_player(merged)
    if player_repo.find_duplicate(merged.full_name, merged.country,
                                  exclude_id=player_id):
        raise DuplicateError("Another player with that name and country exists.")
    try:
        player_repo.update(player_id, {
            k: getattr(merged, k) for k in changes})
    except sqlite3.IntegrityError as exc:
        raise ValidationError("Invalid team or data conflict.") from exc


def delete_player(player_id: int) -> None:
    get_player(player_id)  # raises NotFoundError
    if player_repo.is_referenced(player_id):
        raise InUseError(
            "Player has scorecard/fielding history and cannot be deleted.")
    player_repo.delete(player_id)

def list_teams() -> list[tuple[int, str]]:
    return team_repo.list_teams()