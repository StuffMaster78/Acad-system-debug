from django.apps import AppConfig
from django.conf import settings


class WriterWalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'writer_wallet'
    
    def ready(self):
        """Keep legacy writer_wallet signals disabled by default."""
        if not getattr(settings, "ENABLE_LEGACY_WRITER_WALLET_SIGNALS", False):
            return
        try:
            import writer_wallet.signals_advance  # noqa: F401
        except Exception:
            pass
