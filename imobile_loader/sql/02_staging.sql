INSERT INTO staging.listings
SELECT DISTINCT ON (source, id, scraped_at)
    source,
    id,
    title,
    description,
    county,
    city,
    address,
    price,
    unit_price,
    surface,
    CAST(date_posted AS DATE) AS date_posted,
    CAST(scraped_at AS DATE) AS scraped_at,
    rooms,
    floor,
    built_year,
    is_furnished,
    near_metro
FROM read_json_auto('{file}') AS raw
WHERE NOT EXISTS (
    SELECT 1 FROM staging.listings AS s
    WHERE s.source = raw.source
      AND s.id = raw.id
      AND s.scraped_at = raw.scraped_at
)
ORDER BY source, id, CAST(scraped_at AS DATE) DESC;