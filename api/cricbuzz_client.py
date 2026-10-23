
"""Client for the Cricbuzz Cricket API (RapidAPI)."""

import time
from typing import Any

import requests

import config
from utils.logger import get_logger

log = get_logger(__name__)


class CricbuzzAPIError(Exception):
    """Raised when a Cricbuzz API request fails."""


class CricbuzzClient:
    """Reusable client for Cricbuzz API endpoints."""

    RETRY_STATUS = {500, 502, 503, 504}
    RATE_LIMIT_STATUS = 429

    def __init__(self) -> None:
        """Initialize the API session using configuration settings."""
        if not getattr(config, "RAPIDAPI_KEY", None):
            raise CricbuzzAPIError(
                "RAPIDAPI_KEY is not set in your .env file."
            )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "x-rapidapi-key": config.RAPIDAPI_KEY,
                "x-rapidapi-host": config.RAPIDAPI_HOST,
                "Accept": "application/json",
            }
        )

    # --------------------------------------------------
    # Core HTTP request
    # --------------------------------------------------

    def _get(
        self,
        path: str,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Perform a GET request with bounded retries."""
        url = f"{config.BASE_URL.rstrip('/')}/{path.lstrip('/')}"
        max_retries = max(1, int(getattr(config, "MAX_RETRIES", 3)))
        timeout = getattr(config, "REQUEST_TIMEOUT", 15)

        for attempt in range(1, max_retries + 1):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=timeout,
                )

                # Do not retry HTTP 429: it can mean the API quota
                # has been exhausted, and retries waste requests/time.
                if response.status_code == self.RATE_LIMIT_STATUS:
                    retry_after = response.headers.get("Retry-After")
                    detail = response.text[:300]

                    message = (
                        f"Cricbuzz API rate limit reached for {path}. "
                        "Wait before trying again."
                    )

                    if retry_after:
                        message += f" Retry-After: {retry_after}."

                    if detail:
                        message += f" Details: {detail}"

                    raise CricbuzzAPIError(message)

                # Retry only transient server errors.
                if response.status_code in self.RETRY_STATUS:
                    if attempt == max_retries:
                        response.raise_for_status()

                    log.warning(
                        "HTTP %s on attempt %d/%d for %s",
                        response.status_code,
                        attempt,
                        max_retries,
                        path,
                    )
                    time.sleep(min(2 ** attempt, 8))
                    continue

                # Other 4xx errors should not be retried.
                response.raise_for_status()

                try:
                    data = response.json()
                except ValueError as exc:
                    raise CricbuzzAPIError(
                        f"Invalid JSON returned by {path}."
                    ) from exc

                if not isinstance(data, dict):
                    raise CricbuzzAPIError(
                        f"Unexpected JSON response from {path}: "
                        "expected a JSON object."
                    )

                return data

            except CricbuzzAPIError:
                raise

            except requests.HTTPError as exc:
                status = (
                    exc.response.status_code
                    if exc.response is not None
                    else "unknown"
                )

                detail = ""
                if exc.response is not None:
                    detail = exc.response.text[:300]

                log.error(
                    "HTTP request failed for %s (status %s): %s",
                    path,
                    status,
                    detail or str(exc),
                )

                raise CricbuzzAPIError(
                    f"Request failed for {path}. "
                    f"HTTP status: {status}. "
                    f"Details: {detail or str(exc)}"
                ) from exc

            except (requests.ConnectionError, requests.Timeout) as exc:
                log.warning(
                    "Connection error on attempt %d/%d for %s: %s",
                    attempt,
                    max_retries,
                    path,
                    exc,
                )

                if attempt == max_retries:
                    raise CricbuzzAPIError(
                        f"Connection failed for {path}: {exc}"
                    ) from exc

                time.sleep(min(2 ** attempt, 8))

            except requests.RequestException as exc:
                raise CricbuzzAPIError(
                    f"Network request failed for {path}: {exc}"
                ) from exc

        raise CricbuzzAPIError(
            f"Request failed for {path} after all attempts."
        )

    # --------------------------------------------------
    # Match endpoints
    # --------------------------------------------------

    def live_matches(self) -> dict[str, Any]:
        """Fetch currently live matches."""
        return self._get("/matches/v1/live")

    def recent_matches(self) -> dict[str, Any]:
        """Fetch recently completed matches."""
        return self._get("/matches/v1/recent")

    def scorecard(self, match_id: int | str) -> dict[str, Any]:
        """Fetch the scorecard for a specific match."""
        if str(match_id).strip() == "":
            raise ValueError("match_id cannot be empty.")

        try:
            numeric_id = int(match_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("match_id must be an integer.") from exc

        if numeric_id <= 0:
            raise ValueError("match_id must be greater than zero.")

        return self._get(f"/mcenter/v1/{numeric_id}/scard")

    # --------------------------------------------------
    # Player endpoints
    # --------------------------------------------------

    def search_player(self, name: str) -> dict[str, Any]:
        """Search for a player by name."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Player name cannot be empty.")

        return self._get(
            "/stats/v1/player/search",
            {"plrN": name.strip()},
        )

    # --------------------------------------------------
    # Top statistics endpoint
    # --------------------------------------------------

    def top_stats(
        self,
        stats_type: str,
        match_type: int,
    ) -> dict[str, Any]:
        """Fetch leaderboard statistics.

        Match format IDs used by this project:
            1 = Test
            2 = ODI
            3 = T20I
        """
        if match_type not in (1, 2, 3):
            raise ValueError(
                "match_type must be 1 (Test), 2 (ODI), or 3 (T20I)."
            )

        if not isinstance(stats_type, str) or not stats_type.strip():
            raise ValueError("stats_type cannot be empty.")

        return self._get(
            "/stats/v1/topstats/0",
            {
                "statsType": stats_type.strip(),
                "matchType": match_type,
            },
        )

    # --------------------------------------------------
    # Generic public GET wrapper
    # --------------------------------------------------

    def get(
        self,
        path: str,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Call another API endpoint using the same request handling."""
        if not isinstance(path, str) or not path.strip():
            raise ValueError("API path cannot be empty.")

        return self._get(path, params)

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
