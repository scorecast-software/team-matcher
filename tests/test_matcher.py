from datetime import datetime, timedelta

import pytest

from team_matcher import Candidate, match_fixture, rank_candidates


KICK = datetime(2026, 4, 27, 19, 45)


def _epl_candidates():
    return [
        Candidate("Manchester United", "Liverpool", "Premier League", KICK, payload="MUN-LIV"),
        Candidate("Chelsea", "Arsenal", "Premier League", KICK + timedelta(hours=2), payload="CHE-ARS"),
        Candidate("Tottenham", "Manchester City", "Premier League", KICK - timedelta(hours=3), payload="TOT-MCI"),
    ]


def test_finds_obvious_match():
    m = match_fixture("Man Utd", "Liverpool", "EPL", _epl_candidates(), kickoff=KICK)
    assert m is not None
    assert m.candidate.payload == "MUN-LIV"
    assert m.score >= 0.85
    assert m.high_confidence


def test_returns_none_when_no_candidate_matches():
    m = match_fixture(
        "Real Madrid", "Barcelona", "La Liga", _epl_candidates(), kickoff=KICK
    )
    assert m is None


def test_swap_handled():
    m = match_fixture(
        "Liverpool", "Manchester United", "Premier League",
        _epl_candidates(), kickoff=KICK,
    )
    assert m is not None
    assert m.swapped is True
    assert m.candidate.payload == "MUN-LIV"


def test_time_bonus_disambiguates_when_league_differs():
    # Two candidates with similar team-name partial overlap but different times.
    cands = [
        Candidate("Real Madrid", "Barcelona", "Spanish Primera", KICK, payload="A"),
        Candidate("Real Madrid", "Barcelona", "Friendly", KICK + timedelta(hours=8), payload="B"),
    ]
    # Query league "ESP D1" shares no tokens with either; only time decides.
    m = match_fixture("Real Madrid", "Barcelona", "ESP D1", cands, kickoff=KICK)
    assert m is not None
    assert m.candidate.payload == "A"
    assert m.time_bonus > 0.0


def test_threshold_filters_weak_match():
    cands = [Candidate("Liverpool", "Chelsea", "EPL", KICK)]
    m = match_fixture("Arsenal", "Tottenham", "EPL", cands, kickoff=KICK, threshold=0.5)
    assert m is None


def test_rank_candidates_sorted():
    ranked = rank_candidates("Man Utd", "Liverpool", "EPL", _epl_candidates(), kickoff=KICK)
    assert len(ranked) == 3
    assert ranked[0].score >= ranked[1].score >= ranked[2].score


def test_no_kickoff_disables_bonus():
    cand = Candidate("Manchester United", "Liverpool", "Premier League", KICK)
    ranked = rank_candidates("Man Utd", "Liverpool", "EPL", [cand], kickoff=None)
    assert ranked[0].time_bonus == 0.0
