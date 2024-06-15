"""
Utility functions for varous tasks of infobeamer CMS.
"""

import hashlib
import random
import secrets
import string
import time
import re
import os

def get_time():
    """
    Get the current time in the format HH:MM:SS.

    Returns:
        str: Current time formatted as HH:MM:SS.
    """
    current_time = time.localtime()
    return time.strftime("%H:%M:%S", current_time)

def logging(message:str):
    """
    Log a message with a timestamp.

    Args:
        message (str): The message to log.
    """
    print(f"[{get_time()}]: {message}")

def generate_random_string(length):
    """
    Generate a random string of the specified length containing uppercase and
    lowercase letters as well as digits.

    Args:
        length (int): Length of the random string to generate.

    Returns:
        str: Random string of specified length containing uppercase and
        lowercase letters as well as digits.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_secret_token(length=64):
    """
    Generate a secure random token.

    Args:
        length (int, optional): Length of the token. Defaults to 64.

    Returns:
        str: Secure random token.
    """
    return secrets.token_urlsafe(length)

def hash_sha_512(to_hash:str):
    """
    Hash a string using SHA-512 algorithm.

    Args:
        to_hash (str): The string to hash.

    Returns:
        str: Hashed string in hex.
    """
    return hashlib.sha3_512(to_hash.encode("utf-8")).hexdigest()

def sanitize_string(content:str, extend_allowed_chars=False):
    """
    Remove all characters that are not whitelisted.
    Allow: a-z, A-Z, 0-9, underscore, score, dot
    
    Output for error messages might use the extend_allowed_chars parameter
    in order to allow spaces.

    Args:
        content (str): The string to sanitize.

    Returns:
        str: sanitized string.
    """
    pattern = r'a-zA-Z0-9_\-.' # RE pattern with whitelisted chars
    if extend_allowed_chars: pattern = r"a-zA-Z0-9_\-.\s"
    # Replace chars that aren't whitelisted
    sanitized_content = re.sub(f'[^{pattern}]', "", content)
    return sanitized_content

def get_file_path(base_dir:str, file_name:str):
    """
    Construct a normalized filepath and return it.
    In case of an error or multiple dots in the path, return False

    Args:
        base_dir (str): The path to the file to construct a path for.
        file_name (str): The filename with which the path ends.

    Returns:
        str: normalized path on success
        bool: False on error
    """
    try:
        file_path = os.path.normpath(os.path.join(base_dir, file_name))
    except: return False

    if file_path.count(".") > 1:
        return False

    return file_path
