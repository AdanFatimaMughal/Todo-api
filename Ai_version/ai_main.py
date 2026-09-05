from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="To-Do API")


# Request model
class TodoCreate(BaseModel):
    title: str
    completed: bool = False


# Response model
class Todo(TodoCreate):
    id: int


# In-memory storage
todos = []
next_id = 1


# CREATE - POST /todos
@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    global next_id

    if not todo.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    new_todo = Todo(
        id=next_id,
        title=todo.title,
        completed=todo.completed
    )

    todos.append(new_todo)
    next_id += 1

    return new_todo


# READ ALL - GET /todos
@app.get("/todos", response_model=list[Todo], status_code=status.HTTP_200_OK)
def get_todos():
    return todos


# READ ONE - GET /todos/{id}
@app.get("/todos/{todo_id}", response_model=Todo, status_code=status.HTTP_200_OK)
def get_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return todo

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Todo not found"
    )


# UPDATE - PUT /todos/{id}
@app.put("/todos/{todo_id}", response_model=Todo, status_code=status.HTTP_200_OK)
def update_todo(todo_id: int, updated_todo: TodoCreate):
    if not updated_todo.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            updated = Todo(
                id=todo_id,
                title=updated_todo.title,
                completed=updated_todo.completed
            )

            todos[index] = updated
            return updated

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Todo not found"
    )


# DELETE - DELETE /todos/{id}
@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos.pop(index)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Todo not found"
    )