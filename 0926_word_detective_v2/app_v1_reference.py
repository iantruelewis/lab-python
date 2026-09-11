# Probability AI/Human Word Detector
# ref: https://pai.stanford.edu/pai/share/oaYzTKOcexGsnJg5QaF9

# v1 specification:
    # * replicate basic UI and functionality from original application reference
    # * source and organize data sets for AI-written and Human-written responses
    # * develop basic streamlit / pandas / striprtf functionality
    # * launch v1 from terminal and configure local development workspace
    # * test functionality across all specifications and document results
    # * write v2 specs to improvement log and experiment with UI refactoring

######


import re
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st
from striprtf.striprtf import rtf_to_text


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Can You Spot the AI?",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# DATASETS
# --------------------------------------------------

DATASETS = {
    "Reddit: Like I'm 5": "data/reddit.rtf",
    "Medical Q&A": "data/medical.rtf",
    "Financial Q&A": "data/financial.rtf",
    "CS/AI Wikipedia": "data/wikipedia.rtf",
}


# --------------------------------------------------
# LOAD RTF FILE
# --------------------------------------------------

@st.cache_data
def load_rtf(filepath):

    path = Path(filepath)

    if not path.exists():
        return ""

    raw_rtf = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return rtf_to_text(raw_rtf)


# --------------------------------------------------
# PARSE DATASET
# --------------------------------------------------

def parse_dataset(text):

    """
    Extract AI and human responses.

    Expected structure:

    ai
    response text
    (Question: ...)

    human
    response text
    (Question: ...)
    """

    ai_responses = []
    human_responses = []

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Find every AI/Human label
    pattern = re.compile(
        r"(?im)^(ai|human)\s*$"
    )

    matches = list(pattern.finditer(text))

    for i, match in enumerate(matches):

        author = match.group(1).lower()

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        response = text[start:end].strip()

        # Remove the appended question
        response = re.split(
            r"\(Question:",
            response,
            flags=re.IGNORECASE
        )[0].strip()

        if not response:
            continue

        if author == "ai":
            ai_responses.append(response)

        elif author == "human":
            human_responses.append(response)

    return ai_responses, human_responses


# --------------------------------------------------
# WORD DETECTION
# --------------------------------------------------

def contains_word(text, word):

    """
    Check whether a response contains a word.

    Uses word boundaries so:

    'art' does not match 'article'
    """

    pattern = rf"\b{re.escape(word.lower())}\b"

    return bool(
        re.search(
            pattern,
            text.lower()
        )
    )


# --------------------------------------------------
# CALCULATE WORD STATISTICS
# --------------------------------------------------

def calculate_word_stats(
    word,
    ai_responses,
    human_responses
):

    ai_count = sum(
        contains_word(response, word)
        for response in ai_responses
    )

    human_count = sum(
        contains_word(response, word)
        for response in human_responses
    )

    total_ai = len(ai_responses)
    total_human = len(human_responses)

    p_ai = (
        ai_count / total_ai
        if total_ai else 0
    )

    p_human = (
        human_count / total_human
        if total_human else 0
    )

    if p_human > 0:
        ratio = p_ai / p_human
    else:
        ratio = None

    return {
        "word": word,
        "ai_count": ai_count,
        "human_count": human_count,
        "total_ai": total_ai,
        "total_human": total_human,
        "p_ai": p_ai,
        "p_human": p_human,
        "ratio": ratio
    }


# --------------------------------------------------
# GET ALL WORDS
# --------------------------------------------------

def extract_words(responses):

    words = []

    for response in responses:

        found_words = re.findall(
            r"\b[a-zA-Z]+\b",
            response.lower()
        )

        words.extend(found_words)

    return words


# --------------------------------------------------
# BUILD WORD TABLE
# --------------------------------------------------

