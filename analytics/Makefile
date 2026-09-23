.PHONY: all ingest clean-data build export quality test lint app refresh

all: ingest clean-data quality build export test

ingest:
	python -m src.ingest_matches
	python -m src.ingest_fpl

clean-data:
	python -m src.clean_matches
	python -m src.clean_players

build:
	python -m src.load
	dbt build                   # models + tests, in dependency order

export:
	python -m src.bi_export

quality:
	python -m src.quality

test:
	pytest -v

app:
	streamlit run app/dashboard.py

refresh:
	python -m src.ingest_matches --current-only
	python -m src.ingest_fpl --refresh
	python -m src.clean_matches
	python -m src.clean_players
	python -m src.quality
	python -m src.load
	dbt build                   # is the model correct?
	python -m src.bi_export