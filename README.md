# Aegis Event-Bus (Agent A0) · v0.1

This is the secure, auditable, and scalable backbone for the Aegis Multi-Agent AI ecosystem. It is designed to handle job requests, manage data, and emit events for other agents to consume.

---
## Features

- **FastAPI Service:** Provides a modern, asynchronous API for job management.
- **JWT Authentication:** Endpoints are secured, requiring a valid token for access.
- **SQLite Backend:** Simple, file-based, and reliable data persistence.
- **Automated Folder Creation:** Creates a standardized directory structure for each new job.
- **MQTT Event Publishing:** Broadcasts a `job.created` event for other agents.
- **Containerized:** Runs entirely within Docker via a simple `docker-compose` command.
- **Automated Testing:** Includes a full suite of unit tests with `pytest` and automated CI via GitHub Actions.

---

## Prerequisites

| Tool           | Notes                          |
| -------------- | ------------------------------ |
| Python         | 3.11+                          |
| Docker         | Latest version                 |
| Docker Compose | Latest version (usually incl. with Docker) |

---

## 🚀 Quick Start (Using Docker Compose)

This is the recommended way to run the application.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/aegis-event-bus.git](https://github.com/your-username/aegis-event-bus.git)
    cd aegis-event-bus
    ```

2.  **Configure Environment:**
    Copy the example environment file. No changes are needed for default local startup.
    ```bash
    cp .env.example .env
    ```

3.  **Run the Application Stack:**
    This single command will build and start the FastAPI service and the MQTT broker.
    ```bash
    docker compose up --build
    ```

---

## Accessing the Services

- **API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **MQTT Broker:** `localhost:1883`

---

## 🧪 Running Tests

1.  Create and activate a Python virtual environment.
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2.  Install dependencies.
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the test suite.
    ```bash
    pytest -v
    ```
    ---
## Advanced Usage

### Pagination

The `GET /jobs` endpoint supports cursor-based pagination.

`GET /jobs?limit=20&cursor=<last_id>`

This will return a JSON object with `items` and a `next_cursor`. To fetch the next page, make the same request again, passing the received `next_cursor` value in the `cursor` query parameter.

### Generate an Admin JWT

You can generate a long-lived token for administrative or testing purposes using the built-in CLI.

```bash
python -m app.cli create-token admin --minutes 1440