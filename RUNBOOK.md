# RUNBOOK — Classify a German vocabulary dataset and generate study tables

Reproducible instructions to take a **new German↔English vocabulary TSV** and produce
a three-column classified TSV plus study tables.

Example in this repo: the docs below refer to the current dataset (`A1.tsv`, 1936 words),
but every step is dataset-independent.

---

## 1. Assumptions

- Dataset is **German ↔ English** vocabulary.
- File is **UTF-8**, tab-separated, two columns: `German<TAB>English`.
- The **first line is a header** (any text — it is replaced).
- The word-type rules in `add_types.py` are German-specific; they do not need changes
  as long as the dataset is German.

## 2. Input — where the file goes

Put the dataset at the repo root and name it `A1.tsv`. That is the value of `PATH`
in all four scripts:

| Script | `PATH` (line ~4) | Purpose |
|---|---|---|
| `add_types.py` | `A1.tsv` | adds the `Type` column |
| `build_study.py` | `A1.tsv` | noun study table |
| `build_verbs.py` | `A1.tsv` | verb study table |
| `build_other.py` | `A1.tsv` | the 11 remaining types |

If the file has another name, edit `PATH` in all four scripts.

## 3. Process — commands

Run in this order (classification must run first; the builders read the `Type` column):

```bash
python add_types.py              # classify -> 3-column A1.tsv + by_type/*.md

python build_study.py            # draft for nouns
python build_study.py --merge    # -> study/nouns.md

python build_verbs.py            # draft for verbs
python build_verbs.py --merge    # -> study/verbs.md

python build_other.py            # drafts for the other 11 types
python build_other.py --merge    # -> study/<type>.md
```

Each builder is idempotent; re-running after edits is safe.

## 4. Authored content (per-dataset, not derivable)

The scripts auto-fill article/base/singular/plural/genitive, separable/reflexive and
meanings. **Example sentences and inflections are authored per row** and stored as
chunk files. They do not exist for a new dataset — the merge step prints
`missing <N>` rows instead. Fill them, then re-run the merge.

Row **IDs are the A1.tsv row order (1…N)** and are printed in the `missing` report.

| Table | Chunk location | One line per row |
|---|---|---|
| nouns | `study/_sentences/*.tsv` | `id<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| verbs | `study/verbs/_verbs/*.tsv` | `id<TAB>VERB_TYPE<TAB>ich<TAB>du<TAB>er<TAB>wir<TAB>ihr<TAB>sie<TAB>PRÄTERITUM<TAB>PARTIZIP_II<TAB>AUX<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| adjective | `study/adjective/_chunks/*.tsv` | `id<TAB>COMPARATIVE<TAB>SUPERLATIVE<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| adverb | `study/adverb/_chunks/*.tsv` | `id<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| article | `study/article/_chunks/*.tsv` | `id<TAB>TYPE<TAB>NOM_SG<TAB>ACC_SG<TAB>DAT_SG<TAB>GEN_SG<TAB>NOM_PL<TAB>ACC_PL<TAB>DAT_PL<TAB>GEN_PL<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| conjunction | `study/conjunction/_chunks/*.tsv` | `id<TAB>TYPE<TAB>WORD_ORDER<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| interjection | `study/interjection/_chunks/*.tsv` | `id<TAB>SITUATION<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| number | `study/number/_chunks/*.tsv` | `id<TAB>NUMBER_TYPE<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| particle | `study/particle/_chunks/*.tsv` | `id<TAB>PARTICLE_TYPE<TAB>FUNCTION<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| phrase-expression | `study/phrase-expression/_chunks/*.tsv` | `id<TAB>SITUATION<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| preposition | `study/preposition/_chunks/*.tsv` | `id<TAB>CASE<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| pronoun | `study/pronoun/_chunks/*.tsv` | `id<TAB>PRONOUN_TYPE<TAB>NOM<TAB>ACC<TAB>DAT<TAB>GEN<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |
| question-word | `study/question-word/_chunks/*.tsv` | `id<TAB>FUNCTION<TAB>DE_SENTENCE<TAB>EN_SENTENCE` |

Use `—` for not-applicable cells (e.g. no plural, non-comparable adjective).

## 5. Configuration — changes vs constants

**Stays the same for every dataset:**
- Input layout (`German<TAB>English` + header), the 13-type taxonomy,
  all four scripts, chunk formats above, the commands, and the output layout.
- German word-type rules (the word lists and special cases inside `add_types.py`).

**Must change for a new dataset:**
- The data file itself (and `PATH` if the name differs).
- The authored chunk files (section 4).

**Optional, only if the tools print problems:**
- When `add_types.py` prints `??` rows (word not recognised), classify them by adding
  the word to the matching set or to `SPECIAL` at the top of the script.
- `build_study.py` has small override maps (`ARTICLE_FIX`, `PLURAL_OVERRIDES`,
  `GENITIVE_OVERRIDES`) used to correct typos in the *current* source data. Only touch
  them if the new dataset shows wrong output.

## 6. Output

| Path | Content |
|---|---|
| `A1.tsv` | input + `Type` column (`German<TAB>English<TAB>Type`) |
| `by_type/*.md` | one word list per type (13 files) |
| `study/*.md` | study tables: `nouns`, `verbs`, `adjective`, `adverb`, `article`, `conjunction`, `interjection`, `number`, `particle`, `phrase-expression`, `preposition`, `pronoun`, `question-word` |
| `study/<type>/{_draft.tsv,_chunks|_sentences|_verbs}` | intermediate + authored data |

## 7. Validation

1. **Classification:** `python add_types.py` prints no `PROBLEM ROWS`.
2. **Merge completeness:** each builder's `--merge` prints `missing 0`.
3. **Row counts:** each `study/<type>.md` row count equals the number of rows of that
   `Type` in `A1.tsv`.
4. **No empty cells:** every cell is filled except deliberate `—`.
5. **Table shape:** every row in a table contains exactly one more `|` than it has
   columns (the column count is fixed per table by its builder spec).

Example of a passing run (current dataset): `build_study.py --merge` → 1124 noun rows,
`build_verbs.py --merge` → 313 verb rows, `build_other.py --merge` → 496 rows across
the 11 types, all `missing 0`.