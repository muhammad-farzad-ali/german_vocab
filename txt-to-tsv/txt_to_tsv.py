import os
import re
import sys

from openai import OpenAI

INPUT_PATH = os.path.join(os.path.dirname(__file__), "input.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output.tsv")

SYSTEM_PROMPT = """\
You are a German vocabulary parser. You will receive a raw vocabulary list from a \
German textbook (Goethe A1). Your job is to extract every vocabulary entry and output \
a clean two-column TSV: German (column 1) and English (column 2).

Rules:
1. Strip chapter/section headers (e.g. "Kapitel 1 – Rund ums Essen", "AB 1a", "1b", \
page numbers like "4", "1", "5", etc.).
2. Strip pronunciation dots (e.g. "dẹcken" → "decken", "fẹtt" → "fett").
3. For German entries: keep articles, plural forms, and separable verb markers. \
Include conjugation/grammar in parentheses when present. \
Example: "geben (gibt, hat gegeben)" stays as-is.
4. For English entries: keep the plain translation. Include usage context in \
parentheses when it adds meaning. \
Example: "to give (Can you give me the bread, please?)"
5. Preserve the "here:" prefix in English when the word has a special contextual meaning. \
Example: "here: but" or "here: just, simply"
6. Each output line must be exactly: GERMAN<tab>ENGLISH
7. One vocabulary pair per line. No blank lines, no headers, no commentary.
8. If a German entry has multiple senses from different sections (e.g. the same word \
appears in 1a and 1b with different meanings), output both as separate rows.

Example input lines and their expected output:

Input:
  1a aber (Hilfst du mir? – Aber gern.)
  äußern
  die Currywurst, -würste

Output:
  aber (Hilfst du mir? – Aber gern.)\there: but (Will you help me? – But gladly.)
  äußern\tto express
  die Currywurst, -würste\tsausage with curry sauce (German fast food dish)

More examples of the exact output format:
  die Autobahn, -en\thighway
  geben (gibt, hat gegeben)\tto give (Can you give me the bread, please?)
  das Gefühl, -e\tfeeling
  egal\tall the same
  einfach (Das muss einfach sein!)\there: just, simply (It just has to be!)
  Schlüsselwort, -wörter\tkeyword
  die WG, -s\tapartment share, housing cooperative
"""


def build_user_prompt(raw_text: str) -> str:
    return (
        "Below is the raw vocabulary list. Parse every entry into "
        "German<tab>English rows following the system rules.\n\n"
        f"{raw_text}"
    )


def parse_tsv_response(text: str) -> list[tuple[str, str]]:
    """Parse the model response into (german, english) pairs."""
    # Strip markdown code fences if present
    text = re.sub(r"```(?:tsv)?\s*\n?", "", text)
    text = re.sub(r"```\s*$", "", text)
    text = text.strip()

    pairs = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) == 2:
            german, english = parts
            if german.strip() and english.strip():
                pairs.append((german.strip(), english.strip()))
        elif len(parts) == 1 and parts[0].strip():
            match = re.match(r"^(.+?)\s{2,}(.+)$", parts[0])
            if match:
                pairs.append((match.group(1).strip(), match.group(2).strip()))
    return pairs


def split_by_chapter(text: str) -> list[str]:
    """Split input into chapter chunks, keeping header lines with each chunk."""
    lines = text.splitlines(keepends=True)
    chapter_starts = []
    for i, line in enumerate(lines):
        if re.match(r"^Kapitel \d+", line):
            chapter_starts.append(i)

    if not chapter_starts:
        return [text]

    chunks = []
    # Content before first chapter (e.g. intro lines)
    if chapter_starts[0] > 0:
        preamble = "".join(lines[: chapter_starts[0]]).strip()
        if preamble:
            chunks.append(preamble)

    for idx, start in enumerate(chapter_starts):
        end = chapter_starts[idx + 1] if idx + 1 < len(chapter_starts) else len(lines)
        chunk = "".join(lines[start:end]).strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    chunks = split_by_chapter(raw_text)
    print(f"Split input into {len(chunks)} chunks.")

    all_pairs: list[tuple[str, str]] = []
    total_prompt = 0
    total_completion = 0

    for i, chunk in enumerate(chunks):
        first_line = chunk.splitlines()[0][:60]
        print(f"  [{i + 1}/{len(chunks)}] {first_line}... ({len(chunk)} chars)")

        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.0,
            max_tokens=16384,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(chunk)},
            ],
        )

        raw_output = response.choices[0].message.content
        if not raw_output:
            print(f"  Warning: empty response for chunk {i + 1}", file=sys.stderr)
            continue

        pairs = parse_tsv_response(raw_output)
        print(f"    -> {len(pairs)} pairs")

        total_prompt += response.usage.prompt_tokens
        total_completion += response.usage.completion_tokens

        # Check for truncation (hit max tokens)
        if response.usage.completion_tokens >= 16384:
            print(
                f"  WARNING: chunk {i + 1} may be truncated (hit 16384 completion tokens)",
                file=sys.stderr,
            )

        all_pairs.extend(pairs)

    print(f"\nTotal: {len(all_pairs)} vocabulary pairs.")
    print(f"Total tokens: prompt={total_prompt}, completion={total_completion}")

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        f.write("German\tEnglish\n")
        for german, english in all_pairs:
            f.write(f"{german}\t{english}\n")

    print(f"Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
