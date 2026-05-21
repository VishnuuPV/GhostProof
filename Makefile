.PHONY: test lint api ai dashboard extension docker

test:
	cd backend && pytest
	cd ai-services && pytest

lint:
	cd backend && ruff check app tests
	cd ai-services && ruff check ghostproof_ai service tests

api:
	cd backend && uvicorn app.main:app --reload --port 8000

ai:
	cd ai-services && uvicorn service.main:app --reload --port 8100

dashboard:
	cd frontend && npm run dev

extension:
	cd extension && npm run build

docker:
	docker compose up --build
