import os


class FeatureFlags:
    def __init__(self):
        self.flags = {
            "NEW_CHECKOUT": os.getenv("FF_NEW_CHECKOUT", "false") == "true",
            "BILLING_V2": os.getenv("FF_BILLING_V2", "false") == "true",
            "NOTIFICATIONS_V2": (
                os.getenv("FF_NOTIFICATIONS_V2", "false") == "true"
            ),
            "ORDER_ENGINE_V2": (
                os.getenv("FF_ORDER_ENGINE_V2", "false") == "true"
            ),
        }

    def is_enabled(self, flag: str) -> bool:
        return self.flags.get(flag, False)


feature_flags = FeatureFlags()


def feature(flag: str) -> bool:
    return feature_flags.is_enabled(flag)
