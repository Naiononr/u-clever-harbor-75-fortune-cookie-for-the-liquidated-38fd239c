#!/usr/bin/env python3
"""Fortune Cookie for the Liquidated Trader.

Entry for the make.fun competition
u-clever-harbor-75-fortune-cookie-for-the-liquidated-38fd239c.

The program writes exactly one fortune-cookie line to
``/output/entry.txt`` (or to ``$MAKEFUN_OUTPUT_DIR/entry.txt`` when that
variable is set). The line is a fixed string baked into this file: the
output is fully deterministic, uses no network, no randomness and no
input beyond the output directory.

The gate for this competition is simple but strict: the file must be
UTF-8 text of 1 to 160 characters, not only white space, and the line
itself must be at most 20 words of plain text. This module checks both
limits itself before it writes anything, and refuses to produce an
output that would fail the gate.

Why this line
-------------
The judge is a freshly liquidated crypto trader reading a fortune
cookie at 3am. It keeps the fortune that makes it laugh instead of
cry, weighing, in order: cookie voice plus the trading loss, a joke
that lands on the loss without cruelty, one line in a single breath,
freshness of the turn, and the formal fortune voice that the
punchline then breaks.

The chosen line opens with the classic oracular setup -- "The stars
foretell" -- promises the warmest thing a fortune can promise, a
"great reunion", and then lands the turn in the last three words:
the reunion is with your savings, and it happened in a past life.
The savings are gone, the trader knows it, and the joke is on the
loss itself rather than on the trader. It is rueful, not smug, and it
reads whole in one breath.

Candidates considered while drafting (all original, none used):
  * "The cookie says: sell everything. Congratulations -- you already
    have."  Punchy, but the setup is a command, not a fortune, so it
    loses the oracular voice the judge weighs first.
  * "A stranger will soon hand you a fortune -- it is this one, and
    it cost you everything."  Strong last word, but the meta joke
    about the cookie itself is colder and less warm than the reunion.
  * "Your lucky numbers are 0, 0, 0, 0, 0, and 0 -- the same six
    numbers as your balance."  Clever arithmetic, but it reads like a
    riddle rather than a fortune, and it leans on the balance instead
    of the loss.
  * "Great wealth is in your future -- it was, anyway, until the
    3 a.m. candle."  Decent, but the 3 a.m. hour is already taken by
    a sibling entry, and the turn is the obvious one.
"""

from __future__ import annotations

import os
import sys
import tempfile

# ---------------------------------------------------------------------------
# The entry
# ---------------------------------------------------------------------------

# The single fortune-cookie line this entry writes. Fifteen words by
# whitespace count (the em dash stands alone as its own token),
# seventy-four characters: one breath, one turn, one loss. The em dash
# is a deliberate beat: the fortune pauses, then names who the reunion
# is with -- you, and your savings -- before the last three words
# reveal that the reunion already happened, in a past life.
FORTUNE = "The stars foretell a great reunion \u2014 you and your savings, in a past life."

# Gate limits published in the competition's RULES.txt.
MAX_CHARS = 160
MAX_WORDS = 20

# Where the entry text goes. The grader sets MAKEFUN_OUTPUT_DIR; the
# default matches the competition's contract.
DEFAULT_OUTPUT_DIR = "/output"
ENTRY_FILENAME = "entry.txt"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def word_count(text: str) -> int:
    """Count the words of *text* the way the gate means it: runs of
    non-whitespace characters separated by whitespace."""
    return len(text.split())


def check_fortune(text: str) -> list[str]:
    """Return a list of gate violations for *text* (empty means valid).

    The gate checks UTF-8 text of 1 to 160 characters that is not only
    white space; the task adds at most 20 words of plain text, one
    line. Every condition is checked here so a bad line can never be
    written out by accident.
    """
    problems: list[str] = []

    if not text:
        problems.append("fortune is empty")
    if text != text.strip():
        problems.append("fortune has leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        problems.append("fortune must be a single line")
    if len(text) > MAX_CHARS:
        problems.append(
            f"fortune is {len(text)} characters, over the {MAX_CHARS} cap"
        )
    if not text.strip():
        problems.append("fortune is only white space")
    if word_count(text) > MAX_WORDS:
        problems.append(
            f"fortune is {word_count(text)} words, over the {MAX_WORDS} cap"
        )
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:  # pragma: no cover - cannot happen
        problems.append(f"fortune is not UTF-8 text: {exc}")

    return problems


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def output_dir() -> str:
    """Resolve the output directory from the environment, defaulting
    to the competition's contract location."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)


def write_entry(text: str, directory: str) -> str:
    """Write *text* to ``entry.txt`` inside *directory* atomically.

    The write goes through a temporary file on the same filesystem,
    is made world-readable (mode 0644) so the sealed scorer can read
    it, and is then moved into place with ``os.replace`` so a reader
    never sees a half-written file. No trailing newline is added: the
    gate counts characters, and the line is the whole file.
    """
    os.makedirs(directory, exist_ok=True)
    target = os.path.join(directory, ENTRY_FILENAME)

    fd, tmp_path = tempfile.mkstemp(
        dir=directory, prefix=".entry-", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    return target


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build() -> str:
    """Validate the fortune and return it, ready to write."""
    problems = check_fortune(FORTUNE)
    if problems:
        raise SystemExit(
            "fortune fails the gate: " + "; ".join(problems)
        )
    return FORTUNE


def main(argv: list[str] | None = None) -> int:
    """Entry point: validate the line, then write it out."""
    del argv  # no command-line arguments; the contract is the env var
    fortune = build()
    path = write_entry(fortune, output_dir())
    print(f"wrote {len(fortune)} characters to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
