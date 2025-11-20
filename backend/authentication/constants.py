# authentication/constants.py
ROLE_CLIENT = 'client'
ROLE_WRITER = 'writer'
ROLE_SUPPORT = 'support'
ROLE_EDITOR = 'editor'
ROLE_ADMIN = 'admin'
ROLE_SUPERADMIN = 'superadmin'

ROLE_HIERARCHY = {
    ROLE_CLIENT: 0,
    ROLE_WRITER: 1,
    ROLE_SUPPORT: 2,
    ROLE_EDITOR: 3,
    ROLE_ADMIN: 4,
    ROLE_SUPERADMIN: 5,
}