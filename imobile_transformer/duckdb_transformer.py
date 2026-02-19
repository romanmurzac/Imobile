import re
import duckdb
import argparse
from pathlib import Path
from datetime import datetime, date


DB_PATH = Path(__file__).parent.parent / "data/warehouse/imobile.duckdb"
SQL_DIR = Path(__file__).parent / "sql"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR = Path(__file__).parent.parent / "data/processed"

con = duckdb.connect(DB_PATH)


def run_sql(file: Path):
    print(f"Running {file.name}...")
    try:
        con.execute(file.read_text(encoding="utf-8"))
        print(f"Done {file.name}")
    except Exception as e:
        print(f"Failed {file.name}: {e}")


def extract_date_from_filename(file: Path) -> date:
    match = re.search(r"(\d{4}_\d{2}_\d{2})", file.stem)
    if match:
        return datetime.strptime(match.group(1), "%Y_%m_%d").date()
    return None


def get_files_to_process(mode: str, from_date: str = None, specific_date: str = None) -> list[Path]:
    all_files = sorted(PROCESSED_DIR.glob("*.json"))

    if mode == "fullload":
        return all_files

    elif mode == "from":
        cutoff = datetime.strptime(from_date, "%Y-%m-%d").date()
        return [f for f in all_files if extract_date_from_filename(f) >= cutoff]

    elif mode == "date":
        target = datetime.strptime(specific_date, "%Y-%m-%d").date()
        return [f for f in all_files if extract_date_from_filename(f) == target]

    return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["fullload", "from", "date"], required=True)
    parser.add_argument("--from-date", help="Start date for 'from' mode, format: YYYY-MM-DD")
    parser.add_argument("--specific-date", help="Specific date for 'date' mode, format: YYYY-MM-DD")
    args = parser.parse_args()

    if args.mode == "from" and not args.from_date:
        raise ValueError("--from-date is required for 'from' mode")
    if args.mode == "date" and not args.specific_date:
        raise ValueError("--specific-date is required for 'date' mode")

    files = get_files_to_process(args.mode, args.from_date, args.specific_date)

    if not files:
        print("No files found for the given parameters")
    else:
        run_sql(SQL_DIR / "01_schemas.sql")

        for file in files:
            print(f"Staging {file.name}...")
            try:
                sql = (SQL_DIR / "02_staging.sql").read_text(encoding="utf-8").replace(
                    "{file}", str(file.resolve()).replace("\\", "/")
                )
                con.execute(sql)
                print(f"Done {file.name}")
            except Exception as e:
                print(f"Failed {file.name}: {e}")

        run_sql(SQL_DIR / "03_dim.sql")
        # run_sql(SQL_DIR / "04_mart.sql")

    con.close()