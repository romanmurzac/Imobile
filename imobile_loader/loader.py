import sys
import duckdb

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.args_processor import get_files_to_process
from utils.args_parser import parse_args

DB_PATH = Path(__file__).parent.parent / "data/warehouse/imobile.duckdb"
SQL_DIR = Path(__file__).parent / "sql"
PROCESSED_DIR = Path(__file__).parent.parent / "data/processed"
MART_PATH = Path(__file__).parent.parent / "data/mart"
DIM_PATH = Path(__file__).parent.parent / "data/dim"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
MART_PATH.parent.mkdir(parents=True, exist_ok=True)
DIM_PATH.parent.mkdir(parents=True, exist_ok=True)


class DuckDBRunner:
    def __init__(self, db_path: Path) -> None:
        self.con = duckdb.connect(db_path)

    def run_sql(self, path: Path, reference: bool = False, file: str = None) -> None:
        if file:
            print(f"Running {path.name} query for file {file.name} ...")
        else:
            print(f"Running {path.name} query ...")
        try:
            if reference:
                sql = path.read_text(encoding="utf-8").replace(
                    "{file}", str(file.resolve()).replace("\\", "/")
                )
                self.con.execute(sql)
            else:
                self.con.execute(path.read_text(encoding="utf-8"))
            print(f"Successfully executed {path.name} query.\n")
        except Exception as e:
            print(f"Failed to execute {path.name} query: {e}\n")

    def close_con(self) -> None:
        self.con.close()


if __name__ == "__main__":
    args = parse_args()
    
    files = get_files_to_process(
        PROCESSED_DIR, args.source, args.mode, args.from_date, args.specific_date
    )

    if not files:
        print("No files found for the given parameters. Exiting...")
    else:
        conn = DuckDBRunner(DB_PATH)
        conn.run_sql(SQL_DIR / "01_schemas.sql")

        for file in files:
            conn.run_sql(SQL_DIR / "02_staging.sql", True, file)

        conn.run_sql(SQL_DIR / "03_dim.sql")
        conn.run_sql(SQL_DIR / "04_mart.sql")

        conn.close_con()
