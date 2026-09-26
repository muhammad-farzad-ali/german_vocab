# -*- coding: utf-8 -*-
import re, os, sys

PATH = "A1.tsv"
STUDY = "study"

EXTRA_ARTICLE = []


def norm_cell(g):
    g0 = g.strip()
    if g0.endswith('"') and g0[:-1].rstrip().endswith(")"):
        g0 = g0[:-1]
    g0 = g0.replace("\t", " ")
    return g0


def clean_meaning(en):
    m = re.sub(r"\([^()]*\)", "", en)
    m = re.sub(r"^here:\s*", "", m)
    m = re.sub(r"\s+", " ", m).strip()
    return m


MEANING_FIX = {
    "Xtra- (Morgen ist in Wien ein Extra-Konzert von Mark Forster.)": "extra",
}


def head_of(g0):
    return re.split(r"[,()]", g0)[0].strip().strip('"')


def load_type(t, extra=()):
    rows = []
    for ln in open(PATH, encoding="utf-8").read().splitlines()[1:]:
        parts = ln.rstrip("\n").split("\t")
        if len(parts) == 3:
            g, e, tt = parts
        else:
            g = "\t".join(parts[:-2])
            e = parts[-2]
            tt = parts[-1]
        if tt == t:
            rows.append((g, e))
    rows.extend(extra)
    return rows


# cols: (header, source, ref)
#   source 'id' -> the row id
#   source 'parse'/'base'/'meaning' -> parsed value
#   source 'chunk' -> authored value at index ref
SPECS = {
    "adjective": dict(
        src="Adjective",
        label="adjectives",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("COMPARATIVE", "chunk", 0),
            ("SUPERLATIVE", "chunk", 1),
            ("EN_MEANING", "meaning", None),
            ("DE_SENTENCE", "chunk", 2),
            ("EN_SENTENCE_TRANSLATION", "chunk", 3),
        ],
    ),
    "adverb": dict(
        src="Adverb",
        label="adverbs",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("EN_MEANING", "meaning", None),
            ("DE_SENTENCE", "chunk", 0),
            ("EN_SENTENCE_TRANSLATION", "chunk", 1),
        ],
    ),
    "article": dict(
        src="Article",
        label="articles",
        extra=EXTRA_ARTICLE,
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("TYPE", "chunk", 0),
            ("NOM_SG", "chunk", 1),
            ("ACC_SG", "chunk", 2),
            ("DAT_SG", "chunk", 3),
            ("GEN_SG", "chunk", 4),
            ("NOM_PL", "chunk", 5),
            ("ACC_PL", "chunk", 6),
            ("DAT_PL", "chunk", 7),
            ("GEN_PL", "chunk", 8),
            ("EN_MEANING", "meaning", None),
            ("DE_SENTENCE", "chunk", 9),
            ("EN_SENTENCE_TRANSLATION", "chunk", 10),
        ],
    ),
    "conjunction": dict(
        src="Conjunction",
        label="conjunctions",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("TYPE", "chunk", 0),
            ("WORD_ORDER", "chunk", 1),
            ("EN_MEANING", "meaning", None),
            ("DE_SENTENCE", "chunk", 2),
            ("EN_SENTENCE_TRANSLATION", "chunk", 3),
        ],
    ),
    "interjection": dict(
        src="Interjection",
        label="interjections",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("EN_MEANING", "meaning", None),
            ("SITUATION", "chunk", 0),
            ("DE_SENTENCE", "chunk", 1),
            ("EN_SENTENCE_TRANSLATION", "chunk", 2),
        ],
    ),
    "number": dict(
        src="Number",
        label="numbers",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("NUMBER_TYPE", "chunk", 0),
            ("EN_MEANING", "meaning", None),
            ("DE_SENTENCE", "chunk", 1),
            ("EN_SENTENCE_TRANSLATION", "chunk", 2),
        ],
    ),
    "particle": dict(
        src="Particle",
        label="particles",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("PARTICLE_TYPE", "chunk", 0),
            ("FUNCTION", "chunk", 1),
            ("EN_MEANING", "meaning", None),
            ("DE_SENTENCE", "chunk", 2),
            ("EN_SENTENCE_TRANSLATION", "chunk", 3),
        ],
    ),
    "phrase-expression": dict(
        src="Phrase / expression",
        label="phrases",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("EN_MEANING", "meaning", None),
            ("SITUATION", "chunk", 0),
            ("DE_SENTENCE", "chunk", 1),
            ("EN_SENTENCE_TRANSLATION", "chunk", 2),
        ],
    ),
    "preposition": dict(
        src="Preposition",
        label="prepositions",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("CASE", "chunk", 0),
            ("EN_MEANING", "meaning", None),
            ("DE_SENTENCE", "chunk", 1),
            ("EN_SENTENCE_TRANSLATION", "chunk", 2),
        ],
    ),
    "pronoun": dict(
        src="Pronoun",
        label="pronouns",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("PRONOUN_TYPE", "chunk", 0),
            ("NOM", "chunk", 1),
            ("ACC", "chunk", 2),
            ("DAT", "chunk", 3),
            ("GEN", "chunk", 4),
            ("EN_MEANING", "meaning", None),
            ("DE_SENTENCE", "chunk", 5),
            ("EN_SENTENCE_TRANSLATION", "chunk", 6),
        ],
    ),
    "question-word": dict(
        src="Question word",
        label="question words",
        cols=[
            ("ID", "id", None),
            ("BASE_WORD", "base", None),
            ("FUNCTION", "chunk", 0),
            ("EN_MEANING", "meaning", None),
            ("DE_SENTENCE", "chunk", 1),
            ("EN_SENTENCE_TRANSLATION", "chunk", 2),
        ],
    ),
}


