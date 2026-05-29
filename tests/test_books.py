def test_list_books_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

# Header needed for write operations (matches your auth.py)
AUTH = {"X-API-KEY": "super-secret-key-123"}

def test_create_book(client):
    response = client.post(
        "/books",
        json={"title":"Test Driven Development", "author": "Kent Beck", "year": 2002},
        headers=AUTH
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Driven Development"
    assert data["id"] == 1

def test_create_book_without_key_fails(client):
    response = client.post(
        "/books",
        json={"title":"No Auth", "author": "Nobody", "year": 2000}
        # no headers -> no API key
    )
    assert response.status_code == 401

def test_get_missing_book_returns_404(client):
    response = client.get("/books/999")
    assert response.status_code == 404


def test_create_then_get(client):
    # Create a book...
    create = client.post(
        "/books",
        json={"title": "Refactoring", "author": "Martin Fowler", "year": 2018},
        headers=AUTH,
    )
    book_id = create.json()["id"]
    # ...then fetch it back
    get = client.get(f"/books/{book_id}")
    assert get.status_code == 200
    assert get.json()["author"] == "Martin Fowler"