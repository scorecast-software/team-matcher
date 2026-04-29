from team_matcher import tokenize


def test_basic_lowercasing():
    assert tokenize("LIVERPOOL") == {"liverpool"}


def test_strip_accents():
    assert "munich" in tokenize("FC Bayern München")  # munchen -> munich via alias


def test_drop_stop_words():
    # "Real" and "FC" are dropped, "madrid" remains
    assert tokenize("Real Madrid CF") == {"madrid"}
    assert tokenize("Manchester FC") == {"manchester"}


def test_keep_distinguishing_words():
    # "United" and "City" are NOT stop-words
    assert tokenize("Manchester United") == {"manchester", "united"}
    assert tokenize("Manchester City") == {"manchester", "city"}


def test_alias_normalization():
    assert tokenize("Man Utd") == tokenize("Manchester United")


def test_strip_parentheticals_and_age():
    assert tokenize("River Plate (Reserves)") == {"river", "plate"}
    assert tokenize("Spain U21") == {"spain"}


def test_short_tokens_dropped():
    assert "x" not in tokenize("X Liverpool")
    assert "liverpool" in tokenize("X Liverpool")
