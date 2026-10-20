# Codebook: `5000_woorden.csv`

This codebook describes every column in `data/5000_woorden.csv`, the word list used by the [5000 Nederlandse woorden](https://5000-nederlandse-woorden-flashcards.streamlit.app/) app.

## File at a glance

| Property | Value |
|---|---|
| Format | Comma-separated values (CSV) |
| Encoding | UTF-8 with BOM (`utf-8-sig`), so accents and IPA display correctly in Excel |
| Rows | 5,032 (one row per meaning or grammatical function of a word) |
| Distinct words | 4,839 |
| Columns | 29 |
| Sort order | By `rank`, then by `id` |
| Language variety | Dutch as used in the Netherlands; English translations in American spelling |

## Unit of observation

Each row is **one meaning or grammatical function of a word**. A word with several functions has several rows sharing the same `rank` and `word`, for example:

| id | rank | word | pos | english |
|---|---|---|---|---|
| 0555-1 | 555 | voorkomen | verb | to occur; to happen; to appear (VOORkomen) |
| 0555-2 | 555 | voorkomen | verb | to prevent (voorKOmen) |
| 0555-3 | 555 | voorkomen | noun | appearance; look |

## Empty values

- **Blank cell**: the column does not apply to this row (e.g. `verb_type` for a noun).
- **`-` (hyphen)**: the column applies but there is no such form (e.g. `plural` = `-` for an uncountable noun, `comparative` = `-` for an adjective that is not compared, `verb_present_ik` = `-` for an impersonal verb such as *regenen*).

## Columns

### Identification and frequency

| Column | Type | Description | Values / example |
|---|---|---|---|
| `id` | text | Unique key for the row: four-digit rank, a hyphen, and the meaning number within that word. | `0555-2` = second meaning of the word at rank 555 |
| `rank` | integer | Frequency rank of the word (1 = most frequent). All meanings of a word share the same rank. Ranks 1–1921 follow the order of the source list. In the 2000–3000, 3000–4000 and 4000–5000 bands, words were ranked within their band by corpus frequency (`wordfreq` Zipf score), starting at 2001, 3001 and 4001. Gaps in the numbering are expected (duplicates in the source were merged). | `1` … `4978` |
| `frequency_band` | category | Frequency band of the word in the source list. | `0-2000`, `2000-3000`, `3000-4000`, `4000-5000` |

### Word and meaning

| Column | Type | Description | Values / example |
|---|---|---|---|
| `word` | text | The Dutch word in its dictionary form (infinitive for verbs, singular for nouns, base form for adjectives). A few entries are inflected forms or abbreviations because they appear that way in the source list. | `voorkomen`, `gezeten`, `d.w.z.` |
| `pos` | category | Grammatical function (part of speech) of this meaning. | `noun`, `verb`, `adjective`, `adverb`, `preposition`, `conjunction`, `numeral`, `indefinite numeral`, `interjection`, `abbreviation`, `abbreviation (noun)`, `article`, `particle`, `pronominal adverb`, `proper noun`, and pronoun types: `personal`, `possessive`, `reflexive`, `reciprocal`, `demonstrative`, `relative`, `interrogative`, `indefinite`, `emphatic pronoun` |
| `english` | text | English translation(s) of this meaning, separated by semicolons. Clarifications are in parentheses. | `to prevent (voorKOmen)` |

### Nouns

| Column | Type | Description | Values / example |
|---|---|---|---|
| `article` | category | Definite article. `de/het` means both are used, sometimes with different meanings (see `notes`). | `de`, `het`, `de/het`; blank for non-nouns |
| `plural` | text | Plural form. Alternatives are separated by `/`. `-` = no plural in normal use. | `huizen`, `-` |

### Adjectives

| Column | Type | Description | Values / example |
|---|---|---|---|
| `adj_e_form` | text | Inflected form used before nouns (the "-e form"). Same as the base form for adjectives that do not inflect. | `scheef` → `scheve` |
| `comparative` | text | Comparative form. `-` = not normally compared. | `groter` |
| `superlative` | text | Superlative form. `meest …` = formed with *meest*. | `grootst`, `meest gespannen` |

### Verbs

| Column | Type | Description | Values / example |
|---|---|---|---|
| `verb_present_ik` | text | Present tense, first person singular. Separable verbs are given in main-clause order; reflexive verbs include *me*. | `kom voor`, `schaam me` |
| `verb_past_ik` | text | Past tense, first person singular. Alternatives are separated by `/`. | `kwam voor`, `raadde / ried` |
| `verb_past_participle` | text | Past participle. | `voorgekomen` |
| `auxiliary` | category | Auxiliary verb for the perfect tense. `hebben/zijn` = both are used, depending on meaning or context (see `notes`). | `hebben`, `zijn`, `hebben/zijn`, `zijn/hebben` |
| `verb_type` | category | Conjugation type. `mixed` = weak past tense with a strong participle (or vice versa), e.g. *bakken – bakte – gebakken*. | `regular`, `irregular`, `mixed` |
| `reflexive` | category | Whether the verb is used with a reflexive pronoun (*zich*). | `yes` (always), `optional` (in some meanings), `no` |
| `separable` | category | Whether the verb is separable (*voorkomen → ik kom voor*). | `yes`, `no` |

### Fixed expressions

| Column | Type | Description | Values / example |
|---|---|---|---|
| `has_fixed_combination` | yes/no | `yes` if `fixed_combination` or `er_het_combination` contains something. | `yes`, `no` |
| `fixed_combination` | text | Common fixed combinations, idioms or collocations with this word, each followed by an English gloss in parentheses; several are separated by `;`. | `in de mode (in fashion); uit de mode (out of fashion)` |
| `er_het_combination` | text | Fixed expressions with *er* or *het*, including impersonal verbs. | `het regent (it's raining)`, `er is / er zijn (there is / there are)` |

### Pronunciation

| Column | Type | Description | Values / example |
|---|---|---|---|
| `ipa` | text | Pronunciation in the International Phonetic Alphabet (Netherlands Dutch), between slashes. `ˈ` marks the stressed syllable. | `/ˈvoːrkoːmə(n)/` |
| `stress` | text | The word split into syllables with `·`; the stressed syllable is in CAPITALS. | `VOOR·ko·men` |

### Example sentences

| Column | Type | Description | Values / example |
|---|---|---|---|
| `example1_nl` | text | First example sentence in Dutch (level A2–B2). The target word is marked with `**…**`. | `Dit woord **komt** vaak **voor** in kranten.` |
| `example1_en` | text | English translation of the first example; the corresponding word(s) are marked with `**…**`. | `This word **occurs** often in newspapers.` |
| `example2_nl` | text | Second example sentence in Dutch. | |
| `example2_en` | text | English translation of the second example. | |

The `**…**` markers are Markdown bold; the app shows these words in **bold**. A separable verb can have two marked parts in one sentence (`**komt** … **voor**`).

### Usage information

| Column | Type | Description | Values / example |
|---|---|---|---|
| `register` | text | Style or register label. Blank = neutral. Several labels are separated by `;`. The app's *Hide offensive words* option removes rows whose register contains `offensive`. | `formal`, `informal`, `literary`, `old-fashioned`, `vulgar`, `offensive`, `Flemish`, `legal`, `administrative`, `dated` |
| `notes` | text | Free-text notes: differences in meaning between articles or stress patterns, false friends, cultural background, everyday alternatives, and why a word ranks where it does (e.g. a form that is also the plural of another word). | `Also plural of 'land' (countries), the likely reason for its high frequency.` |

## Derived in the app (not in the CSV)

| Field | Description |
|---|---|
| `level` | Estimated CEFR level, calculated from `rank` when the app loads the data: A1 = 1–750, A2 = 751–1500, B1 = 1501–2500, B2 = 2501–3750, C1 = 3751+. This is a rough guide, not an official classification. The cutoffs are set in `LEVEL_CUTOFFS` in `app.py`. |

## Source and caveats

- **Word list**: based on the frequency list by Suzanne Hazenberg and Jan Hulstijn. Typos and duplicates were corrected; duplicates were merged under the higher rank, and the merge is mentioned in `notes`.
- **Generated content**: translations, grammar, IPA, register labels and example sentences were generated with Claude and checked automatically for completeness and consistency (required fields, valid values, balanced `**` markers). Occasional errors are possible.
- **Ranking in the 2000+ bands**: corpus frequencies count spelling forms, so a few words rank high because the same spelling is also a common form of another word or an English name (e.g. *landen*, *boeken*, *state*). This is explained in `notes` for each case.
