import os
from functools import cache

_PROMPT_DIR = os.path.dirname(os.path.abspath(__file__))


@cache
def load_prompt(name: str) -> str:
    path = os.path.join(_PROMPT_DIR, f"{name}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with open(path) as f:
        return f.read().strip()
