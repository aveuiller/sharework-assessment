# Sharework Assessment

## What it does

## Structure

The project is structured as follows:

- `data`        Data required for the application to work. This may be replaced by an actual database sometimes.
- `inputs`      The assessment input, that are not used nor modified during the program execution.
- `sharework`   Python package containing the actual code.
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

Finally, the following command runs the project:
```bash
$ poetry run sharework_backend
$ poetry run sharework_matching
```
