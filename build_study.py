# -*- coding: utf-8 -*-
import re, os, sys

PATH = "A1.tsv"
STUDY_DIR = "study"
DRAFT = os.path.join(STUDY_DIR, "_draft.tsv")
SENTENCES = os.path.join(STUDY_DIR, "sentences.tsv")
SENT_CHUNKS = os.path.join(STUDY_DIR, "_sentences")
OUT_MD = os.path.join(STUDY_DIR, "nouns.md")


def load_rows():
    rows = []
    for ln in open(PATH, encoding="utf-8").read().splitlines()[1:]:
        parts = ln.rstrip("\n").split("\t")
        if len(parts) == 3:
            g, e, t = parts
        else:
            g = "\t".join(parts[:-2])
            e = parts[-2]
            t = parts[-1]
        if t == "Noun":
            rows.append((g, e))
    return rows


def umlaut(word):
    lw = word.lower()
    idx = -1
    for i, ch in enumerate(lw):
        if ch in "aou":
            idx = i
    if idx < 0:
        return word
    if lw[idx] == "u" and idx > 0 and lw[idx - 1] == "a":
        rep = "Ä" if word[idx - 1].isupper() else "ä"
        return word[: idx - 1] + rep + word[idx:]
    ch = word[idx]
    rep = {"a": "ä", "o": "ö", "u": "ü"}[ch.lower()]
    if ch.isupper():
        rep = rep.upper()
    return word[:idx] + rep + word[idx + 1 :]


# --- article fix for entries without a leading article ---
ARTICLE_FIX = {
    "Würstchen, -": "das",
    'Wort, -er"': "das",
    "Frau (Guten Morgen, Frau Weber.)": "die",
    "Herr (Guten Tag, Herr Hansen.)": "der",
    "Fußball (Sg. ohne Artikel) (Er spielt gern Fußball.)": "der",
    "Basketball (Sg. ohne Artikel)": "der",
    "Karate": "das",
    "Tennis (Sg. ohne Artikel)": "das",
    "Yoga (Sg. ohne Artikel)": "das",
    "Zumba (Sg. ohne Artikel)": "das",
    "Dank (Sg.) (Vielen Dank.)": "der",
    "saft, -e (Ich trinke gerne Saft.)": "der",
    "Uhr (Wie viel Uhr ist es?)": "die",
    "Achtung (Sg. ohne Artikel) (Achtung: Sofia weiß nichts!)": "die",
    "Mist (Sg.) (Mist, mein Akku ist gleich leer.)": "der",
    "der Alter (Sg.)": "das",
    "der Kurzform, -en": "die",
    "der Altbauwohnung, -en": "die",
    "der Ortsveränderung, -en": "die",
}

NO_ARTICLE = {
    "Bulgarisch",
    "Deutsch (Ich spreche Deutsch.)",
    "Englisch",
    "Indonesisch",
    "Italienisch",
    "Japanisch",
    "Russisch",
    "Serbisch",
    "Ungarisch",
    "Spanisch",
    "Türkisch",
    "Arabisch",
    "Französisch",
    "Portugiesisch",
    "Polnisch",
    "Rätoromanisch",
    "Deutschland",
    "Algerien",
    "Brasilien",
    "Japan",
    "Österreich",
    "Frankreich",
    "Griechenland",
    "Italien",
    "Mexiko",
    "Portugal",
    "Thailand",
    "Polen",
    "Russland",
    "Spanien",
    "Südamerika",
    "Co (Kneipen & Co)",
    "qm (= Quadratmeter)",
}

# remove junk override in PLURAL_OVERRIDES

# base-word normalization for messy source entries
BASE_FIX = {
    "saft, -e (Ich trinke gerne Saft.)": "Saft",
    "die Servierte, -n": "Serviette",
    "das Dritt (Arbeiten Sie zu dritt.)": "Dritt",
}

