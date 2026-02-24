-- Close records where attributes have changed
UPDATE dim.listings
SET
    valid_to = (
        SELECT s.scraped_at
        FROM staging.listings AS s
        WHERE s.source = dim.listings.source
          AND s.id = dim.listings.id
          AND (
            dim.listings.title IS DISTINCT FROM s.title OR
            dim.listings.description IS DISTINCT FROM s.description OR
            dim.listings.county IS DISTINCT FROM s.county OR
            dim.listings.city IS DISTINCT FROM s.city OR
            dim.listings.address IS DISTINCT FROM s.address OR
            dim.listings.price IS DISTINCT FROM s.price OR
            dim.listings.unit_price IS DISTINCT FROM s.unit_price OR
            dim.listings.surface IS DISTINCT FROM s.surface OR
            dim.listings.date_posted IS DISTINCT FROM s.date_posted OR
            dim.listings.rooms IS DISTINCT FROM s.rooms OR
            dim.listings.floor IS DISTINCT FROM s.floor OR
            dim.listings.built_year IS DISTINCT FROM s.built_year OR
            dim.listings.is_furnished IS DISTINCT FROM s.is_furnished OR
            dim.listings.near_metro IS DISTINCT FROM s.near_metro
          )
        ORDER BY s.scraped_at ASC
        LIMIT 1
    ),
    is_current = FALSE
WHERE dim.listings.is_current = TRUE
  AND EXISTS (
    SELECT 1 FROM staging.listings AS s
    WHERE s.source = dim.listings.source
      AND s.id = dim.listings.id
      AND (
        dim.listings.title IS DISTINCT FROM s.title OR
        dim.listings.description IS DISTINCT FROM s.description OR
        dim.listings.county IS DISTINCT FROM s.county OR
        dim.listings.city IS DISTINCT FROM s.city OR
        dim.listings.address IS DISTINCT FROM s.address OR
        dim.listings.price IS DISTINCT FROM s.price OR
        dim.listings.unit_price IS DISTINCT FROM s.unit_price OR
        dim.listings.surface IS DISTINCT FROM s.surface OR
        dim.listings.date_posted IS DISTINCT FROM s.date_posted OR
        dim.listings.rooms IS DISTINCT FROM s.rooms OR
        dim.listings.floor IS DISTINCT FROM s.floor OR
        dim.listings.built_year IS DISTINCT FROM s.built_year OR
        dim.listings.is_furnished IS DISTINCT FROM s.is_furnished OR
        dim.listings.near_metro IS DISTINCT FROM s.near_metro
      )
);

-- Insert new or changed records
INSERT INTO dim.listings
SELECT
    s.source, s.id, s.title, s.description, s.county, s.city, s.address,
    s.price, s.unit_price, s.surface, s.date_posted, s.scraped_at,
    s.rooms, s.floor, s.built_year, s.is_furnished, s.near_metro,
    s.scraped_at AS valid_from,
    NULL AS valid_to,
    TRUE AS is_current
FROM staging.listings AS s
WHERE NOT EXISTS (
    SELECT 1 FROM dim.listings AS d
    WHERE d.source = s.source
      AND d.id = s.id
      AND d.is_current = TRUE
);

-- Save the data on disk
COPY dim.listings
TO '../data/dim/listings.parquet'
(FORMAT PARQUET);