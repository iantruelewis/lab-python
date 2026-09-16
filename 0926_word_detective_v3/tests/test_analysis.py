from src.analysis import build_presence_matrix, build_word_table, calculate_word_stats, response_contains_word, tokenize, wilson_interval
from src.models import Dataset, Response


def dataset() -> Dataset:
    return Dataset("Test", (
        Response("ai", "Super special answer."),
        Response("ai", "A super answer."),
        Response("human", "A careful answer."),
        Response("human", "A human answer."),
    ))


def test_tokenize_preserves_internal_apostrophe():
    assert tokenize("It's a small test.") == ("it's", "a", "small", "test")


def test_word_matching_uses_word_boundaries():
    assert response_contains_word("super super answer", "super")
    assert not response_contains_word("superb answer", "super")


def test_probability_uses_responses_not_occurrences():
    stats = calculate_word_stats(dataset(), "super")
    assert stats.ai_count == 2
    assert stats.total_ai == 2
    assert stats.p_ai == 1.0


def test_zero_frequency_is_represented():
    stats = calculate_word_stats(dataset(), "special")
    assert stats.ai_only is True
    assert stats.ratio is None
    assert stats.p_value is not None


def test_wilson_interval_is_bounded():
    low, high = wilson_interval(5, 10)
    assert 0 <= low <= 0.5 <= high <= 1


def test_presence_matrix_matches_direct_calculation():
    words, ai, human = build_presence_matrix(dataset())
    idx = words.index("super")
    assert int(ai[:, idx].sum()) == 2
    assert int(human[:, idx].sum()) == 0


def test_word_table_keeps_one_sided_words_and_q_values():
    table = build_word_table(dataset(), minimum_support=1)
    row = table.loc[table["word"] == "special"].iloc[0]
    assert bool(row["ai_only"])
    assert "q_value" in table.columns


def test_bh_adjustment_is_monotonic_in_ranked_p_values():
    from src.analysis import _benjamini_hochberg
    q = _benjamini_hochberg([0.001, 0.01, 0.2, 0.5])
    assert all(0 <= value <= 1 for value in q)
    assert q[0] <= q[1] <= q[2] <= q[3]
