"""Similarity primitives.

Single-string similarity is a hybrid Jaccard + Containment metric:

    sim = 0.4 * jaccard + 0.6 * containment

where ``containment = |A intersect B| / min(|A|, |B|)`` makes the metric robust
to length asymmetry ("Olancho" vs "Olancho FC" -> 1.0 after stop-word filter).

Pair scoring (home vs away vs league) uses weights 0.4 / 0.4 / 0.2 and tries
both direct and swapped orientations, returning the better one.
"""

from __future__ import annotations

from team_matcher.normalize import tokenize

JACCARD_WEIGHT = 0.4
CONTAINMENT_WEIGHT = 0.6

HOME_WEIGHT = 0.4
AWAY_WEIGHT = 0.4
LEAGUE_WEIGHT = 0.2


def _jc(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    union = len(a | b)
    smaller = min(len(a), len(b))
    return JACCARD_WEIGHT * (inter / union) + CONTAINMENT_WEIGHT * (inter / smaller)


def similarity(name_a: str, name_b: str) -> float:
    """Hybrid similarity score in [0, 1].

    >>> round(similarity("Manchester United", "Man Utd"), 2)
    1.0
    >>> round(similarity("Real Madrid", "Atletico Madrid"), 2)
    1.0
    >>> similarity("Liverpool", "Chelsea")
    0.0
    """
    return _jc(tokenize(name_a), tokenize(name_b))


def score_pair(
    home_a: str,
    away_a: str,
    league_a: str,
    home_b: str,
    away_b: str,
    league_b: str,
) -> tuple[float, bool]:
    """Score a fixture pair. Returns ``(score, swapped)``.

    ``swapped=True`` means the best score was achieved with home/away swapped
    (some feeds invert team order).
    """
    th_a, ta_a = tokenize(home_a), tokenize(away_a)
    th_b, ta_b = tokenize(home_b), tokenize(away_b)
    lg = _jc(tokenize(league_a), tokenize(league_b))
    direct = HOME_WEIGHT * _jc(th_a, th_b) + AWAY_WEIGHT * _jc(ta_a, ta_b) + LEAGUE_WEIGHT * lg
    swapped = HOME_WEIGHT * _jc(th_a, ta_b) + AWAY_WEIGHT * _jc(ta_a, th_b) + LEAGUE_WEIGHT * lg
    if swapped > direct:
        return swapped, True
    return direct, False
