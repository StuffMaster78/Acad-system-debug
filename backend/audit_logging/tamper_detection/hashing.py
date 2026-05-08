import hashlib
import json


class AuditHashingService:

    @staticmethod
    def compute_hash(payload: dict) -> str:

        serialized = json.dumps(
            payload,
            sort_keys=True,
            default=str,
        )

        return hashlib.sha256(
            serialized.encode()
        ).hexdigest()