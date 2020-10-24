CREATE TABLE IF NOT EXISTS "companies"
(
    "id"          integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "source_id"   integer      NOT NULL,
    "source_name" varchar(64)  NOT NULL,
    "name"        varchar(512) NOT NULL,
    "website"     varchar(512) NULL,
    "email"       varchar(512) NULL,
    "phone"       varchar(512) NULL,
    "address"     varchar(512) NULL,
    "postal_code" varchar(512) NULL,
    "city"        varchar(512) NULL,
    "country"     varchar(512) NULL
);
CREATE TABLE IF NOT EXISTS "matches"
(
    "id"               integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "left_company_id"  integer NOT NULL REFERENCES "companies" ("id") DEFERRABLE INITIALLY DEFERRED,
    "right_company_id" integer NOT NULL REFERENCES "companies" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "matches_left_company_id_ae152d81" ON "matches" ("left_company_id");
CREATE INDEX "matches_right_company_id_17e298fb" ON "matches" ("right_company_id");
