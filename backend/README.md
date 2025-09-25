# Course Validator Backend

FastAPI backend for the Course Validator application that analyzes and validates course ideas.

## Setup

1. Create and activate virtual environment:
```bash
uv venv
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
uv sync
```

3. Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

4. Start MongoDB (make sure MongoDB is installed and running)

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic
│   ├── models/        # Pydantic models
│   ├── db/           # Database connection and queries
│   └── main.py       # FastAPI application
├── tests/            # Test files
├── .env.example      # Example environment variables
└── README.md         # This file
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

- Use `uvicorn app.main:app --reload` for development
- Run tests with `pytest`
- Format code with `black`
- Check types with `mypy` 