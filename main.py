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
        print(f"Running collector: {collector.name}")
        collector.collect(context)

    print()

    print("Validating...")

    for validator in validators_loaded:
        print(f"Running validator: {validator.name}")
        validator.validate(context)

    print(f"{'Validator':<15} {'Setting':<50} {'Value':<100} {'Result':>6}")
    for result in context.results:
        output = f"{result[0][:15]:<15} {result[1][:50]:<50} {result[2][:100]:<100} {result[3]:>6}"
        if result[3] == 'Fail':
            output = f"\033[41m{output}\033[0m"
        print(output)

if __name__ == "__main__":
    main()