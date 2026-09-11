# Word Detective v2

Word Detective explores differences in word usage between AI-generated and human-written responses using response-level conditional probabilities.

## Milestone 2 — Analysis Engine

```text
RTF source
   ↓
ingestion.py
   ↓
Dataset / Response models
   ↓
analysis.py
   ↓
WordStats / DataFrame
   ↓
future Streamlit UI
```

### Core definitions

- P(W | AI) = AI responses containing W / total AI responses
- P(W | Human) = Human responses containing W / total Human responses

A response counts once regardless of how many times the word appears.

### Current metrics

- response support in each population
- conditional probability
- probability difference
- AI/Human ratio when defined
- log ratio when both probabilities are non-zero
- AI-only / human-only classification
- Wilson confidence intervals
- chi-square p-value when expected cell counts are sufficient

Sparse-word significance testing is intentionally conservative in this milestone. Multiple-comparison correction and Fisher's exact testing remain candidates for a later milestone.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
pytest
```

The original v1 implementation is retained as `app_v1_reference.py`.
