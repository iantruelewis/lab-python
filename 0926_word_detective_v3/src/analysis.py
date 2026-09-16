import math
import re
from collections import Counter

import pandas as pd
from scipy import sparse
from scipy.stats import chi2_contingency, fisher_exact

from .models import Dataset, WordStats

WORD_PATTERN = re.compile(r"(?u)\b[a-zA-Z]+(?:['’][a-zA-Z]+)?\b")


def normalize_word(word: str) -> str:
    return word.strip().lower().replace("’", "'")


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(
        match.group(0).lower().replace("’", "'")
        for match in WORD_PATTERN.finditer(text)
    )


def response_word_set(text: str) -> frozenset[str]:
    return frozenset(tokenize(text))


def response_contains_word(text: str, word: str) -> bool:
    target = normalize_word(word)
    return bool(target) and target in response_word_set(text)


def vocabulary(dataset: Dataset, minimum_length: int = 3) -> tuple[str, ...]:
    return tuple(sorted({
        word for response in dataset.responses
        for word in response_word_set(response.text)
        if len(word) >= minimum_length
    }))


def build_presence_matrix(dataset: Dataset, minimum_length: int = 3):
    """Build a sparse response x vocabulary binary matrix."""
    words = vocabulary(dataset, minimum_length)
    word_index = {word: i for i, word in enumerate(words)}

    def build_rows(responses):
        rows, cols = [], []
        for row_idx, response in enumerate(responses):
            for word in response_word_set(response.text):
                col_idx = word_index.get(word)
                if col_idx is not None:
                    rows.append(row_idx)
                    cols.append(col_idx)
        data = [1] * len(rows)
        return sparse.csr_matrix((data, (rows, cols)), shape=(len(responses), len(words)), dtype='uint8')

    return words, build_rows(dataset.ai_responses), build_rows(dataset.human_responses)


def _wilson(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials <= 0:
        return 0.0, 0.0
    p = successes / trials
    denominator = 1 + z*z/trials
    center = (p + z*z/(2*trials)) / denominator
    margin = z * math.sqrt(p*(1-p)/trials + z*z/(4*trials*trials)) / denominator
    return max(0.0, center-margin), min(1.0, center+margin)


def _p_value(ai_count: int, human_count: int, total_ai: int, total_human: int) -> float | None:
    if total_ai <= 0 or total_human <= 0:
        return None
    table = [[ai_count, total_ai-ai_count], [human_count, total_human-human_count]]
    try:
        _, _, _, expected = chi2_contingency(table, correction=False)
    except ValueError:
        return None
    if (expected < 5).any():
        return float(fisher_exact(table, alternative="two-sided").pvalue)
    return float(chi2_contingency(table, correction=False).pvalue)


def _benjamini_hochberg(p_values: list[float]) -> list[float]:
    if not p_values:
        return []
    n = len(p_values)
    order = sorted(range(n), key=p_values.__getitem__)
    adjusted = [1.0] * n
    running = 1.0
    for rank in range(n, 0, -1):
        idx = order[rank-1]
        running = min(running, p_values[idx] * n / rank)
        adjusted[idx] = min(1.0, running)
    return adjusted


def _stats_from_counts(word: str, ai_count: int, human_count: int, total_ai: int, total_human: int) -> WordStats:
    p_ai = ai_count / total_ai if total_ai else 0.0
    p_human = human_count / total_human if total_human else 0.0
    ratio = p_ai / p_human if p_human else None
    log2_ratio = math.log2(ratio) if ratio and ratio > 0 else None
    ai_low, ai_high = _wilson(ai_count, total_ai)
    human_low, human_high = _wilson(human_count, total_human)
    return WordStats(
        word=word, ai_count=ai_count, human_count=human_count,
        total_ai=total_ai, total_human=total_human, p_ai=p_ai, p_human=p_human,
        difference=p_ai-p_human, ratio=ratio, log2_ratio=log2_ratio,
        ai_only=ai_count > 0 and human_count == 0,
        human_only=human_count > 0 and ai_count == 0,
        ai_ci_low=ai_low, ai_ci_high=ai_high,
        human_ci_low=human_low, human_ci_high=human_high,
        p_value=_p_value(ai_count, human_count, total_ai, total_human),
    )


def calculate_word_stats(dataset: Dataset, word: str) -> WordStats:
    target = normalize_word(word)
    ai_count = sum(response_contains_word(r.text, target) for r in dataset.ai_responses)
    human_count = sum(response_contains_word(r.text, target) for r in dataset.human_responses)
    return _stats_from_counts(target, ai_count, human_count, dataset.ai_count, dataset.human_count)


def build_word_table(dataset: Dataset, minimum_length: int = 3, minimum_support: int = 1) -> pd.DataFrame:
    words, ai_matrix, human_matrix = build_presence_matrix(dataset, minimum_length)
    if not words:
        return pd.DataFrame()
    ai_counts = ai_matrix.sum(axis=0).A1.astype(int)
    human_counts = human_matrix.sum(axis=0).A1.astype(int)
    rows = []
    for word, ai_count, human_count in zip(words, ai_counts, human_counts):
        if max(ai_count, human_count) < minimum_support:
            continue
        rows.append(_stats_from_counts(word, int(ai_count), int(human_count), dataset.ai_count, dataset.human_count).__dict__)
    table = pd.DataFrame(rows)
    if table.empty:
        return table
    valid = table["p_value"].notna()
    table["q_value"] = float("nan")
    if valid.any():
        table.loc[valid, "q_value"] = _benjamini_hochberg(table.loc[valid, "p_value"].tolist())
    return table.sort_values("difference", ascending=False, ignore_index=True)


def top_words(table: pd.DataFrame, n: int = 20, direction: str = "ai") -> pd.DataFrame:
    if table.empty:
        return table.copy()
    column = "difference"
    result = table.sort_values(column, ascending=(direction == "human"), ignore_index=True)
    return result.head(n)
