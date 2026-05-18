import hashlib


class PercentageRollout:

    @staticmethod
    def is_enabled(
        key: str,
        actor_id: int,
        percentage: int,
    ) -> bool:
        seed = f"{key}:{actor_id}"

        hashed = hashlib.md5(seed.encode()).hexdigest()

        bucket = int(hashed, 16) % 100

        return bucket < percentage