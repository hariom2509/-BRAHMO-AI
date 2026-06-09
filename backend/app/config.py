import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Check if Supabase config is provided and non-empty
IS_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "your_url" and SUPABASE_KEY != "your_key")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# Database path for SQLite fallback
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db.sqlite3")
