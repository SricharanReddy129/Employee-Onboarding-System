from datetime import datetime
import random
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

    # Month letters → February
    month_letters = list(now.strftime("%B"))  # ['F','e','b','r','u','a','r','y']

    # Datetime digits → 20250213223323
    datetime_digits = list(now.strftime("%Y%m%d%H%M%S"))

    # Interleave month letters and datetime digits
    mixed = list(itertools.zip_longest(month_letters, datetime_digits, fillvalue=""))
    token_core = "".join(a + b for a, b in mixed)

    # Shuffle characters (excluding final random letter)
    token_chars = list(token_core)
    random.shuffle(token_chars)

    # Random alphabet suffix
    random_letter = secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    return "".join(token_chars) + random_letter