@st.cache_data
def build_word_table(
    ai_responses_tuple,
    human_responses_tuple
):

    ai_responses = list(ai_responses_tuple)
    human_responses = list(human_responses_tuple)

    all_words = set(
        extract_words(ai_responses)
        +
        extract_words(human_responses)
    )

    rows = []

    for word in all_words:

        # Ignore very short words
        if len(word) < 3:
            continue

        stats = calculate_word_stats(
            word,
            ai_responses,
            human_responses
        )

        # Only include words that appear
        # in both datasets
        if (
            stats["p_ai"] > 0
            and
            stats["p_human"] > 0
        ):

            rows.append(stats)

    df = pd.DataFrame(rows)

    if not df.empty:

        df = df.sort_values(
            "ratio",
            ascending=False
        )

    return df


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("Can You Spot the AI? 🤖")

st.markdown(
    """
Compare how often words appear in AI-written
and human-written responses.

For each word, we estimate:

**P(W | AI)** = probability a response contains
the word, given that the response was written by AI.

**P(W | Human)** = probability a response contains
the word, given that the response was written by a human.
"""
)


# --------------------------------------------------
# DATASET SELECTOR
# --------------------------------------------------

dataset_name = st.radio(
    "Choose a dataset:",
    list(DATASETS.keys()),
    horizontal=True
)

filepath = DATASETS[dataset_name]

text = load_rtf(filepath)

ai_responses, human_responses = parse_dataset(text)


# --------------------------------------------------
# DATASET INFO
# --------------------------------------------------

st.divider()

st.subheader(dataset_name)

col1, col2 = st.columns(2)

col1.metric(
    "AI responses",
    len(ai_responses)
)

col2.metric(
    "Human responses",
    len(human_responses)
)


# --------------------------------------------------
# WORD SEARCH
# --------------------------------------------------

st.divider()

st.subheader("Try a word")

word = st.text_input(
    "Enter any word:",
    placeholder="Try 'super', 'special', 'because'..."
)

if word:

    word = word.strip().lower()

    stats = calculate_word_stats(
        word,
        ai_responses,
        human_responses
    )

    st.subheader(
        f'Worked Example: "{word}"'
    )

    st.markdown(
        f"""
### AI

The word **"{word}"** appears in
**{stats["ai_count"]} of {stats["total_ai"]}**
AI responses.

\[
P(W|AI)
=
\\frac{{{stats["ai_count"]}}}
{{{stats["total_ai"]}}}
=
{stats["p_ai"]:.3f}
\]

### Human

The word **"{word}"** appears in
**{stats["human_count"]} of {stats["total_human"]}**
human responses.

\[
P(W|Human)
=
\\frac{{{stats["human_count"]}}}
{{{stats["total_human"]}}}
=
{stats["p_human"]:.3f}
\]
"""
    )

    if stats["ratio"] is not None:

        st.metric(
            "AI / Human Ratio",
            f'{stats["ratio"]:.2f}x'
        )

    else:

        st.info(
            "This word did not appear in any human responses, "
            "so the ratio is undefined."
        )


# --------------------------------------------------
# BUILD RESULTS
# --------------------------------------------------

st.divider()

st.subheader(
    "Words AI Uses More Often"
)

with st.spinner(
    "Analyzing word probabilities..."
):

    df = build_word_table(
        tuple(ai_responses),
        tuple(human_responses)
    )


# --------------------------------------------------
# FILTER RESULTS
# --------------------------------------------------

if not df.empty:

    # Require meaningful appearance
    results = df[
        (df["ai_count"] >= 3)
        &
        (df["human_count"] >= 1)
    ].copy()

    results = results.sort_values(
        "ratio",
        ascending=False
    )

    display_df = results[
        [
            "word",
            "p_ai",
            "p_human",
            "ratio"
        ]
    ].copy()

    display_df.columns = [
        "Word",
        "P(Word | AI)",
        "P(Word | Human)",
        "AI / Human Ratio"
    ]

    st.dataframe(
        display_df.head(25),
        use_container_width=True,
        hide_index=True
    )

    if len(display_df) > 25:

        with st.expander(
            f"Show all {len(display_df)} words"
        ):

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

else:

    st.warning(
        "No word statistics could be calculated."
    )