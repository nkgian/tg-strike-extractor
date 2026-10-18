import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _load_env():
    """
    Loads environment variables from a .env file stored inside the active
    virtual environment so that API keys never end up in the repository.
    Falls back to a .env file in the project root if no venv is detected.
    """
    venv_dir = os.getenv("VIRTUAL_ENV")
    if not venv_dir and sys.prefix != sys.base_prefix:
        venv_dir = sys.prefix

    if venv_dir:
        venv_env = Path(venv_dir) / ".env"
        if venv_env.is_file():
            load_dotenv(venv_env)
            return

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")


_load_env()

FIRMS_API_KEY = os.getenv("FIRMS_API_KEY")

LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "openai/gpt-oss-20b")
LOCAL_LLM_API_KEY = os.getenv("LOCAL_LLM_API_KEY", "not-needed")
