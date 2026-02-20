#!/bin/bash

set -e
set -u

# -----------------------------
# Defaults
# -----------------------------
MODE=""
DATE=""
SPECIFIC_DATE=""
SOURCES=()

PATH_SCRAPER="./imobile_scraper"
PATH_TRANSFORMER="../imobile_transformer"
PATH_LOADER="../imobile_loader"

# -----------------------------
# Arguments parsing
# -----------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      shift
      while [[ $# -gt 0 && "$1" != --* ]]; do
        SOURCES+=("$1")
        shift
      done
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --from-date)
      DATE="$2"
      shift 2
      ;;
    --specific_date)
      SPECIFIC_DATE="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage:"
      echo "  --source all | spider1 spider2"
      echo "  --mode full_load | from --from-date YYYY-MM-DD | date --specific-date YYYY-MM-DD"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# -----------------------------
# Validation
# -----------------------------
if [[ -z "$MODE" || ${#SOURCES[@]} -eq 0 ]]; then
  echo "--source and --mode are required"
  exit 1
fi

if [[ "$MODE" == "from" && -z "$DATE" ]]; then
  echo "--mode from requires --from-date"
  exit 1
fi

if [[ "$MODE" == "date" && -z "$SPECIFIC_DATE" ]]; then
  echo "--mode date requires --specific-date"
  exit 1
fi

# -----------------------------
# Determine spiders
# -----------------------------
cd ${PATH_SCRAPER}

if [[ "${SOURCES[0]}" == "all" ]]; then
  SPIDERS=$(scrapy list)
else
  SPIDERS="${SOURCES[@]}"
fi

# -----------------------------
# Run impobile_scraper
# -----------------------------
# for spider in $SPIDERS; do
#   echo "----- INGESTING SOURCE: $spider -----"
#   scrapy crawl $spider
# done

# -----------------------------
# Run imobile_transformer
# -----------------------------
cd ${PATH_TRANSFORMER}

for spider in $SPIDERS; do
  echo "----- TRANSFORMING SOURCE: $spider, MODE: $MODE -----"

  case "$MODE" in
    full_load)
      python ${spider}_transformer.py --source ${spider} --mode $MODE
      ;;
    from)
      python ${spider}_transformer.py --source ${spider} --mode $MODE --from-date $DATE
      ;;
    date)
      python ${spider}_transformer.py --source ${spider} --mode $MODE --specific-date $SPECIFIC_DATE
      ;;
    *)
      echo "Invalid mode: $MODE"
      exit 1
      ;;
  esac
done

# -----------------------------
# Run imobile_loader
# -----------------------------
cd ${PATH_LOADER}

echo "----- LOADING SOURCES: ${SOURCES[*]}, MODE: $MODE -----"

case "$MODE" in
  full_load)
    python loader.py --source ${SOURCES[*]} --mode $MODE
    ;;
  from)
    python loader.py --source ${SOURCES[*]} --mode $MODE --from-date $DATE
    ;;
  date)
    python loader.py --source ${SOURCES[*]} --mode $MODE --specific-date $SPECIFIC_DATE
    ;;
  *)
    echo "Invalid mode: $MODE"
    exit 1
    ;;
esac

echo "Imobile pipeline finished successfully!"