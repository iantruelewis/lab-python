from dataclasses import dataclass
from typing import Literal


Author = Literal["ai", "human"]


@dataclass(frozen=True)
class Response:
    """A single source response with its author class."""
    author: Author
    text: str


@dataclass(frozen=True)
class Dataset:
    """A parsed Word Detective dataset."""
    name: str
    responses: tuple[Response, ...]

    @property
    def ai_responses(self) -> tuple[Response, ...]:
        return tuple(
            r for r in self.responses
            if r.author == "ai"
        )

    @property
    def human_responses(self) -> tuple[Response, ...]:
        return tuple(
            r for r in self.responses
            if r.author == "human"
        )

    @property
    def ai_count(self) -> int:
        return len(self.ai_responses)

    @property
    def human_count(self) -> int:
        return len(self.human_responses)


@dataclass(frozen=True)
class WordStats:
    """Response-level statistics for one word."""
    word: str
    ai_count: int
    human_count: int
    total_ai: int
    total_human: int
    p_ai: float
    p_human: float
    difference: float
    ratio: float | None
    log_ratio: float | None
    ai_only: bool
    human_only: bool
    ai_ci_low: float
    ai_ci_high: float
    human_ci_low: float
    human_ci_high: float
    p_value: float | None
    q_value: float | None = None