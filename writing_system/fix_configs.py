# fix_configs.py  (pure Python; no Django import)
import json, sys, os
from pathlib import Path

# allow importing compat from your package
sys.path.insert(0, os.path.abspath("."))

from notifications_system.registry.compat import (
    normalize_broadcast, normalize_digest, normalize_notifications
)

def fix_one(path: Path, fn):
    if not path.exists():
        print(f"[skip] missing: {path}")
        return
    original = json.loads(path.read_text())
    normalized = fn(original)
    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_text(json.dumps(original, indent=2, ensure_ascii=False))
    path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False))
    print(f"[ok] fixed: {path}  (backup: {backup.name})")

def main(cfg_dir: str):
    d = Path(cfg_dir)
    fix_one(d / "broadcast_event_config.json", normalize_broadcast)
    fix_one(d / "digest_event_config.json", normalize_digest)
    fix_one(d / "notification_event_config.json", normalize_notifications)

if __name__ == "__main__":
    cfg_dir = sys.argv[1] if len(sys.argv) > 1 else "./notifications_system/registry/configs"
    main(cfg_dir)