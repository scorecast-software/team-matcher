"""Normalization & tokenization.

Pipeline:
    raw string -> NFKD strip accents -> lowercase
              -> remove parentheticals (e.g. "(W)", "(II)")
              -> drop UNN age tags ("U17", "U21")
              -> drop reserve markers
              -> split on whitespace and punctuation
              -> filter stop-words and 1-char tokens
              -> apply alias map (e.g. "utd" -> "united")
              -> return Set[str]
"""

from __future__ import annotations

import re
import unicodedata
from typing import Set

# ---- Stop-words --------------------------------------------------------------
# Generic club designators and language particles that carry no identifying
# information across most leagues. Intentionally OMITS 'united', 'city',
# 'town', 'team' -- those distinguish same-city clubs (Manchester United vs
# Manchester City).
STOP_WORDS: Set[str] = {
    # club-type designators
    "fc", "sc", "cf", "mfc", "afc", "fk", "pk", "bk", "if", "rb",
    "ud", "ad", "ac", "as", "ca", "cd", "sk", "nk", "ss", "sv", "vfl",
    "rcd", "ssd", "asd", "bsc", "ksc", "gfc", "fcu",
    "club", "deportivo", "atletico", "athletic", "sporting", "real",
    # particles
    "de", "del", "la", "el", "los", "las", "da", "do", "dos", "the",
}

# ---- Token aliases -----------------------------------------------------------
# Maps short/non-English variants to a canonical English token.
TOKEN_ALIASES: dict[str, str] = {
    "utd": "united",
    "man": "manchester",
    "intl": "international",
    "munchen": "munich",
    "moskva": "moscow",
    "moscou": "moscow",
}


def add_stop_word(token: str) -> None:
    """Add a token to the in-memory stop-word set (case-insensitive)."""
    STOP_WORDS.add(token.lower())


def add_token_alias(source: str, canonical: str) -> None:
    """Register a token alias (case-insensitive)."""
    TOKEN_ALIASES[source.lower()] = canonical.lower()


_PARENS_RE = re.compile(r"\s*\(.*?\)")
_AGE_RE = re.compile(r"\b[uU]\d{2}\b")
_RES_RE = re.compile(r"\b(reserves?|res)\b", re.IGNORECASE)
_TOKEN_SPLIT_RE = re.compile(r"[\s\-_.,/]+")
_TOKEN_CLEAN_RE = re.compile(r"[^a-z0-9]")


def _normalize(s: str) -> str:
    if not s:
        return ""
    # NFKD + strip combining marks (accents)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = _PARENS_RE.sub("", s)
    s = _AGE_RE.sub("", s)
    s = _RES_RE.sub("", s)
    return s.lower().strip()


def tokenize(name: str) -> Set[str]:
    """Tokenize a team name into a normalized, stop-word-filtered set.

    >>> sorted(tokenize("Manchester Utd FC"))
    ['manchester', 'united']
    >>> sorted(tokenize("Atletico Madrid"))
    ['madrid']
    >>> sorted(tokenize("Real Madrid CF"))
    ['madrid']
    """
    norm = _normalize(name)
    if not norm:
        return set()
    out: Set[str] = set()
    for raw in _TOKEN_SPLIT_RE.split(norm):
        t = _TOKEN_CLEAN_RE.sub("", raw)
        if len(t) <= 1:
            continue
        if t in STOP_WORDS:
            continue
        t = TOKEN_ALIASES.get(t, t)
        out.add(t)
    return out
