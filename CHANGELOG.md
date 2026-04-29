# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-29

### Added

- Initial public release.
- `tokenize()` — normalize and tokenize a team name.
- `similarity()` — Jaccard + Containment hybrid score for two names.
- `score_pair()` — score a fixture pair (home + away + league) with swap detection.
- `match_fixture()` / `rank_candidates()` — high-level fixture matcher with optional kickoff-time bonus.
- `add_stop_word()`, `add_token_alias()` — runtime configuration hooks.
- Type hints, `py.typed` marker.
- Test suite covering normalization, similarity, swap detection, time bonus.
