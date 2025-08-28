from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Form, Header
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from contextlib import asynccontextmanager # <--- 1. Import asynccontextmanager

# --- Pydantic Models ---
class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, min_length=2, max_length=500)
    rating: float = Field(ge=0, le=10)

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, min_length=2, max_length=500)
    rating: float = Field(ge=0, le=10)

# --- In-memory database ---
BOOKS: List[Book] = []

def create_books_without_api():
    """Helper function to populate the in-memory list of books."""
    if BOOKS: return
    book_1 = Book(id="663b5300-df83-496d-ac2e-4838239a4811", title="The Great Gatsby", author="F. Scott Fitzgerald", description="A novel about the American Dream.", rating=8.8)
    book_2 = Book(id="90361a71-925c-487d-934c-60c61ce6c299", title="To Kill a Mockingbird", author="Harper Lee", description="A story of justice and innocence.", rating=9.3)
    book_3 = Book(id="43ec1e74-a27d-458c-b996-31884023cacd", title="1984", author="George Orwell", description="A dystopian social science fiction novel.", rating=9.0)
    book_4 = Book(id="2a6bf615-2425-4e55-a15a-0dde0533e7bb", title="The Catcher in the Rye", author="J. D. Salinger", description="A story about teenage angst and alienation.", rating=8.1)
    BOOKS.extend([book_1, book_2, book_3, book_4])

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI): # <--- 2. Define the lifespan context manager
    # Code to run on startup
    print("INFO:     Application startup: Populating initial book data.")
    create_books_without_api()
    yield
    # Code to run on shutdown (e.g., closing database connections, cleaning up resources)
    print("INFO:     Application shutdown: Clearing book data.")
    BOOKS.clear()

# --- FastAPI App Instance ---
app = FastAPI(title="Standard API example-Books", lifespan=lifespan) # <--- 3. Pass lifespan to the app

# --- API Endpoints ---
@app.post("/login/")
async def login(book_number: int, username: str = Optional[Header(None)], password: str = Optional[Header(None)]):
    if username == "FastAPIUser" and password == "test1234":
        return BOOKS[book_number]
    return 'Invalid User'

@app.get("/books", response_model=List[Book])
async def read_all_books(books_to_return: Optional[int] = None, min_rating: Optional[float] = None):
    books_result = BOOKS
    if min_rating is not None:
        books_result = [book for book in books_result if book.rating >= min_rating]
    if books_to_return and books_to_return > 0:
        return books_result[:books_to_return]
    return books_result

@app.get("/books/{book_id}", response_model=Book)
async def read_book_by_UUID(book_id: UUID):
    for item in BOOKS:
        if item.id == book_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found.")

@app.post("/books", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book_in: BookCreate):
    new_book = Book(id=uuid4(), **book_in.model_dump())
    BOOKS.append(new_book)
    return new_book

@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: UUID, book_update: BookCreate):
    for index, item in enumerate(BOOKS):
        if item.id == book_id:
            updated_book = Book(id=book_id, **book_update.model_dump())
            BOOKS[index] = updated_book
            return updated_book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found.")

@app.delete("/books/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_book(book_id: UUID):
    for index, item in enumerate(BOOKS):
        if item.id == book_id:
            del BOOKS[index]
            return f'Book with ID {book_id} was deleted.'
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found.")