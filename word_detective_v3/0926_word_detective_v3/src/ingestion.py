import re
from pathlib import Path

from striprtf.striprtf import rtf_to_text

from .models import Dataset, DatasetValidation, Response

AUTHOR_PATTERN = re.compile(r"(?im)^\s*(ai|human)\s*$")
QUESTION_PATTERN = re.compile(r"\(Question:", re.IGNORECASE)


def load_rtf(path: str | Path) -> str:
    path = Path(path)
    raw_rtf = path.read_text(encoding="utf-8", errors="ignore")
    return rtf_to_text(raw_rtf)


def _strip_question(text: str) -> tuple[str, bool]:
    match = QUESTION_PATTERN.search(text)
    if match is None:
        return text.strip(), False
    return text[:match.start()].strip(), True


def parse_responses(text: str) -> tuple[Response, ...]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    matches = list(AUTHOR_PATTERN.finditer(normalized))
    responses: list[Response] = []

    for index, match in enumerate(matches):
        author = match.group(1).lower()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
        raw_response = normalized[start:end].strip()
        response, _ = _strip_question(raw_response)
        if response:
            responses.append(Response(author=author, text=response))

    return tuple(responses)


def load_dataset(name: str, path: str | Path) -> Dataset:
    return Dataset(name=name, responses=parse_responses(load_rtf(path)))


def validate_dataset(dataset: Dataset) -> DatasetValidation:
    ai = [r.text for r in dataset.responses if r.author == "ai"]
    human = [r.text for r in dataset.responses if r.author == "human"]
    question_markers_removed = sum(
        1 for response in dataset.responses if QUESTION_PATTERN.search(response.text) is None
    )
    return DatasetValidation(
        name=dataset.name,
        total_responses=len(dataset.responses),
        ai_responses=len(ai),
        human_responses=len(human),
        balanced=len(ai) == len(human),
        ai_duplicates=len(ai) - len(set(ai)),
        human_duplicates=len(human) - len(set(human)),
        empty_responses=sum(not r.text.strip() for r in dataset.responses),
        question_markers_removed=question_markers_removed,
    )
