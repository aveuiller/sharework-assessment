CREATE TABLE IF NOT EXISTS matches (
    id                 INTEGER PRIMARY KEY,
    company_a_source   VARCHAR (64),
    company_a_id       INTEGER,
    company_b_source   VARCHAR (64),
    company_b_id       INTEGER,
    score              FLOAT,
    success_criteria   VARCHAR (512)
);