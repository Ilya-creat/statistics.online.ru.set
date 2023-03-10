import re


def check_email(email):
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
        return False
    return True


def has_uppercase(text):
    for c in text:
        if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            return True
    return False


def has_lowercase(text):
    for c in text:
        if c in 'abcdefghijklmnopqrstuvwxyz':
            return True
    return False


def has_digit(text):
    for c in text:
        if c in '1234567890':
            return True
    return False


def is_valid_password(password):
    if len(password) < 6:
        return False

    if not has_uppercase(password):
        return False

    if not has_lowercase(password):
        return False

    if not has_digit(password):
        return False

    return True


def is_valid_login(login):
    if len(login) < 4:
        return False

    return has_lowercase(login) or has_uppercase(login)
