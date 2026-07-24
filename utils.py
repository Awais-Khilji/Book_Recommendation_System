"""
utils.py
--------
Shared helper functions: data loading, cover-image resolution, small
formatting helpers, and CSV export used by the Streamlit app.
"""

from __future__ import annotations

import base64
import os
from io import StringIO
from typing import Optional
from xml.sax.saxutils import escape

import pandas as pd
import streamlit as st

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "books.csv")

REQUIRED_COLUMNS = [
    "book_id", "title", "author", "genre", "language", "publication_year",
    "average_rating", "num_ratings", "popularity_score", "num_pages",
    "description", "publisher",
]

# A small palette of placeholder cover colors (tuned to match the app's
# warm "library" theme), cycled per-book so cards feel visually distinct
# even without real cover art.
_COVER_PALETTE = [
    "7A2E2E", "C08A3E", "3E5C4A", "2E4A6B", "6B3E5C",
    "8A5A2E", "4A6B5C", "5C4A6B", "6B4A2E", "2E6B5C",
]


def _wrap_title(title: str, max_chars: int = 15, max_lines: int = 4) -> list[str]:
    """Wraps a title into a handful of short lines for the SVG cover."""
    words = title.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines[:max_lines]


@st.cache_data(show_spinner=False)
def load_books(path: str = DATA_PATH) -> pd.DataFrame:
    """Loads and lightly cleans the book catalogue."""
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"books.csv is missing required columns: {missing}")

    df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce").fillna(0.0)
    df["popularity_score"] = pd.to_numeric(df["popularity_score"], errors="coerce").fillna(0.0)
    df["num_ratings"] = pd.to_numeric(df["num_ratings"], errors="coerce").fillna(0).astype(int)
    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce").fillna(0).astype(int)
    df["num_pages"] = pd.to_numeric(df["num_pages"], errors="coerce").fillna(0).astype(int)
    df["description"] = df["description"].fillna("No description available.")
    df["genre"] = df["genre"].fillna("Uncategorized")
    df["language"] = df["language"].fillna("Unknown")

    return df


@st.cache_data(show_spinner=False)
def cover_url(book_id: int, title: str, author: str = "") -> str:
    """
    Returns a book-cover image as a local SVG data URI (base64-encoded).

    This avoids any network round-trip (unlike a remote placeholder-image
    service), so cards render instantly even on slow or offline connections.
    Deterministically colored per book_id so the same book always gets the
    same cover.
    """
    color = _COVER_PALETTE[int(book_id) % len(_COVER_PALETTE)]
    lines = _wrap_title(str(title))
    title_tspans = "".join(
        f'<tspan x="150" dy="{0 if i == 0 else 26}">{escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    start_y = 190 - (len(lines) - 1) * 13
    author_line = escape(author[:28]) if author else ""

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="300" height="440" viewBox="0 0 300 440">
        <defs>
            <linearGradient id="g{book_id}" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#{color}"/>
                <stop offset="100%" stop-color="#{color}dd"/>
            </linearGradient>
        </defs>
        <rect width="300" height="440" rx="12" fill="url(#g{book_id})"/>
        <rect x="14" y="14" width="272" height="412" rx="6" fill="none" stroke="#ffffff55" stroke-width="1.5"/>
        <circle cx="150" cy="90" r="26" fill="#ffffff22"/>
        <text x="150" y="99" font-family="Georgia, serif" font-size="26" fill="#ffffff" text-anchor="middle">&#128214;</text>
        <text x="150" y="{start_y}" font-family="Georgia, serif" font-size="20" font-weight="700"
              fill="#ffffff" text-anchor="middle">{title_tspans}</text>
        <text x="150" y="404" font-family="Arial, sans-serif" font-size="13" fill="#ffffffcc"
              text-anchor="middle">{author_line}</text>
    </svg>
    """.strip()

    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def genre_options(df: pd.DataFrame) -> list[str]:
    return ["Any"] + sorted(df["genre"].dropna().unique().tolist())


def author_options(df: pd.DataFrame) -> list[str]:
    return ["Any"] + sorted(df["author"].dropna().unique().tolist())


def language_options(df: pd.DataFrame) -> list[str]:
    return ["Any"] + sorted(df["language"].dropna().unique().tolist())


def year_bounds(df: pd.DataFrame) -> tuple[int, int]:
    return int(df["publication_year"].min()), int(df["publication_year"].max())


def to_csv_download(df: pd.DataFrame) -> str:
    """Serializes a recommendation result DataFrame to CSV text for export."""
    buf = StringIO()
    export_cols = [c for c in [
        "title", "author", "genre", "language", "publication_year",
        "average_rating", "popularity_score", "num_ratings",
        "recommendation_score", "similarity_score",
    ] if c in df.columns]
    df[export_cols].to_csv(buf, index=False)
    return buf.getvalue()


def star_string(rating: float) -> str:
    """Renders a 0-5 rating as a star string, e.g. '★★★★☆ 4.2'."""
    full = int(round(rating))
    full = max(0, min(5, full))
    return "★" * full + "☆" * (5 - full) + f"  {rating:.1f}"


def truncate(text: str, length: int = 140) -> str:
    text = text or ""
    return text if len(text) <= length else text[: length - 1].rstrip() + "…"