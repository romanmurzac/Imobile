import duckdb
import json
import numpy as np
import pandas as pd

from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data/warehouse/imobile.duckdb"
SQL_DIR = Path(__file__).parent / "sql/tests"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def run_sql(file):
    con = duckdb.connect(DB_PATH)
    result = con.execute(file.read_text()).df()
    print(result)
    con.close()
    return result


def check_tables():
    con = duckdb.connect(DB_PATH)

    print("\n--- TABLES ---")
    print(con.execute("SHOW ALL TABLES").df())
    
    print("\n--- STAGING COUNT ---")
    print(con.execute("SELECT COUNT(*) FROM staging.listings").fetchone()[0])
    
    print("\n--- DIM COUNT ---")
    print(con.execute("SELECT COUNT(*) FROM dim.listings").fetchone()[0])
    
    print("\n--- STAGING SAMPLE ---")
    print(con.execute("SELECT * FROM staging.listings LIMIT 5").df())
    
    print("\n--- DIM SAMPLE ---")
    print(con.execute("SELECT * FROM dim.listings LIMIT 5").df())

    con.close()


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


if __name__ == "__main__":
    # check_tables()
    
    result = run_sql(SQL_DIR / "test.sql")
    path = Path("data/output/test.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf8") as file:
        json.dump(result.to_dict(orient="records"), file, ensure_ascii=False, indent=2, cls=DateEncoder)
    