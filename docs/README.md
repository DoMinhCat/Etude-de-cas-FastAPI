# Etude de cas GarageOS - DePlano

A simple multi-organisation REST API with **role-based access control**, basic **JWT authentication**, and **timeline tracking** for clients, technicians, and interventions.

## Getting Started

### Quick Launch

Get the API up and running swiftly:

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Configure your environment variables
uvicorn main.app:app --reload

```

### Prerequisites

Ensure you have the following installed:

- **PostgreSQL**
- **Docker Compose**
- **Docker Desktop**
- **Python 3.13** or higher

### Docker Build

For a containerized setup:

```
docker-compose up -d
docker exec -it <CONTAINER_ID> sh # Copy the container's id named 'api'
alembic upgrade head
python seed.py

```

## Role-Based Access Control (RBAC)

This API implements RBAC with distinct permissions for `client` and `tech` roles.

### `Tech` Role Permissions (Tech only)

- **Clients:** `GET`, `PATCH`, `DELETE` client information.
- **Technicians:** `PATCH`, `DELETE` technician information.
- **Creation:** Create new clients, technicians, and interventions.
- **Lists:** List all clients, list all interventions.
- **Interventions:** `PATCH`, `DELETE` intervention details.
- **Events:** Create new events for interventions.

### All Other Endpoints

Accessible to **both** `client` and `tech` roles.

## API Endpoints

Detailed API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Status

- `GET /health` : Check API status.

### Clients

- `POST /clients`: Create a client **within the technician's current organization**. (Requires unique username, phone, email).
- `GET /clients`: List clients (supports pagination with `limit`/`offset`, filtering by `q` for first/last name, email).
- `GET /clients/{id}`: Get client information.
- `PATCH /clients/{id}`: Update client details.
- `DELETE /clients/{id}`: Soft-delete a client.

_Similar endpoints are available for **Technicians** (e.g., `/technicians`, `/technicians/{tech_id}`)._

### Interventions/tickets

- `POST /items`: Create an intervention (must be linked to a client from the same organization).
- `GET /items`: List interventions (supports filters by `tech`/`client username`, `statut`, `client id`).
- `GET /items/{id}`: Get intervention information.
- `PATCH /items/{id}`: Update intervention. Status transition rules: `pending` -> `in_progress` -> `completed`. Can be `cancelled` at any time.
- `DELETE /items/{id}`: Soft-delete an intervention.

### Timeline (Progression Log)

- `POST /items/{id}/events`: Add an event to an intervention (Event types: `started`, `updated`, `completed`, `deleted`).
- `GET /items/{id}/events`: List chronological events for an intervention.

## Authentication

- Uses **JWT (JSON Web Tokens)** via **OAuth2** for secure access.
- **Username** is case-insensitive, **password** is case-sensitive.
- `org_id` and `role` are attached in the token/header for access control.

## Error Handling

The API provides clear HTTP status codes for various error scenarios:

- **`400 Bad Request`**: The server cannot process the request due to invalid syntax, missing parameters, or other client-side errors.
- **`401 Unauthorized`**: The client lacks valid authentication credentials for the target resource. This usually means a missing or invalid JWT token.
- **`404 Not Found`**: The requested resource could not be found on the server/in the current organisation.
- **`409 Conflict`**: The request could not be completed due to a conflict with the current state of the target resource (e.g., not respecting enum status transition rule).
- **`500 Internal Server Error`**: An unexpected condition was encountered by the server, preventing it from fulfilling the request.

## Security

The API incorporates several security headers to enhance protection:

- **XSS (Cross-Site Scripting) Protection:** Mitigates clickjacking and other XSS vulnerabilities.
- **No Sniff:** Prevents browsers from MIME-sniffing a response away from the declared `Content-Type`.
- **No Referrer:** Controls what referrer information is sent with requests.
- **Permissions Policy:** Allows or denies the use of browser features by the document.
- **X-Frame-Options:** Prevents the page from being rendered in an `<iframe>`, `<frame>`, `<embed>`, or `<object>`.

## Attention

- A **technician** is allowed to delete their own account.
- An **Admin** role can be introduced for additional control and oversight.

### Initial data provided for Testing

- **Clients:**

  - **Org 1:** `username: cat`, `password: deplano`
  - **Org 2:** `username: alex`, `password: deplano`

- **Technicians:**

  - **Org 1:** `username: tech1`, `password: deplano`
  - **Org 2:** `username: tech2`, `password: de`
