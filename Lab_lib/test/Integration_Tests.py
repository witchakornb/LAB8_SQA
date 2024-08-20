from fastapi.testclient import TestClient
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from fastapi.testclient import TestClient
from src.main import app, User, Book, Borrowlist, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

# Setup the database connection to the provided library.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_borrowlist(db_session):
    # Add a user and a book for testing
    user = User(username="test_borrower111", fullname="Test Borrower")
    db_session.add(user)
    db_session.commit()

    book = Book(title="Test Borrow Book111", firstauthor="Author Borrow", isbn="1122334455")
    db_session.add(book)
    db_session.commit()

    # Create a borrowlist entry using query parameters
    response = client.post(f"/borrowlist/?user_id={user.id}&book_id={book.id}")

    # Add debug information
    if response.status_code != 200:
        print("Response content:", response.content)

    assert response.status_code == 200

    # Verify that the borrowlist entry was correctly created
    borrowlist_entry = db_session.query(Borrowlist).filter_by(user_id=user.id, book_id=book.id).first()
    assert borrowlist_entry is not None
    assert borrowlist_entry.user_id == user.id
    assert borrowlist_entry.book_id == book.id

    # Clean up: delete the borrowlist entry, user, and book
    db_session.delete(borrowlist_entry)
    db_session.delete(user)
    db_session.delete(book)
    db_session.commit()

def test_get_borrowlist(db_session):
    # Add a user and a book for testing
    user = User(username="test_retriever", fullname="Test Retriever")
    db_session.add(user)
    db_session.commit()

    book = Book(title="Test Retrieve Book", firstauthor="Author Retrieve", isbn="5544332211")
    db_session.add(book)
    db_session.commit()

    # Create a borrowlist entry
    borrowlist_entry = Borrowlist(user_id=user.id, book_id=book.id)
    db_session.add(borrowlist_entry)
    db_session.commit()

    # Retrieve the borrow list for the user
    response = client.get(f"/borrowlist/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["user_id"] == user.id
    assert data[0]["book_id"] == book.id

    # Clean up: delete the borrowlist entry, user, and book
    db_session.delete(borrowlist_entry)
    db_session.delete(user)
    db_session.delete(book)
    db_session.commit()