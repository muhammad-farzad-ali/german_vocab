# -*- coding: utf-8 -*-
import re, sys, os, collections

PATH = "A1.tsv"
FOLDER = "by_type"

SPECIAL = {}

PHRASE = {
    "guten Tag",
    "guten Morgen",
    "guten Abend",
    "gute Nacht",
    "auf Wiedersehen",
    "auf Wiederhören",
    "bis bald",
    "bis später",
    "bis dann",
    "guten Appetit",
    "gute Besserung",
    "zum Wohl",
    "wie bitte",
    "ein bisschen",
    "noch einmal",
    "noch mal",
    "zu Fuß",
    "zu Hause",
    "nach Hause",
    "auf jeden Fall",
    "nicht mehr",
    "nicht nur",
    "schon wieder",
    "am Samstagabend",
    "zum Schluss",
    "da vorne",
    "ein paar",
    "grüß Gott",
    "danke schön",
    "zum Glück",
}

VERB_WORDS = {
    "jogen",
    "achten auf",
    "stellen",
    "führen",
    "machen",
    "stimmen",
    "leben",
    "husten",
    "öffnen",
    "aufräumen",
    "sauber machen",
    "legen",
    "sein",
}

ARTICLE = {"der", "die", "das", "den", "dem", "ein", "kein", "jede"}
POSS = {"mein", "dein", "sein", "ihr", "unser", "euer", "Ihr"}

PRONOUN = {
    "ich",
    "du",
    "er",
    "sie",
    "wir",
    "ihr",
    "Sie",
    "dir",
    "mich",
    "dich",
    "mir",
    "uns",
    "euch",
    "ihn",
    "Ihnen",
    "sich",
    "jemand",
    "alles",
    "nichts",
    "alle",
    "beide",
    "selbst",
    "andere",
    "mehrere",
    "viel",
    "die meisten",
    "diese",
}

QW = {
    "was",
    "wer",
    "wen",
    "wem",
    "wo",
    "woher",
    "wohin",
    "warum",
    "wie",
    "wie lange",
    "wie viel",
    "wie viele",
    "welcher",
    "welche",
    "welches",
}

INTERJ = {
    "hallo",
    "ciao",
    "tschüs",
    "hey",
    "hi hi",
    "prost",
    "hurra",
    "moin",
    "grüezi",
    "danke",
}

PARTICLE = {"ja", "nein", "doch", "mal", "bitte"}

CONJ = {"und", "oder", "aber", "denn", "wenn", "als", "also"}

PREP = {
    "auf",
    "in",
    "aus",
    "nach",
    "mit",
    "für",
    "durch",
    "von",
    "zu",
    "ab",
    "bei",
    "pro",
    "über",
    "bis",
    "um",
    "seit",
    "an",
    "gegen",
    "hinter",
    "neben",
    "unter",
    "zwischen",
    "ohne",
    "gegenüber",
    "außerhalb",
    "vor",
    "am",
    "bis zu",
    "von … bis",
    "rund um",
}

NUM = {
    "eins",
    "zwei",
    "drei",
    "vier",
    "fünf",
    "sechs",
    "sieben",
    "acht",
    "neun",
    "zehn",
    "elf",
    "zwölf",
    "dreizehn",
    "vierzehn",
    "fünfzehn",
    "sechzehn",
    "siebzehn",
    "achtzehn",
    "neunzehn",
    "zwanzig",
    "dreißig",
    "vierzig",
    "fünfzig",
    "sechzig",
    "siebzig",
    "achtzig",
    "neunzig",
    "hundert",
    "einhundert",
    "tausend",
    "eintausend",
    "null",
    "minus",
    "plus",
}

