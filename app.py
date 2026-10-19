"""5000 Nederlandse woorden — flashcards (Streamlit app).

Run locally with:  streamlit run app.py
"""
from __future__ import annotations

import importlib
import random
from pathlib import Path

import streamlit as st

import vocab

st.set_page_config(page_title="5000 Nederlandse woorden", page_icon="🇳🇱", layout="centered")

# After an update on GitHub, a running Streamlit server can keep the *old* vocab.py
# in memory. Reload it once if a newer function is missing.
if not hasattr(vocab, "search_words"):
    vocab = importlib.reload(vocab)
if not hasattr(vocab, "search_words"):
    st.error("Your vocab.py is an older version without the search function. "
             "Upload the latest vocab.py to GitHub (same folder as app.py).")
    st.stop()

from vocab import (  # noqa: E402
    filter_vocab,
    find_data_file,
    has_value,
    highlight_dutch,
    load_vocab,
    options,
    sample_words,
    search_words,
)


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #
@st.cache_data
def get_data(path_str: str, modified: float):
    # 'modified' is only part of the cache key: a new/changed CSV reloads automatically.
    return load_vocab(path_str)


try:
    data_path = find_data_file(Path(__file__).parent)
    df = get_data(str(data_path), data_path.stat().st_mtime)
    data_name = data_path.name
except (FileNotFoundError, ValueError) as err:
    st.error(str(err))
    st.stop()

MAX_RANK = int(df["rank"].max())
RANGE_PRESETS = {
    "1 – 500": (1, 500),
    "1 – 1000": (1, 1000),
    "1001 – 2000": (1001, 2000),
    "2001 – 3000": (2001, 3000),
    "3001 – 4000": (3001, 4000),
    "4001 – 5000": (4001, 5000),
    "All words": (1, MAX_RANK),
    "Custom range": None,
}


# --------------------------------------------------------------------------- #
# Sidebar: practice settings
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("Practice settings")

    preset = st.selectbox("Frequency range", list(RANGE_PRESETS), index=1,
                          help="Rank 1 is the most frequent word in Dutch.")
    if RANGE_PRESETS[preset] is None:
        c1, c2 = st.columns(2)
        rank_min = c1.number_input("From rank", 1, MAX_RANK, 1, step=50)
        rank_max = c2.number_input("To rank", 1, MAX_RANK, min(1000, MAX_RANK), step=50)
        if rank_min > rank_max:
            rank_min, rank_max = rank_max, rank_min
    else:
        rank_min, rank_max = RANGE_PRESETS[preset]

    n_cards = st.number_input("Number of flashcards", min_value=1, max_value=100, value=10, step=5)

    st.subheader("Filters")
    pos = st.multiselect("Grammatical function", options(df, "pos"),
                         placeholder="All (choose one or more)")
    articles = st.multiselect("Nouns: de / het", options(df, "article"),
                              placeholder="All", help="Choosing one keeps only nouns.")
    verb_types = st.multiselect("Verbs: regular / irregular", options(df, "verb_type"),
                                placeholder="All", help="Choosing one keeps only verbs.")
    separable = st.multiselect("Verbs: separable", options(df, "separable"), placeholder="All")
    reflexive = st.multiselect("Verbs: reflexive", options(df, "reflexive"), placeholder="All")
    fixed_only = st.checkbox("Only words with a fixed combination")
    er_het_only = st.checkbox("Only expressions with er / het")
    exclude_offensive = st.checkbox("Hide offensive words")

    st.caption(f"Data: `{data_name}` · {len(df)} entries")

filtered = filter_vocab(
    df, int(rank_min), int(rank_max),
    pos=pos, articles=articles, verb_types=verb_types,
    reflexive=reflexive, separable=separable,
    fixed_only=fixed_only, er_het_only=er_het_only,
    exclude_offensive=exclude_offensive,
)


# --------------------------------------------------------------------------- #
# Deck state: a new random deck when settings change or on request
# --------------------------------------------------------------------------- #
settings_key = (rank_min, rank_max, n_cards, tuple(pos), tuple(articles), tuple(verb_types),
                tuple(reflexive), tuple(separable), fixed_only, er_het_only, exclude_offensive)

ss = st.session_state
ss.setdefault("deck_no", 0)


def new_deck():
    ss.deck_no += 1
    ss.deck = sample_words(filtered, int(n_cards), seed=random.randrange(1 << 30))
    ss.settings_key = settings_key


if ss.get("settings_key") != settings_key:
    new_deck()


def answer_key(rank: int) -> str:
    return f"show_{ss.deck_no}_{rank}"


def toggle(key: str):
    ss[key] = not ss.get(key, False)


def set_all(value: bool):
    for cid in ss.deck:
        ss[answer_key(cid)] = value


# --------------------------------------------------------------------------- #
# Card rendering
# --------------------------------------------------------------------------- #
def md(text: str) -> str:
    """Make data safe for Streamlit markdown ($ would trigger LaTeX)."""
    return str(text).replace("$", "\\$")


