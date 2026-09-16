from dataclasses import dataclass
from typing import Literal

Author = Literal["ai", "human"]

@dataclass(frozen=True)
class Response:
    author: Author
    text: str

@dataclass(frozen=True)
class Dataset:
    name: str
    responses: tuple[Response, ...]

    @property
    def ai_responses(self) -> tuple[Response, ...]:
        return tuple(r for r in self.responses if r.author == "ai")

    @property
    def human_responses(self) -> tuple[Response, ...]:
        return tuple(r for r in self.responses if r.author == "human")

    @property
    def ai_count(self) -> int:
        return len(self.ai_responses)

    @property
    def human_count(self) -> int:
        return len(self.human_responses)

@dataclass(frozen=True)
class DatasetValidation:
    name: str
    total_responses: int
    ai_responses: int
    human_responses: int
    balanced: bool
    ai_duplicates: int
    human_duplicates: int
    empty_responses: int
    question_markers_removed: int

@dataclass(frozen=True)
class WordStats:
    word: str
    ai_count: int
    human_count: int
    total_ai: int
    total_human: int
    p_ai: float
    p_human: float
    difference: float
    ratio: float | None
    log2_ratio: float | None
    ai_only: bool
    human_only: bool
    ai_ci_low: float
    ai_ci_high: float
    human_ci_low: float
    human_ci_high: float
    p_value: float | None
    q_value: float | None = None
