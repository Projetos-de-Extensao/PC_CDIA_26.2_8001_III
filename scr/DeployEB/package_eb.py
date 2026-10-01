from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

APP_DIR = Path(__file__).resolve().parent
ARCHIVE_PATH = APP_DIR / "app.zip"
EXCLUDED_DIRS = {
    ".elasticbeanstalk",
    ".git",
    ".venv",
    "__pycache__",
    "media",
    "staticfiles",
    "venv",
}
EXCLUDED_FILES = {"app.zip", "db.sqlite3"}

with ZipFile(ARCHIVE_PATH, "w", compression=ZIP_DEFLATED) as archive:
    for path in APP_DIR.rglob("*"):
        relative_path = path.relative_to(APP_DIR)
        if any(part in EXCLUDED_DIRS for part in relative_path.parts):
            continue
        if path.is_file() and path.name not in EXCLUDED_FILES:
            archive.write(path, relative_path.as_posix())

print(f"Pacote criado: {ARCHIVE_PATH}")
