import re
import json
import argparse

from pathlib import Path
from datetime import datetime, timedelta, date


class PubliCleaner:

    PATTERN_PRICE = r"[^\d]"
    PATTERN_UNIT_PRICE = r"(\d{3,5})\s*eur\s*/\s*m2"
    PATTERN_SURFACE = r"(\d{2,4})\s*m2"
    PATTERN_POSTED_DATE = r"(\d{1,2})\s+([a-zăîșț]+)"

    def read_json(self, path: str):
        with open(path, "r", encoding="utf8") as file:
            return json.load(file)

    def write_json(self, path: str, data):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def extract_str_single(self, raw: dict, key: str) -> str:
        data = raw.get(key, "")
        if isinstance(data, list):
            return data[0].strip() if data and data[0] else None
        return data

    def extract_str_multiple(self, raw: dict, key: str) -> list:
        result_1 = None
        result_2 = None
        result_3 = ""
        parts = [p.strip() for p in raw.get(key, "")[0].split(",") if p.strip()]
        if len(parts) == 1:
            result_1 = parts[0].capitalize()
        elif len(parts) == 2:
            result_1 = parts[-1].capitalize()
            result_2 = parts[0].capitalize()
        elif len(parts) >= 3:
            result_1 = parts[-1].capitalize()
            result_2 = parts[-2].capitalize()
            result_3 = ", ".join(parts[:-2]).capitalize()
        return [result_1, result_2, result_3]

    def extract_int_from_single(self, raw: str, pattern: str) -> int:
        if not raw:
            return None
        digits = re.sub(pattern, "", raw.lower())
        return int(digits) if digits else None

    def extract_int_from_multiple(self, raw: str, pattern: str) -> int:
        if not raw:
            return None
        match = re.search(pattern, raw.lower())
        return int(match.group(1)) if match else None

    def parse_date(
        self,
        raw: dict,
        process_str: str,
        reference_str: str = None,
        pattern: str = None,
    ) -> str:

        if not raw:
            return None

        process_date = (
            self.extract_str_single(raw, process_str)
            if isinstance(raw.get(process_str, ""), list)
            else raw.get(process_str, "")
        )
        reference_date = (
            self.extract_str_single(raw, reference_str)
            if isinstance(raw.get(reference_str, ""), list)
            else raw.get(reference_str, "")
        )

        if not reference_date:
            return datetime.fromisoformat(process_date.replace("Z", "+00:00")).strftime(
                "%Y-%m-%d"
            )

        ref_dt = datetime.fromisoformat(reference_date.replace("Z", "+00:00"))

        months = {
            "ianuarie": 1,
            "februarie": 2,
            "martie": 3,
            "aprilie": 4,
            "mai": 5,
            "iunie": 6,
            "iulie": 7,
            "august": 8,
            "septembrie": 9,
            "octombrie": 10,
            "noiembrie": 11,
            "decembrie": 12,
        }

        if "azi" in process_date:
            return ref_dt.strftime("%Y-%m-%d")
        if "ieri" in process_date:
            return (ref_dt - timedelta(days=1)).strftime("%Y-%m-%d")

        match = re.search(pattern, process_date)
        if not match:
            return None
        day = int(match.group(1))
        month = months.get(match.group(2))
        if not month:
            return None
        year = ref_dt.year if month <= ref_dt.month else ref_dt.year - 1
        return datetime(year, month, day).strftime("%Y-%m-%d")

    def extract_rooms(self, raw):
        text = f"{raw.get('title','')} {raw.get('description','')}".lower()
        if "garsonier" in text:
            return 1
        match = re.search(r"(\d+)\s*(camere|camera|cam)", text)
        return int(match.group(1)) if match else None

    def extract_floor(self, raw):
        text = f"{raw.get('title','')} {raw.get('description','')}".lower()
        if "demisol" in text:
            return -1
        elif "parter" in text:
            return 0
        elif "mansard" in text:
            return 99
        match = re.search(r"(etajul|etaj|et)\s*(\d+)", text)
        return int(match.group(2)) if match else None

    def extract_built_year(self, raw):
        text = f"{raw.get('title', '')} {raw.get('description', '')}".lower()
        match = re.search(
            r"\b(bloc|construit|edificat|an(?:ul)?|din|în)\s*(19\d{2}|20\d{2})", text
        )
        return int(match.group(2)) if match else None

    def extract_furnished(self, raw):
        text = f"{raw.get('description','')}".lower()

        if re.search(r"\bnemobilat[ăa]?\b", text):
            return False
        if re.search(r"\bmobilat[ăa]?\b", text):
            return True
        return None

    def extract_metro(self, raw):
        text = f"{raw.get('description','')}".lower()
        return True if re.search(r"\bmetrou(l)?\b", text) else None


def extract_date_from_filename(file: Path) -> date:
    match = re.search(r"(\d{4}_\d{2}_\d{2})", file.stem)
    if match:
        return datetime.strptime(match.group(1), "%Y_%m_%d").date()
    return None


def get_files_to_process(mode: str, from_date: str = None, specific_date: str = None) -> list[Path]:
    raw_dir = Path(__file__).parent.parent / "data/raw"
    all_files = sorted(raw_dir.glob("*.json"))

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
        cleaner = PubliCleaner()
        for raw_file in files:
            print(f"Processing {raw_file.name}...")
            data = cleaner.read_json(raw_file)
            processed = []
            for item in data:
                county, city, address = cleaner.extract_str_multiple(item, "location")
                unit_price_surface = cleaner.extract_str_single(item, "unit_price_surface")
                processed.append(
                    {
                        "source": cleaner.extract_str_single(item, "source"),
                        "id": cleaner.extract_str_single(item, "id"),
                        "title": cleaner.extract_str_single(item, "title"),
                        "description": cleaner.extract_str_single(item, "description"),
                        "county": county,
                        "city": city,
                        "address": address if address else None,
                        "price": cleaner.extract_int_from_single(
                            cleaner.extract_str_single(item, "price"), cleaner.PATTERN_PRICE
                        ),
                        "unit_price": cleaner.extract_int_from_multiple(
                            unit_price_surface, cleaner.PATTERN_UNIT_PRICE
                        ),
                        "surface": cleaner.extract_int_from_multiple(
                            unit_price_surface, cleaner.PATTERN_SURFACE
                        ),
                        "date_posted": cleaner.parse_date(
                            item, "date_posted", "scraped_at", cleaner.PATTERN_POSTED_DATE
                        ),
                        "scraped_at": cleaner.parse_date(item, "scraped_at"),
                        "rooms": cleaner.extract_rooms(item),
                        "floor": cleaner.extract_floor(item),
                        "built_year": cleaner.extract_built_year(item),
                        "is_furnished": cleaner.extract_furnished(item),
                        "near_metro": cleaner.extract_metro(item),
                    }
                )
            output_path = Path(__file__).parent.parent / f"data/processed/{raw_file.stem}_processed.json"
            cleaner.write_json(output_path, processed)
            print(f"Done {raw_file.name} → {output_path.name}")