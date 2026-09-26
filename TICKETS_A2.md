# Implementation tickets — a2 dataset

Applies the documented workflow (see `RUNBOOK.md`) to the fresh dataset
`a2.tsv` at the repo root. The A1 outputs were cleared; all `study/` and
`by_type/` output is regenerated from scratch.

## Dataset facts

- Source file: `a2.tsv` (never modified; copy preserved as input reference).
- Format: UTF-8 TSV, `German<TAB>English`, header on line 1, all rows 2-column
  (no embedded tabs, no trailing empty column).
- Row count: 1,476 vocabulary rows.
- Notation differences vs A1 that the pipeline must handle:
  - plural/Sg/Pl markers use `(Singular)` / `(Plural)` (not `(Sg.)` / `(Pl.)`),
  - noun plurals often given inline with umlauts (`-würste`, `Töpfe`,
    `-bücher`, `Eindrücke`) instead of A1's `-er"` quote convention,
  - separable verbs marked inside the conjugation paren (`geht weiter`,
    `nimmt heraus`) rather than with `|`.

---

## T0 — De-genericize the pipeline (edits to the 4 shared scripts)

Remove A1-specific hardcoding that would corrupt a fresh dataset:

- `add_types.py`:
  - remove the `Bulgarisch` prepend block,
  - remove the `der Mann, -er (Mann…` special-case row rewrite,
  - remove the consecutive-duplicate-row skip (keep blank-line skip),
  - prune stale A1 `SPECIAL` exact-string entries.
- `build_study.py`:
  - plural/Sg/Pl detection accepts `(Singular)` and `(Plural)`,
  - plural derivation handles inline-umlaut suffixes (replace matching base
    tail) alongside the existing quote-marker rule.
- `build_verbs.py`:
  - drop the A1 `EXCLUDE` list,
  - derive the separable prefix from conjugation parens (`geht weiter` →
    prefix `weiter`).
- `build_other.py`:
  - disable the `EXTRA_ARTICLE` injection of `sein, seine`.

Validation: no phantom rows; `python add_types.py` on a2 produces one row per
source row (no dedup/prepend); noun plurals like `Currywurst → die
Currywürste`, `Topf → die Töpfe`.

## T1 — Ingest

Copy `a2.tsv` → `A1.tsv` (the `PATH` used by all scripts). Verify line count and
2-column shape. `a2.tsv` remains untouched.

## T2 — Classify

Run `python add_types.py`. The classifier prints `??` rows for words it cannot
type; classify them by adding the head word to the matching type set or to
`SPECIAL`. Aim: zero `??`. Commit.

## T3 — Nouns

- `python build_study.py`: auto-computes article/base/singular/plural/genitive.
- Review output, especially `(Singular)` / `(Plural)` rows and inline-umlaut
  plurals; add a2 cell-level overrides only where the source is wrong.
- Author sentences: `study/_sentences/chunk_*.tsv`, one line
  `id<TAB>DE_SENTENCE<TAB>EN_SENTENCE` per noun (IDs = A1.tsv row order).
- `--merge`, validate (rows == noun count, `missing 0`, no empty cells).
  Commit.

## T4 — Verbs

- `python build_verbs.py`: verify base/separable/reflexive extraction.
- Author conjugations + sentences: `study/verbs/_verbs/*.tsv`,
  `id<TAB>VERB_TYPE<TAB>ich<TAB>du<TAB>er<TAB>wir<TAB>ihr<TAB>sie<TAB>PRÄTERITUM<TAB>PARTIZIP_II<TAB>AUX<TAB>DE_SENTENCE<TAB>EN_SENTENCE`.
- Use a2's `(X, hat/ist Y)` data to derive präteritum/partizip/aux where visible.
- `--merge`, validate, commit.

## T5 — Other 11 types

- `python build_other.py` builds each draft; author per-type chunks
  `study/<slug>/_chunks/*.tsv` (`id<TAB>…` in the order defined by
  `build_other.py` `SPECS`): adjective comparative/superlative, article and
  pronoun declensions, preposition case, particle type+function,
  interjection/phrase situation, conjunction type+word order, number type,
  question-word function, plus DE/EN sentences for all.
- `--merge`, validate each, commit.

## T6 — Final validation

Per `RUNBOOK.md` §7: no `??` from classification; every `--merge` reports
`missing 0`; each `study/<type>.md` row count equals that type's count in
`A1.tsv`; every cell filled except deliberate `—`; `|`-count shape per table.
Final commit + push.