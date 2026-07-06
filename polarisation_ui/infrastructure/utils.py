"""Infrastructure-layer utilities — folder naming helpers for the Dropbox hierarchy."""

import re
from datetime import datetime


def sanitize_subterm_for_folder(subterm: str, max_length: int = 20) -> str:
    """Sanitize a subterm string for safe use in a directory name.

    Replaces whitespace with underscores, removes characters that are not
    alphanumeric, underscores, or hyphens, then truncates to *max_length*.
    """
    cleaned = re.sub(r"\s+", "_", subterm.strip())
    cleaned = re.sub(r"[^\w\-]", "", cleaned)
    return cleaned[:max_length]


def create_dropbox_foldername(
    group_letter: str,
    tk_designation: str,
    sanitized_subterm: str = "",
) -> str:
    """Build the Dropbox folder name for a measurement group.

    Format: ``<Weekday><Group><TK>[-<Subterm>]``
    Example: ``MonATK08-Polariser``.
    """
    day = datetime.now().strftime("%a")
    base = f"{day}{group_letter}{tk_designation}"
    if sanitized_subterm:
        return f"{base}-{sanitized_subterm}"
    return base
