import pytest

from team_matcher import score_pair, similarity


def test_identical_names():
    assert similarity("Liverpool FC", "Liverpool FC") == pytest.approx(1.0)


def test_abbreviation_matches_full_name():
    # Manchester United vs Man Utd
    assert similarity("Manchester United", "Man Utd") == pytest.approx(1.0)


def test_different_clubs_zero():
    assert similarity("Liverpool", "Chelsea") == 0.0


def test_swap_detection():
    score, swapped = score_pair(
        "Liverpool", "Chelsea", "Premier League",
        "Chelsea", "Liverpool", "Premier League",
    )
    assert swapped is True
    assert score >= 0.9


def test_partial_match_below_one():
    # Same city different club
    s = similarity("Manchester United", "Manchester City")
    assert 0.0 < s < 1.0


def test_pair_with_league_only_weak():
    # Same league, totally different teams should still be low
    score, _ = score_pair(
        "Liverpool", "Chelsea", "Premier League",
        "Arsenal", "Tottenham", "Premier League",
    )
    assert score < 0.3
