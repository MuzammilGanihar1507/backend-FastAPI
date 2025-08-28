from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

app = FastAPI(title="Todo Application")

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class CreateTodoItem(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, le= 10, description="Priority level to be set between 0 and 10")
    complete: bool


@app.get("/")
async def read_all(db:Session = Depends(get_db)):
    return db.query(models.TodoList).all()

@app.get("/todo_item/{item_id}")
async def read_todo_item(item_id: int, db:Session = Depends(get_db)):
    todo_item = db.query(models.TodoList).filter(models.TodoList.id == item_id).first()

    if todo_item is not None:
        return todo_item
    http_exception()

@app.post("/create_todo_item")
async def create_todo_item(todo_item: CreateTodoItem, db:Session = Depends(get_db)):
    todo_model = models.TodoList()
    todo_model.title = todo_item.title
    todo_model.description = todo_item.description
    todo_model.priority = todo_item.priority
    todo_model.complete = todo_item.complete

    db.add(todo_model)
    db.commit()

    return {'status_code': 201,
            'transaction': 'Success'}

@app.put("/todo_item/{item_id}")
async def update_to_do(item_id: int, todo_item: CreateTodoItem, db: Session = Depends(get_db)):
    todo_item_match = db.query(models.TodoList).filter(models.TodoList.id == item_id).first()

    if todo_item_match is None:
        http_exception()

    todo_item_match.title = todo_item.title
    todo_item_match.description = todo_item.description
    todo_item_match.priority = todo_item.priority
    todo_item_match.complete = todo_item.complete

    db.add(todo_item_match)
    db.commit()

    return {'status_code': 200,
            'transaction': 'Success'}

@app.delete("/todo_item/{item_id}")
async def delete_todo_item(item_id: int, db:Session = Depends(get_db)):
    todo_item_match = db.query(models.TodoList).filter(models.TodoList.id == item_id).first()

    if todo_item_match is None:
        http_exception()

    db.query(models.TodoList).filter(models.TodoList.id == item_id).delete()
    db.commit()

    return {'status_code': 200,
            'transaction': 'Success'}


def http_exception():
    raise HTTPException(status_code=404, detail="Item not in the To Do List")

