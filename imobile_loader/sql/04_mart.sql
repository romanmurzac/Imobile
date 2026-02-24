-- Listing timeline by source and id
CREATE OR REPLACE VIEW mart.listings_table AS
SELECT
    date_posted,
    valid_from,
    county,
    city,
    address,
    price,
    unit_price,
    surface,
    rooms,
    floor,
    built_year,
    is_furnished,
    near_metro,
    title
FROM
    dim.listings
WHERE
    is_current = True;


-- Save the data on disk
COPY mart.listings_table
TO '../data/mart/listings_table.parquet'
(FORMAT PARQUET);