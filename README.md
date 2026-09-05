# Task API

A small in-memory CRUD API for managing a to-do list, built with FastAPI.

Built for FlyRank Internship · Backend Track · W2 · Assignment A1.

## How to install & run

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install fastapi uvicorn
uvicorn main:app --reload --port 8000
```

Then open **http://localhost:8000/docs** for interactive Swagger UI, or hit the API directly at `http://localhost:8000`.

Data lives only in memory — restarting the server resets it back to 3 example tasks.

## Endpoints

| Method | Path              | Description                          | Success | Errors        |
|--------|-------------------|---------------------------------------|---------|---------------|
| GET    | `/`               | API info                              | 200     | –             |
| GET    | `/health`         | Health check                          | 200     | –             |
| GET    | `/tasks`          | List all tasks (supports `?done=` and `?search=`) | 200 | – |
| GET    | `/tasks/{id}`     | Get a single task                     | 200     | 404           |
| POST   | `/tasks`          | Create a task (`{"title": "..."}`)    | 201     | 400           |
| PUT    | `/tasks/{id}`     | Update a task's `title` and/or `done` | 200     | 400, 404      |
| DELETE | `/tasks/{id}`     | Delete a task                         | 204     | 404           |
| GET    | `/stats`          | Task counts (extra)                   | 200     | –             |
| POST   | `/reset`          | Reset to the 3 example tasks (extra)  | 200     | –             |

## Sample curl output
![alt text](<screenshots/Screenshot 2026-09-04 223530.png>)
![alt text](<screenshots/Screenshot 2026-09-04 222202.png>)

## Swagger screenshot
![Creating a task via POST /tasks](<screenshots/Screenshot 2026-09-04 215856.png>)

Full CRUD cycle confirmed via Swagger — task created, appears in the list, then deleted:
![List after creation](<screenshots/Screenshot 2026-09-04 220320.png>)
![List after deletion](<screenshots/Screenshot 2026-09-04 221042.png>)

## The mortality experiment

Created a few tasks, restarted the server, hit `GET /tasks` — the new tasks were gone and only the original 3 seed tasks remained. That's because the "database" is just a Python list living in the process's memory: as soon as the process exits, that memory is freed and nothing is left on disk.
This is exactly why Week 3 introduces a real database.

## AI vs me

**My prompt:**

I'm building a to-do API in Python using FastAPI. It should perform full CRUD operations, run at http://localhost:8001, use no database (in-memory storage only), and include Swagger UI. I expect the API to use status codes 200, 201, 204, 400, and 404 where appropriate.

**What the AI did better:**
It reused a single Pydantic model (TodoCreate) for both creating and updating tasks, which is more concise than my two separate models. It also correctly implemented all 5 status codes I explicitly asked for on the happy path.

**What it got wrong or quietly ignored:**

1. **Wrong status code on invalid input.** I asked for `400` on bad requests, but 
sending an empty body returns FastAPI's default `422` with a `{"detail": [...]}` 
error shape — not `400` or my `{"error": "..."}` format:

![AI version returns 422 instead of 400](<screenshots/Screenshot ai-422-bug.png>)

2. **A real data-corruption bug in PUT.** Because it reused the same model 
(with `completed` defaulting to `False`) for updates, sending 
`{"title": "done task again"}` without `completed` silently reset a task's 
`completed` status back to `false` — even though it had just been marked `true`:

![completed silently resets to false on partial PUT](<screenshots/Screenshot ai-put-bug.png>)

3. **Missing endpoints.** My version has 9 endpoints total — the 5 CRUD 
routes plus `GET /` (API info), `GET /health`, `GET /stats`, and 
`POST /reset`. The AI's version only implemented the 5 CRUD routes and 
nothing else, since my prompt never mentioned the extras.

![my version](<screenshots/Screenshot my-version.png>)
![ai version](<screenshots/Screenshot ai-version.png>)

4. **Different naming.** It used `/todos` and `completed` instead of my 
`/tasks` and `done` — not wrong, just a different vocabulary since I never 
specified field or path names.

**What my prompt forgot to specify:**

The exact error response JSON shape ({"error": "..."} vs FastAPI's default)
That partial updates shouldn't reset unmentioned fields
Endpoint and field names
The / and /health endpoints
