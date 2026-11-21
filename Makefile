.PHONY: install dev-frontend dev-backend test test-ml train-ml seed-data build-frontend docker-dev

install:
	cd frontend && npm install

dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && PYTHONPATH=..:. ../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

test:
	PYTHONPATH=backend:. .venv/bin/pytest backend/tests

test-ml:
	.venv/bin/python3 ml/src/evaluate.py

train-ml:
	PYTHONPATH=. .venv/bin/python3 -c "from ml.src.train import train_model; train_model(epochs=3, batch_size=2, hidden_channels=64)"

seed-data:
	.venv/bin/python3 scripts/download_sample_data.py

build-frontend:
	cd frontend && npm run build

docker-dev:
	cd backend && docker compose up -d
