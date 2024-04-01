import random
import secrets
import string
import time

from PIL import Image

def get_time():
    current_time = time.localtime()
    return time.strftime("%H:%M:%S", current_time)

def logging(message:str):
    print(f"[{get_time()}]: {message}")

def generate_random_string(length):
    # Define the characters allowed for the random string
    characters = string.ascii_letters + string.digits    
    # Generate the random string
    return ''.join(random.choice(characters) for _ in range(length))

def generate_secret_token(length=32):
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)