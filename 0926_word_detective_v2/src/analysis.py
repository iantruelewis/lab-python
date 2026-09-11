import math
import re
import pandas as pd
from scipy.stats import chi2_contingency
from .models import Dataset, WordStats

WORD_PATTERN = re.compile(r"(?u)\b[a-zA-Z]+(?:['’][a-zA-Z]+)?\b")

def normalize_word(word: str) -> str:
    return word.strip().lower()

def tokenize(text: str) -> tuple[str, ...]:
    return tuple(match.group(0).lower().replace("’", "'") for match in WORD_PATTERN.finditer(text))

def response_contains_word(text: str, word: str) -> bool:
    target = normalize_word(word)
    return bool(target) and target in set(tokenize(text))

def word_support(dataset: Dataset, word: str) -> tuple[int, int]:
    target = normalize_word(word)
    ai_count = sum(response_contains_word(r.text, target) for r in dataset.ai_responses)
    human_count = sum(response_contains_word(r.text, target) for r in dataset.human_responses)
    return ai_count, human_count

def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials <= 0:
        return 0.0, 0.0
    p = successes / trials
    denominator = 1 + z**2 / trials
    center = (p + z**2 / (2 * trials)) / denominator
    margin = z * math.sqrt((p * (1 - p) / trials) + (z**2 / (4 * trials**2))) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)

def _log_ratio(p_ai: float, p_human: float) -> float | None:
    if p_ai <= 0 or p_human <= 0:
        return None
    return math.log(p_ai / p_human)

def _ratio(p_ai: float, p_human: float) -> float | None:
    return None if p_human == 0 else p_ai / p_human

def _chi_square_p_value(ai_count: int, human_count: int, total_ai: int, total_human: int) -> float | None:
    if total_ai <= 0 or total_human <= 0:
        return None
    table = [[ai_count, total_ai - ai_count], [human_count, total_human - human_count]]
    try:
        _, p_value, _, expected = chi2_contingency(table, correction=False)
    except ValueError:
        return None
    if (expected < 5).any():
        return None
    return float(p_value)

def calculate_word_stats(dataset: Dataset, word: str) -> WordStats:
    target = normalize_word(word)
    ai_count, human_count = word_support(dataset, target)
    total_ai, total_human = dataset.ai_count, dataset.human_count
    p_ai = ai_count / total_ai if total_ai else 0.0
    p_human = human_count / total_human if total_human else 0.0
    ai_low, ai_high = wilson_interval(ai_count, total_ai)
    human_low, human_high = wilson_interval(human_count, total_human)
    return WordStats(
        word=target,
        ai_count=ai_count,
        human_count=human_count,
        total_ai=total_ai,
        total_human=total_human,
        p_ai=p_ai,
        p_human=p_human,
        difference=p_ai - p_human,
        ratio=_ratio(p_ai, p_human),
        log_ratio=_log_ratio(p_ai, p_human),
        ai_only=ai_count > 0 and human_count == 0,
        human_only=human_count > 0 and ai_count == 0,
        ai_ci_low=ai_low,
        ai_ci_high=ai_high,
        human_ci_low=human_low,
        human_ci_high=human_high,
        p_value=_chi_square_p_value(ai_count, human_count, total_ai, total_human),
    )

def vocabulary(dataset: Dataset, minimum_length: int = 3) -> tuple[str, ...]:
    return tuple(sorted({word for response in dataset.responses for word in tokenize(response.text) if len(word) >= minimum_length}))

def build_word_table(dataset: Dataset, minimum_length: int = 3, minimum_support: int = 1) -> pd.DataFrame:
    rows = []
    for word in vocabulary(dataset, minimum_length):
        stats = calculate_word_stats(dataset, word)
        if max(stats.ai_count, stats.human_count) >= minimum_support:
            rows.append(stats.__dict__)
    if not rows:
        return pd.DataFrame(columns=["word","ai_count","human_count","total_ai","total_human","p_ai","p_human","difference","ratio","log_ratio","ai_only","human_only","ai_ci_low","ai_ci_high","human_ci_low","human_ci_high","p_value","q_value"])
    return pd.DataFrame(rows).sort_values(by="difference", ascending=False, ignore_index=True)
