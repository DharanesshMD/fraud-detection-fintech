Minimal additions for Phase A: FastAPI prediction endpoint, dummy model, Dockerfile, and tests.

Run tests locally with:

    pip install -r requirements.txt
    pytest -q

Run the API locally with:

    uvicorn src.api.predict:app --reload

Or use docker-compose:

    docker compose up --build
