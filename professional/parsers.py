"""
Helpers for parsing the multi-line text fields stored on `home.Profile`
into structured pieces the professional-page template can render.

The Profile model stores skills, core_competencies, languages, and
interests as free-form text (one item / category per line). These
helpers turn that text into lists of chips / categories that the
template can iterate over without doing any parsing itself.
"""

from typing import List, Tuple


def parse_skill_categories(text: str) -> List[Tuple[str, List[str]]]:
    """Parse Profile.skills into a list of (category, [items]) tuples.

    The expected format is one category per line, e.g.
        Languages: Python, SQL, JavaScript
        Data Science & ML: Pandas, NumPy, scikit-learn

    Lines without a colon are treated as a single chip with no category.
    Empty / whitespace-only lines are skipped.
    """
    if not text:
        return []
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            cat, _, items = line.partition(":")
            cat = cat.strip()
            chips = [c.strip() for c in items.split(",") if c.strip()]
            out.append((cat, chips))
        else:
            # No colon — treat the whole line as a chip under a generic
            # "Skills" category.
            out.append(("", [line]))
    return out


def parse_simple_lines(text: str) -> List[str]:
    """Parse a multi-line text field into a clean list of strings.

    Used for core_competencies, achievements (fallback), interests.
    Splits on newlines OR commas; trims; drops empties.
    """
    if not text:
        return []
    pieces = []
    for line in text.splitlines():
        for piece in line.split(","):
            piece = piece.strip()
            if piece:
                pieces.append(piece)
    return pieces


def parse_languages(text: str) -> List[Tuple[str, str]]:
    """Parse Profile.languages into a list of (language, level) tuples.

    Expected format: one per line as 'Language: Level'.
    Falls back to (line, '') when no colon is present.
    """
    if not text:
        return []
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            lang, _, level = line.partition(":")
            out.append((lang.strip(), level.strip()))
        else:
            out.append((line, ""))
    return out
