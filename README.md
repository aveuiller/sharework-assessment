# Sharework Assessment

## What it does

### Backend

The package `sharework.backend`, provides a rest API to list Companies and Matches.
This API can also be used to delete matches.

### Matching

The package `sharework.matching` provides a modular matching engine, based on a set
of criterion to note the similarity between companies of two data-sources.

This matching engine can ingest data from CSV and SQLite backends.
It can also output data to a CSV and SQLite format.

## Structure

The project structure is as follows:

- `data`        Data required for the application to work. This may be replaced by an actual database sometimes.
- `inputs`      The assessment input, that are not used nor modified during the program execution.
- `sharework`   Python package containing the actual code. The code is separated in one package
                per exercise, `backend` and `matching`.
- `tests`       All unit and integration tests for the code.

## How to Use

This project use [poetry](https://python-poetry.org/) as a build manager.
If you are not familiar with it, the following section will give the main intended usage.

### Install

When cloning the project, poetry has already fixed all dependencies versions through
`poetry.lock`, to install the project locally on your virtual environment use:
```bash
$ poetry install
```

### Run tests

Once installed, you can run the project tests with:
```bash
$ poetry run pytest [--cov]
```

### Start the project

#### Matching

To run the matching engine, you can use the following command.
```bash
$ poetry run sharework_matching
```

For the time being, all configuration should be done manually in the 
[main function](sharework/matching/__init__.py).
However, some CLI arguments could be easily added as every configuration is injectable in the services.

As there seems to be duplicates of companies in both datasets, the project is doing a full cartesian product
of datasets.
So for the given dataset of 8723 x 8795 companies, the worker needs between 2 and 3 hours to complete,
depending on your load as well as the amount of worker you dedicate to it. 

Some complete results are available in the data directory,
both for a [strict comparison](data/out.csv.3h_fromcsv_strict) 
and a [non-strict comarison](data/out.csv.2h_fromcsv_notstrict).
To know more about the comparison process, you can read the [CompanyMatcher documentation](sharework/matching/matcher.py).

#### Backend


To start the backend server, you can use the following command.
```bash
$ poetry run sharework_backend
```

Once the server is running, you can query it as follow:
```bash
# List all companies
$ curl "http://127.0.0.1:5000/company?limit=3&page=0" | jq

# Fetch one company by ID
$ curl "http://127.0.0.1:5000/company/42" | jq

# Fetch all matches, with a possible filter by company
$ curl "http://127.0.0.1:5000/match?company=4420&limit=10&page=0" | jq

# Fetch one match specifically
$ curl "http://127.0.0.1:5000/match/10" | jq

# Delete a match
$ curl -X DELETE "http://127.0.0.1:5000/match/10" | jq
```