def detail_lines(row: dict) -> list[str]:
    pos_ = row["pos"]
    lines: list[tuple[str, str]] = []

    if pos_.startswith("noun") or pos_ == "abbreviation (noun)":
        lines += [("Article", row["article"]), ("Plural", row["plural"])]
    if pos_ in ("adjective", "indefinite numeral", "adverb"):
        lines += [("-e form", row["adj_e_form"]),
                  ("Comparative", row["comparative"]),
                  ("Superlative", row["superlative"])]
    if pos_ == "verb":
        participle = row["verb_past_participle"]
        if has_value(row["auxiliary"]) and has_value(participle):
            participle = f"({row['auxiliary']}) {participle}"
        lines += [("Present (ik)", row["verb_present_ik"]),
                  ("Past (ik)", row["verb_past_ik"]),
                  ("Past participle", participle)]
    lines += [("Fixed combination", row["fixed_combination"]),
              ("With er / het", row["er_het_combination"])]
    if pos_.startswith("noun") and str(row["plural"]).strip() in ("-", "—"):
        lines = [(l, "no plural" if l == "Plural" else v) for l, v in lines]
    return [f"**{label}:** {md(value)}" for label, value in lines if has_value(value)]


def render_answer(row: dict):
    head = f"**{md(row['pos']).capitalize()}**"
    if has_value(row["article"]):
        head += f" · {row['article']}"
    st.markdown(f"{head}  \n*{md(row['english'])}*")

    details = detail_lines(row)
    if details:
        st.markdown("  \n".join(details))

    pron = [p for p in (row["ipa"], row["stress"]) if has_value(p)]
    if pron:
        st.markdown(f"**Pronunciation:** {md(pron[0])}"
                    + (f" · stress: {md(pron[1])}" if len(pron) > 1 else ""))

    examples = []
    for i in (1, 2):
        nl, en = row[f"example{i}_nl"], row[f"example{i}_en"]
        if has_value(nl):
            nl = highlight_dutch(nl, row)
            line = f"{i}. {md(nl)}"
            if has_value(en):
                line += f"  \n   :gray[{md(en).replace('[', '(').replace(']', ')')}]"
            examples.append(line)
    if examples:
        st.markdown("**Examples:**  \n" + "\n".join(examples))

    if has_value(row["register"]):
        st.markdown(f":orange[⚠️ Register: {md(row['register'])}]")
    if has_value(row["notes"]):
        st.caption(md(row["notes"]))


def render_card(rows: list[dict], key: str | None = None, default_shown: bool = False):
    """One card per word; every matching function/meaning goes in the answer."""
    first = rows[0]
    key = key or answer_key(first["rank"])
    shown = ss.get(key, default_shown)
    ss[key] = shown
    with st.container(border=True):
        left, right = st.columns([5, 1])
        left.markdown(f"### {md(first['word'])}")
        right.caption(f"rank {first['rank']}")
        st.button("Hide answer" if shown else "Show answer", key=f"btn_{key}",
                  on_click=toggle, args=(key,), type="secondary" if shown else "primary")
        if shown:
            for i, row in enumerate(rows):
                if i:
                    st.divider()
                if len(rows) > 1:
                    st.caption(f"Meaning {i + 1} of {len(rows)}")
                render_answer(row)


# --------------------------------------------------------------------------- #
# Main page
# --------------------------------------------------------------------------- #
st.title("5000 Nederlandse woorden")

# --------------------------------------------------------------------------- #
# Search: look up any word in the full list (ignores the practice filters)
# --------------------------------------------------------------------------- #
s1, s2 = st.columns([3, 1])
query = s1.text_input("🔍 Search a word", placeholder="e.g. voorkomen, liep, huizen",
                      help="Finds the word itself, words starting with it, and inflected "
                           "forms (plurals, verb forms, -e forms). Accents are optional.")
search_english = s2.checkbox("Also English", help="Also search the English translations.")
if query.strip():
    hits = search_words(df, query, include_english=search_english)
    if not hits:
        st.warning(f"No words found for '{query}'.")
    else:
        st.caption(f"{len(hits)} result(s) for '{query}' (searching all words; filters ignored)"
                   + (" · showing the first 50" if len(hits) == 50 else ""))
        all_rows = {rank: grp.to_dict("records") for rank, grp in df[df["rank"].isin(hits)].groupby("rank")}
        for i, rank in enumerate(hits):
            # The best match opens with its answer shown; others start closed.
            render_card(all_rows[rank], key=f"search_{query}_{rank}", default_shown=(i == 0))
    st.info("Clear the search box to go back to your flashcards.")
    st.stop()
n_words = filtered["rank"].nunique()
st.caption(f"Ranks {rank_min}–{rank_max} · {n_words} matching words ({len(filtered)} meanings)")

if filtered.empty:
    st.warning("No words match these settings. Widen the range or remove a filter.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.button("🔀 New cards", on_click=new_deck, use_container_width=True)
c2.button("Show all answers", on_click=set_all, args=(True,), use_container_width=True)
c3.button("Hide all answers", on_click=set_all, args=(False,), use_container_width=True)

if len(ss.deck) < n_cards:
    st.info(f"Only {len(ss.deck)} words match, so you get {len(ss.deck)} cards.")

# Only the meanings that match the filters are shown (all of them when no filter is set).
by_rank = {rank: grp.to_dict("records") for rank, grp in filtered.groupby("rank")}
for rank in ss.deck:
    if rank in by_rank:
        render_card(by_rank[rank])
