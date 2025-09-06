## Project Overview

This repository contains the Week 1 solution for the AI Engineering Lab. It includes:
- Python backend (Flask + Flask-RESTX)
- React frontend (Create React App)
- Unit tests and CI coverage reporting

---

## Backend Setup

### Requirements
- macOS (tested) or Linux
- Python 3.10+ recommended
- Git
- Optional: Docker (for containerized runs)

### Quick Start
```bash
git clone <your-repo-url>.git
cd group-2
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Run the Application
```bash
export FLASK_APP=backend.app:app
flask run --port 8000
```
Open API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Running Tests and Coverage
```bash
python -m unittest discover backend/tests -v
pip install coverage
coverage run -m unittest discover backend/tests
coverage report -m
coverage xml
```

---

## Frontend Setup

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

### Available Scripts
```bash
npm start      # Runs the app in development mode
npm test       # Launches the test runner
npm run build  # Builds the app for production
npm run eject  # Ejects configuration (irreversible)
```
Open [http://localhost:3000](http://localhost:3000) to view in your browser.

---

## API Documentation

The backend exposes REST endpoints via Flask-RESTX. Swagger UI is available at `/docs`.

### Namespaces
- Counting (`/Counting`)
- Correction (`/Correction`)
- Auth (`/Auth`)

### Counting
- **POST** `/Counting/count`
	- Upload one or more images and get object count, labels, and segments.
	- Content-Type: `multipart/form-data`
	- Form fields:
		- `item_type` (string, required): Type of item to count.
		- `image` (file, required): Image file (.png, .jpg, .jpeg, .bmp, .gif).
	- Optional headers:
		- `X-User-Id`: Associate the saved result with a user.
	- Success 200 response:
		- `{ "result_id": "<id>", "count": <int>, "labels": [..], "segments": <int> }`
	- Error responses:
		- 400 for missing/invalid inputs, 500 for save/model errors.

### Correction
- **POST** `/Correction/correct`
	- Submit corrected count for a previous result.
	- Content-Type: `application/json`
	- Body: `{ "result_id": "<id>", "correct_count": <int> }`
	- Responses:
		- 200 `{ "message": "Correction saved" }`
		- 400 `{ "error": "Missing result_id or correct_count" }`
		- 500 `{ "error": "Database error: ..." }`

### Auth
- **POST** `/Auth/register`
	- Body: `{ "email": "user@example.com", "password": "pass123" }`
	- 201 Created on success; 200 with message if already exists.
- **POST** `/Auth/login`
	- Body: `{ "email": "user@example.com", "password": "pass123" }`
	- 200 on success with `{ user_id, email }`, 401 if invalid.
- **POST** `/Auth/forgot-password`
	- Body: `{ "email": "user@example.com" }`
	- 200 returns plaintext password if user exists; 404 otherwise.
- **GET** `/Auth/previous-results?user_id=<id>`
	- Or pass header `X-User-Id: <id>`
	- 200 returns list of prior results for that user.

---

## Project Structure

- backend/
	- app/ (Flask app)
	- models/ (ML and DB code)
	- tests/ (unit tests)
- front-end/
	- react-app/ (React frontend)
- .gitlab-ci.yml (CI pipeline)
- README.md (this file)

---

## CI/CD

The GitLab pipeline:
- Uses pytorch/pytorch:latest image
- Caches pip and venv to speed up builds
- Installs requirements, torch (CPU), and runs unittest with coverage
- Publishes coverage.xml artifact for 1 week

---

## Troubleshooting

- Port already in use: change the port (e.g., --port 8080).
- Missing libs (Linux): install libgl1 and libglib2.0-0 (already handled in CI).
- PyTorch install is slow on GPU wheels: use CPU index URL shown above.
