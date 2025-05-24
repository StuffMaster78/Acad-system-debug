from users.models import User

ROLE_HIERARCHY = {
    User.CLIENT: 0,
    User.WRITER: 1,
    User.SUPPORT: 2,
    User.EDITOR: 3,
    User.ADMIN: 4,
    User.SUPERADMIN: 5,
}