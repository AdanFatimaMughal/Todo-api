"""
Task API — a small in-memory CRUD API for managing to-do tasks.
FlyRank Internship · Backend Track · W2 · A1

Run with:
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000/docs for Swagger UI.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small in-memory CRUD API for managing a to-do list.",
)

# ---------------------------------------------------------------------------
# Stage 2: in-memory "database" — just a Python list, pre-filled with 3 tasks
# ---------------------------------------------------------------------------

tasks: List[dict] = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Read FastAPI docs", "done": True},
    {"id": 3, "title": "Push to GitHub", "done": False},
]
next_id = 4  # simple counter for new task ids


def find_task(task_id: int) -> Optional[dict]:
    return next((t for t in tasks if t["id"] == task_id), None)


# Request/response models -----------------------------------------------

class TaskCreate(BaseModel):
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------------------------------------------------------------------------
# Stage 1: root + health
# ---------------------------------------------------------------------------

@app.get("/", summary="API info")
def root():
    """Describes the API and lists available endpoints."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    """Used to check the server is alive."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Stage 2: Read
# ---------------------------------------------------------------------------

@app.get("/tasks", summary="List tasks (optionally filter/search)")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    """
    Returns all tasks.

    Optional query params (extras):
    - done: filter by completion status, e.g. /tasks?done=true
    - search: filter by title substring, e.g. /tasks?search=milk
    """
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search is not None:
        needle = search.lower()
        result = [t for t in result if needle in t["title"].lower()]
    return result


@app.get("/tasks/{task_id}", summary="Get a single task")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# ---------------------------------------------------------------------------
# Stage 3: Create
# ---------------------------------------------------------------------------

@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(payload: TaskCreate):
    global next_id
    title = payload.title.strip() if payload.title else ""
    if not title:
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

    new_task = {"id": next_id, "title": title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


# ---------------------------------------------------------------------------
# Stage 4: Update & Delete
# ---------------------------------------------------------------------------

@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Provide at least one of: title, done")

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        task["title"] = title

    if payload.done is not None:
        task["done"] = payload.done

    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
    return None


# ---------------------------------------------------------------------------
# Extras (optional stretch goals)
# ---------------------------------------------------------------------------

@app.get("/stats", summary="Task stats")
def stats():
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done, "open": total - done}


@app.post("/reset", summary="Reset to the 3 example tasks")
def reset():
    global tasks, next_id
    tasks = [
        {"id": 1, "title": "Buy milk", "done": False},
        {"id": 2, "title": "Read FastAPI docs", "done": True},
        {"id": 3, "title": "Push to GitHub", "done": False},
    ]
    next_id = 4
    return {"status": "reset", "tasks": tasks}


# ---------------------------------------------------------------------------
# Make 400/404 errors always come back as {"error": "..."} JSON, per spec
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # A malformed/invalid request body (e.g. wrong type) is a client error -> 400,
    # not FastAPI's default 422.
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})
