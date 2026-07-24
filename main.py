from context import Context
from loader import load

import collectors
import validators

from collector import Collector
from validator import Validator


def main():

    print("Infrastructure Audit")

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
    print("Collecting...")

    for collector in collectors_loaded:
        print(f"Running collector: {collector.name}")
        collector.collect(context)

    print()

    print("Validating...")

    for validator in validators_loaded:
        print(f"Running validator: {validator.name}")
        validator.validate(context)

    # Define Column Widths
    testCol     = 25
    settingCol  = 35
    valueCol    = 75
    expectedCol = 75
    resultCol   = 6

    print(f"{'Validator'.ljust(testCol)} {'Setting'.ljust(settingCol)} {'Value'.ljust(valueCol)} {'Expected Value'.ljust(expectedCol)} {'Result'.rjust(resultCol)}")
    for result in context.results:
        outcome = 'Pass' if result['passes'] else 'Fail'
        output = f"{str(result['validator'])[:testCol].ljust(testCol)} {str(result['config'])[:settingCol].ljust(settingCol)} {str(result['value_fnd'])[:valueCol].ljust(valueCol)} {str(result['value_exp'])[:expectedCol].ljust(expectedCol)} {outcome.rjust(resultCol)}"
        if not result['passes']:
            output = f"\033[41m{output}\033[0m"
        print(output)

if __name__ == "__main__":
    main()