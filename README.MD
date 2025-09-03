> Complete this template and keep it at the top of your README. Delete this instruction.

# Group <NUMBER>

| Name | Email | FIM ID |
| ---- | ----- | ------ |
|Ali Akbar | akbar01@ads.uni-passau.de      |@akbar        |
|Saeid Khalilian      |khalil10@ads.uni-passau.de       |@khalilian        |
|Yunus Emre Balkis      |balkis01@ads.uni-passau.de       |@balkis        |

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