ADJ = {
    "gut",
    "international",
    "informell",
    "deutsch",
    "alt",
    "groß",
    "bekannt",
    "neu",
    "persönlich",
    "blau",
    "grün",
    "rot",
    "männlich",
    "weiblich",
    "breit",
    "hoch",
    "lang",
    "leicht",
    "schwer",
    "einfach",
    "schnell",
    "langsam",
    "laut",
    "leise",
    "ruhig",
    "sportlich",
    "voll",
    "leer",
    "warm",
    "kalt",
    "heiß",
    "süß",
    "lecker",
    "frisch",
    "teuer",
    "günstig",
    "schlecht",
    "böse",
    "froh",
    "glücklich",
    "zufrieden",
    "verheiratet",
    "ledig",
    "lieb",
    "herzlich",
    "freundlich",
    "höflich",
    "unhöflich",
    "pünktlich",
    "spät",
    "normal",
    "arbeitslos",
    "beliebt",
    "langweilig",
    "neutral",
    "schrecklich",
    "egal",
    "fit",
    "müde",
    "hungrig",
    "faul",
    "krank",
    "gesund",
    "satt",
    "wach",
    "frei",
    "fertig",
    "offen",
    "geschlossen",
    "geöffnet",
    "besetzt",
    "kaputt",
    "doof",
    "eng",
    "attraktiv",
    "individuell",
    "lebendig",
    "original",
    "praktisch",
    "bequem",
    "topaktuell",
    "aktuell",
    "argentinisch",
    "asiatisch",
    "deutschsprachig",
    "zentral",
    "offiziell",
    "inoffiziell",
    "negativ",
    "positiv",
    "maskulin",
    "feminin",
    "neutrum",
    "braun",
    "gelb",
    "grau",
    "lila",
    "orange",
    "schwarz",
    "weiß",
    "wunderschön",
    "wunderbar",
    "populär",
    "berühmt",
    "interessant",
    "schön",
    "toll",
    "super",
    "supernett",
    "cool",
    "okay",
    "sauber",
    "sonnig",
    "bewölkt",
    "windig",
    "bestimmt",
    "eigene",
    "besondere",
    "erste",
    "letzte",
    "nächste",
    "weitere",
    "ganz",
    "halb",
    "doppelt",
    "passend",
    "ähnlich",
    "verschieden",
    "thematisch",
    "unregelmäßig",
    "trennbar",
    "unbestimmt",
    "betont",
    "fleißig",
    "eilig",
    "geehrt",
    "fehlend",
    "verletzt",
    "verboten",
    "extra",
    "Xtra-",
    "gegenseitig",
    "länger",
    "besser",
    "rund",
    "lila",
    "lustig",
    "klein",
    "kreativ",
    "nett",
    "stressig",
    "abwechselnd",
    "falsch",
    "willkommen",
    "typisch",
    "offline",
    "gefährlich",
    "perfekt",
    "anstrengend",
    "hell",
    "online",
    "anders",
}

ADV = {
    "so",
    "sehr",
    "hier",
    "immer",
    "oft",
    "meistens",
    "normalerweise",
    "täglich",
    "regelmäßig",
    "zusammen",
    "gern",
    "gerne",
    "zurück",
    "wieder",
    "heute",
    "gestern",
    "morgen",
    "jetzt",
    "abends",
    "morgens",
    "mittags",
    "nachmittags",
    "vormittags",
    "nachts",
    "samstags",
    "dann",
    "danach",
    "vorher",
    "später",
    "zuerst",
    "sofort",
    "endlich",
    "hoffentlich",
    "tatsächlich",
    "eigentlich",
    "gerade",
    "vorgestern",
    "früher",
    "oben",
    "unten",
    "links",
    "rechts",
    "geradeaus",
    "vorne",
    "draußen",
    "überall",
    "unterwegs",
    "dazu",
    "daneben",
    "her",
    "kaum",
    "selten",
    "einmal",
    "dreimal",
    "zweimal",
    "mindestens",
    "insgesamt",
    "ebenso",
    "genug",
    "viel zu",
    "wenig",
    "früh",
    "schon",
    "erst",
    "noch",
    "nur",
    "nur noch",
    "mehr",
    "sonst",
    "auch",
    "bar",
    "auswendig",
    "allein",
    "manchmal",
    "nie",
    "nicht",
    "gleichfalls",
    "top",
    "total",
    "gar",
    "sicher",
    "echt",
    "wirklich",
    "genau",
    "natürlich",
    "vielleicht",
    "leider",
    "da",
    "zurzeit",
    "maximal",
    "circa",
    "ungefähr",
    "darauf",
    "rund",
}


