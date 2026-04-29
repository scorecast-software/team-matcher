"""Match a fixture from feed A against candidates from feed B.

Run: python examples/premier_league.py
"""

from datetime import datetime, timedelta

from team_matcher import Candidate, match_fixture, rank_candidates


def main() -> None:
    kickoff = datetime(2026, 4, 27, 19, 45)

    # Feed B candidates (e.g. official statistics provider)
    candidates = [
        Candidate("Manchester United FC", "Liverpool FC", "Premier League", kickoff),
        Candidate("Chelsea FC", "Arsenal FC", "Premier League", kickoff + timedelta(hours=2)),
        Candidate("Tottenham Hotspur", "Manchester City", "Premier League",
                  kickoff - timedelta(hours=3)),
    ]

    # Query from feed A (e.g. odds provider with shorter team names)
    match = match_fixture(
        home="Man Utd",
        away="Liverpool",
        league="EPL",
        candidates=candidates,
        kickoff=kickoff,
    )

    if match:
        print(f"Best match: {match.candidate.home} vs {match.candidate.away}")
        print(f"  Score:      {match.score:.3f} (base {match.base_score:.3f}"
              f" + time bonus {match.time_bonus:.3f})")
        print(f"  Confidence: {'HIGH' if match.high_confidence else 'normal'}")
        print(f"  Swapped:    {match.swapped}")
    else:
        print("No match above threshold.")

    print("\nFull ranking:")
    for m in rank_candidates("Man Utd", "Liverpool", "EPL", candidates, kickoff=kickoff):
        print(f"  {m.score:.3f}  {m.candidate.home} vs {m.candidate.away}")


if __name__ == "__main__":
    main()
