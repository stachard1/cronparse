# cronparse

> Human-readable cron expression parser and validator with next-run previews

---

## Installation

```bash
pip install cronparse
```

---

## Usage

```python
from cronparse import CronExpression

cron = CronExpression("0 9 * * 1-5")

# Get a human-readable description
print(cron.describe())
# → "At 09:00 AM, Monday through Friday"

# Validate an expression
print(cron.is_valid())
# → True

# Preview the next scheduled runs
for run in cron.next_runs(count=3):
    print(run)
# → 2024-05-13 09:00:00
# → 2024-05-14 09:00:00
# → 2024-05-15 09:00:00
```

### Validation

```python
from cronparse import validate

result = validate("99 25 * * *")
print(result.valid)    # → False
print(result.errors)   # → ["Hour value '25' out of range (0-23)"]
```

---

## Features

- Parse and describe any standard 5-field cron expression
- Validate expressions with detailed error messages
- Preview upcoming run times from any reference datetime
- Zero external dependencies

---

## License

This project is licensed under the [MIT License](LICENSE).