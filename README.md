# Kanji Dictionary Editor

A backend API for editing kanji dictionary data for the jouyou kanji project. This project uses FastAPI for the REST API, and stores data in a Mongo database.

## Setup

Install python dependencies:

```bash
pip install -r requirements.txt
```

This API requires a running mongo database to work.

## Running the App

There are some required environment variables that have to be set before starting the backend API:

```bash
PROJECT_NAME=kanji_manager
FIRST_SUPERUSER=a@dmin.nl
FIRST_SUPERUSER_PASSWORD=pw
```

Then the backend can be started using the following command:

```bash
uvicorn app.main:app --reload --log-level 'debug'
```

or just use the `Makefile` and the make command, which sets the variables for local testing purposes:

```bash
make app-start
```
