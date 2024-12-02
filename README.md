# Natural Python

A natural language interface for Python programming that allows you to write Python code using English-like commands.

## Features

- Natural language Python code interpretation
- Support for basic Python operations (variables, math, strings, lists)
- Advanced operations (file handling, JSON, regex, datetime)
- Web-based IDE with syntax highlighting
- Real-time code execution
- Error handling and debugging
- Support for input/output operations

## Examples

```python
# Basic Operations
Make a number called score equal to 10
Add 5 to score
Print score  # Output: 15

# String Operations
Create a string called greeting with "Hello World"
Convert greeting to uppercase
Print greeting  # Output: HELLO WORLD

# List Operations
Make a list numbers equal to [1, 2, 3, 4, 5]
Add 6 to numbers
Sort numbers
Print numbers  # Output: [1, 2, 3, 4, 5, 6]

# Advanced Operations
Calculate square root of 16
Generate random number between 1 and 10
Format string "Hello {}" with "Alice"
```

## Project Structure

```
natural-python/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── interpreter/
│   │       ├── __init__.py
│   │       └── interpreter.py
│   ├── requirements.txt
│   ├── setup.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   └── pages/
│   │       ├── index.tsx
│   │       └── api/
│   │           └── run_code.ts
│   ├── package.json
│   └── tsconfig.json
└── docker-compose.yml
```

## Setup

### Backend

```bash
# Create and activate virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m app.main
```

### Frontend

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev
```

### Docker

Run the entire stack using Docker Compose:

```bash
docker-compose up
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Environment Variables

Create a `.env.local` file in the frontend directory:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## API Endpoints

### POST /api/run_code
Execute Python code written in natural language.

Request:
```json
{
  "code": "Make a number called x equal to 10\nAdd 5 to x\nPrint x"
}
```

Response:
```json
{
  "output": "Created x = 10\nUpdated x to 15\n15"
}
```

### POST /api/input
Handle user input during code execution.

Request:
```json
{
  "input": "Hello World"
}
```

Response:
```json
{
  "output": ["Input received"],
  "result": "Hello World"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 