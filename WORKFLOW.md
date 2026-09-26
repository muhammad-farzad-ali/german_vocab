# German Vocabulary Workflow — How This Project Was Built (Repeatable)

This document records exactly how the A1 German vocabulary project was created and
pushed, so the same steps can be repeated on future projects (B1, another language,
or any two-column vocabulary TSV).

---

## 1. What the project is

A Goethe-A1 German vocabulary list converted from a plain **two-column TSV**
(`German	English`) into a **three-column TSV** with a word-type column, and then
grouped into per-type Markdown files.

Scale: **1,936 words** classified into **13 word types**.

Artifacts:

| File | Purpose |
|---|---|
| `A1.tsv` | Main data: `German	English	Type` (header row) |
| `A1 copy.tsv` | Pristine original 2-column backup (do not edit) |
| `add_types.py` | Classifier + Markdown generator. Running it rebuilds everything |
| `by_type/*.md` | One Markdown file per word type listing the words |
| `.gitignore` | Ignore Python caches and editor/OS junk |

---

## 2. The type taxonomy (13 types)

| Type | Count | Example row |
|---|---|---|
| Noun | 1124 | `die Autobahn, -en	highway` |
| Verb | 317 | `heißen, er heißt, hat geheißen	to be called` |
| Adjective | 179 | `gut (Guten Tag!)	good` |
| Adverb | 112 | `leider	unfortunately` |
| Preposition | 52 | `mit (+ D.)	with` |
| Number | 34 | `zwanzig	twenty` |
| Phrase / expression | 32 | `guten Tag	Good day!` |
| Pronoun | 30 | `ich	I` |
| Article | 15 | `ein, eine	a` |
| Question word | 13 | `woher	from where` |
| Interjection | 10 | `hallo	hello` |
| Particle | 10 | `mal	sometime` |
| Conjunction | 8 | `aber	but` |

Notes:
- Proper nouns (countries `Deutschland`, languages `Spanisch`, months,
  weekdays) are folded into **Noun**.
- Separable verbs keep the `|` prefix marker, e.g. `zu|ordnen`.

---

## 3. How classification works

`add_types.py` reads `A1.tsv` and classifies each row with `classify(german, english)`.
The `head` (the word part before the first `(` or `,`) is used for list matching,
so parenthetical usage notes are stripped automatically, e.g. `kurz (Schreiben Sie
einen kurzen Text.)` → head `kurz`.

Priority chain (first match wins):

1. **`SPECIAL`** — exact-string overrides for context-dependent words where the
   same head word has two types, e.g.:
   - `klar (Kommst du heute? - Klar.)` → Adverb vs `klar (…Alles klar.)` → Adjective
   - `richtig (…richtig oder falsch?)` → Adjective vs `richtig (…richtig hungrig.)` → Adverb
   - `denn (Was denn?)` → Particle vs `denn (…, denn man kann…)` → Conjunction
2. **`PHRASE`** — greetings/formulas → `Phrase / expression`
3. **Verbs** — any of:
   - contains `|` (separable verb: `an|rufen`)
   - matches `, er/es/ich …` conjugation pattern (`gehen, er geht, ist gegangen`)
   - contains `(sich)` (reflexive: `freuen (sich)`)
   - ends with ` sein` (`erkältet sein`, `auf sein`)
   - head in `VERB_WORDS` (exceptions whose English doesn't start with "to ")
   - English starts with `to ` (and German is not capitalized)
4. **`ARTICLE` / `POSS`** — `der/die/das/den/dem/ein/kein/jede`; possessive forms
   like `sein, seine` (head + comma → Article)
5. **Closed-class lists** — Pronouns, Question words, Interjections, Particles,
   Conjunctions, Prepositions, Numbers (explicit word sets)
6. **`ADJ` then `ADV`** — headword lists for adjectives and adverbs
7. **Nouns** — article + following Capitalized word (`die Flasche`, `der/die Kranke`),
   or any German word starting with a capital letter (proper nouns)
8. **Fallback** — returns `??<head>`; the script prints these rows so you can fix them

Current state: **zero** `??` fallback rows.

### Edge cases handled explicitly
- One row's German cell contains an embedded tab (`der Mann, -er (Mann<TAB>bin ich froh!)"`).
  The script reconstructs it exactly so column 2 (English) is not lost.
- Imported rows can contain a trailing double quote (`Wort, -er"`); they are
  stripped only for classification and preserved in the output.
- Re-running is **idempotent** (the script also repairs/regenerates the file, so
  double-runs don't duplicate rows).

---

## 4. How to regenerate

Requirements: Python 3.

```bash
python add_types.py
```

This:
1. rebuilds `A1.tsv` (3 columns, header `German	English	Type`),
2. rewrites all `by_type/*.md` files (one per type, bullets `- German — English`),
3. prints any unclassified `??` rows for manual fixing.

---

## 5. Repeat on a future project

1. Put your 2-column vocab file in a fresh folder, e.g. `B1/B1.tsv`
   (columns: `German	English`).
2. Copy `add_types.py` next to it.
3. Edit the top of the script:
   - `PATH = "B1.tsv"`
   - `FOLDER = "by_type"`
4. Run it. It writes `B1.tsv` with the `Type` column.
5. Check the printed `??` rows and classify them:
   - Best fix: nothing — most unclassified rows are just missing from a word list.
     Add the head word to the matching set (`ADJ`, `ADV`, ...).
   - For context-dependent words (same word, two types), add the exact German
     string to `SPECIAL`.
6. Re-run until the script reports no problems, then use the generated
   `by_type/*.md` files for flashcards/docs.

---

## 6. Git + GitHub setup (used for this repo)

The vocab repo is **dedicated** — it was initialized inside its own folder and has
nothing to do with the parent `D:\personal_projects` monorepo.

```bash
# in the project folder
git init
git add .
git commit -m "first commit"

# single default branch "main"
git branch -M main

# wire up remote
git remote add origin git@github.com:<user>/<repo>.git

# first push, set tracking
git push -u origin main
```

`.gitignore` used (Python + editor/OS):

```gitignore
# Python
__pycache__/
*.py[cod]
.ruff_cache/

# Editors
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

### Gotcha: "Host key verification failed" on push

On a fresh machine the GitHub SSH host key may be missing from `known_hosts`,
which makes `git push` fail before it even checks credentials. Fix:

```bash
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
git push -u origin main
```

---

## 7. Lessons learned (from doing it the messy way)

- Keep a pristine copy of the input (`A1 copy.tsv`) before transforming data;
  it made verifying the final TSV trivial (`German/English` columns matched
  byte-for-byte).
- If a classifier script is run against an already-classified file, it can
  corrupt rows (duplicated type columns). Prefer scripts that write from a
  clean input, and make them idempotent.
- Validate after every run: expected line count, no empty cells, expected type
  distribution, and column count per row.