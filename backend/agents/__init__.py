from pathlib import Path

from dotenv import load_dotenv


# Project root:
# AI-Product-Architect/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load environment variables from the project's .env file.
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)