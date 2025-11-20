# scripts/check_event_configs.py (run with your venv)
from notifications_system.registry.validator import validate_all_in_dir

ok, results = validate_all_in_dir(
    config_dir="notifications_system/events",  # adjust path
    schema_name="event_config_schema",
    glob="*.json",
)

for path, res in results:
    if not res.ok:
        print(f"\n{path}:")
        for e in res.errors:
            print("  " + e)

print("\nALL GOOD" if ok else "\nSOME FILES FAILED")