def classify(german, english):
    g = german.strip().strip('"')
    if g in SPECIAL:
        return SPECIAL[g]
    head = g.split("(")[0].split(",")[0].strip()
    if head in PHRASE:
        return "Phrase / expression"
    if "|" in g:
        return "Verb"
    if re.search(r",\s*(er|es|ich)\s+", g):
        return "Verb"
    if "(sich)" in g:
        return "Verb"
    if g.endswith(" sein"):
        return "Verb"
    if head in VERB_WORDS:
        return "Verb"
    if head in ARTICLE:
        return "Article"
    if head in POSS and "," in g:
        return "Article"
    if head in PRONOUN:
        return "Pronoun"
    if head in QW:
        return "Question word"
    if head in INTERJ:
        return "Interjection"
    if head in PARTICLE:
        return "Particle"
    if head in CONJ:
        return "Conjunction"
    if head in PREP:
        return "Preposition"
    if head in NUM:
        return "Number"
    if head in ADJ:
        return "Adjective"
    if head in ADV:
        return "Adverb"
    if english.strip().lower().startswith("to ") and not g[:1].isupper():
        return "Verb"
    ART = r"(der|die|das|den|dem|ein|eine|kein|keine)"
    if re.match(r"^(%s)( ?/ ?(%s))?\s+[A-ZÄÖÜ]" % (ART, ART), g):
        return "Noun"
    if g[:1].isupper():
        return "Noun"
    return "??" + head


def split_row(line):
    s = line.rstrip("\r\n")
    parts = s.split("\t")
    if parts and parts[-1] == "":
        parts = parts[:-1]
    if len(parts) >= 2:
        german = parts[0]
        english = parts[-1]
        if len(parts) > 2:
            german = "\t".join(parts[:-1])
        return german, english
    return s, ""


with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

newline = "\r\n" if "\r\n" in content else "\n"
lines = content.splitlines()
problems = []

rows = []
for ln in lines[1:]:
    if not ln.strip():
        continue
    cells = ln.split("\t")
    g = cells[0]
    e = cells[1] if len(cells) > 1 else ""
    rows.append((g, e))

out = ["German\tEnglish\tType"]
for g, e in rows:
    t = classify(g, e)
    if t.startswith("??"):
        problems.append((g, e, t))
        t = t[2:]
    out.append(g + "\t" + e + "\t" + t)

with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(newline.join(out) + newline)

print("rows:", len(out))
if problems:
    print("PROBLEM ROWS:")
    for p in problems:
        print(p)


def build_markdown():
    groups = collections.defaultdict(list)
    for ln in open(PATH, encoding="utf-8").read().splitlines()[1:]:
        if not ln.strip():
            continue
        parts = ln.split("\t")
        t = parts[-1]
        if len(parts) == 3:
            g, e = parts[0], parts[1]
        else:
            g = "\t".join(parts[:-2])
            e = parts[-2]
        groups[t].append((g, e))

    os.makedirs(FOLDER, exist_ok=True)
    created = []
    for t, items in groups.items():
        slug = t.lower().replace(" / ", "-").replace(" ", "-")
        path = os.path.join(FOLDER, slug + ".md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# %s (%d)\n\n" % (t, len(items)))
            for g, e in items:
                f.write("- %s — %s\n" % (g, e))
        created.append(path)
    return created


created = build_markdown()
print("markdown files:")
for c in sorted(created):
    print("  ", c)
