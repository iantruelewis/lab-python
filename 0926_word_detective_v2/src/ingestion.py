import re
from pathlib import Path

from striprtf.striprtf import rtf_to_text

from .models import Dataset, Response


AUTHOR_PATTERN = re.compile(
    r"(?im)^\s*(ai|human)\s*$"
)

QUESTION_PATTERN = re.compile(
    r"\(Question:",
    re.IGNORECASE
)


def load_rtf(path: str | Path) -> str:
    """Convert an RTF source file to plain text."""
    path = Path(path)

    raw_rtf = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return rtf_to_text(raw_rtf)


def _strip_question(
    text: str
) -> tuple[str, bool]:
    """Return response text before the appended question,
    plus whether a question marker was found.
    """

    match = QUESTION_PATTERN.search(text)

    if match is None:
        return text.strip(), False

    return text[:match.start()].strip(), True


def parse_responses(
    text: str
) -> tuple[Response, ...]:
    """Parse AI/human records from converted source text."""

    normalized = (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    matches = list(
        AUTHOR_PATTERN.finditer(normalized)
    )

    responses: list[Response] = []

    for index, match in enumerate(matches):

        author = match.group(1).lower()

        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(normalized)

        raw_response = normalized[
            start:end
        ].strip()

        response, _ = _strip_question(
            raw_response
        )

        if response:
            responses.append(
                Response(
                    author=author,
                    text=response
                )
            )

    return tuple(responses)


def load_dataset(
    name: str,
    path: str | Path
) -> Dataset:
    """Load and parse one dataset."""

    return Dataset(
        name=name,
        responses=parse_responses(
            load_rtf(path)
        )
    )


def validate_dataset(
    dataset: Dataset
) -> dict[str, object]:
    """Return non-destructive validation findings."""

    ai = [
        r.text
        for r in dataset.responses
        if r.author == "ai"
    ]

    human = [
        r.text
        for r in dataset.responses
        if r.author == "human"
    ]

    return {
        "name": dataset.name,

        "total_responses":
            len(dataset.responses),

        "ai_responses":
            len(ai),

        "human_responses":
            len(human),

        "balanced":
            len(ai) == len(human),

        "ai_duplicates":
            len(ai) - len(set(ai)),

        "human_duplicates":
            len(human) - len(set(human)),

        "empty_responses":
            sum(
                not r.text.strip()
                for r in dataset.responses
            ),

        "unrecognized_authors":
            sorted(
                {
                    r.author
                    for r in dataset.responses
                    if r.author
                    not in {"ai", "human"}
                }
            ),
    }