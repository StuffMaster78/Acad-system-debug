from django.urls import path, include

urlpatterns = [
    path('account-unlock/', include('authentication.urls.account_unlock')),        # views/account_unlock_views.py
    path('account/', include('authentication.urls.account')),                      # views/account.py
    path('auth/', include('authentication.urls.authentication')),                  # views/authentication.py
    path('deletion/', include('authentication.urls.deletion')),                    # views/deletion.py
    path('forbidden/', include('authentication.urls.forbidden_access')),           # views/forbidden_access.py
    path('mfa/settings/', include('authentication.urls.mfa_settings')),            # views/mfa_settings.py
    path('mfa/', include('authentication.urls.mfa')),                              # views/mfa.py
    path('mfa-views/', include('authentication.urls.mfa_views')),                  # views/mfa_views.py
    path('passkey/', include('authentication.urls.passkey_views')),                # views/passkey_views.py
    path('sessions/', include('authentication.urls.sessions_management')),         # views/sessions_management.py
    path('passkeys/devices/', include('urls.devices')), #views/devices.py
]
