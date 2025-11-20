def check_rule(rule_code: str, metrics) -> bool:
    mapping = {
        "top_10_3_weeks": lambda m: m.top_10_streak_weeks >= 3,
        "big_earner": lambda m: m.total_earned_usd >= 1000,
        "no_revisions": lambda m: m.zero_revision_orders >= 10,
        "cool_head": lambda m: m.completed_orders >= 20 and m.dispute_rate == 0,
        "hot_streak": lambda m: m.activity_streak_days >= 7,
        "chosen_one": lambda m: m.preferred_by_count >= 5,
    }
    fn = mapping.get(rule_code)
    return fn(metrics) if fn else False