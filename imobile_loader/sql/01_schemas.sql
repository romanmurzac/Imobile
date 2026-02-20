CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dim;
CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE IF NOT EXISTS staging.listings (
    source VARCHAR,
    id VARCHAR,
    title VARCHAR,
    description VARCHAR,
    county VARCHAR,
    city VARCHAR,
    address VARCHAR,
    price INTEGER,
    unit_price INTEGER,
    surface INTEGER,
    date_posted DATE,
    scraped_at DATE,
    rooms INTEGER,
    floor INTEGER,
    built_year INTEGER,
    is_furnished BOOLEAN,
    near_metro BOOLEAN
);

CREATE TABLE IF NOT EXISTS dim.listings (
    source VARCHAR,
    id VARCHAR,
    title VARCHAR,
    description VARCHAR,
    county VARCHAR,
    city VARCHAR,
    address VARCHAR,
    price INTEGER,
    unit_price INTEGER,
    surface INTEGER,
    date_posted DATE,
    scraped_at DATE,
    rooms INTEGER,
    floor INTEGER,
    built_year INTEGER,
    is_furnished BOOLEAN,
    near_metro BOOLEAN,
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN,
    PRIMARY KEY (source, id, valid_from)
);