from context import Context
from loader import load

import collectors
import validators

from collector import Collector
from validator import Validator


def main():

    print("Infrastructure Audit")
    print()

    context = Context()

    print("Loading collectors...")

    collectors_loaded = load(
        collectors,
        Collector
    )

    print(f"Loaded {len(collectors_loaded)} collector(s).")

    print("Loading validators...")

    validators_loaded = load(
        validators,
        Validator
    )

    print(f"Loaded {len(validators_loaded)} validator(s).")

    print()

    print("Collecting...")

    for collector in collectors_loaded:
        collector.collect(context)

    print()

    print("Validating...")

    for validator in validators_loaded:
        validator.validate(context)


if __name__ == "__main__":
    main()