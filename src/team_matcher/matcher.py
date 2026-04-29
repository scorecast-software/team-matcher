"""High-level fixture matcher.

When matching a fixture across feeds you almost always have a *kickoff time*
in addition to team names. Different feeds use wildly different league
conventions ("POR D1" vs "Portuguese Primeira Liga") that share zero tokens,
so a kickoff proximity bonus is a stronger signal than league text.

This module returns the best candidate above a threshold, optionally giving a
bonus when the candidate's kickoff is close to the query's kickoff.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List, Optional

from team_matcher.similarity import score_pair


DEFAULT_THRESHOLD = 0.55
HIGH_CONFIDENCE = 0.85
TIME_BONUS_NEAR_MINUTES = 30
TIME_BONUS_FAR_MINUTES = 90
TIME_BONUS_MAX = 0.20
TIME_BONUS_FAR = 0.05


@dataclass(frozen=True)
class Candidate:
    """One fixture from the candidate feed.

    Attributes:
        home, away: team names (any reasonable formatting)
        league: league/competition name (use ``""`` if unknown)
        kickoff: datetime; pass ``None`` to skip the time bonus
        payload: any user-supplied object (id, full row, etc.) returned in Match
    """

    home: str
    away: str
    league: str = ""
    kickoff: Optional[datetime] = None
    payload: object = None


@dataclass(frozen=True)
class Match:
    """Result of a single fixture match."""

    candidate: Candidate
    score: float
    base_score: float
    time_bonus: float
    swapped: bool
    high_confidence: bool = field(init=False)

    def __post_init__(self) -> None:
        # frozen dataclass workaround
        object.__setattr__(self, "high_confidence", self.score >= HIGH_CONFIDENCE)


def _time_bonus(query_dt: Optional[datetime], cand_dt: Optional[datetime]) -> float:
    if query_dt is None or cand_dt is None:
        return 0.0
    diff_min = abs((query_dt - cand_dt).total_seconds()) / 60.0
    if diff_min <= TIME_BONUS_NEAR_MINUTES:
        # Linear ramp: 0 min -> +TIME_BONUS_MAX, 30 min -> 0
        return TIME_BONUS_MAX * (1.0 - diff_min / TIME_BONUS_NEAR_MINUTES)
    if diff_min <= TIME_BONUS_FAR_MINUTES:
        return TIME_BONUS_FAR
    return 0.0


def rank_candidates(
    home: str,
    away: str,
    league: str,
    candidates: Iterable[Candidate],
    *,
    kickoff: Optional[datetime] = None,
) -> List[Match]:
    """Score and sort all candidates (descending). Does NOT apply a threshold."""
    out: List[Match] = []
    for c in candidates:
        base, swapped = score_pair(home, away, league, c.home, c.away, c.league)
        bonus = _time_bonus(kickoff, c.kickoff)
        out.append(
            Match(
                candidate=c,
                score=min(1.0, base + bonus),
                base_score=base,
                time_bonus=bonus,
                swapped=swapped,
            )
        )
    out.sort(key=lambda m: m.score, reverse=True)
    return out


def match_fixture(
    home: str,
    away: str,
    league: str,
    candidates: Iterable[Candidate],
    *,
    kickoff: Optional[datetime] = None,
    threshold: float = DEFAULT_THRESHOLD,
) -> Optional[Match]:
    """Return the best match above ``threshold``, or ``None``.

    Args:
        home, away, league: query fixture
        candidates: iterable of :class:`Candidate`
        kickoff: query kickoff; if provided AND a candidate has ``kickoff``,
            applies a proximity bonus (up to +0.20 within 30 min)
        threshold: minimum final score (default 0.55)
    """
    ranked = rank_candidates(home, away, league, candidates, kickoff=kickoff)
    if not ranked:
        return None
    best = ranked[0]
    return best if best.score >= threshold else None
