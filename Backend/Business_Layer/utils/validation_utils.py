import re
from fastapi import HTTPException, status

def validate_non_empty(value: str, field_name: str = "Field") -> str:
    """
    Ensures the given string is not empty or whitespace.
    - Strips leading/trailing spaces.
    - Raises ValueError if empty or None.
    """
    if not value or not isinstance(value, str):
        raise ValueError(f"{field_name} cannot be null or empty")

    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be blank or just spaces")

    return cleaned


def validate_numbers_only(value: str, field_name: str = "Field") -> str:
    """
    Ensures the given string contains only numeric digits.
    - Strips spaces.
    - No letters, commas, or symbols allowed.
    """
    cleaned = validate_non_empty(value, field_name)

    if not cleaned.isdigit():
        raise ValueError(f"{field_name} must contain only numeric digits")

    return cleaned


def validate_alphabets_only(value: str, field_name: str = "Field") -> str:
    """
    Ensures the given string contains only alphabets and spaces.
    - Strips leading/trailing spaces.
    - No digits or special characters allowed.
    """
    cleaned = validate_non_empty(value, field_name)

    if not re.match(r"^[A-Za-z\s]+$", cleaned):
        raise ValueError(f"{field_name} must contain only alphabets and spaces")

    return cleaned


def validate_name(first_name: str) -> str:
    """
    Validates the first name.
    Rules:
      - Must not be empty
      - Only alphabets and spaces allowed
      - Automatically trims leading/trailing spaces
    """
    if not first_name or not first_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="First name cannot be empty"
        )

    # Trim spaces first
    first_name = first_name.strip()

    # Allow only alphabets and spaces
    if not re.match(r"^[A-Za-z ]+$", first_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="First name can only contain alphabets and spaces"
        )

    return first_name


def validate_email(email: str) -> str:
    """
    Validates email address.
    Rules:
      - Must not be empty
      - Must follow standard email format
      - Automatically trims leading/trailing spaces
    """
    if not email or not email.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email cannot be empty"
        )

    email = email.strip()

    # Simple and practical regex for email format
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    return email


def validate_country_code(country_code: str) -> str:
    """
    Validates a country calling code.
    - Only digits allowed (no '+', spaces, or symbols)
    - Length must be between 1 and 4 digits
    - Removes any leading/trailing spaces before validation
    """
    code = country_code.strip()

    if not code:
        raise ValueError("Country code cannot be empty.")

    if not re.fullmatch(r"\d{1,4}", code):
        raise ValueError("Invalid country code format. It should contain only 1–4 digits without '+' or spaces.")

    return code


def validate_phone_number(phone_number: str) -> str:
    """
    Validates and normalizes a phone number for database storage.
    - Removes spaces, dashes, brackets, and dots.
    - Ensures only digits remain.
    - Checks length (7–15 digits as per E.164 standard).
    - Returns normalized version (digits only).
    """
    if not phone_number or not isinstance(phone_number, str):
        raise ValueError("Phone number cannot be empty or null")

    # Remove common formatting characters
    cleaned = re.sub(r"[()\s\-\.]", "", phone_number)

    # Ensure only digits remain
    if not cleaned.isdigit():
        raise ValueError("Phone number must contain only digits")

    # Validate length (E.164 standard: 7–15 digits)
    if not 7 <= len(cleaned) <= 15:
        raise ValueError("Phone number length must be between 7 and 15 digits")

    return cleaned


def validate_designation(designation: str) -> str:
    """
    Validates a designation field.
    - Strips leading and trailing spaces.
    - Ensures it's not empty after trimming.
    - Allows only letters, spaces, periods, and hyphens (e.g., 'Sr. Software Engineer', 'Vice-President').
    - Returns the cleaned string.
    """
    if not designation or not isinstance(designation, str):
        raise ValueError("Designation cannot be empty or null")

    # Remove leading and trailing spaces
    cleaned = designation.strip()

    if not cleaned:
        raise ValueError("Designation cannot be empty or just spaces")

    # Allow letters, spaces, dots, and hyphens
    if not re.match(r"^[A-Za-z\s\.-]+$", cleaned):
        raise ValueError("Designation can only contain letters, spaces, periods, and hyphens")

    return cleaned


def validate_package(package: str) -> str:
    """
    Validates a salary package value.
    - Strips leading/trailing spaces.
    - Ensures it's not empty.
    - Allows only numeric digits (no commas, symbols, or alphabets).
    - Returns the cleaned numeric string.
    """
    if not package or not isinstance(package, str):
        raise ValueError("Package cannot be empty or null")

    # Remove leading/trailing spaces
    cleaned = package.strip()

    if not cleaned:
        raise ValueError("Package cannot be empty or just spaces")

    # Ensure only digits
    if not cleaned.isdigit():
        raise ValueError("Package must contain only numeric digits")

    return cleaned


def validate_currency(currency: str) -> str:
    """
    Validates a currency code.
    - Strips leading and trailing spaces.
    - Ensures it's not empty.
    - Allows only uppercase letters (ISO 4217 format, e.g., 'USD', 'INR', 'EUR').
    - Length must be exactly 3 characters.
    - Returns the cleaned uppercase code.
    """
    if not currency or not isinstance(currency, str):
        raise ValueError("Currency cannot be empty or null")

    cleaned = currency.strip().upper()

    if not cleaned:
        raise ValueError("Currency cannot be empty or just spaces")

    if not re.match(r"^[A-Z]{3}$", cleaned):
        raise ValueError("Currency must be a valid 3-letter uppercase code (e.g., USD, INR, EUR)")

    return cleaned
