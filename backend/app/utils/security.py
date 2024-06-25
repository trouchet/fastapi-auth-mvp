import re

import uuid

def is_valid_uuid(uuid_str: str):
    """
    This function checks if the provided string is a valid UUID format.

    Args:
        uuid_str: The string to be validated as a UUID.

    Returns:
        True if the string is a valid UUID, False otherwise.
    """
    try:
        # Attempt to convert the string to a UUID object
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        # If conversion fails, it's not a valid UUID
        return False

def is_email_valid(email: str):
    """
    This function checks if the provided string is a valid email address format.

    Args:
        email: The email address string to be validated.

    Returns:
        True if the email format is valid, False otherwise.
    """
    # Improved regular expression for email validation
    email_regex = r"(^([a-zA-Z0-9_\-\.]+)@([a-zA-Z\-_]+\.)+[a-zA-Z]{2,}$)"

    # Check if the email matches the regular expression
    return bool(re.match(email_regex, email))

def password_validity_obj(
    invalid_password_message: str, 
    validity_map: callable
):
    return {
        "invalidation_message": invalid_password_message,
        "validity_map": validity_map
    }

def any_on_string(string: str, string_map: callable):
    return any(string_map(char) for char in string)

def has_lowercase(password: str):
    return any_on_string(password, str.islower)

def has_uppercase(password: str):
    return any_on_string(password, str.isupper)

def has_digit(password: str):
    return any_on_string(password, str.isdigit)

def has_special(password: str):
    def is_special_map(char):
        return not (char.isalnum() or char.isspace())
    return any_on_string(password, is_special_map)

MIN_PASSWORD_LENGTH=8
def has_min_length(password: str, min_length: int = MIN_PASSWORD_LENGTH):
    return len(password) >= MIN_PASSWORD_LENGTH

def without_space(password: str):
    return not any_on_string(password, lambda char: char.isspace())

def password_must_have_str(condition_str: str) -> str:
    return f"Password must have {condition_str}"

def password_cannot_have_str(condition_str: str) -> str:
    return f"Password cannot have {condition_str}"

# Conditions 
CONDITION_LIST=[
    ("has_lowercase", password_must_have_str("lowercase characters"), has_lowercase),
    ("has_uppercase", password_must_have_str("uppercase characters"), has_uppercase),
    ("has_digit", password_must_have_str("numbers"), has_digit),
    ("has_special", password_must_have_str("special characters"), has_special),
    (
        "is_long_enough", 
        password_must_have_str(f"at least {MIN_PASSWORD_LENGTH} characters"), 
        has_min_length
    ),
    ("without_blank", password_cannot_have_str("spaces"), without_space)
]


def get_password_validity_metadict():
    return {
        condition_key: password_validity_obj(invalid_message, invalidation_map)
        for condition_key, invalid_message, invalidation_map in CONDITION_LIST
    }


def apply_password_validity_dict(password: str):
    password_validity_metadict=get_password_validity_metadict()

    password_validity_metadict={
        validity_key: {
            "invalidation_message": condition_dict["invalidation_message"],
            "is_valid": condition_dict["validity_map"](password)
        }
        for validity_key, condition_dict in password_validity_metadict.items()
    }

    return password_validity_metadict


def get_invalid_password_conditions(password: str):
    password_validity_dict=apply_password_validity_dict(password)

    return {
        condition_key: condition_dict["invalidation_message"]
        for condition_key, condition_dict in password_validity_dict.items()
        if not condition_dict["is_valid"]
    }


def is_password_valid(password: str):
    password_validity_dict=apply_password_validity_dict(password)

    return all(
        condition_dict["is_valid"]
        for condition_dict in password_validity_dict.values()
    )
