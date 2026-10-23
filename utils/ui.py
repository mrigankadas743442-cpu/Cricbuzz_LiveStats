"""One wrapper that turns any page error into a friendly message + a log."""
import sqlite3
import uuid
from contextlib import contextmanager

import streamlit as st

from api.cricbuzz_client import CricbuzzAPIError
from utils.exceptions import AppError
from utils.logger import get_logger

log = get_logger(__name__)


@contextmanager
def friendly_errors(area: str):
    """Usage:  with friendly_errors("Charts"):  ...page code...

    The traceback goes to logs/app.log; the user sees a short message
    and a reference ID that matches the log line.
    """
    try:
        yield
    except Exception as exc:
        # st.stop() / st.rerun() are control-flow signals, not errors.
        if type(exc).__module__.startswith("streamlit"):
            raise
        ref = uuid.uuid4().hex[:8]
        log.exception("[%s] %s failed", ref, area)

        if isinstance(exc, CricbuzzAPIError):
            msg = f"The cricket API is unavailable right now: {exc}"
        elif isinstance(exc, AppError):
            msg = str(exc)                      # already user-friendly
        elif isinstance(exc, sqlite3.Error):
            msg = ("There was a problem reading the database. "
                   "Try `python scripts/build_from_cache.py`.")
        else:
            msg = "Something unexpected went wrong on this page."
        st.error(f"{msg}  (reference: {ref})")
        st.stop()