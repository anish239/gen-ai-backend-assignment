# Gen AI Analytics Query Simulator Backend

This project is a lightweight backend service simulating a simplified version of a Generative AI Analytics data query system, built as part of a candidate assignment. It allows users to ask questions in natural language and receive simulated data insights based on keyword recognition.

**Live Demo URL:** https://gen-ai-backend-anish.onrender.com

## Tech Stack

- **Language:** Python 3.x
- **Framework:** Flask
- **Web Server (for deployment):** Gunicorn
- **Database:** In-Memory Python list of dictionaries (mock data)
- **Authentication:** Simple Static API Key (`X-API-Key` header)
- **Deployment Platform:** Render

## Project Structure

gen-ai-sim-backend/
├── venv/ # Virtual environment (ignored by git)
├── app.py # Main Flask application, routes, auth
├── logic.py # Mock data, query parsing, execution logic
├── requirements.txt # Python dependencies (Flask, Gunicorn)
├── README.md # This file
├── .gitignore # Git ignore rules

## Setup and Running Locally

1.  **Clone the repository:**

    ```bash
    git clone <Your-GitHub-Repo-URL>
    cd <Your-Repo-Directory>
    ```

    _(Replace with your actual repo URL/directory name if sharing)_

2.  **Create and activate a virtual environment:**

    ```bash
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\\venv\\Scripts\\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask development server:**

    ```bash
    python app.py
    ```

    The API will start running, typically at `http://127.0.0.1:5001`.

5.  **Required API Key:** For testing locally or against the deployed version, you must include the following API key in your requests via the `X-API-Key` header:
    `my-super-secret-key-123`

## API Documentation

The base URL is `http://127.0.0.1:5001` when running locally, or the **Live Demo URL** (`https://gen-ai-backend-anish.onrender.com`) above when using the deployed version.

**Authentication:**
All API endpoints (`/query`, `/explain`, `/validate`) require an `X-API-Key` header containing the correct API key (`my-super-secret-key-123`). Requests without a valid key will receive a `401 Unauthorized` response.

**Common Request Headers:**

- `Content-Type: application/json`
- `X-API-Key: my-super-secret-key-123`

---

### 1. Query Data Endpoint (`/query`)

- **Method:** `POST`
- **Description:** Accepts a natural language query, attempts to parse it using keyword spotting, executes the simulated query against the in-memory data, and returns the result.
- **Request Body:**
  ```json
  {
    "query": "Your natural language query string"
  }
  ```
- **Success Response (Status Code: `200 OK`):**
  - If the action was `list`: `{"result": [array of matching data objects]}`
  - If the action was `count`: `{"result": integer_count}`
  - If the action was `sum` or `average`: `{"result": numerical_value}`
- **Error Responses:**
  - `400 Bad Request`: If JSON is malformed, the `query` field is missing, or the query fails validation during parsing (e.g., asking for `sum` without a valid field). Body: `{"error": "Error description"}`.
  - `401 Unauthorized`: If the `X-API-Key` header is missing or incorrect. Body: `{"error": "Unauthorized - Missing or invalid API Key"}`.
  - `500 Internal Server Error`: If an unexpected error occurs during query execution logic. Body: `{"error": "An internal error occurred..."}`.

---

### 2. Explain Query Endpoint (`/explain`)

- **Method:** `POST`
- **Description:** Accepts a natural language query and returns a breakdown of how the simple parsing logic interpreted it, including the identified intent, simulated SQL, and parsing steps. Does not execute the query.
- **Request Body:**
  ```json
  {
    "query": "Your natural language query string"
  }
  ```
- **Success Response (Status Code: `200 OK`):**
  ```json
  {
      "query": "Original query string",
      "simulated_sql": "SELECT ... FROM sales WHERE ... (simulated)",
      "parsing_steps": [
          "Starting query analysis.",
          "Identified action keyword: '...'." ,
          "Query parsing complete."
      ],
      "parsed_intent": {
          "action": "list | count | sum | average",
          "target_field": "sales | quantity | rows | null",
          "filters": {"field_name": "value", ...}
       },
      "is_understood": true | false,
       "validation_reason": "Reason why it is or isn't valid (e.g., 'Query parsed successfully.', 'Action 'sum' requires a field...')"
  }
  ```
