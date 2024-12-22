import os

CONFIG_FILE_PATH = "config.txt"

def load_api_key():
    """Loads the OpenAI API key from the config file."""
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as file:
            return file.read().strip()
    return ""

def save_api_key(api_key):
    """Saves the OpenAI API key to the config file."""
    with open(CONFIG_FILE_PATH, "w") as file:
        file.write(api_key)