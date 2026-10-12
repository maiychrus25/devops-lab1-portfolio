#!/usr/bin/env python3
"""Reject broken tag nesting in the static portfolio using Python's stdlib."""

from html.parser import HTMLParser
from pathlib import Path
import sys


VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class NestingCheck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.tags = set()

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.tags.add(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            raise ValueError(f"unexpected closing tag </{tag}>")
        self.stack.pop()


def main():
    if len(sys.argv) != 2:
        print("usage: validate-html.py FILE", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    try:
        source = path.read_text(encoding="utf-8")
        if not source.lstrip().lower().startswith("<!doctype html>"):
            raise ValueError("missing HTML5 doctype")
        parser = NestingCheck()
        parser.feed(source)
        parser.close()
        # shortcut: rejects omitted optional HTML end tags; use an HTML5 validator if the page starts relying on them.
        if parser.stack:
            raise ValueError(f"unclosed tag <{parser.stack[-1]}>")
        if not {"html", "head", "title", "body"}.issubset(parser.tags):
            raise ValueError("required document tags are missing")
    except (OSError, ValueError) as error:
        print(f"HTML validation failed: {error}", file=sys.stderr)
        return 1

    print(f"HTML structure valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
