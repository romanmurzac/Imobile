import re

from pathlib import Path
from datetime import datetime, date


def _extract_date_from_filename(file: Path) -> date:
    match = re.search(r"(\d{4}_\d{2}_\d{2})", file.stem)
    if match:
        return datetime.strptime(match.group(1), "%Y_%m_%d").date()
    return None


def _filter_by_sources(files: list[Path], sources: list[str] | None) -> list[Path]:
    if sources == ["all"]:
        return files
    return [f for f in files if any(f.name.startswith(src) for src in sources)]


def get_files_to_process(
    path: Path,
    sources: list[str],
    mode: str,
    from_date: str = None,
    specific_date: str = None,
) -> list[Path]:
    all_files = sorted(path.glob("*.json"))

    if mode == "full_load":
        files = all_files

    elif mode == "from":
        cutoff = datetime.strptime(from_date, "%Y-%m-%d").date()
        files = [f for f in all_files if _extract_date_from_filename(f) >= cutoff]

    elif mode == "date":
        target = datetime.strptime(specific_date, "%Y-%m-%d").date()
        files = [f for f in all_files if _extract_date_from_filename(f) == target]

    else:
        files = []

    return _filter_by_sources(files, sources)
