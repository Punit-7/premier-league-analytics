.PHONY: all ingest clean-data build export quality test lint app refresh

all: ingest build export quality test

ingest:
	python -m src.ingest_matches
	python -m src.ingest_fpl

clean-data:
	python -m src.clean

build: clean-data
	python -m src.load

export:
	python -m src.export_bi

quality:
	python -m src.quality

test:
	pytest -v

app:
	streamlit run app/dashboard.py

refresh:
	python -m src.ingest_matches --current-only
	python -m src.ingest_fpl --refresh
	python -m src.clean
	python -m src.quality
	python -m src.load
	python -m src.export_bi