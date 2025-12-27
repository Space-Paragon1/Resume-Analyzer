# tests/test_parsing.py
from __future__ import annotations
import types
import pytest

from src.parsing import clean_text, read_text_input, extract_text_from_pdf

def test_clean_text_removes_nbsp_and_collapses_spaces_and_tabs():
    raw = "Hello\xa0\xa0World\t\tThis   is   spaced"
    out = clean_text(raw)
    assert out == "Hello World This is spaced"

def test_clean_text_collapses_multiple_blank_lines_to_double_newline():
    raw = "Line1\n\n\n\nLine2\n\n\nLine3"
    out = clean_text(raw)
    assert out == "Line1\n\nLine2\n\nLine3"

def test_clean_text_strips_edges():
    raw = "   Hello \n"
    out = clean_text(raw)
    assert out == "Hello"

def test_read_text_input_handles_none_and_empty():
    assert read_text_input(None) == ""
    assert read_text_input("") == ""
    assert read_text_input(" \n\t ") == ""

def test_read_text_input_uses_clean_text():
    raw = "A\xa0B   C"
    assert read_text_input(raw) == "A B C"

def test_extract_text_from_pdf_uses_fitz_open_and_cleans(monkeypatch):
    # Build a fake "doc" iterable that yields "pages" with get_text("text")
    class FakePage:
        def __init__(self, txt: str):
            self._txt = txt
        def get_text(self, mode: str):
            assert mode == "text"
            return self._txt

    class FakeDoc:
        def __iter__(self):
            return iter([
                FakePage("Hello\xa0World\n\n\n\n"),
                FakePage("Second\t\tPage   Text"),
            ])

    def fake_open(*, stream, filetype):
        # Verify we pass the right arguments
        assert isinstance(stream, (bytes, bytearray))
        assert filetype == "pdf"
        return FakeDoc()

    # Patch the fitz.open used inside src.parsing
    import src.parsing as parsing_mod
    monkeypatch.setattr(parsing_mod.fitz, "open", fake_open)

    out = extract_text_from_pdf(b"%PDF-FAKE%")
    # Should be cleaned and joined
    assert out == "Hello World\n\nSecond Page Text"
