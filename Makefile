install:
	pip install -r requirements.txt

migrate:
	alembic upgrade head

run:
	uvicorn src.main:app --reload

test:
	pytest

docker-build:
	docker build -t tickethub .

docker-run:
	docker compose up --build
