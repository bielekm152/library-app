# Module books.py handles the book domain: loading books, borrowing, returning,
# borrowing extension, and persisting changes into books.csv.
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, Final, cast

import pandas
from pandas import DataFrame

logger = logging.getLogger(__name__)

BOOKS_DTYPE: Final[dict[str, type[str] | type[int]]] = {
    'id': str,
    'name': str,
    'author': str,
    'isbn': str,
    'state': int,
    'date': str,
    'user': str,
    'return_date': str,
}
BOOK_CATEGORIES: Final[list[str]] = [
    "Fantasy",
    "Sci-Fi",
    "Detective",
    "Thriller",
    "Historical",
    "Biography",
    "Classics",
    "Other"
]

# Class Book represents a single book and operations over the CSV data store.
class Book:
    # Initializes a book instance and loads its data when ID is provided.
    # Inputs: book_id (str|None) - book identifier.
    # Returns: None.
    def __init__(self, book_id: str | None = None) -> None:
        self.id: str | None = book_id
        self.author: str | None = None
        self.isbn: str | None = None
        self.name: str | None = None
        self.category: str | None = None
        self.state: int | None = None
        self.date: str | None = None
        self.user: str | None = None
        self.return_date: str | None = None
        if self.id is not None:
            self.define_book()

    @staticmethod
    # Loads books from books.csv and normalizes missing category values.
    # Inputs: no inputs.
    # Returns: pandas.DataFrame with books.
    def load_books_data() -> DataFrame:
        logger.debug("Loading books data from books.csv")
        data = pandas.read_csv("books.csv", dtype=cast(Any, BOOKS_DTYPE))

        # Keep backward compatibility with older CSV files without category column.
        if 'category' not in data.columns:
            data['category'] = 'Other'

        data['category'] = data['category'].fillna('Other').astype(str).str.strip()
        data.loc[data['category'] == '', 'category'] = 'Other'
        return data

    @staticmethod
    # Returns the fixed list of allowed book categories.
    # Inputs: no inputs.
    # Returns: list[str] with category names.
    def get_categories() -> list[str]:
        return BOOK_CATEGORIES

    # Loads one book detail by ID into instance attributes.
    # Inputs: no inputs (uses self.id).
    # Returns: None.
    def define_book(self) -> None:
        data = Book.load_books_data()

        data['id'] = data['id'].str.strip()

        mask = (data['id'] == str(self.id))
        filtered_data = data[mask]

        if not filtered_data.empty:
            self.name = str(filtered_data['name'].iloc[0])
            self.author = str(filtered_data['author'].iloc[0])
            self.isbn = str(filtered_data['isbn'].iloc[0])
            self.category = str(filtered_data['category'].iloc[0])
            self.state = int(filtered_data['state'].iloc[0])
            self.date = str(filtered_data['date'].iloc[0])
            self.user = str(filtered_data['user'].iloc[0])
            self.return_date = str(filtered_data['return_date'].iloc[0])
            logger.debug("Loaded book detail: book_id=%s name=%s state=%s", self.id, self.name, self.state)
        else:
            logger.warning("Book not found for book_id=%s", self.id)

    # Borrows a book for the given user and sets due date to +30 days.
    # Inputs: user_id (str|int) - ID of the borrowing user.
    # Returns: bool - True when borrowing succeeds, otherwise False.
    def borrow_book(self, user_id: str | int) -> bool:
        if not self.state:
            now = datetime.now()
            data = Book.load_books_data()
            data['id'] = data['id'].str.strip()
            mask = (data['id'] == str(self.id))

            data.loc[mask, 'state'] = 1
            data.loc[mask, 'date'] = now.strftime('%d-%m-%Y')
            data.loc[mask, 'user'] = user_id
            data.loc[mask, 'return_date'] = (now + pandas.Timedelta(days=30)).strftime('%d-%m-%Y')

            data.to_csv("books.csv", index=False)
            self.state = 1
            self.date = now.strftime('%d-%m-%Y')
            self.return_date = (now + pandas.Timedelta(days=30)).strftime('%d-%m-%Y')
            logger.info("Book borrowed: book_id=%s user_id=%s return_date=%s", self.id, user_id, self.return_date)
            return True

        logger.warning("Borrow failed: book_id=%s user_id=%s reason=already_borrowed", self.id, user_id)
        return False

    # Returns a book if it is borrowed and belongs to the given user.
    # Inputs: user (str|int) - ID of the returning user.
    # Returns: bool - True when return succeeds, otherwise False.
    def return_book(self, user: str | int) -> bool:
        if self.state and self.user == user:
            data = Book.load_books_data()
            data['id'] = data['id'].str.strip()
            mask = (data['id'] == str(self.id))

            data.loc[mask, 'state'] = 0
            data.loc[mask, 'date'] = '-'
            data.loc[mask, 'user'] = '-'
            data.loc[mask, 'return_date'] = '-'

            data.to_csv("books.csv", index=False)
            self.state = 0
            self.date = '-'
            self.user = '-'
            self.return_date = '-'
            logger.info("Book returned: book_id=%s user_id=%s", self.id, user)
            return True

        logger.warning("Return failed: book_id=%s user_id=%s reason=not_borrowed_by_user", self.id, user)
        return False

    # Extends the borrowing period of a book by a given number of days.
    # Inputs: user_id (str|int) - user ID, extension_days (int) - number of days.
    # Returns: bool - True when extension succeeds, otherwise False.
    def extend_borrowing(self, user_id: str | int, extension_days: int = 14) -> bool:
        if not self.state or self.user != str(user_id):
            logger.warning("Extend failed: book_id=%s user_id=%s reason=not_borrowed_by_user", self.id, user_id)
            return False

        try:
            current_due = datetime.strptime(str(self.return_date), '%d-%m-%Y')
        except ValueError:
            current_due = datetime.now()

        new_due = current_due + pandas.Timedelta(days=extension_days)

        data = Book.load_books_data()
        data['id'] = data['id'].str.strip()
        mask = (data['id'] == str(self.id))
        data.loc[mask, 'return_date'] = new_due.strftime('%d-%m-%Y')
        data.to_csv("books.csv", index=False)

        self.return_date = new_due.strftime('%d-%m-%Y')
        logger.info("Borrowing extended: book_id=%s user_id=%s new_return_date=%s", self.id, user_id, self.return_date)
        return True

    # Deletes a book from the book list by ID.
    # Inputs: no inputs (uses self.id).
    # Returns: None.
    def delete_book(self) -> None:
        data = Book.load_books_data()
        data['id'] = data['id'].str.strip()
        data = data[data['id'] != str(self.id)]
        data.to_csv("books.csv", index=False)
        logger.info("Book deleted: book_id=%s", self.id)

    @staticmethod
    # Adds a new book into books.csv.
    # Inputs: name (str), author (str), isbn (str), category (str).
    # Returns: None.
    def add_book(name: str, author: str, isbn: str, category: str) -> None:
        data = Book.load_books_data()
        data['id'] = data['id'].str.strip()
        new_id = str(data['id'].astype(int).max() + 1)
        new_book = {
            'id': new_id,
            'name': name,
            'author': author,
            'isbn': isbn,
            'category': category,
            'state': '0',
            'date': '-',
            'user': '-',
            'return_date': '-'
        }
        data = pandas.concat([data, pandas.DataFrame([new_book])], ignore_index=True)
        data.to_csv("books.csv", index=False)
        logger.info("Book added: book_id=%s name=%s isbn=%s category=%s", new_id, name, isbn, category)
