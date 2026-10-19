"""Data helpers for the 5000 Nederlandse woorden flashcard app.

Kept free of Streamlit so the logic can be tested on its own.
"""
from __future__ import annotations

import random
import re
from pathlib import Path

import pandas as pd

# The app uses the first file that exists.
DATA_CANDIDATES = [
    "data/5000_woorden.csv",
    "data/dutch_vocab_pilot.csv",
]

REQUIRED_COLUMNS = [
    "id", "rank", "frequency_band", "word", "pos", "english", "article", "plural",
    "adj_e_form", "comparative", "superlative",
    "verb_present_ik", "verb_past_ik", "verb_past_participle", "auxiliary",
    "verb_type", "reflexive", "separable", "has_fixed_combination",
    "fixed_combination", "er_het_combination", "ipa", "stress",
    "example1_nl", "example1_en", "example2_nl", "example2_en", "register", "notes",
]

# Values meaning "not applicable" in the data.
EMPTY_VALUES = {"", "-", "—", "nan", "NaN"}


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def find_data_file(base_dir: str | Path = ".") -> Path:
    base = Path(base_dir)
    for name in DATA_CANDIDATES:
        path = base / name
        if path.exists():
            return path
    raise FileNotFoundError(
        "No vocabulary file found. Put the CSV in one of: " + ", ".join(DATA_CANDIDATES)
    )


def load_vocab(path: str | Path) -> pd.DataFrame:
    # utf-8-sig strips the BOM that makes the file readable in Excel.
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")
    for col in df.columns:
        df[col] = df[col].str.strip()
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["rank"]).sort_values(["rank", "id"]).reset_index(drop=True)
    return df


def has_value(value: str | None) -> bool:
    return value is not None and str(value).strip() not in EMPTY_VALUES


# --------------------------------------------------------------------------- #
# Filtering and sampling
# --------------------------------------------------------------------------- #
def filter_vocab(
    df: pd.DataFrame,
    rank_min: int,
    rank_max: int,
    pos: list[str] | None = None,
    articles: list[str] | None = None,
    verb_types: list[str] | None = None,
    reflexive: list[str] | None = None,
    separable: list[str] | None = None,
    fixed_only: bool = False,
    er_het_only: bool = False,
    exclude_offensive: bool = False,
) -> pd.DataFrame:
    """Return the rows that match every active filter.

    Empty lists / False mean "no filter". Noun- and verb-specific filters keep
    only rows where that property is filled in (e.g. choosing 'het' keeps only
    het-nouns).
    """
    out = df[(df["rank"] >= rank_min) & (df["rank"] <= rank_max)]
    if pos:
        out = out[out["pos"].isin(pos)]
    if articles:
        out = out[out["article"].isin(articles)]
    if verb_types:
        out = out[out["verb_type"].isin(verb_types)]
    if reflexive:
        out = out[out["reflexive"].isin(reflexive)]
    if separable:
        out = out[out["separable"].isin(separable)]
    if fixed_only:
        out = out[out["has_fixed_combination"] == "yes"]
    if er_het_only:
        out = out[out["er_het_combination"].map(has_value)]
    if exclude_offensive:
        out = out[~out["register"].str.contains("offensive", case=False)]
    return out


def sample_ids(df: pd.DataFrame, n: int, seed: int | None = None) -> list[str]:
    ids = df["id"].tolist()
    rng = random.Random(seed)
    return rng.sample(ids, min(n, len(ids)))


def options(df: pd.DataFrame, col: str) -> list[str]:
    """Sorted distinct non-empty values of a column, for filter widgets."""
    return sorted(v for v in df[col].unique() if has_value(v))


# --------------------------------------------------------------------------- #
# Bolding the target word in example sentences
# --------------------------------------------------------------------------- #
_SPLIT_RE = re.compile(r"\s*(?:/|,|;)\s*")
_PAREN_RE = re.compile(r"\([^)]*\)")
_SKIP_TOKENS = {"er", "het", "me", "je", "zich", "ons", "...", "…", "-", "—"}
_PARTICLES = {"aan", "af", "bij", "door", "in", "mee", "na", "om", "op", "over", "terug",
              "toe", "uit", "voor", "weg", "samen", "tegen", "vast", "los", "neer", "achter"}
_VOWELS = "aeiou"


def _tokens(value: str) -> list[str]:
    out = []
    for part in _SPLIT_RE.split(_PAREN_RE.sub("", value or "")):
        for tok in part.split():
            tok = tok.strip(".,!?'\"")
            if tok and tok.lower() not in _SKIP_TOKENS:
                out.append(tok)
    return out


def _past_plurals(past: str) -> set[str]:
    """Guess past-plural forms: liep -> liepen, begon -> begonnen, keek -> keken."""
    p = past.lower()
    if p.endswith(("de", "te")):
        return {p + "n"}
    forms = {p + "en"}
    if len(p) >= 2 and p[-1] not in _VOWELS:
        forms.add(p + p[-1] + "en")                      # begon -> begonnen
        if len(p) >= 3 and p[-2] == p[-3] and p[-2] in _VOWELS:
            forms.add(p[:-2] + p[-1] + "en")             # keek -> keken
    return forms


def target_forms(row: dict) -> tuple[set[str], set[str]]:
    """Return (core forms, separable particles) of a row's word."""
    core: set[str] = set()
    particles: set[str] = set()
    word = row.get("word", "")
    core.add(word.lower())
    core.update(t.lower() for t in _tokens(word))
    for col in ("plural", "adj_e_form", "comparative", "superlative", "verb_past_participle"):
        core.update(t.lower() for t in _tokens(row.get(col, "")))

    if row.get("pos") == "verb":
        for col in ("verb_present_ik", "verb_past_ik"):
            toks = [t.lower() for t in _tokens(row.get(col, ""))]
            for t in toks:
                if row.get("separable") == "yes" and t in _PARTICLES:
                    particles.update({t, "er" + t})        # uit -> eruit
                else:
                    core.add(t)
                    if col == "verb_present_ik":
                        core.update({t + "t", t + "en"})
                    else:
                        core.update(_past_plurals(t))
        core.add(word.lower()[:-1] + "t")               # gaan -> gaat, zien -> ziet
        if word.endswith("en"):
            core.add(word[:-2] + "end")                  # present participle
        part = row.get("verb_past_participle", "")
        if has_value(part):
            core.add(part.lower() + "e")
    if row.get("pos") in ("adjective", "indefinite numeral"):
        core.update({word.lower() + "e", word.lower() + "er", word.lower() + "st"})
    return {f for f in core if len(f) > 1}, particles


def _bold(sentence: str, forms: set[str]) -> tuple[str, bool]:
    if not forms:
        return sentence, False
    pattern = re.compile(
        r"(?<!\w)(" + "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True)) + r")(?!\w)",
        re.IGNORECASE,
    )
    new, n = pattern.subn(r"**\1**", sentence)
    return new, n > 0


def highlight_dutch(sentence: str, row: dict) -> str:
    """Bold the target word. Markers already in the data (**...**) win."""
    if not has_value(sentence) or "**" in sentence:
        return sentence
    core, particles = target_forms(row)
    new, found = _bold(sentence, core)
    if found and particles:
        new, _ = _bold(new, particles)
    return new


def strip_markers(text: str) -> str:
    return text.replace("**", "") if isinstance(text, str) else text
