import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DEFAULT_DB_URI = os.getenv("DEFAULT_DB_URI")
DEFAULT_DATA_FOLDER = Path(os.getenv("DEFAULT_DATA_FOLDER"))
STUDY_AREA = os.getenv("STUDY_AREA")
