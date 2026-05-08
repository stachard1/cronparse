"""Pre-defined cron expression templates with descriptions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Template:
    name: str
    expression: str
    description: str
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name}: {self.expression} — {self.description}"


_BUILTIN_TEMPLATES: List[Template] = [
    Template("every_minute",   "* * * * *",       "Every minute",                  ["frequent"]),
    Template("every_5min",     "*/5 * * * *",     "Every 5 minutes",               ["frequent"]),
    Template("every_15min",    "*/15 * * * *",    "Every 15 minutes",              ["frequent"]),
    Template("every_30min",    "*/30 * * * *",    "Every 30 minutes",              ["frequent"]),
    Template("hourly",         "0 * * * *",       "Every hour at minute 0",        ["hourly"]),
    Template("daily_midnight", "0 0 * * *",       "Daily at midnight",             ["daily"]),
    Template("daily_noon",     "0 12 * * *",      "Daily at noon",                 ["daily"]),
    Template("weekly_monday",  "0 9 * * 1",       "Every Monday at 09:00",         ["weekly"]),
    Template("monthly_first",  "0 0 1 * *",       "First day of every month",      ["monthly"]),
    Template("yearly",         "0 0 1 1 *",       "Once a year on Jan 1 midnight", ["yearly"]),
    Template("weekdays_9am",   "0 9 * * 1-5",     "Weekdays at 09:00",             ["weekly", "business"]),
    Template("weekends",       "0 10 * * 6,0",    "Weekends at 10:00",             ["weekly"]),
]


class TemplateRegistry:
    """Registry for built-in and user-defined cron templates."""

    def __init__(self) -> None:
        self._templates: Dict[str, Template] = {
            t.name: t for t in _BUILTIN_TEMPLATES
        }

    def register(self, template: Template) -> Template:
        """Add or overwrite a named template."""
        if not template.name:
            raise ValueError("Template name must not be empty.")
        self._templates[template.name] = template
        return template

    def get(self, name: str) -> Optional[Template]:
        """Return a template by name, or None."""
        return self._templates.get(name)

    def all(self) -> List[Template]:
        """Return all registered templates."""
        return list(self._templates.values())

    def by_tag(self, tag: str) -> List[Template]:
        """Return templates matching *tag* (case-insensitive)."""
        tag_lower = tag.lower()
        return [t for t in self._templates.values() if tag_lower in [x.lower() for x in t.tags]]

    def search(self, query: str) -> List[Template]:
        """Return templates whose name or description contains *query*."""
        q = query.lower()
        return [
            t for t in self._templates.values()
            if q in t.name.lower() or q in t.description.lower()
        ]

    def remove(self, name: str) -> bool:
        """Remove a template by name. Returns True if it existed."""
        return self._templates.pop(name, None) is not None
