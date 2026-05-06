"""Tests for cronparse.scheduler."""

import pytest

from cronparse.exceptions import CronParseError
from cronparse.scheduler import CronScheduler, ScheduledJob


class TestCronScheduler:
    def _make(self) -> CronScheduler:
        return CronScheduler()

    # ------------------------------------------------------------------
    def test_add_returns_scheduled_job(self):
        s = self._make()
        job = s.add("heartbeat", "* * * * *")
        assert isinstance(job, ScheduledJob)

    def test_add_stores_job(self):
        s = self._make()
        s.add("heartbeat", "* * * * *")
        assert len(s) == 1

    def test_add_with_description(self):
        s = self._make()
        job = s.add("daily", "0 9 * * *", description="Morning digest")
        assert job.description == "Morning digest"

    def test_add_invalid_expression_raises(self):
        s = self._make()
        with pytest.raises(CronParseError):
            s.add("bad", "99 * * * *")

    def test_add_empty_name_raises(self):
        s = self._make()
        with pytest.raises(ValueError):
            s.add("", "* * * * *")

    def test_get_existing_job(self):
        s = self._make()
        s.add("job1", "0 0 * * *")
        job = s.get("job1")
        assert job is not None
        assert job.name == "job1"

    def test_get_missing_job_returns_none(self):
        s = self._make()
        assert s.get("ghost") is None

    def test_remove_job(self):
        s = self._make()
        s.add("tmp", "* * * * *")
        s.remove("tmp")
        assert len(s) == 0

    def test_remove_missing_raises(self):
        s = self._make()
        with pytest.raises(KeyError):
            s.remove("nope")

    def test_all_jobs_returns_list(self):
        s = self._make()
        s.add("a", "* * * * *")
        s.add("b", "0 12 * * *")
        jobs = s.all_jobs()
        assert len(jobs) == 2
        assert all(isinstance(j, ScheduledJob) for j in jobs)

    def test_iter(self):
        s = self._make()
        s.add("x", "5 4 * * *")
        names = [j.name for j in s]
        assert names == ["x"]

    def test_summary_structure(self):
        s = self._make()
        s.add("daily", "0 6 * * *", description="Dawn job")
        rows = s.summary()
        assert len(rows) == 1
        row = rows[0]
        assert set(row.keys()) == {"name", "expression", "description", "next_runs"}
        assert row["name"] == "daily"
        assert len(row["next_runs"]) == 3

    def test_scheduled_job_str(self):
        job = ScheduledJob(name="ping", expression="*/5 * * * *")
        assert "ping" in str(job)
        assert "*/5 * * * *" in str(job)

    def test_next_runs_returns_iso_strings(self):
        s = self._make()
        job = s.add("every_minute", "* * * * *")
        runs = job.next_runs(2)
        assert len(runs) == 2
        # Basic ISO-8601 sanity check
        for r in runs:
            assert "T" in r
