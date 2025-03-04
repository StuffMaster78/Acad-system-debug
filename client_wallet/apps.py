from django.apps import AppConfig

class ClientWalletConfig(AppConfig):
    name = 'client_wallet'

    def ready(self):
        import client_wallet.signals  # Corrected import statement