def parsed(row):
    g, e = row
    g0 = norm_cell(g)
    meaning = clean_meaning(e)
    if g0 in MEANING_FIX:
        meaning = MEANING_FIX[g0]
    return {"base": head_of(g0), "meaning": meaning}


def main():
    for slug, spec in SPECS.items():
        rows = load_type(spec["src"], spec.get("extra", ()))
        d = os.path.join(STUDY, slug)
        os.makedirs(os.path.join(d, "_chunks"), exist_ok=True)
        n_chunk_cols = sum(1 for _, s, _ in spec["cols"] if s == "chunk")
        out = []
        for i, row in enumerate(rows, 1):
            p = parsed(row)
            out.append("\t".join([str(i), p["base"], p["meaning"]]))
        with open(os.path.join(d, "_draft.tsv"), "w", encoding="utf-8") as f:
            f.write("\t".join(["id", "base", "en_meaning"]) + "\n")
            f.write("\n".join(out) + "\n")
        print(slug, len(rows))


def load_chunks(slug):
    d = os.path.join(STUDY, slug, "_chunks")
    data = {}
    if not os.path.isdir(d):
        return data
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".tsv"):
            continue
        for ln in open(os.path.join(d, fn), encoding="utf-8"):
            parts = ln.rstrip("\n").split("\t")
            if len(parts) >= 2:
                data[parts[0]] = parts[1:]
    return data


def merge():
    for slug, spec in SPECS.items():
        chunks = load_chunks(slug)
        rows = [
            ln.split("\t")
            for ln in open(os.path.join(STUDY, slug, "_draft.tsv"), encoding="utf-8")
            .read()
            .splitlines()[1:]
        ]
        order = spec["cols"]
        headers = [h for h, _, _ in order]
        lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
        missing = []
        for r in rows:
            ident, base, meaning = r
            c = chunks.get(ident)
            if not c:
                missing.append(ident)
                c = ["—"] * 12
            ci = 0
            cells = []
            for h, src, ref in order:
                if src == "id":
                    v = ident
                elif src == "base":
                    v = base
                elif src == "meaning":
                    v = meaning
                else:
                    v = c[ref] if ref < len(c) else ""
                    if v in ("", None):
                        v = "—"
                cells.append(str(v).replace("|", "\\|"))
            lines.append("| " + " | ".join(cells) + " |")
        with open(os.path.join(STUDY, slug + ".md"), "w", encoding="utf-8") as f:
            f.write(
                "# German A1 %s — study table (%d)\n\n" % (spec["label"], len(rows))
            )
            f.write("\n".join(lines) + "\n")
        print(slug, "rows", len(rows), "missing", len(missing))


if __name__ == "__main__":
    if "--merge" in sys.argv:
        merge()
    else:
        main()
