import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        nargs="+",
        help="Sources to process: 'all' or one/more source prefixes e.g. --source source_1 source_2",
        required=True,
    )
    parser.add_argument("--mode", choices=["full_load", "from", "date"], required=True)
    parser.add_argument(
        "--from-date", help="Start date for 'from' mode, format: YYYY-MM-DD"
    )
    parser.add_argument(
        "--specific-date", help="Specific date for 'date' mode, format: YYYY-MM-DD"
    )
    args = parser.parse_args()

    if args.mode == "from" and not args.from_date:
        raise ValueError("--from-date is required for 'from' mode")
    if args.mode == "date" and not args.specific_date:
        raise ValueError("--specific-date is required for 'date' mode")

    return args
