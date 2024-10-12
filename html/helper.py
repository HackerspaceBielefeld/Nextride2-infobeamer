"""
@file helper.py
@brief Utility functions for various tasks of the infobeamer CMS.

This module provides low-level utility functions for tasks such as time retrieval,
secure token generation, hashing, string sanitization, and 
file path construction. These functions are designed to be robust, reusable, 
and can be integrated into third-party extensions.

@details
- The functions within this module are meant to be used by both internal 
    components and third-party extensions.
- Includes functionalities for generating secure tokens, messages with 
    timestamps, hashing data, sanitizing strings, and validating file paths.

@dependencies
- hashlib: Provides hashing functions such as SHA-512.
- secrets: Provides cryptographically secure random number generation.
- time: Used for time retrieval and formatting.
- re: Regular expressions used for string sanitization.
- os: Provides operating system interfaces, such as file path manipulation.
- typing: For type hinting, used to specify the types returned by certain functions.

@note
- These functions are general-purpose utilities, making them reusable in 
    various contexts, beyond just the infobeamer CMS.

@author Inflac
@date 2024
"""

import hashlib
import secrets
import time
import re
import os

from typing import Union

def get_time(format:str="%H:%M:%S") -> str:
    """
    @brief Get the current time formatted according to the specified format.

    This function returns the current local time as a string, formatted using 
    the provided format. The default format is HH:MM:SS.

    @param format The format string for time formatting, following the rules of 
                    Python's strftime. Defaults to "%H:%M:%S".

    @return str: The current time formatted according to the provided format.
    """

    current_time = time.localtime()
    return time.strftime(format, current_time)

def generate_random(length=64) -> str:
    """
    @brief Generate a secure random token.

    @param length The length of the token. Defaults to 64.

    @return str: Secure random token.
    """

    return secrets.token_urlsafe(length)

def hash_sha_512(to_hash:str) -> str:
    """
    @brief Hash a string using the SHA-512 algorithm.

    @param to_hash The string to hash.

    @return str: Hashed string in hexadecimal format or emptry string
                    in case an error occured while encoding.
    """

    try:
        to_hash = to_hash.encode("utf-8")
    except UnicodeEncodeError as e:
        return ""

    return hashlib.sha3_512(to_hash).hexdigest()

def sanitize_string(content:str, extend_allowed_chars=False) -> str:
    """
    @brief Remove all characters from a string that are not whitelisted.

    Allowed characters: a-z, A-Z, 0-9, underscore, dash, dot.
    Optionally, allow spaces when extend_allowed_chars is True.

    @param content The string to sanitize.
    @param extend_allowed_chars If True, spaces will be allowed in the output.

    @return str: Sanitized string.
    """

    pattern = r'a-zA-Z0-9_\-.'  # RE pattern with whitelisted chars
    if extend_allowed_chars:
        pattern = r"a-zA-Z0-9_\-.\s"

    # Replace chars that aren't whitelisted
    sanitized_content = re.sub(f'[^{pattern}]', "", content)
    return sanitized_content

def get_file_path(base_dir:str, file_name:str) -> Union[str, bool]:
    """
    @brief Construct a normalized file path and return it.

    In case of an error or multiple dots in the path, False is returned.
    This function ensures that file paths are constructed securely and correctly.

    @param base_dir The base directory for the file path.
    @param file_name The filename to append to the base directory.

    @return str: The constructed and normalized file path on success.
    @return bool: False if the file path contains errors or multiple dots.
    """

    try:
        file_path = os.path.normpath(os.path.join(base_dir, file_name))
    except: return False

    if file_path.count(".") > 1:
        return False

    return file_path
