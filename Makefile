.PHONY: install backend frontend dev

install:
	uv sync --directory backend
	uv sync --directory frontend

backend:
	uv run --directory backend python init_db.py
	uv run --directory backend uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend:
	uv run --project frontend streamlit run frontend/app.py --server.port 8501

dev:
	@echo "Initializing database..."
	@uv run --directory backend python init_db.py
	@echo "Starting backend :8000 and frontend :8501 ..."
	@trap 'kill 0' SIGINT; \
	uv run --directory backend uvicorn main:app --reload --host 0.0.0.0 --port 8000 & \
	uv run --project frontend streamlit run frontend/app.py --server.port 8501; \
	wait
