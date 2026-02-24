import os
from pathlib import Path

os.environ.setdefault('DATABASE_URL', f"sqlite:///{Path('test_api.db').resolve()}")
