from src.analysis import build_word_table, calculate_word_stats, response_contains_word, tokenize, wilson_interval
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

def test_word_matching_is_response_level():
    assert response_contains_word("super super answer", "super")
    assert not response_contains_word("superb answer", "super")

def test_probability_uses_responses_not_occurrences():
    stats = calculate_word_stats(dataset(), "super")
    assert stats.ai_count == 2 and stats.total_ai == 2 and stats.p_ai == 1.0

def test_zero_frequency_is_represented():
    stats = calculate_word_stats(dataset(), "special")
    assert stats.ai_count == 1 and stats.human_count == 0 and stats.ai_only and stats.ratio is None

def test_difference_and_log_ratio_are_available():
    stats = calculate_word_stats(dataset(), "super")
    assert stats.difference == 1.0 and stats.log_ratio is None

def test_wilson_interval_is_bounded():
    low, high = wilson_interval(5, 10)
    assert 0 <= low <= 0.5 <= high <= 1

def test_word_table_keeps_one_sided_words():
    table = build_word_table(dataset(), minimum_support=1)
    row = table.loc[table["word"] == "special"].iloc[0]
    assert bool(row["ai_only"])