# plural overrides, keyed by the normalised German cell
PLURAL_OVERRIDES = {
    "saft, -e (Ich trinke gerne Saft.)": "die Säfte",
    "Uhr (Wie viel Uhr ist es?)": "die Uhren",
    "Fußball (Sg. ohne Artikel) (Er spielt gern Fußball.)": "—",
    "Basketball (Sg. ohne Artikel)": "—",
    "Karate": "—",
    "Tennis (Sg. ohne Artikel)": "—",
    "Yoga (Sg. ohne Artikel)": "—",
    "Zumba (Sg. ohne Artikel)": "—",
    "Achtung (Sg. ohne Artikel) (Achtung: Sofia weiß nichts!)": "—",
    "Dank (Sg.) (Vielen Dank.)": "—",
    "Mist (Sg.) (Mist, mein Akku ist gleich leer.)": "—",
    "Co (Kneipen & Co)": "—",
    "qm (= Quadratmeter)": "—",
    "die Pizza, -s/Pizzen": "die Pizzas / die Pizzen",
    "das Parfüm, -e/-s": "die Parfüme / die Parfüms",
    "die Saison, -en/-s": "die Saisonen / die Saisons",
    "das Stück, -e/-": "die Stücke",
    "die Kosmetik, -a": "die Kosmetika",
    "die Computerfirma, -firmen": "die Computerfirmen",
    "das Gesprächsthema, -themen": "die Gesprächsthemen",
    "das Geburtsdatum, -daten": "die Geburtsdaten",
    "der Aussagesatz, -e": "die Aussagesätze",
    "der Lernwortschatz, -e": "die Lernwortschätze",
    "der Markt, -e": "die Märkte",
    "der Supermarkt, -e": "die Supermärkte",
    "der Hafen, -": "die Häfen",
    "der Garten, -": "die Gärten",
    "der Biergarten, -": "die Biergärten",
    "der Vater, -": "die Väter",
    "der Bruder, -": "die Brüder",
    "der Großvater, -": "die Großväter",
    "der Mantel, -": "die Mäntel",
    "der Laden, -": "die Läden",
    "der Buchladen, -": "die Buchläden",
    "der Schuhladen, -": "die Schuhläden",
    "der Secondhand-Laden, -": "die Secondhand-Läden",
    "der Flughafen, -": "die Flughäfen",
    "der Mund, -er": "die Münder",
    "der Mann, -er (Der Mann möchte ein Brötchen.)": "die Männer",
    "der Mann, -er (Mein Mann und ich frühstücken zusammen.)": "die Männer",
    "der Mann, -er (Mann bin ich froh!)": "die Männer",
    "der Saft, -e (Nehmen Sie einen Saft gegen den Husten.)": "die Säfte",
    "Frau (Guten Morgen, Frau Weber.)": "die Frauen",
    "Herr (Guten Tag, Herr Hansen.)": "die Herren",
    "die Bank, -e (Die Leute sitzen auf der Bank.)": "die Bänke",
    "der Gruß, -e (Liebe Grüße)": "die Grüße",
    "der Platz, -e (Das Kino ist am Potsdamer Platz.)": "die Plätze",
    "die Auskunft, -e (Auskunft geben)": "die Auskünfte",
    'das Dorf, -e"': "die Dörfer",
}


# (duplicate removed)
def _plain(word):
    return word.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss")


def repl_plural(base, s):
    # a2-style inline umlaut suffix: replace the matching base tail
    if any(ch in s for ch in "äöü"):
        sp = _plain(s)
        for L in range(len(base) - 1, 0, -1):
            if sp.startswith(_plain(base[-L:])):
                return base[:-L] + s
    return base + s


def compute_plural(article, base, cell):
    if cell in PLURAL_OVERRIDES:
        return PLURAL_OVERRIDES[cell]
    if re.search(r"Sg\.|Singular", cell):
        return "—"
    pl = re.search(r",\s*([^\s(]+)", cell.split("(", 1)[0])
    if not pl:
        return "—"
    token = pl.group(1).strip()
    # full plural word appears as token without leading dash
    if not token.startswith("-"):
        return "die " + token
    s = token[1:]
    if s == "":
        return "die " + base
    if '"' in s:  # legacy quote-marker umlaut (A1 style)
        return "die " + umlaut(base) + s.replace('"', "")
    if "/" in s:
        forms = [repl_plural(base, p) for p in s.split("/") if p]
        return "die " + " / die ".join(forms)
    return "die " + repl_plural(base, s)


# --- genitive ---
N_DECL = {
    "Junge",
    "Kollege",
    "Kunde",
    "Nachbar",
    "Mensch",
    "Herr",
    "Student",
    "Patient",
    "Laborant",
    "Architekt",
    "Polizist",
    "Journalist",
    "Jurist",
    "Statist",
    "Solist",
    "Therapeut",
    "Physiotherapeut",
    "Fotograf",
}
MONOSYLL_ES = {
    "Mann",
    "Tag",
    "Arm",
    "Kopf",
    "Zug",
    "Haus",
    "Buch",
    "Kind",
    "Tisch",
    "Weg",
    "Satz",
    "Platz",
    "Fluss",
    "Fuß",
    "Grund",
    "Berg",
    "Hof",
    "Baum",
    "Blick",
    "Punkt",
    "See",
    "Jahr",
    "Geld",
    "Land",
    "Wort",
    "Bett",
    "Glas",
    "Lied",
    "Ziel",
    "Ende",
    "Mund",
    "Markt",
}
GENITIVE_OVERRIDES = {
    "der Name, -n": "des Namens",
    "der Buchstabe, -n": "des Buchstabens",
    "das Dritt (Arbeiten Sie zu dritt.)": "—",
    "der Alter (Sg.)": "des Alters",
    'der Notarzt, -e"': "des Notarztes",
    "die USA (Pl.)": "—",
}
SIBILANT = ("s", "ß", "z", "x", "sch", "tz", "ss")


