"""Tests for cronparse.export."""

import csv
import io

from cronparse.export import to_csv, to_text
from cronparse.history import CronHistory


EXPR_WILDCARD = "* * * * *"
EXPR_DAILY = "0 9 * * *"


def _make_history() -> CronHistory:
    """Return a CronHistory with two entries for use in tests."""
    h = CronHistory()
    h.add(EXPR_WILDCARD, label="every minute")
    h.add(EXPR_DAILY)
    return h


def _csv_rows(output: str) -> list[list[str]]:
    """Parse CSV output into a list of rows, including the header."""
    return list(csv.reader(io.StringIO(output)))


class TestToCsv:
    def test_returns_string(self):
        assert isinstance(to_csv(_make_history()), str)

    def test_header_row_present(self):
        output = to_csv(_make_history())
        header = _csv_rows(output)[0]
        assert header == ["expression", "label", "added_at", "description"]

    def test_correct_number_of_data_rows(self):
        output = to_csv(_make_history())
        rows = _csv_rows(output)
        assert len(rows) == 3  # header + 2 entries

    def test_expression_column_correct(self):
        output = to_csv(_make_history())
        expressions = [r[0] for r in _csv_rows(output)[1:]]
        assert EXPR_WILDCARD in expressions
        assert EXPR_DAILY in expressions

    def test_label_column_populated(self):
        output = to_csv(_make_history())
        labels = {r[0]: r[1] for r in _csv_rows(output)[1:]}
        assert labels[EXPR_WILDCARD] == "every minute"
        assert labels[EXPR_DAILY] == ""

    def test_description_column_present_when_human_true(self):
        output = to_csv(_make_history(), human=True)
        descriptions = [r[3] for r in _csv_rows(output)[1:]]
        assert all(d != "" for d in descriptions)

    def test_description_column_empty_when_human_false(self):
        output = to_csv(_make_history(), human=False)
        descriptions = [r[3] for r in _csv_rows(output)[1:]]
        assert all(d == "" for d in descriptions)


class TestToText:
    def test_returns_string(self):
        assert isinstance(to_text(_make_history()), str)

    def test_one_line_per_entry(self):
        output = to_text(_make_history())
        lines = output.strip().splitlines()
        assert len(lines) == 2

    def test_expression_appears_in_line(self):
        output = to_text(_make_history())
        assert EXPR_WILDCARD in output
        assert EXPR_DAILY in output

    def test_label_appears_in_line(self):
        output = to_text(_make_history())
        assert "[every minute]" in output

    def test_human_description_included_by_default(self):
        output = to_text(_make_history())
        assert "\u2014" in output  # em-dash separator

    def test_human_description_omitted_when_false(self):
        output = to_text(_make_history(), human=False)
        assert "\u2014" not in output
