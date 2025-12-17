from datetime import datetime
import secrets
import itertools
import hashlib

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def generate_mixed_month_time_token() -> str:
    """
    Example output:
    S0e9P3t1e4m2b5e7rA9

    - Letters come from the current month name
    - Digits come from HHMMSS
    - Mixed together
    - Random letter added to avoid collisions
    """
    now = datetime.utcnow()

    month_letters = list(now.strftime("%B"))      # e.g. ['S','e','p','t','e','m','b','e','r']
    time_digits = list(now.strftime("%H%M%S"))    # e.g. ['1','4','3','2','4','5']

    mixed = list(itertools.zip_longest(month_letters, time_digits, fillvalue=""))
    token_core = "".join(a + b for a, b in mixed)

    random_letter = secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    return f"{token_core}{random_letter}"
