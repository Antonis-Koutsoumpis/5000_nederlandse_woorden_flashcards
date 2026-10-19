# 5000 Nederlandse woorden — flashcards

A Streamlit app for practicing the 5,000 most frequent Dutch words with flashcards.

The word list is based on the Hazenberg & Hulstijn frequency list. Every entry has an English translation, grammar information, IPA pronunciation, and two example sentences with translations.

## Features

- **Frequency range:** pick a preset (1–500, 1–1000, 1001–2000, …) or a custom rank range such as 300–700.
- **Number of cards:** choose how many random flashcards to draw.
- **Show / hide answers:** each card has one button that shows the answer and, clicked again, hides it. There are also buttons to show or hide all answers at once.
- **Structured answers:**
  - the grammatical function and the English translation (in italics)
  - nouns: de/het and plural
  - adjectives: -e form, comparative, superlative
  - verbs: present (ik), past (ik), past participle with hebben/zijn, regular/irregular, separable, reflexive
  - fixed combinations and er/het expressions
  - pronunciation (IPA + stressed syllable)
  - two example sentences with the target word in **bold** in both Dutch and English
- **Search:** type any Dutch word (e.g. *voorkomen*) to look it up in the full list. Inflected forms also work (*liep* finds *lopen*, *huizen* finds *huis*), accents are optional, and you can tick *Also English* to search the translations. Search ignores the practice filters; clear the box to return to your flashcards.
- **Filters:** grammatical function (one or more), de/het nouns, regular/irregular verbs, separable or reflexive verbs, words with a fixed combination, expressions with er/het, and an option to hide offensive words.

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
2. `data/dutch_vocab_pilot.csv` (the 51-word pilot)

To switch to the full list, add `data/5000_woorden.csv`; nothing in the code needs to change. You can delete the pilot file then.

The file is comma-separated UTF-8 with a BOM, so it opens correctly in Excel. Main columns:

| Column | Meaning |
|---|---|
| `id` | Unique key `RANK-MEANING`, e.g. `0555-2` = second meaning of the word at rank 555 |
| `rank` | Frequency rank (1 = most frequent). Words ranked 2001+ were ranked within their source band using corpus frequencies |
| `frequency_band` | Band in the source list: 0-2000, 2000-3000, 3000-4000, 4000-5000 |
| `word`, `pos`, `english` | Dutch word, grammatical function, English translation |
| `article`, `plural` | Nouns: de/het and plural (`-` = no plural) |
| `adj_e_form`, `comparative`, `superlative` | Adjectives |
| `verb_present_ik`, `verb_past_ik`, `verb_past_participle`, `auxiliary` | Verb forms; separable verbs in main-clause order (`kom voor`) |
| `verb_type`, `reflexive`, `separable` | regular/irregular/mixed; yes/no/optional; yes/no |
| `has_fixed_combination`, `fixed_combination`, `er_het_combination` | Fixed expressions |
| `ipa`, `stress` | IPA (Netherlands Dutch) and stressed syllable in capitals (`be·LO·ven`) |
| `example1_nl` … `example2_en` | Example sentences; `**…**` marks the target word |
| `register`, `notes` | e.g. "offensive", usage notes |

A word with several grammatical functions or meanings has one row per function, all sharing the same rank.

## Credits

Word list based on the frequency list by Suzanne Hazenberg and Jan Hulstijn. Translations, grammar, pronunciation and example sentences were generated with Claude and may contain occasional errors. Corrections are welcome via issues or pull requests.
