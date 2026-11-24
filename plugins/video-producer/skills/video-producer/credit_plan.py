import argparse
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path


def credits(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise ValueError(f'{name}: enter the exact numeric credit quote.')
    exact = Decimal(value)
    if not exact.is_finite() or exact < 0:
        raise ValueError(f'{name}: credits must be finite and non-negative.')
    return int(exact.to_integral_value(rounding=ROUND_CEILING))


def check(plan):
    cap = credits(plan['cap'], 'cap') if type(plan['cap']) is int else None
    if cap is None:
        raise ValueError('cap: enter an integer credit budget.')
    spent = credits(plan.get('spent', 0), 'spent')
    reserve = credits(plan.get('reserve', 0), 'reserve')
    shots = plan['shots']
    if not isinstance(shots, list) or not shots:
        raise ValueError('shots: enter at least one current quote.')
    amounts = {}
    for shot in shots:
        name = shot['id']
        count = shot.get('count', 1)
        if not isinstance(name, str) or not name.strip() or name in amounts:
            raise ValueError('Every line needs a unique, non-empty shot ID.')
        if type(count) is not int or count < 1:
            raise ValueError(f'{name}: count must be a positive integer.')
        amounts[name] = credits(shot['quoted_credits'], name) * count
    planned = sum(amounts.values())
    remaining = cap - spent - reserve - planned
    return {'cap': cap, 'spent': spent, 'reserve': reserve, 'planned': planned,
            'remaining': remaining, 'within_budget': remaining >= 0, 'line_items': amounts}


def main():
    parser = argparse.ArgumentParser(description='Check a quoted Higgsfield shot plan against a credit cap.')
    parser.add_argument('plan', type=Path)
    args = parser.parse_args()
    try:
        with args.plan.open(encoding='utf-8-sig') as source:
            result = check(json.load(source, parse_float=Decimal))
    except (KeyError, OSError, TypeError, ValueError, InvalidOperation) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result['within_budget'] else 2


if __name__ == '__main__':
    sys.exit(main())
