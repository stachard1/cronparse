"""Tests for cronparse.forecast and cronparse.forecast_export."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from cronparse.forecast import ForecastWindow, forecast
from cronparse.forecast_export import to_json, to_text
from cronparse.exceptions import CronParseError


_BASE = datetime(2024, 6, 1, 0, 0, 0)


class TestForecast:
    def test_returns_forecast_window_instance(self):
        result = forecast("* * * * *", start=_BASE, hours=1)
        assert isinstance(result, ForecastWindow)

    def test_every_minute_one_hour_gives_60_runs(self):
        result = forecast("* * * * *", start=_BASE, hours=1)
        assert result.count == 60

    def test_hourly_one_day_gives_24_runs(self):
        result = forecast("0 * * * *", start=_BASE, hours=24)
        assert result.count == 24

    def test_daily_midnight_one_week_gives_7_runs(self):
        result = forecast("0 0 * * *", start=_BASE, hours=24 * 7)
        assert result.count == 7

    def test_run_times_are_datetime_instances(self):
        result = forecast("0 * * * *", start=_BASE, hours=3)
        assert all(isinstance(dt, datetime) for dt in result.run_times)

    def test_all_run_times_within_window(self):
        result = forecast("* * * * *", start=_BASE, hours=2)
        for dt in result.run_times:
            assert _BASE <= dt < result.end

    def test_invalid_expression_raises(self):
        with pytest.raises(CronParseError):
            forecast("99 * * * *", start=_BASE, hours=1)

    def test_runs_per_hour_every_minute(self):
        result = forecast("* * * * *", start=_BASE, hours=1)
        assert abs(result.runs_per_hour - 60.0) < 0.01

    def test_expression_stored_on_result(self):
        expr = "30 6 * * *"
        result = forecast(expr, start=_BASE, hours=24)
        assert result.expression == expr

    def test_str_contains_expression(self):
        result = forecast("0 0 * * *", start=_BASE, hours=24)
        assert "0 0 * * *" in str(result)


class TestForecastExport:
    def _windows(self):
        return [forecast("0 * * * *", start=_BASE, hours=3)]

    def test_to_json_returns_string(self):
        assert isinstance(to_json(self._windows()), str)

    def test_to_json_is_valid_json(self):
        data = json.loads(to_json(self._windows()))
        assert isinstance(data, list)

    def test_to_json_contains_required_keys(self):
        data = json.loads(to_json(self._windows()))
        keys = {"expression", "start", "end", "count", "runs_per_hour", "run_times"}
        assert keys <= data[0].keys()

    def test_to_json_run_count_matches(self):
        fw = forecast("0 * * * *", start=_BASE, hours=3)
        data = json.loads(to_json([fw]))
        assert data[0]["count"] == fw.count

    def test_to_text_returns_string(self):
        assert isinstance(to_text(self._windows()), str)

    def test_to_text_contains_expression(self):
        text = to_text(self._windows())
        assert "0 * * * *" in text

    def test_to_text_empty_list(self):
        assert to_text([]) == "No forecast data."