def compute_genitive(article, base, cell):
    if cell in GENITIVE_OVERRIDES:
        return GENITIVE_OVERRIDES[cell]
    if article == "die":
        return "der " + base
    if article not in ("der", "das"):
        return "—"
    if base in N_DECL:
        if base == "Herr":
            return "des Herrn"
        if base == "Nachbar":
            return "des Nachbarn"
        if base.endswith("e"):
            return "des " + base + "n"
        return "des " + base + "en"
    if base in MONOSYLL_ES:
        return "des " + base + "es"
    if base.rstrip('"').endswith(SIBILANT):
        return "des " + base + "es"
    return "des " + base + "s"


def clean_meaning(en):
    m = re.sub(r"\([^()]*\)", "", en)
    m = re.sub(r"^here:\s*", "", m)
    m = re.sub(r"\s+", " ", m).strip()
    return m


def norm_cell(g):
    g0 = g.strip()
    # strip a trailing '"' only when it is an export artifact after a ')'
    if g0.endswith('"') and g0[:-1].rstrip().endswith(")"):
        g0 = g0[:-1]
    g0 = g0.replace("\t", " ")
    return g0


def parse(row):
    g, e = row
    g0 = norm_cell(g)
    cell = g0
    if cell in ARTICLE_FIX or cell in NO_ARTICLE or not re.match(r"^(der|die|das)", g0):
        if cell in ARTICLE_FIX:
            article = ARTICLE_FIX[cell]
        elif cell in NO_ARTICLE:
            article = "—"
        else:
            article = "—"
    else:
        m = re.match(r"^((?:der|die|das)(?:/(?:der|die|das))?)\s+", g0)
        article = m.group(1) if m else "—"

    # base word: strip article, comma-part, and parenthetical usage note
    rest = re.sub(r"^((?:der|die|das)(?:/(?:der|die|das))?\s+)", "", g0)
    base = re.split(r"[,()]", rest)[0].strip().strip('"')
    if cell in BASE_FIX:
        base = BASE_FIX[cell]

    pl_only = bool(re.search(r"\(Pl\.\)|Plural", cell))
    sg_only_or_pl = bool(re.search(r"\((?:Sg\.|Pl\.|Singular|Plural)\)", cell))

    if pl_only:
        singular = "—"
        plural = "die " + base
        genitive = "—"
    else:
        if article == "—":
            singular = base
        else:
            singular = article + " " + base
        plural = compute_plural(article, base, cell)
        genitive = compute_genitive(article, base, cell)

    meaning = clean_meaning(e)
    return {
        "cell": cell,
        "article": article,
        "base": base,
        "singular": singular,
        "plural": plural,
        "genitive": genitive,
        "meaning": meaning,
    }


def main():
    os.makedirs(STUDY_DIR, exist_ok=True)
    nouns = load_rows()
    out = []
    for i, row in enumerate(nouns, 1):
        d = parse(row)
        out.append(
            "\t".join(
                [
                    str(i),
                    d["cell"],
                    d["article"],
                    d["base"],
                    d["singular"],
                    d["plural"],
                    d["genitive"],
                    d["meaning"],
                ]
            )
        )

    with open(DRAFT, "w", encoding="utf-8") as f:
        f.write(
            "\t".join(
                [
                    "id",
                    "cell",
                    "article",
                    "base",
                    "singular",
                    "plural",
                    "genitive",
                    "en_meaning",
                ]
            )
            + "\n"
        )
        f.write("\n".join(out) + "\n")
    print("draft rows:", len(out))


def load_sentences():
    sents = {}
    for fn in sorted(os.listdir(SENT_CHUNKS)) if os.path.isdir(SENT_CHUNKS) else []:
        if not fn.endswith(".tsv"):
            continue
        for ln in open(os.path.join(SENT_CHUNKS, fn), encoding="utf-8"):
            parts = ln.rstrip("\n").split("\t")
            if len(parts) >= 3:
                sents[parts[0]] = (parts[1], parts[2])
    if os.path.exists(SENTENCES):
        for ln in open(SENTENCES, encoding="utf-8"):
            parts = ln.rstrip("\n").split("\t")
            if len(parts) >= 3:
                sents[parts[0]] = (parts[1], parts[2])
    return sents


def merge():
    sents = load_sentences()
    rows = [
        ln.split("\t") for ln in open(DRAFT, encoding="utf-8").read().splitlines()[1:]
    ]
    headers = [
        "BASE_WORD",
        "ARTICLE",
        "SINGULAR",
        "PLURAL",
        "GENITIVE",
        "EN_MEANING",
        "DE_SENTENCE",
        "EN_SENTENCE_TRANSLATION",
    ]
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    missing = []
    for r in rows:
        ident, cell, article, base, singular, plural, gen, meaning = r
        de, en = sents.get(ident, ("", ""))
        if not de:
            missing.append(ident)
        cells = [base, article, singular, plural, gen, meaning, de, en]
        cells = [c.replace("|", "\\|") for c in cells]
        lines.append("| " + " | ".join(cells) + " |")
    os.makedirs(STUDY_DIR, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# German A1 nouns — study table (%d)\n\n" % len(rows))
        f.write("\n".join(lines) + "\n")
    print("markdown rows:", len(rows), "| sentences missing:", len(missing))


if __name__ == "__main__":
    if "--merge" in sys.argv:
        merge()
    else:
        main()
