# 5000 Nederlandse woorden — flashcards

A Streamlit app for practicing the 5,000 most frequent Dutch words with flashcards.

The word list is based on the Hazenberg & Hulstijn frequency list. Every entry has an English translation, grammar information, IPA pronunciation, and two example sentences with translations.

The repository is linked with the Streamlit app [5000 Nederlandse woorden](https://5000-nederlandse-woorden-flashcards.streamlit.app/).

## Features

- **Frequency range:** pick a preset (1–500, 1–1000, 1001–2000, …) or a custom rank range such as 300–700.
- **Estimated level (A1–C1):** every word gets a CEFR-style level estimated from its frequency rank, shown on each card next to the rank (e.g. `rank 2103 · B1`) and available as a filter. See *Estimated levels* below.
- **Number of cards:** choose how many random flashcards to draw.
- **Show / hide answers:** each card has one button that shows the answer and, clicked again, hides it. There are also buttons to show or hide all answers at once.
- **Structured answers:**
  - the grammatical function and the English translation (in italics)
  - nouns: de/het and plural
  - adjectives: -e form, comparative, superlative
  - verbs: present (ik), past (ik), past participle with hebben/zijn
  - fixed combinations and er/het expressions
  - pronunciation (IPA + stressed syllable)
  - two example sentences with the target word in **bold** in both Dutch and English
- **Search:** type any Dutch word (e.g. *voorkomen*) to look it up in the full list. Inflected forms also work (*liep* finds *lopen*, *huizen* finds *huis*), accents are optional, and you can tick *Also English* to search the translations. Search ignores the practice filters; clear the box to return to your flashcards.
- **Filters:** estimated level (one or more), grammatical function (one or more), de/het nouns, regular/irregular verbs, separable or reflexive verbs, words with a fixed combination, expressions with er/het, and an option to hide offensive words.

## Estimated levels

The level is **not** stored in the CSV; the app derives it from the frequency rank when it loads the data:

| Level | Ranks |
|---|---|
| A1 | 1–750 |
| A2 | 751–1500 |
| B1 | 1501–2500 |
| B2 | 2501–3750 |
| C1 | 3751 and higher |

This is a rough guide, not an official CEFR classification. Frequency and difficulty don't always match: some everyday words are relatively rare in corpora (e.g. *ontbijt*, rank 2103, B1), and some frequent words are formal (e.g. *derhalve*). The level filter is combined with the frequency range, so choose *All words* as the range to filter on level alone. To change the cutoffs, edit `LEVEL_CUTOFFS` in `app.py`.

## Run locally

```bash
git clone https://github.com/<your-username>/5000_nederlandse_woorden_flashcards.git
cd 5000_nederlandse_woorden_flashcards
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), click **Create app**, and choose this repository.
3. Set the main file path to `app.py` and deploy.

## Project structure

```
.
├── app.py              # Streamlit interface
├── vocab.py            # loading, filtering, sampling, bolding (no Streamlit)
├── merge_batches.py    # combines data/batches/*.csv into data/5000_woorden.csv
├── data/
│   ├── 5000_woorden.csv   # the merged word list (see below)
│   ├── codebook.md        # what every column in 5000_woorden.csv means
│   └── batches/           # batch_001.csv = ranks 1-100, batch_002.csv = 101-200, ...
├── requirements.txt
└── README.md
```

## Adding new batches

Put new batch files in `data/batches/` and run:

```bash
python merge_batches.py
```

This rebuilds `data/5000_woorden.csv` (sorted by rank, checked for duplicate ids). To use another output name: `python merge_batches.py data/other_name.csv`.

## The data file

The app reads the first file it finds, in this order:

1. `data/5000_woorden.csv` (the full list)
2. `data/dutch_vocab_pilot.csv` (the small pilot file, used only as a fallback)

The pilot file is no longer needed once `data/5000_woorden.csv` is in place.

The file is comma-separated UTF-8 with a BOM, so it opens correctly in Excel. It has 4,839 words in 5,032 rows. Every column is described in [`data/codebook.md`](data/codebook.md).

A word with several grammatical functions or meanings has one row per function, all sharing the same rank.

## Credits

Word list based on the frequency list by Suzanne Hazenberg and Jan Hulstijn. Translations, grammar, pronunciation and example sentences were generated with Claude and may contain occasional errors. Corrections are welcome via issues or pull requests.
