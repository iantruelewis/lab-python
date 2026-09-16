from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import build_word_table, calculate_word_stats, normalize_word, top_words
from src.ingestion import load_dataset, validate_dataset

st.set_page_config(page_title="Word Detective", page_icon="🔎", layout="wide")

BASE_DIR = Path(__file__).parent
DATASETS = {
    "Reddit: Like I'm 5": BASE_DIR / "data" / "reddit.rtf",
    "Medical Q&A": BASE_DIR / "data" / "medical.rtf",
    "Financial Q&A": BASE_DIR / "data" / "financial.rtf",
    "CS/AI Wikipedia": BASE_DIR / "data" / "wikipedia.rtf",
}

st.title("Word Detective")
st.caption("Explore word-level differences between AI-generated and human-written responses.")

@st.cache_data(show_spinner=False)
def get_dataset(name: str):
    return load_dataset(name, DATASETS[name])

@st.cache_data(show_spinner=False)
def get_table(name: str, minimum_length: int, minimum_support: int):
    return build_word_table(get_dataset(name), minimum_length, minimum_support)

with st.sidebar:
    st.header("Dataset")
    dataset_name = st.selectbox("Choose a dataset", list(DATASETS))
    st.divider()
    st.header("Analysis settings")
    minimum_length = st.slider("Minimum word length", 2, 10, 3)
    minimum_support = st.slider("Minimum response support", 1, 50, 5)
    st.caption("Support is the number of responses containing the word. A response counts once, regardless of repetitions.")

dataset = get_dataset(dataset_name)
validation = validate_dataset(dataset)
table = get_table(dataset_name, minimum_length, minimum_support)

c1, c2, c3, c4 = st.columns(4)
c1.metric("AI responses", f"{validation.ai_responses:,}")
c2.metric("Human responses", f"{validation.human_responses:,}")
c3.metric("Vocabulary", f"{len(table):,}")
c4.metric("Balanced", "Yes" if validation.balanced else "No")

st.markdown("### Investigate a word")
word = st.text_input("Enter a word", placeholder="e.g. super").strip()

if word:
    stats = calculate_word_stats(dataset, word)
    left, right = st.columns(2)
    with left:
        st.subheader(f'“{stats.word}”')
        a, b = st.columns(2)
        a.metric("P(word | AI)", f"{stats.p_ai:.1%}", f"{stats.ai_count:,} / {stats.total_ai:,}")
        b.metric("P(word | Human)", f"{stats.p_human:.1%}", f"{stats.human_count:,} / {stats.total_human:,}")
    with right:
        st.subheader("Association")
        a, b = st.columns(2)
        a.metric("Difference", f"{stats.difference:+.1%}")
        b.metric("Ratio", "undefined" if stats.ratio is None else f"{stats.ratio:.2f}×")
        st.caption("Positive difference means the word appears in a larger share of AI responses; negative means human responses.")
    st.write("**95% Wilson intervals**")
    interval = pd.DataFrame({
        "Group": ["AI", "Human"],
        "Probability": [stats.p_ai, stats.p_human],
        "Lower": [stats.ai_ci_low, stats.human_ci_low],
        "Upper": [stats.ai_ci_high, stats.human_ci_high],
    })
    st.dataframe(interval.style.format({"Probability": "{:.2%}", "Lower": "{:.2%}", "Upper": "{:.2%}"}), hide_index=True, use_container_width=True)
    if stats.p_value is not None:
        st.caption(f"Two-sided association test p = {stats.p_value:.4g}. Use the ranked table's q-value for multiple-comparison-adjusted interpretation.")
    else:
        st.caption("No p-value is available for this word.")

st.markdown("### What stands out?")
if table.empty:
    st.info("No words meet the current filters.")
else:
    left, right = st.columns(2)
    with left:
        st.subheader("More associated with AI")
        ai_view = top_words(table, 15, "ai")[["word", "ai_count", "human_count", "p_ai", "p_human", "difference", "q_value"]]
        st.dataframe(ai_view.style.format({"p_ai":"{:.2%}", "p_human":"{:.2%}", "difference":"{:+.2%}", "q_value":"{:.3g}"}), hide_index=True, use_container_width=True)
    with right:
        st.subheader("More associated with humans")
        human_view = top_words(table, 15, "human")[["word", "ai_count", "human_count", "p_ai", "p_human", "difference", "q_value"]]
        st.dataframe(human_view.style.format({"p_ai":"{:.2%}", "p_human":"{:.2%}", "difference":"{:+.2%}", "q_value":"{:.3g}"}), hide_index=True, use_container_width=True)

st.markdown("### Full vocabulary")
show = table[["word", "ai_count", "human_count", "p_ai", "p_human", "difference", "ratio", "log2_ratio", "p_value", "q_value", "ai_only", "human_only"]]
st.dataframe(
    show.style.format({
        "p_ai":"{:.2%}", "p_human":"{:.2%}", "difference":"{:+.2%}",
        "ratio": lambda x: "—" if pd.isna(x) else f"{x:.2f}×",
        "log2_ratio": lambda x: "—" if pd.isna(x) else f"{x:+.2f}",
        "p_value": lambda x: "—" if pd.isna(x) else f"{x:.3g}",
        "q_value": lambda x: "—" if pd.isna(x) else f"{x:.3g}",
    }),
    hide_index=True,
    use_container_width=True,
    height=520,
)

with st.expander("Dataset diagnostics"):
    st.write({
        "Dataset": validation.name,
        "Total responses": validation.total_responses,
        "AI responses": validation.ai_responses,
        "Human responses": validation.human_responses,
        "Balanced": validation.balanced,
        "Duplicate AI responses": validation.ai_duplicates,
        "Duplicate human responses": validation.human_duplicates,
        "Empty responses": validation.empty_responses,
    })

with st.expander("Methodology"):
    st.markdown("""
**Unit of observation:** response. A word contributes one positive observation if it appears anywhere in the response, regardless of how many times it is repeated.

**Conditional probability:** `P(W | AI) = AI responses containing W / total AI responses`; the human calculation is analogous.

**Difference:** `P(W | AI) − P(W | Human)`. This is the primary directional measure because it remains defined when one group has zero observations.

**Ratio:** `P(W | AI) / P(W | Human)`. It is shown only when the human probability is non-zero; a zero denominator is not silently converted into an arbitrary value.

**Log2 ratio:** `log2(P(W | AI) / P(W | Human))`, shown when both probabilities are non-zero. Positive values favor AI; negative values favor human.

**Uncertainty:** 95% Wilson intervals are used for the two conditional probabilities.

**Association testing:** sparse 2×2 tables use Fisher's exact test; denser tables use chi-square. Benjamini–Hochberg false-discovery-rate correction produces `q_value` across the displayed vocabulary table.

These statistics describe associations in these datasets. They do not constitute a classifier or establish that a particular word is intrinsically an “AI word.”
""")

st.caption("Word Detective v3 · analytical engine separated from the interface")
