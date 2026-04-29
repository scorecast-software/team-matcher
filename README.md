# team-matcher

[![PyPI version](https://img.shields.io/pypi/v/team-matcher.svg)](https://pypi.org/project/team-matcher/)
[![Python versions](https://img.shields.io/pypi/pyversions/team-matcher.svg)](https://pypi.org/project/team-matcher/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/scorecast/team-matcher/actions/workflows/ci.yml/badge.svg)](https://github.com/scorecast/team-matcher/actions/workflows/ci.yml)

**Fuzzy matcher for sports team names across data feeds.**
Pure Python, zero dependencies, well-tested.

If you've ever joined data from two sports providers, you've hit this:

| Feed A          | Feed B                     |
| --------------- | -------------------------- |
| Man Utd         | Manchester United FC       |
| Real Madrid CF  | Real Madrid                |
| Hearts          | Heart of Midlothian        |
| Bayern München  | FC Bayern Munich           |
| LDU             | Liga Dep. Universitaria    |

Naive `==` fails. `difflib` is fragile (`Manchester United` vs `Manchester City` are 84% similar). This library uses a **Jaccard + Containment hybrid** with stop-word filtering, plus an optional **kickoff-time proximity bonus** when matching whole fixtures, so cross-feed name variation, abbreviations, and inconsistent league naming all work out of the box.

> ⚙️ Used in production at [scorecast.info](https://scorecast.info) to link millions of football fixtures across data sources.

## Install

```bash
pip install team-matcher
```

Requires Python 3.9+.

## Quick start

### 1. Compare two team names

```python
from team_matcher import similarity

similarity("Manchester United", "Man Utd")        # 1.0
similarity("Manchester United", "Manchester City") # 0.5
similarity("Liverpool", "Chelsea")                 # 0.0
```

### 2. Match a fixture against candidates

```python
from datetime import datetime
from team_matcher import Candidate, match_fixture

kickoff = datetime(2026, 4, 27, 19, 45)

candidates = [
    Candidate("Manchester United FC", "Liverpool FC",
              league="Premier League", kickoff=kickoff,
              payload="match_id_123"),
    Candidate("Chelsea", "Arsenal",
              league="Premier League", kickoff=kickoff,
              payload="match_id_124"),
]

match = match_fixture(
    home="Man Utd",
    away="Liverpool",
    league="EPL",
    kickoff=kickoff,
    candidates=candidates,
)

if match:
    print(match.score)              # 1.0
    print(match.candidate.payload)  # "match_id_123"
    print(match.swapped)            # False
```

### 3. Inspect ranking

```python
from team_matcher import rank_candidates

for m in rank_candidates("Man Utd", "Liverpool", "EPL",
                         candidates, kickoff=kickoff):
    print(f"{m.score:.3f}  {m.candidate.home} vs {m.candidate.away}")
```

## How it works

### Token-based similarity

Each name is normalized (lowercase, strip accents, drop parentheticals like `(W)` or `(Reserves)` and age tags like `U21`), then split on whitespace and punctuation. Stop-words (`fc`, `sc`, `cf`, `real`, `atletico`, language particles…) are filtered out. Common variants are aliased (`utd` → `united`, `man` → `manchester`, `münchen` → `munich`).

Two token sets are then compared with a **hybrid metric**:

```
sim = 0.4 * jaccard(A, B) + 0.6 * containment(A, B)
containment(A, B) = |A intersect B| / min(|A|, |B|)
```

Containment makes the metric robust to length asymmetry — `Olancho` vs `Olancho FC` collapse to the same single-token set after stop-word filtering and score `1.0`.

### Pair scoring

A fixture pair (home + away + league) is scored as

```
score = 0.4 * sim(home_a, home_b)
      + 0.4 * sim(away_a, away_b)
      + 0.2 * sim(league_a, league_b)
```

The matcher tries both team orderings and picks the higher score, returning a `swapped: bool` flag.

### Kickoff-time bonus (the secret sauce)

League names are **wildly inconsistent** between feeds (`POR D1` vs `Portuguese Primeira Liga` share zero tokens). When the same fixture appears in two feeds, **the kickoff time is the strongest available signal**. If both query and candidate have a `kickoff`, an additional bonus is applied:

| time delta | bonus       |
| ---------- | ----------- |
| ≤ 30 min   | up to +0.20 |
| ≤ 90 min   | +0.05       |
| > 90 min   | 0           |

This single rule typically boosts cross-feed match rate from ~10% to >65% in our benchmarks.

## Configuration

You can extend the stop-word set and alias map at runtime:

```python
from team_matcher import add_stop_word, add_token_alias

add_stop_word("clube")
add_token_alias("psg", "paris")
```

You can also tune the threshold:

```python
match_fixture(..., threshold=0.65)   # default 0.55
```

The default of `0.55` is calibrated for cross-feed football data; raise it for stricter matching.

## What this library is **not**

- ❌ Not a database, not a service. It's a 200-line pure-Python module.
- ❌ Not a name **canonicalization** dictionary. If your feeds use `Hearts` and `Heart of Midlothian`, you'll need a small alias dictionary on top — fuzzy alone can't bridge that gap.
- ❌ Not specific to football. Tokenization rules are sport-agnostic; replace stop-words for basketball, MMA, etc.

## Development

```bash
git clone https://github.com/scorecast/team-matcher
cd team-matcher
pip install -e ".[dev]"
pytest
ruff check src tests
mypy src
```

## License

MIT — see [LICENSE](./LICENSE).

---

Built and battle-tested at **[ScoreCast](https://scorecast.info)** — football odds analytics platform tracking value bets across millions of matches. If this library saves you a few hours, consider giving us a ⭐ on GitHub.
