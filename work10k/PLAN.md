# 10k expansion — working plan (read this after any context reset)

User request (2026-11-07): re-rank using the 10k list (Fonzie-byte / Liam Rosen), add new words,
new columns, YouGlish links, fixed-preposition multiple-choice tab. Push to GitHub
(repo clone: /home/claude/5000_nederlandse_woorden_flashcards; pushes were REFUSED at start —
user asked to install Claude GitHub App; retry `git push` before each report).

Decisions (user agreed to all suggestions):
- Rank = best 10k-list position of any form of the lemma (lemmatized with simplemma).
- Names (capital-only in the list), brands, foreign words, single letters: excluded.
- Our words not in the 10k list: OPTION B = estimated position from old rank (estimate.py).
- Levels: same cutoffs; everything above 3750 = C1.
- New column `expression_type`: "expr = idiom|phrasal verb|collocation" items joined by " | ",
  covering fixed_combination items and, for separable/prepositional verbs, the verb itself.
- `synonyms`, `antonyms`: easy Dutch words, up to 2 each, "; " separated, blank if none.
- YouGlish: app builds https://youglish.com/pronounce/<word>/dutch/nl ; for multi-word
  expressions also link, with note "results may be inaccurate for phrases".
- Fixed prepositions: columns `fixed_preposition` (e.g. aan), `preposition_phrase`
  (deelnemen aan iets), `preposition_example_nl` (preposition marked **aan**), `preposition_example_en`.
  Exercise = separate tab, multiple choice (4 prepositions).

Files:
- build_rank.py -> ours_pos.csv, new_lemmas.csv ; filter_new.py -> new_candidates.csv
- estimate.py -> ours_ranked.csv (position for every existing word)
- enrich/eNNN.txt : enrichment lines for existing rows (ids = CURRENT ids from 5000_woorden.csv)
  format: id|synonyms|antonyms|expression_type|prep|prep_phrase|prep_ex_nl|prep_ex_en
- newwords/nNNN.py : full entries for new lemmas (batchlib helpers + extra kw)
- assemble.py : builds final data/woorden.csv with new ranks/ids
Progress log at bottom.

## Progress
- Follow-up scheduled: trig_01Ybi5hbMBF7ZTaao3nK4Woe at 2026-11-07T21:08Z. Push works (branch wip-10k-expansion).
- App updated (YouGlish, expression labels, synonyms/antonyms, Fixed prepositions tab) — committed on wip branch; app tolerates missing new columns.
- enrich e001 done (format: id|syn|ant|types|prep ~ phrase ~ nl ~ en; check with enrichlib.py check N; save with ./save.sh)
- 2026-11-07: ENRICHMENT COMPLETE — e001..e051 all validated and pushed (all 5,032 existing rows).
- Next: new 10k lemmas (Task 12) -> work10k/newwords/, then assemble.py (Task 13).
- assemble.py written: builds data/woorden.csv (renamed from 5000_woorden.csv; original frozen at work10k/base_5000.csv,
  enrichlib reads the frozen copy). README.md and data/codebook.md are GENERATED from work10k/templates/*.tmpl
  (WORDS_N/ROWS_N filled in) — edit the templates, not the outputs.
- New words: newwords/nNNN.py with ROWS built by newlib helpers (N/V/A/O + syn/ant/fx/xt/fp/p10/sense);
  check: python3 newlib.py check N ; then rerun assemble.py and commit.
