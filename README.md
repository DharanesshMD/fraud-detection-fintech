# fraud-detection-fintech

Minimal prototype for Phase A: a FastAPI prediction endpoint, a dummy model, a Dockerfile, and tests.

## Features

- FastAPI prediction endpoint
- Example dummy model and inference code
- Dockerfile and docker-compose for local deployment
- Tests with pytest

## Quickstart

1. Install dependencies:

    pip install -r requirements.txt

2. Run tests:

    pytest -q

3. Run the API locally:

    uvicorn src.api.predict:app --reload

4. Run with Docker:

    docker compose up --build

## Repository

- Author: Dharanessh M D (https://github.com/DharanesshMD)

## License

MIT
