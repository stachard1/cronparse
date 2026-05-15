"""Tests for cronparse.chain."""
import pytest

from cronparse.chain import ChainStep, CronChain
from cronparse.exceptions import CronParseError


class TestCronChain:
    def _make(self, name: str = "pipeline") -> CronChain:
        return CronChain(name=name)

    # --- add ---

    def test_add_returns_chain_step(self):
        chain = self._make()
        step = chain.add("* * * * *")
        assert isinstance(step, ChainStep)

    def test_add_stores_step(self):
        chain = self._make()
        chain.add("0 * * * *")
        assert len(chain.steps) == 1

    def test_add_with_label(self):
        chain = self._make()
        step = chain.add("0 9 * * 1", label="weekly report")
        assert step.label == "weekly report"

    def test_add_strips_label_whitespace(self):
        chain = self._make()
        step = chain.add("* * * * *", label="  trimmed  ")
        assert step.label == "trimmed"

    def test_add_with_delay(self):
        chain = self._make()
        step = chain.add("*/5 * * * *", delay_minutes=10)
        assert step.delay_minutes == 10

    def test_add_invalid_expression_raises(self):
        chain = self._make()
        with pytest.raises(CronParseError):
            chain.add("not a cron")

    def test_add_negative_delay_raises(self):
        chain = self._make()
        with pytest.raises(ValueError):
            chain.add("* * * * *", delay_minutes=-1)

    def test_add_multiple_steps(self):
        chain = self._make()
        chain.add("0 6 * * *")
        chain.add("0 7 * * *")
        chain.add("0 8 * * *")
        assert len(chain) == 3

    # --- remove ---

    def test_remove_step_by_index(self):
        chain = self._make()
        chain.add("0 1 * * *")
        chain.add("0 2 * * *")
        chain.remove(0)
        assert len(chain) == 1
        assert chain.steps[0].expression == "0 2 * * *"

    def test_remove_invalid_index_raises(self):
        chain = self._make()
        with pytest.raises(IndexError):
            chain.remove(0)

    # --- reorder ---

    def test_reorder_moves_step(self):
        chain = self._make()
        chain.add("0 1 * * *", label="first")
        chain.add("0 2 * * *", label="second")
        chain.reorder(0, 1)
        assert chain.steps[0].label == "second"
        assert chain.steps[1].label == "first"

    def test_reorder_out_of_range_raises(self):
        chain = self._make()
        chain.add("* * * * *")
        with pytest.raises(IndexError):
            chain.reorder(0, 5)

    # --- summary ---

    def test_summary_empty_chain(self):
        chain = self._make("empty")
        assert "(empty)" in chain.summary()

    def test_summary_lists_steps(self):
        chain = self._make("myjob")
        chain.add("0 6 * * *", label="morning")
        chain.add("0 18 * * *", label="evening")
        text = chain.summary()
        assert "myjob" in text
        assert "morning" in text
        assert "evening" in text

    # --- __str__ on ChainStep ---

    def test_step_str_no_label_no_delay(self):
        step = ChainStep(expression="* * * * *")
        assert str(step) == "* * * * *"

    def test_step_str_with_label_and_delay(self):
        step = ChainStep(expression="0 9 * * *", label="standup", delay_minutes=5)
        result = str(step)
        assert "standup" in result
        assert "+5m" in result
