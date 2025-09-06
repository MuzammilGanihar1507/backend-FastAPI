from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from auth import get_current_user, get_user_exception

app = FastAPI(title="Todo Application")

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
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

@app.get("/todo_list/user") 
async def read_all_of_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    This API returns all the todo_items of the logged in user.
    """
    if user is None:
        raise get_user_exception
    return db.query(models.TodoList).filter(models.TodoList.owner_id == user.get("id")).all()

@app.get("/todo_list/{item_id}")
async def read_todo_item(item_id: int, user: dict = Depends(get_current_user) , db:Session = Depends(get_db)):
    """
    This API returns the todo_item based on the item_id in the URL of the logged in user.
    """
    if user is None:
        raise get_user_exception
    else:
        todo_item = db.query(models.TodoList).filter(models.TodoList.id == item_id).filter(models.TodoList.owner_id == user.get("id")).first()

    if todo_item is not None:
        return todo_item
    raise http_exception()

@app.post("/create_todo_item")
async def create_todo_item(todo_item: CreateTodoItem, user: dict = Depends(get_current_user),  db:Session = Depends(get_db)):
    if user is None:
        raise get_user_exception 
       
    todo_model = models.TodoList()
    todo_model.title = todo_item.title
    todo_model.description = todo_item.description
    todo_model.priority = todo_item.priority
    todo_model.complete = todo_item.complete
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return {'status_code': 201,
            'transaction': 'Success'}

@app.put("/todo_item/{item_id}")
async def update_todo(item_id: int, todo_item: CreateTodoItem, user: dict = Depends(get_current_user) , db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception

    todo_item_match = db.query(models.TodoList).filter(models.TodoList.id == item_id).filter(models.TodoList.owner_id == user.get("id")).first()

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
async def delete_todo_item(item_id: int, user: dict = Depends(get_current_user) , db:Session = Depends(get_db)):
    if user is None:
        raise get_user_exception
    
    todo_item_match = db.query(models.TodoList).filter(models.TodoList.id == item_id).filter(models.TodoList.owner_id == user.get("id")).first()

    if todo_item_match is None:
        http_exception()

    db.query(models.TodoList).filter(models.TodoList.id == item_id).delete()
    db.commit()

    return {'status_code': 200,
            'transaction': 'Success'}


def http_exception():
    raise HTTPException(status_code=404, detail="Item not in the To Do List")

