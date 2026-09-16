# Word Detective v3

Word Detective explores word-level differences between AI-generated and human-written responses.

## v3 changes

- Separates ingestion, domain models, statistical analysis, and Streamlit UI.
- Uses a sparse response × vocabulary presence matrix for repeated analysis.
- Keeps words observed in only one population instead of dropping them.
- Uses probability difference as the primary directional metric.
- Reports raw ratio only when its denominator is non-zero.
- Adds log2 ratio for interpretable symmetric association strength.
- Adds 95% Wilson intervals.
- Uses Fisher's exact test for sparse 2×2 tables and chi-square for denser tables.
- Applies Benjamini–Hochberg false-discovery-rate correction across word-level p-values.
- Adds configurable minimum word length and minimum response support.
- Adds dataset diagnostics and methodology documentation in the UI.
- Retains the original v1 application as `app_v1_reference.py`.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
streamlit run app.py
```

Run tests with:

```bash
pytest
```

## Statistical definition

For word W:

`P(W | AI) = AI responses containing W / total AI responses`

`P(W | Human) = Human responses containing W / total Human responses`

A response counts once regardless of how many times W occurs inside it.

The application describes associations within these datasets. It is not a trained classifier and should not be interpreted as proving that any particular word is inherently AI-generated.
