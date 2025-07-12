# ----------- Variables -----------
APP_NAME=real_estate_rag
APP_MODULE=app.main:app
HOST=0.0.0.0
PORT=8000
VENV=.venv

# ----------- Commands ------------

.PHONY: help run dev install clean lint format test migrate ingest

help:
	@echo "Usage:"
	@echo "  make install       Install dependencies"
	@echo "  make run           Run the FastAPI app"
	@echo "  make dev           Run app with auto-reload (development)"
	@echo "  make format        Format code with black"
	@echo "  make lint          Lint code with flake8"
	@echo "  make ingest        Trigger ingestion script"
	@echo "  make migrate       Create database schema"
	@echo "  make clean         Remove __pycache__ and .pyc files"

install:
	python -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

run:
	$(VENV)/bin/uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT)

dev:
	$(VENV)/bin/uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

format:
	black $(APP_NAME)

lint:
	flake8 $(APP_NAME)

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

migrate:
	python -c "from app.db.session import Base, engine; Base.metadata.create_all(bind=engine)"

ingest:
	curl -X POST http://$(HOST):$(PORT)/ingest/listings
