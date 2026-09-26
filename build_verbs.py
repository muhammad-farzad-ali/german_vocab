# -*- coding: utf-8 -*-
import re, os, sys

PATH = "A1.tsv"
STUDY_DIR = os.path.join("study", "verbs")
DRAFT = os.path.join(STUDY_DIR, "_draft.tsv")
CONJ_CHUNKS = os.path.join(STUDY_DIR, "_verbs")
OUT_MD = os.path.join("study", "verbs.md")

EXCLUDE = {}

SEPARABLE_FIX = {
    "sauber machen": "sauber",
}


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


def load_verbs():
    rows = []
    for ln in open(PATH, encoding="utf-8").read().splitlines()[1:]:
        parts = ln.rstrip("\n").split("\t")
        if len(parts) == 3:
            g, e, t = parts
        else:
            g = "\t".join(parts[:-2])
            e = parts[-2]
            t = parts[-1]
        if t == "Verb" and g.strip() not in EXCLUDE:
            rows.append((g, e))
    return rows


SEPARABLE_PREFIXES = sorted(
    [
        "zurück",
        "heraus",
        "zusammen",
        "weiter",
        "vor",
        "nach",
        "mit",
        "ein",
        "aus",
        "auf",
        "an",
        "ab",
        "zu",
        "um",
        "hoch",
        "raus",
        "fern",
        "frei",
        "leid",
        "weh",
        "statt",
        "kennen",
        "dazu",
        "vorbei",
    ],
    key=len,
    reverse=True,
)


def parse_verb(g, e):
    g0 = norm_cell(g)
    reflexive = "yes" if ("(sich)" in g0 or re.search(r"\bsich\b", g0)) else "—"
    separable = "—"
    head0 = re.split(r"[,()]", g0)[0].strip().strip('"')
    if "|" in g0:
        left, right = g0.split("|", 1)
        separable = left.strip()
        base = re.split(r"[,()]", right)[0].strip().strip('"')
    else:
        base = head0
        base = re.sub(
            r"\s+(auf|an|zu|mit|für|über|aus|bei|nach|in)\s*(\+)?\s*$", "", base
        )
        for pref in SEPARABLE_PREFIXES:
            if base.startswith(pref) and len(base) > len(pref):
                separable = pref
                base = base[len(pref) :].strip()
                break
    aux = "—"
    partizip = "—"
    m = re.search(r",\s*(?:er|es|ich|sie)\s+\S+,\s*(hat|ist)\s+(\S+)", g0)
    if not m:
        m = re.search(r"\([^)]*,\s*(hat|ist)\s+(\S+)\)", g0)
    if m:
        aux = {"hat": "haben", "ist": "sein"}[m.group(1)]
        partizip = m.group(2)
    separable = SEPARABLE_FIX.get(head0, separable)
    return {
        "base": base,
        "separable": separable,
        "reflexive": reflexive,
        "aux": aux,
        "partizip": partizip,
        "meaning": clean_meaning(e),
    }


def main():
    os.makedirs(STUDY_DIR, exist_ok=True)
    verbs = load_verbs()
    out = []
    for i, (g, e) in enumerate(verbs, 1):
        d = parse_verb(g, e)
        out.append(
            "\t".join(
                [
                    str(i),
                    d["base"],
                    d["separable"],
                    d["reflexive"],
                    d["aux"],
                    d["partizip"],
                    d["meaning"],
                ]
            )
        )
    with open(DRAFT, "w", encoding="utf-8") as f:
        f.write(
            "\t".join(
                [
                    "id",
                    "base",
                    "separable",
                    "reflexive",
                    "aux_from_src",
                    "partizip_from_src",
                    "en_meaning",
                ]
            )
            + "\n"
        )
        f.write("\n".join(out) + "\n")
    print("verb draft rows:", len(out))


def load_conj():
    conj = {}
    if not os.path.isdir(CONJ_CHUNKS):
        return conj
    for fn in sorted(os.listdir(CONJ_CHUNKS)):
        if not fn.endswith(".tsv"):
            continue
        for ln in open(os.path.join(CONJ_CHUNKS, fn), encoding="utf-8"):
            parts = ln.rstrip("\n").split("\t")
            if len(parts) >= 13:
                conj[parts[0]] = parts[1:]
    return conj


def merge():
    conj = load_conj()
    rows = [
        ln.split("\t") for ln in open(DRAFT, encoding="utf-8").read().splitlines()[1:]
    ]
    headers = [
        "ID",
        "BASE_WORD",
        "VERB_TYPE",
        "SEPARABLE",
        "REFLEXIVE",
        "PRESENT_ICH",
        "PRESENT_DU",
        "PRESENT_ER_SIE_ES",
        "PRESENT_WIR",
        "PRESENT_IHR",
        "PRESENT_SIE",
        "PRÄTERITUM",
        "PARTIZIP_II",
        "AUXILIARY",
        "EN_MEANING",
        "DE_SENTENCE",
        "EN_SENTENCE_TRANSLATION",
    ]
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    missing = []
    for r in rows:
        ident, base, sep, refl, aux_src, part_src, meaning = r
        c = conj.get(ident)
        if not c:
            missing.append(ident)
            c = ["", "—", "—", "—", "—", "—", "—", "—", "—", "—", "—", "—"]
        (
            vtype,
            p_ich,
            p_du,
            p_er,
            p_wir,
            p_ihr,
            p_sie,
            präter,
            partizip,
            aux,
            de,
            en,
        ) = c
        if partizip in ("", "—"):
            partizip = part_src if part_src != "—" else "—"
        if aux in ("", "—"):
            aux = aux_src if aux_src != "—" else "—"
        cells = [
            ident,
            base,
            vtype,
            sep,
            refl,
            p_ich,
            p_du,
            p_er,
            p_wir,
            p_ihr,
            p_sie,
            präter,
            partizip,
            aux,
            meaning,
            de,
            en,
        ]
        cells = [c2.replace("|", "\\|") for c2 in cells]
        lines.append("| " + " | ".join(cells) + " |")
    os.makedirs("study", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# German A1 verbs — conjugation study table (%d)\n\n" % len(rows))
        f.write("\n".join(lines) + "\n")
    print("markdown rows:", len(rows), "| conjugation missing:", len(missing))


if __name__ == "__main__":
    if "--merge" in sys.argv:
        merge()
    else:
        main()
