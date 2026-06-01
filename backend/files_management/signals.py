from django.dispatch import Signal

# Fired the first time a client successfully downloads a final or
# milestone file attachment. Receivers can use this to trigger downstream
# actions such as order completion checks.
#
# Keyword arguments sent:
# attachment — the FileAttachment that was downloaded
# user — the user who downloaded the file
file_first_downloaded = Signal()
