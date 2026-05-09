"""Additional edge-case tests for cronparse.alias_export."""

import json
import pytest

from cronparse.alias import AliasRegistry
from cronparse.alias_export import from_json, to_json


def _make_registry(*pairs) -> AliasRegistry:
    reg = AliasRegistry()
    for name, expr in pairs:
        reg.register(name, expr)
    return reg


class TestAliasExportEdgeCases:
    def test_to_json_contains_required_keys(self):
        reg = _make_registry(("nightly", "0 2 * * *"))
        data = json.loads(to_json(reg))
        assert "name" in data[0]
        assert "expression" in data[0]
        assert "description" in data[0]

    def test_to_json_description_defaults_to_empty_string(self):
        reg = _make_registry(("weekly", "0 0 * * 0"))
        data = json.loads(to_json(reg))
        assert data[0]["description"] == ""

    def test_from_json_missing_description_key_defaults_empty(self):
        payload = json.dumps([{"name": "test", "expression": "* * * * *"}])
        reg = from_json(payload)
        entry = reg.get("test")
        assert entry is not None
        assert entry.description == ""

    def test_from_json_invalid_expression_raises(self):
        payload = json.dumps([{"name": "bad", "expression": "99 99 99 99 99"}])
        from cronparse.exceptions import CronParseError
        with pytest.raises(CronParseError):
            from_json(payload)

    def test_to_json_ordering_is_alphabetical(self):
        reg = _make_registry(("z_job", "* * * * *"), ("a_job", "0 * * * *"))
        data = json.loads(to_json(reg))
        names = [d["name"] for d in data]
        assert names == sorted(names)

    def test_indent_parameter_respected(self):
        reg = _make_registry(("job", "* * * * *"))
        compact = to_json(reg, indent=None)
        pretty = to_json(reg, indent=4)
        assert "\n" not in compact
        assert "\n" in pretty
