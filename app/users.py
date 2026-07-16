from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$EvyMvRJKChjudMQJrqO91u4HZheP8oE4x7xz1Clr2LNHWqaVnxw4u"
    }
}