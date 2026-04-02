"""!/usr/bin/env python
Infrastructure utilities for file and directory management.

This module provides helper functions for organizing measurement data files
and directories. Utilities here are infrastructure concerns (naming conventions,
path construction, organization) rather than business logic.

Functions:
    sanitize_subterm_for_folder: Clean string for use in folder names.
    create_dropbox_foldername: Create Dropbox-compatible folder structure.
    create_group_name: Generate group identifier from date and letter.

Dependencies:
    - re (standard library)
    - datetime (standard library)
    - polarisation_ui.infrastructure.logging (Debug)
"""

import re
from datetime import datetime

from .logging import Debug


def sanitize_subterm_for_folder(subterm: str, max_length: int = 20) -> str:
    """
    Sanitize string for use in folder names.

    Removes special characters, limits length, and applies abbreviations
    if needed to fit constraints.

    Args:
        subterm: String to sanitize (e.g., experimental group name).
        max_length: Maximum allowed length. Default 20.

    Returns:
        str: Sanitized string safe for folder names.

    Examples:
        >>> sanitize_subterm_for_folder("Test & Validation", 15)
        'Test_Validation'
        >>> sanitize_subterm_for_folder("VeryLongExperimentalGroupName", 10)
        'Ver_Lon_xx'
    """
    if not subterm:
        Debug.debug("Empty subterm provided for folder sanitization.")
        return ""

    # Replace special characters with underscores
    # Keep alphanumeric, spaces, hyphens, underscores, and German umlauts
    sanitized = re.sub(r"[^a-zA-Z0-9\s\-_äöüÄÖÜß]", "_", subterm)

    # Collapse multiple consecutive underscores/spaces
    sanitized = re.sub(r"[_\s]+", "_", sanitized)

    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")

    # If short enough, return as-is
    if len(sanitized) <= max_length:
        Debug.debug(f"Sanitized subterm within length: {sanitized}")
        return sanitized

    # Try abbreviating each word to first 3 letters
    words = sanitized.split("_")
    abbreviated = "_".join(word[:3] for word in words if word)

    if len(abbreviated) <= max_length:
        Debug.debug(f"Abbreviated subterm within length: {abbreviated}")
        return abbreviated

    # Still too long, truncate and append "_xxx"
    Debug.debug(f"Subterm too long after abbreviation, truncating: {abbreviated}")
    return abbreviated[: max_length - 4] + "_xxx"


def create_dropbox_foldername(
    group_letter: str, tk_designation: str, subgroup: str = ""
) -> str:
    """
    Create Dropbox-compatible folder name following naming convention.

    Generates folder names in the format:
    `<Day><Group><TK>-<Subgroup>` (e.g., "MoA01-Mueller")

    This structure supports automated data ingestion and organization.

    Args:
        group_letter: Single group letter (A-Z).
        tk_designation: Test kit code (e.g., "TK08", "TK01").
        subgroup: Optional subgroup identifier for further organization.

    Returns:
        str: Generated folder name.

    Raises:
        ValueError: If group_letter or tk_designation invalid.

    Examples:
        >>> create_dropbox_foldername("A", "TK08", "Mueller")
        'MoATK08-Mueller'  # If Monday
        >>> create_dropbox_foldername("B", "TK01")
        'DiB01'  # If Tuesday
    """
    # Get German weekday abbreviation
    day_abbrs = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    day = day_abbrs[datetime.now().weekday()]

    # Validate inputs
    if not group_letter or not re.match(r"^[A-Z]$", group_letter):
        raise ValueError(f"Invalid group letter: {group_letter} (must be A-Z)")
    if not tk_designation or not re.match(r"^TK\d{1,2}$", tk_designation):
        raise ValueError(f"Invalid TK designation: {tk_designation} (format: TKxx)")

    folder_name = f"{day}{group_letter.upper()}{tk_designation}"
    if subgroup:
        folder_name += f"-{subgroup}"

    Debug.debug(f"Generated Dropbox folder name: {folder_name}")
    return folder_name


def create_group_name(letter: str) -> str:
    """
    Generate group identifier from date and letter.

    Creates standardized group names based on current date and letter.
    Format: `<Semester><Year>_<Day>_<Letter>` (e.g., "SoSe2024_Mo_A")

    Args:
        letter: Single letter (A-Z).

    Returns:
        str: Generated group name.

    Raises:
        ValueError: If letter is invalid.

    Examples:
        >>> create_group_name("A")
        'SoSe2024_Mo_A'  # If summer semester and Monday
        >>> create_group_name("B")
        'WiSe2024_Do_B'  # If winter semester and Thursday
    """
    # Determine semester based on month
    month = datetime.now().month
    semester = "SoSe" if month <= 9 else "WiSe"

    day = datetime.now().strftime("%a")[:2]  # Two-letter day abbreviation
    year = datetime.now().year

    # Validate letter
    if not letter or not re.match(r"^[A-Z]$", letter):
        raise ValueError(f"Invalid group letter: {letter} (must be A-Z)")
    group_name = f"{semester}{year}_{day}_{letter.upper()}"

    Debug.debug(f"Generated group name: {group_name}")
    return group_name
