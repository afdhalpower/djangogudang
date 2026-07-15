#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Clear external PYTHONPATH so our venv packages aren't shadowed
os.environ.pop("PYTHONPATH", None)

# Remove Hermes paths from sys.path — they may contain incompatible
# package versions (e.g. Pillow compiled for Python 3.11 vs our 3.12).
sys.path = [p for p in sys.path if "hermes-agent" not in p]


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
