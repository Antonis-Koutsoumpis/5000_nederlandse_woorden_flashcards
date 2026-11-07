"""6000+ Nederlandse woorden — flashcards (Streamlit app).

Run locally with:  streamlit run app.py
"""
from __future__ import annotations

import importlib
import random
import re
from pathlib import Path
from urllib.parse import quote

import streamlit as st

import vocab

st.set_page_config(page_title="6000+ Nederlandse woorden", page_icon="🇳🇱", layout="centered")

# After an update on GitHub, a running Streamlit server can keep the *old* vocab.py
# in memory. Reload it once if a newer function is missing.
if not hasattr(vocab, "search_words") or "prep_only" not in vocab.filter_vocab.__code__.co_varnames:
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

# Estimated CEFR level, derived from the frequency rank (not stored in the CSV).
LEVEL_CUTOFFS = [(750, "A1"), (1500, "A2"), (2500, "B1"), (3750, "B2")]  # above 3750: C1
LEVELS = ["A1", "A2", "B1", "B2", "C1"]


def level_for_rank(rank: int) -> str:
    for upper, level in LEVEL_CUTOFFS:
        if rank <= upper:
            return level
    return "C1"


df = df.assign(level=df["rank"].map(lambda r: level_for_rank(int(r))))

MAX_RANK = int(df["rank"].max())
RANGE_PRESETS = {
    "1 – 500": (1, 500),
    "1 – 1000": (1, 1000),
    "1001 – 2000": (1001, 2000),
    "2001 – 3000": (2001, 3000),
    "3001 – 4000": (3001, 4000),
    "4001 – 5000": (4001, 5000),
    "5001 – 6000": (5001, 6000),
    f"6001 – {MAX_RANK}": (6001, MAX_RANK),
    "All words": (1, MAX_RANK),
    "Custom range": None,
}


