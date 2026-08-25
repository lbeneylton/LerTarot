from enum import Enum


class UserType(str, Enum):
    client = "client"
    reader = "reader"
    admin = "admin"
