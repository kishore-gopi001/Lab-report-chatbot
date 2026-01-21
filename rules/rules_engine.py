def evaluate_lab(row, thresholds):
    """
    Deterministic rule-based lab classification.
    """

    # 🔑 Use canonical name FIRST, fallback to raw name
    test_name = row.get("canonical_test_name") or row.get("test_name")
    value = row.get("valuenum")
    gender = row.get("gender")

    if test_name is None or value is None:
        return {
            "status": "UNKNOWN",
            "reason": "Missing test name or value"
        }

    if test_name not in thresholds:
        return {
            "status": "UNKNOWN",
            "reason": "No rule configured for this test"
        }

    test_rules = thresholds[test_name]

    rule = test_rules.get(gender) or test_rules.get("ALL")
    if rule is None:
        return {
            "status": "UNKNOWN",
            "reason": "No applicable rule for patient context"
        }

    if "critical_min" in rule and value < rule["critical_min"]:
        return {"status": "CRITICAL", "reason": "Critically low value"}

    if "critical_max" in rule and value > rule["critical_max"]:
        return {"status": "CRITICAL", "reason": "Critically high value"}

    if "min" in rule and value < rule["min"]:
        return {"status": "ABNORMAL", "reason": "Below normal range"}

    if "max" in rule and value > rule["max"]:
        return {"status": "ABNORMAL", "reason": "Above normal range"}

    return {"status": "NORMAL", "reason": "Within normal range"}
