"""team-matcher: fuzzy matching for sports team names across data feeds.

Public API:

    from team_matcher import (
        tokenize,
        similarity,
        score_pair,
        match_fixture,
        Candidate,
        Match,
    )

Example::

    from datetime import datetime
    from team_matcher import match_fixture, Candidate

    candidates = [
        Candidate(home="Manchester United", away="Liverpool",
                  league="Premier League",
                  kickoff=datetime(2026, 4, 27, 19, 45)),
        Candidate(home="Chelsea", away="Arsenal",
                  league="Premier League",
                  kickoff=datetime(2026, 4, 27, 17, 30)),
    ]
    match = match_fixture(
        home="Man Utd", away="Liverpool",
        league="EPL",
        kickoff=datetime(2026, 4, 27, 19, 45),
        candidates=candidates,
    )
    print(match.score, match.candidate.home)
"""

from team_matcher.matcher import (
    Candidate,
    Match,
    match_fixture,
    rank_candidates,
)
from team_matcher.normalize import (
    STOP_WORDS,
    TOKEN_ALIASES,
    add_stop_word,
    add_token_alias,
    tokenize,
)
from team_matcher.similarity import (
    score_pair,
    similarity,
)

__version__ = "0.1.0"

__all__ = [
    "STOP_WORDS",
    "TOKEN_ALIASES",
    # high-level matcher
    "Candidate",
    "Match",
    "__version__",
    "add_stop_word",
    "add_token_alias",
    "match_fixture",
    "rank_candidates",
    "score_pair",
    # similarity primitives
    "similarity",
    # tokens / config
    "tokenize",
]
