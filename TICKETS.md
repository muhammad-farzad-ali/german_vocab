# Implementation tickets — study tables for remaining word types

Refines the German A1 study system (`study/nouns.md`, `study/verbs.md`) to cover all
remaining word types. Each ticket builds one Markdown study table in `study/`.

## Conventions (applied to every ticket)

- **Rows** come from `A1.tsv` filtered by the source `Type` column, in file order.
- **`BASE_WORD`** = the head word of the German cell (parentheticals and `, -en`
  style plural markers stripped). **`EN_MEANING`** = cleaned English (parentheses
  and `here:` notes removed).
- **Sentence columns** = `DE_SENTENCE` (German example) + `EN_SENTENCE_TRANSLATION`
  (its English translation). Short, A1-level, highlighting the target word.
- Empty / not-applicable cells use `—`.
- **Pipeline**: `build_other.py` (per-type spec → draft) + authored chunk files in
  `study/<slug>/_chunks/` + `--merge` to write `study/<slug>.md`.
- **Validation** per table: row count matches source, exact column count, no empty
  cells except deliberate `—`.

---

## T1 — adjective → `study/adjective.md` (179 rows)

Columns: `ID, BASE_WORD, COMPARATIVE, SUPERLATIVE, EN_MEANING, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
Auto: BASE_WORD, EN_MEANING. Author: COMPARATIVE + SUPERLATIVE (`gut→besser→am
besten`, `gross→grösser→am grössten`, `hoch→höher→am höchsten`, `teuer→teurer→am
teuersten`; uncomparable → `—`) + sentence.

## T2 — adverb → `study/adverb.md` (112 rows)

Columns: `ID, BASE_WORD, EN_MEANING, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
Author: sentence per adverb.

## T3 — article → `study/article.md` (16 rows)

Columns: `ID, BASE_WORD, TYPE, NOM_SG, ACC_SG, DAT_SG, GEN_SG, NOM_PL, ACC_PL,
DAT_PL, GEN_PL, EN_MEANING, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
Rows: the 15 `Article`-typed rows **plus** the possessive `sein, seine` (currently
mis-classified as Verb) = complete possessive set.
TYPE: definite / indefinite / negative / possessive / indefinite-determiner (`jede`).
Author: full NOM/ACC/DAT/GEN declension for SG and PL (`der/den/dem/des`, possessives
`mein/meinen/meinem/meines`, neg. `kein/keinen/keinem/keines`; plural of `ein` → `—`).

## T4 — conjunction → `study/conjunction.md` (8 rows)

Columns: `ID, BASE_WORD, TYPE, WORD_ORDER, EN_MEANING, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
TYPE: coordinating (`und`, `oder`, `aber`, `denn`, `also`) vs subordinating (`wenn`,
`als`). WORD_ORDER: `Satzklammer` (Verb-second) vs `Verb am Ende` (verb-final).

## T5 — interjection → `study/interjection.md` (10 rows)

Columns: `ID, BASE_WORD, EN_MEANING, SITUATION, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
SITUATION: greeting / farewell / thanks / toast / cheer / surprise.

## T6 — number → `study/number.md` (34 rows)

Columns: `ID, BASE_WORD, NUMBER_TYPE, EN_MEANING, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
NUMBER_TYPE: `Kardinalzahl`; `minus`/`plus` → `Plus/Minus-Zeichen`; `null` → `Kardinalzahl`.

## T7 — particle → `study/particle.md` (10 rows)

Columns: `ID, BASE_WORD, PARTICLE_TYPE, FUNCTION, EN_MEANING, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
PARTICLE_TYPE: modal particle / answer particle (`ja`, `nein`) / politeness (`bitte`).
FUNCTION: soften, emphasise, affirm, negate, elicit agreement.

## T8 — phrase-expression → `study/phrase-expression.md` (32 rows)

Columns: `ID, BASE_WORD, EN_MEANING, SITUATION, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
SITUATION: greeting / farewell / toasts / restaurant / politeness / time-expressions.

## T9 — preposition → `study/preposition.md` (52 rows)

Columns: `ID, BASE_WORD, CASE, EN_MEANING, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
CASE auto-parsed from `(+ D.)` (28) / `(+ A.)` (9); 15 marker-less rows authored
(`bis`→Akk, `mit/zu/gegenüber`→Dat, `auf/in/über`→D/A, `ab`→Dat, `um`→Akk, …).

## T10 — pronoun → `study/pronoun.md` (30 rows)

Columns: `ID, BASE_WORD, PRONOUN_TYPE, NOM, ACC, DAT, GEN, EN_MEANING, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
PRONOUN_TYPE: personal / indefinite / demonstrative / reflexive. Author NOM/ACC/DAT/GEN
(`ich/mich/mir/meiner`, `du/dich/dir/deiner`, `sich`→`—/sich/sich/—`, indefinite e.g.
`jemand/jemanden/jemandem/—`).

## T11 — question-word → `study/question-word.md` (13 rows)

Columns: `ID, BASE_WORD, FUNCTION, EN_MEANING, DE_SENTENCE, EN_SENTENCE_TRANSLATION`
FUNCTION: person / thing / place / direction / time / reason / manner / quantity.

---

## Delivery order

Small closed classes first (quick validation of the pipeline), biggest last:
interjection → number → conjunction → particle → question-word → phrase-expression →
preposition → adverb → pronoun → article → adjective.
Each type gets its own commit once validated.