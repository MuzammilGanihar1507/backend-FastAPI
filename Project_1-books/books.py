from typing import Optional


from fastapi import FastAPI, HTTPException
from enum import Enum

# Initialize the FastAPI app
app = FastAPI(title="Books API + Directions API")

# --- Book Data and Endpoints ---
BOOKS = {
    'book_1': {'title': 'Title One', 'author': 'Author One'},
    'book_2': {'title': 'Title Two', 'author': 'Author Two'},
    'book_3': {'title': 'Title Three', 'author': 'Author Three'},
    'book_4': {'title': 'Title Four', 'author': 'Author Four'},
    'book_5': {'title': 'Title Five', 'author': 'Author Five'}
}

@app.get("/")
async def get_books_excluding(book_name: Optional[str] = None):
    if book_name:
        new_books = BOOKS.copy()
        del new_books[book_name]
        return new_books
    return BOOKS

@app.post("/")
async def create_new_book(book_title, book_author):
    current_book_id = 0
    if len(BOOKS) > 0:
        for book in BOOKS:
            x = int(book.split('_')[-1])
            if x > current_book_id:
                current_book_id = x
    BOOKS[f'book_{current_book_id + 1}'] = {'title': book_title, 'author': book_author}
    return BOOKS[f'book_{current_book_id + 1}']

@app.put("/{book_name}") # path parameter
async def update_book(book_name: str, book_title: str, book_author: str):
    book_information = {"title": book_title, "author": book_author}
    BOOKS[book_name] = book_information
    return book_information

@app.delete("/{book_name}") # path parameter
async def delete_book(book_name: str):
    del BOOKS[book_name]
    return f'Book {book_name} has been deleted.'

@app.get("/books/{book_name}") # path parameter
async def read_books_by_name(book_name: str):
    book = BOOKS.get(book_name)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# --- Direction Enum and Endpoint ---
class DirectionName(str, Enum):
    north = 'North'
    south = 'South'
    east = 'East'
    west = 'West'

@app.get("/directions/{direction_name}") # path parameter
async def get_direction(direction_name: DirectionName):
    if direction_name == DirectionName.north:
        return {"Direction": direction_name, "sub": "Up"}
    if direction_name == DirectionName.south:
        return {"Direction": direction_name, "sub": "Down"}
    if direction_name == DirectionName.east:
        return {"Direction": direction_name, "sub": "Right"}
    if direction_name == DirectionName.west:
        return {"Direction": direction_name, "sub": "Left"}


@app.get("/assignment/") # query parameter
async def read_book_assignment(book_name: str):
    return BOOKS[book_name]


@app.delete("/assignment/")
async def delete_book_assignment(book_name: str):
    del BOOKS[book_name]
    return BOOKS