from typing import Optional

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: str
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not neeeded on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": 2024,
            }
        }
    }


BOOKS = [
    Book(1, "Computer Science Pro", "codingwithroby", "A very nice book!", 5, 2012),
    Book(2, "Be Fast With FastAPI", "codingwithroby", "A great book!", 5, 2014),
    Book(3, "Master Endpoints", "codingwithroby", "An awesome book!", 5, 2017),
    Book(4, "HP1", "Author 1", "Book description", 2, 2022),
    Book(5, "HP2", "Author 2", "Book description", 3, 2024),
    Book(6, "HP3", "Author 3", "Book description", 1, 2024),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/{id}", status_code=status.HTTP_200_OK)
async def read_book(id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == id:
            return book

    raise HTTPException(404, detail=f"Book with ID {id} not found.")


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(rating: int = Query(gt=0, lt=6)):
    books_to_return = []

    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)

    return books_to_return


@app.get("/books/published/", status_code=status.HTTP_200_OK)
async def read_books_by_published_date(published_date: int = Query(gt=1999, lt=2031)):
    books_to_return = []

    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)

    return books_to_return


@app.post("/books/create_book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False

    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True

    if not book_changed:
        raise HTTPException(404, detail=f"Book with ID {book.id} not found.")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_deleted = False

    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_deleted = True
            break

    if not book_deleted:
        raise HTTPException(404, detail=f"Book with ID {book_id} not found.")


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book
