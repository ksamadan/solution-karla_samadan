install:
	pip install -r requirements.txt

migrate:
	alembic upgrade head

run:
	uvicorn src.main:app --reload

test:
	PYTHONPATH=. pytest

lint:
	ruff check src tests

format:
	ruff format src tests

docker-build:
	docker build -t tickethub .

docker-run:
	docker compose up --build
