from __future__ import annotations

from typing import Any


class RuleOperators:

    @staticmethod
    def evaluate(actual: Any, operator: str, expected: Any) -> bool:

        if operator == "eq":
            return actual == expected

        if operator == "neq":
            return actual != expected

        if operator == "in":
            return actual in expected if expected is not None else False

        if operator == "not_in":
            return actual not in expected if expected is not None else True

        if operator == "contains":
            return bool(actual and expected in actual)

        if operator == "gt":
            return _safe_compare(actual, expected, lambda a, b: a > b)

        if operator == "gte":
            return _safe_compare(actual, expected, lambda a, b: a >= b)

        if operator == "lt":
            return _safe_compare(actual, expected, lambda a, b: a < b)

        if operator == "lte":
            return _safe_compare(actual, expected, lambda a, b: a <= b)

        if operator == "truthy":
            return bool(actual)

        if operator == "falsy":
            return not bool(actual)

        return False


def _safe_compare(a: Any, b: Any, fn) -> bool:
    try:
        if a is None or b is None:
            return False
        return fn(a, b)
    except Exception:
        return False