# --------------------------------------------------------------------------- #
# Sidebar: practice settings
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("Practice settings")

    preset = st.selectbox("Frequency range", list(RANGE_PRESETS), index=list(RANGE_PRESETS).index("All words"),
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
    levels = st.multiselect("Level (estimated)", LEVELS, placeholder="All",
                            help="Estimated from frequency rank: A1 = 1–750, A2 = 751–1500, "
                                 "B1 = 1501–2500, B2 = 2501–3750, C1 = 3751+. "
                                 "Combined with the frequency range above.")
    pos = st.multiselect("Grammatical function", options(df, "pos"),
                         placeholder="All (choose one or more)")
    articles = st.multiselect("Nouns: de / het", options(df, "article"),
                              placeholder="All", help="Choosing one keeps only nouns.")
    verb_types = st.multiselect("Verbs: regular / irregular", options(df, "verb_type"),
                                placeholder="All", help="Choosing one keeps only verbs.")
    separable = st.multiselect("Verbs: separable", options(df, "separable"), placeholder="All")
    reflexive = st.multiselect("Verbs: reflexive", options(df, "reflexive"), placeholder="All")
    expr_types = st.multiselect("Expression type", ["idiom", "phrasal verb", "collocation"],
                                placeholder="All",
                                help="Keeps words with at least one expression of this type "
                                     "(shown under 'Fixed combinations' on the card).")
    fixed_only = st.checkbox("Only words with a fixed combination")
    prep_only = st.checkbox("Only words with a fixed preposition",
                            help="Words used with a fixed preposition (vast voorzetsel), "
                                 "e.g. 'deelnemen aan'.")
    er_het_only = st.checkbox("Only expressions with er / het")
    exclude_offensive = st.checkbox("Hide offensive words")

    st.caption(f"Data: `{data_name}` · {len(df)} entries")

filtered = filter_vocab(
    df, int(rank_min), int(rank_max),
    pos=pos, articles=articles, verb_types=verb_types,
    reflexive=reflexive, separable=separable,
    fixed_only=fixed_only, er_het_only=er_het_only,
    exclude_offensive=exclude_offensive,
    expr_types=expr_types, prep_only=prep_only,
)
if levels:
    filtered = filtered[filtered["level"].isin(levels)]


# --------------------------------------------------------------------------- #
# Deck state: a new random deck when settings change or on request
# --------------------------------------------------------------------------- #
settings_key = (rank_min, rank_max, n_cards, tuple(pos), tuple(articles), tuple(verb_types),
                tuple(reflexive), tuple(separable), fixed_only, er_het_only, exclude_offensive,
                tuple(levels), tuple(expr_types), prep_only)

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


def youglish_url(text: str) -> str:
    """YouGlish search for Dutch as spoken in the Netherlands (NL accent)."""
    return f"https://youglish.com/pronounce/{quote(str(text).strip())}/dutch/nl"


def split_items(text: str) -> list[str]:
    """Split 'a (x; y); b (z)' on semicolons that are not inside parentheses."""
    items, depth, cur = [], 0, ""
    for ch in str(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(depth - 1, 0)
        if ch == ";" and depth == 0:
            items.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        items.append(cur.strip())
    return [i for i in items if i]


def expression_types(row: dict) -> dict[str, str]:
    """'in aantocht zijn = idiom | opgeven = phrasal verb' -> {expr: type}."""
    out = {}
    for part in str(row.get("expression_type", "")).split("|"):
        if "=" in part:
            expr, kind = part.rsplit("=", 1)
            out[expr.strip().lower()] = kind.strip()
    return out


def dutch_part(item: str) -> str:
    """'in aantocht zijn (to be on the way)' -> 'in aantocht zijn'."""
    return re.sub(r"\s*\(.*$", "", item).strip()


def render_expressions(row: dict):
    items = split_items(row.get("fixed_combination", "")) if has_value(row.get("fixed_combination")) else []
    types = expression_types(row)
    # The verb itself can be labeled too (e.g. 'opgeven = phrasal verb').
    listed = {dutch_part(i).lower() for i in items}
    extra = [e for e in types if e not in listed]
    if not items and not extra:
        return
    lines = []
    for expr in extra:
        lines.append(f"- {md(expr)} · `{types[expr]}` · [🎧 YouGlish]({youglish_url(expr)})")
    for item in items:
        nl = dutch_part(item)
        kind = types.get(nl.lower())
        gloss = item[len(nl):].strip()
        line = f"- {md(nl)}" + (f" *{md(gloss)}*" if gloss else "")
        if kind:
            line += f" · `{kind}`"
        line += f" · [🎧 YouGlish]({youglish_url(nl)})"
        lines.append(line)
    st.markdown("**Fixed combinations:**  \n" + "\n".join(lines))
    st.caption("🎧 YouGlish searches work best for single words; results for phrases may be inaccurate.")


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
    if has_value(row.get("preposition_phrase")):
        lines.append(("Fixed preposition", row["preposition_phrase"]))
    lines += [("Synonyms", row.get("synonyms", "")),
              ("Antonyms", row.get("antonyms", "")),
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

    render_expressions(row)

    pron = [p for p in (row["ipa"], row["stress"]) if has_value(p)]
    yg = f"[🎧 Hear it in real conversations (YouGlish, NL)]({youglish_url(row['word'])})"
    if " " in str(row["word"]).strip():
        yg += " · results for phrases may be inaccurate"
    if pron:
        st.markdown(f"**Pronunciation:** {md(pron[0])}"
                    + (f" · stress: {md(pron[1])}" if len(pron) > 1 else "") + f"  \n{yg}")
    else:
        st.markdown(yg)

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
        right.caption(f"rank {first['rank']} · {first.get('level', '')}")
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
st.title("6000+ Nederlandse woorden")


# --------------------------------------------------------------------------- #
# Tab 1: search + flashcards
# --------------------------------------------------------------------------- #
def flashcards_tab():
    # Search: look up any word in the full list (ignores the practice filters)
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
            all_rows = {int(rank): grp.to_dict("records")
                        for rank, grp in df[df["rank"].isin(hits)].groupby("rank")}
            for i, rank in enumerate(hits):
                # The best match opens with its answer shown; others start closed.
                render_card(all_rows[rank], key=f"search_{query}_{rank}", default_shown=(i == 0))
        st.info("Clear the search box to go back to your flashcards.")
        return

    n_words = filtered["rank"].nunique()
    st.caption(f"Ranks {rank_min}–{rank_max} · {n_words} matching words ({len(filtered)} meanings)")
    if filtered.empty:
        st.warning("No words match these settings. Widen the range or remove a filter.")
        return

    c1, c2, c3 = st.columns(3)
    c1.button("🔀 New cards", on_click=new_deck, use_container_width=True)
    c2.button("Show all answers", on_click=set_all, args=(True,), use_container_width=True)
    c3.button("Hide all answers", on_click=set_all, args=(False,), use_container_width=True)

    if len(ss.deck) < n_cards:
        st.info(f"Only {len(ss.deck)} words match, so you get {len(ss.deck)} cards.")

    # Build the cards only for the words in the current deck (grouping the whole
    # filtered list on every click made the app slow for large ranges).
    deck_rows = filtered[filtered["rank"].isin(ss.deck)]
    by_rank = {int(rank): grp.to_dict("records") for rank, grp in deck_rows.groupby("rank")}
    for rank in ss.deck:
        if rank in by_rank:
            render_card(by_rank[rank])


# --------------------------------------------------------------------------- #
# Tab 2: fixed prepositions (vaste voorzetsels), multiple choice
# --------------------------------------------------------------------------- #
PREPOSITIONS = ["aan", "op", "in", "met", "van", "voor", "over", "naar", "om", "tot",
                "bij", "uit", "tegen", "door", "onder", "achter", "na", "tussen"]


def blank_out(sentence: str) -> str:
    """Replace the **marked** preposition(s) with a blank."""
    return re.sub(r"\*\*[^*]+\*\*", "_____", str(sentence))


def new_quiz(pool, n: int):
    ss.quiz_no = ss.get("quiz_no", 0) + 1
    rng = random.Random()
    picked = pool.sample(min(n, len(pool)), random_state=rng.randrange(1 << 30))
    quiz = []
    for row in picked.to_dict("records"):
        answer = row["fixed_preposition"].strip()
        others = [p for p in PREPOSITIONS if p != answer]
        opts = rng.sample(others, 3) + [answer]
        rng.shuffle(opts)
        quiz.append({"row": row, "answer": answer, "options": opts})
    ss.quiz = quiz
    ss.prep_answers = {}
    ss.quiz_key = ss.get("prep_settings")


def record_answer(key: str):
    ss.prep_answers[key] = ss.get(key)


def prepositions_tab():
    st.subheader("Fixed prepositions (vaste voorzetsels)")
    st.caption("Choose the preposition that belongs with the word. Uses the frequency range and "
               "filters from the sidebar.")
    if "fixed_preposition" not in df.columns:
        st.info("This data file has no fixed-preposition column yet.")
        return
    pool = filtered[filtered["fixed_preposition"].map(has_value)]
    if pool.empty:
        st.warning("No words with a fixed preposition match the current settings.")
        return
    n_q = st.number_input("Number of questions", 1, 50, 10, step=5, key="n_prep")
    ss.prep_settings = (settings_key, int(n_q))
    if ss.get("quiz_key") != ss.prep_settings or "quiz" not in ss or "prep_answers" not in ss:
        new_quiz(pool, int(n_q))
    st.button("🔀 New exercise", on_click=new_quiz, args=(pool, int(n_q)))
    st.caption(f"{len(pool)} words with a fixed preposition in this selection.")

    answered = 0
    score = 0
    for i, q in enumerate(ss.quiz):
        row = q["row"]
        key = f"q_{ss.quiz_no}_{i}"
        phrase = re.sub(rf"\b{re.escape(q['answer'])}\b", "_____", row["preposition_phrase"], count=1)
        with st.container(border=True):
            st.markdown(f"**{i + 1}. {md(phrase)}**  \n:gray[{md(row['english'])}]")
            if has_value(row.get("preposition_example_nl")):
                st.markdown(f"*{md(blank_out(row['preposition_example_nl']))}*")
            # The first answer is stored and the question is locked, so feedback is immediate
            # and can't be changed by clicking again.
            choice = ss.prep_answers.get(key)
            if choice is None:
                st.radio("Preposition", q["options"], index=None, horizontal=True, key=key,
                         label_visibility="collapsed", on_change=record_answer, args=(key,))
            else:
                st.radio("Preposition", q["options"], index=q["options"].index(choice),
                         horizontal=True, key=f"{key}_locked", label_visibility="collapsed",
                         disabled=True)
            if choice is not None:
                answered += 1
                if choice == q["answer"]:
                    score += 1
                    st.success(f"✅ Correct: {md(row['preposition_phrase'])}")
                else:
                    st.error(f"❌ The answer is **{q['answer']}**: {md(row['preposition_phrase'])}")
                if has_value(row.get("preposition_example_nl")):
                    st.caption(f"{md(row['preposition_example_nl'])} · {md(row.get('preposition_example_en', ''))}")

    st.metric("Score", f"{score} / {answered}",
              help=f"{answered} of {len(ss.quiz)} questions answered")
    if answered == len(ss.quiz):
        st.success(f"Done! You got {score} of {len(ss.quiz)} right. Press 'New exercise' to try more.")


tab_cards, tab_prep = st.tabs(["🃏 Flashcards", "🧩 Fixed prepositions"])
with tab_cards:
    flashcards_tab()
with tab_prep:
    prepositions_tab()