- **Error Responses:** `400 Bad Request` (for missing/bad JSON/query field), `401 Unauthorized`, `500 Internal Server Error` (if parsing logic itself crashes unexpectedly).

---

### 3. Validate Query Endpoint (`/validate`)

- **Method:** `POST`
- **Description:** Accepts a natural language query and performs only the validation step of the parsing logic to check if the query seems understandable based on known keywords and required fields for certain actions.
- **Request Body:**
  ```json
  {
    "query": "Your natural language query string"
  }
  ```
- **Response:**
  - **If Valid (Status Code: `200 OK`):**
    ```json
    {
      "query": "Original query string",
      "is_valid_for_processing": true,
      "reason": "Query parsed successfully."
    }
    ```
  - **If Invalid (Status Code: `400 Bad Request`):** Also used if request JSON is malformed or `query` field missing.
    ```json
    {
      "query": "Original query string",
      "is_valid_for_processing": false,
      "reason": "Reason why validation failed (e.g., Action 'sum' requires a field...)"
    }
    ```
- **Error Responses:** `401 Unauthorized`, `500 Internal Server Error` (if validation logic itself crashes unexpectedly).

## Sample `curl` Commands for Testing

Using the deployed URL: `https://gen-ai-backend-anish.onrender.com`

**1. Query - Get total sales for Laptops:**

```bash
curl -X POST https://gen-ai-backend-anish.onrender.com/query \
-H "Content-Type: application/json" \
-H "X-API-Key: my-super-secret-key-123" \
-d '{"query": "what is the total sales for laptops"}'

2. Query - List keyboards in North:

curl -X POST https://gen-ai-backend-anish.onrender.com/query \
-H "Content-Type: application/json" \
-H "X-API-Key: my-super-secret-key-123" \
-d '{"query": "show me keyboards in north region"}'

3. Query - Count orders in Feb:

curl -X POST https://gen-ai-backend-anish.onrender.com/query \
-H "Content-Type: application/json" \
-H "X-API-Key: my-super-secret-key-123" \
-d '{"query": "count orders month feb"}'

4. Explain - Average quantity for monitors:

curl -X POST https://gen-ai-backend-anish.onrender.com/explain \
-H "Content-Type: application/json" \
-H "X-API-Key: my-super-secret-key-123" \
-d '{"query": "average quantity for monitors"}'

5. Validate - A query that should fail validation:

curl -X POST https://gen-ai-backend-anish.onrender.com/validate \
-H "Content-Type: application/json" \
-H "X-API-Key: my-super-secret-key-123" \
-d '{"query": "total profit"}'

6. Validate - Valid query:

curl -X POST https://gen-ai-backend-anish.onrender.com/validate \
-H "Content-Type: application/json" \
-H "X-API-Key: my-super-secret-key-123" \
-d '{"query": "list sales in west"}'

7. Test Auth Failure:

curl -X POST https://gen-ai-backend-anish.onrender.com/query \
-H "Content-Type: application/json" \
-H "X-API-Key: incorrect-api-key" \
-d '{"query": "list sales"}'

Deployment Notes
This application is deployed on Render's free tier.

The deployment uses Gunicorn as the WSGI server.

The start command configured on Render is gunicorn --bind 0.0.0.0:$PORT app:app.

Dependencies are installed via pip install -r requirements.txt.
```

**To finalize:**

1.  Copy the corrected markdown above.
2.  Paste it into your `README.md` file, replacing the old content.
3.  Save the file.
4.  Commit and push the final change:
    ```bash
    git add README.md
    git commit -m "Finalize README formatting"
    git push origin main
    ```

You are definitely ready now!
