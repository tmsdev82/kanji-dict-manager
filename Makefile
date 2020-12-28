.EXPORT_ALL_VARIABLES:
PROJECT_NAME=kanji_manager
FIRST_SUPERUSER=a@dmin.nl
FIRST_SUPERUSER_PASSWORD=pw

app-start:
	uvicorn app.main:app --reload --log-level 'debug'