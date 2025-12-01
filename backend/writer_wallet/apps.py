from django.apps import AppConfig


class WriterWalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'writer_wallet'
    
    def ready(self):
        """Import signals when app is ready"""
        import writer_wallet.signals_advance  # noqa