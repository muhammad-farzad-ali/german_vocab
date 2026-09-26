# Implementation tickets — B1 dataset

Applies the documented workflow (see `RUNBOOK.md`) to the fresh dataset `B1.tsv`.

## Dataset facts

- Source file: `B1.tsv` (never modified; copied to `A1.tsv` for the pipeline).
- Format: UTF-8 TSV, `German<TAB>English`, header on line 1, all rows 2-column.
- Word count: 1,807.
- Notation follows the a2 conventions (already supported by the pipeline):
  - `(Singular)` (163 rows) / `(Plural)` (14 rows),
  - inline-umlaut plurals (`der Urgroßvater, -väter`),
  - reflexive verbs via `(sich)` (29 rows),
  - verb conjugation in parens — B1 uses **three** forms: `sauber halten
    (hält sauber, hielt sauber, hat sauber gehalten)` (Präteritum included).

---

## T1 — Ingest + classify

1. Copy `B1.tsv` → `A1.tsv`.
2. Run `python add_types.py`; extend the per-dataset `TRIAGE` map in `add_types.py`
   until no `??` PROBLEM ROWS are printed.
3. Commit.

## T2 — Nouns

- `python build_study.py`; review auto article/base/plural/genitive, especially
  `(Singular)` / `(Plural)` rows and inline-umlaut plurals.
- Add B1 cell-level `PLURAL_OVERRIDES` / `GENITIVE_OVERRIDES` only where wrong.
- Author sentences: `study/_sentences/chunk_*.tsv`, `id<TAB>DE_SENTENCE<TAB>EN_SENTENCE`.
- `--merge`, validate (rows == noun count, `missing 0`, no empty cells). Commit.

## T3 — Verbs

- `python build_verbs.py`; verify base/separable/reflexive and that the 3-form parens
  still supply aux/partizip. Optionally auto-parse Präteritum from them into the draft.
- Author `study/verbs/_verbs/*.tsv`: `id<TAB>VERB_TYPE<TAB>ich<TAB>du<TAB>er<TAB>wir<TAB>ihr<TAB>sie<TAB>PRÄTERITUM<TAB>PARTIZIP_II<TAB>AUX<TAB>DE_SENTENCE<TAB>EN_SENTENCE`.
- `--merge`, validate, commit.

## T4 — Other 11 types

- `python build_other.py`; author `study/<slug>/_chunks/*.tsv` per `SPECS` order
  (adjective comparatives/superlatives, adverb sentences, article/pronoun
  declensions, preposition case, conjunction type+word order, particle
  type+function, interjection/phrase situation, number type, question-word
  function, plus DE/EN sentences).
- `--merge`, validate each, commit.

## T5 — Output + final validation

- Copy the 13 `study/*.md` tables into `output/`.
- Per `RUNBOOK.md` §7: no `??` from classification; every merge reports `missing 0`;
  row counts match B1 type counts; no empty cells; `|`-count shape per table.
- Commit + push.