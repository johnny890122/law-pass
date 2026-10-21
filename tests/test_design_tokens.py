"""LP-0004-07: static/css/tokens.css is the app's one token file and the only home of a color literal."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "static/css/tokens.css"
DECLARED = re.compile(r"^\s*(--[\w-]+)\s*:", re.M)
# The neta-design hex grep, minus HTML character references such as &#160;
LITERAL = re.compile(r"(?<!&)#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")


def test_tokens_cover_the_contract():
    contract = set(DECLARED.findall((ROOT / ".claude/skills/neta-design/tokens/_structure.css").read_text()))
    assert contract - set(DECLARED.findall(TOKENS.read_text())) == set()


def test_no_color_literal_outside_tokens():
    files = [*ROOT.glob("templates/**/*.html"), *ROOT.glob("static/js/**/*.js"), *ROOT.glob("static/css/*.css")]
    hits = [
        f"{path.relative_to(ROOT)}:{number}: {line.strip()}"
        for path in files if path != TOKENS
        for number, line in enumerate(path.read_text().splitlines(), 1) if LITERAL.search(line)
    ]
    assert hits == []


def test_dark_names_exist_in_light():  # LP-0004-09: a misspelled dark name would do nothing silently
    light, dark = TOKENS.read_text().split(':root[data-theme="dark"] {')
    assert set(DECLARED.findall(dark)) - set(DECLARED.findall(light)) == set()


def test_no_os_theme_reading():  # LP-0004-09: the stored choice is the only source of the theme
    files = [*ROOT.glob("templates/**/*.html"), *ROOT.glob("static/js/**/*.js"), *ROOT.glob("static/css/*.css")]
    assert [str(path.relative_to(ROOT)) for path in files if "prefers-color-scheme" in path.read_text()] == []


def test_figma_token_files_are_retired():
    assert not (ROOT / "static/css/design-tokens.css").exists()
    assert not (ROOT / "static/css/design-tokens-dark.css").exists()
