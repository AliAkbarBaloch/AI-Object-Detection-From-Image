> Complete this template and keep it at the top of your README. Delete this instruction.

# Group <NUMBER>

| Name | Email | FIM ID |
| ---- | ----- | ------ |
|Ali Akbar | akbar01@ads.uni-passau.de      |@akbar        |
|Saeid Khalilian      |khalil10@ads.uni-passau.de       |@khalilian        |
|Yunus Emre Balkis      |balkis01@ads.uni-passau.de       |@balkis        |


## AI Engineering Lab – Group 2 (Week 1)


## API Overview

The backend exposes REST endpoints via Flask-RESTX. Swagger UI is available from the app root (depending on how the app mounts the docs).

Namespaces:
- Counting (`/Counting`)
- Correction (`/Correction`)
- Auth (`/Auth`)

### Counting

- POST `/Counting/count`
	- Description: Upload an image and get object count, labels, and segments.
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

- POST `/Correction/correct`
	- Description: Submit corrected count for a previous result.
	- Content-Type: `application/json`
	- Body:
		- `{ "result_id": "<id>", "correct_count": <int> }`
	- Responses:
		- 200 `{ "message": "Correction saved" }`
		- 400 `{ "error": "Missing result_id or correct_count" }`
		- 500 `{ "error": "Database error: ..." }`

### Auth

- POST `/Auth/register`
	- Body: `{ "email": "user@example.com", "password": "pass123" }`
	- 201 Created on success; 200 with message if already exists.

- POST `/Auth/login`
	- Body: `{ "email": "user@example.com", "password": "pass123" }`
	- 200 on success with `{ user_id, email }`, 401 if invalid.

- POST `/Auth/forgot-password`
	- Body: `{ "email": "user@example.com" }`
	- 200 returns plaintext password if user exists; 404 otherwise.

- GET `/Auth/previous-results?user_id=<id>`
	- Or pass header `X-User-Id: <id>`
	- 200 returns list of prior results for that user.

Notes:
- For `/Counting/count`, you can associate results to a user by sending header `X-User-Id: <id>`.
- In CI (when `CI=true`), DB operations are mocked: user records are not persisted; previous results will be empty; insert ids are dummy strings.

### Notes
- Base path: the API namespaces mount at `/Counting`, `/Correction`, and `/Auth`.
- OpenAPI/Swagger: Flask-RESTX generates docs; open the server root or `/` docs endpoint (as configured) to view interactive API docs.


# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.


# Getting Started with Back End

This repository contains the Week 1 solution for the AI Engineering Lab. It includes a Python backend with unit tests and CI coverage reporting.

## Requirements

- macOS (tested) or Linux
- Python 3.10+ recommended
- Git
- Optional: Docker (for containerized runs)

## Quick Start (macOS/Linux)

1) Clone and enter the project:
```bash
git clone <your-repo-url>.git
cd group-2
```

2) Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) Install dependencies:
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
# If you need PyTorch (CPU wheels are fastest to install):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

4) Run the application (choose the command that matches your app):
- If using FastAPI (typical):
```bash
uvicorn backend.main:app --reload --port 8000
```
- If using Flask (typical):
```bash
export FLASK_APP=backend.app:app
flask run --port 8000
```
- If your entrypoint is a script:
```bash
python backend/main.py
# or
python -m backend
```

Update the module path (backend.main:app, backend.app:app, etc.) to match your codebase.

## Running Tests and Coverage

Run unit tests:
```bash
python -m unittest discover backend/tests -v
```

Run with coverage:
```bash
pip install coverage
coverage run -m unittest discover backend/tests
coverage report -m
coverage xml
```

The GitLab CI pipeline (.gitlab-ci.yml) runs these steps automatically and publishes coverage.xml as an artifact.

## API Documentation

Update this section to reflect the real endpoints in your backend. If you are using:
- FastAPI: Interactive docs available at http://localhost:8000/docs and http://localhost:8000/redoc after starting the server.
- Flask: Consider adding flasgger or apispec, or document endpoints manually below.

### Base URL
- Local: http://localhost:8000
- Production/CI: Replace with your deployment URL (if any)

### Auth
- Describe auth if applicable (e.g., no auth, API key, Bearer token).

### Endpoints (template – replace with actual)

1) Health Check
- Method: GET
- Path: /health
- 200 Response:
```json
{ "status": "ok" }
```
- cURL:
```bash
curl -s http://localhost:8000/health
```

2) Inference/Prediction
- Method: POST
- Path: /predict
- Request (example):
```json
{ "inputs": [1.0, 2.0, 3.0] }
```
- 200 Response (example):
```json
{ "prediction": 0.87 }
```
- cURL:
```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{ "inputs": [1.0, 2.0, 3.0] }'
```

3) Add any additional endpoints similarly:
- Method:
- Path:
- Query/Body:
- Responses:
- cURL:

Tip: If using FastAPI, you can export OpenAPI JSON at /openapi.json for client generation and publishing.

## Configuration

- Environment variables (create a .env if supported by your app):
  - Example: MODEL_PATH, LOG_LEVEL, PORT
- Example:
```bash
export PORT=8000
export LOG_LEVEL=info
```

## Project Structure (typical)

- backend/
  - main.py or app.py (application entrypoint)
  - modules/... (your code)
  - tests/ (unit tests)
- .gitlab-ci.yml (CI pipeline for tests and coverage)
- README.md (this file)

## CI/CD

The GitLab pipeline:
- Uses pytorch/pytorch:latest image
- Caches pip and venv to speed up builds
- Installs requirements, torch (CPU), and runs unittest with coverage
- Publishes coverage.xml artifact for 1 week

You can run the same steps locally using the commands in the “Running Tests and Coverage” section.

## Troubleshooting

- Port already in use: change the port (e.g., --port 8080).
- Missing libs (Linux): install libgl1 and libglib2.0-0 (already handled in CI).
- PyTorch install is slow on GPU wheels: use CPU index URL shown above.
