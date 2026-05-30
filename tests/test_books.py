def test_list_books_empty(auth_client):
    response = auth_client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

# # Header needed for write operations (matches your auth.py)
# AUTH = {"X-API-KEY": "super-secret-key-123"}

def test_create_book(auth_client):
    response = auth_client.post(
        "/books",
        json={"title":"Test Driven Development", "author": "Kent Beck", "year": 2002},
        # headers=AUTH
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Driven Development"
    assert data["id"] == 1

def test_create_book_without_token_fails(client):
    response = client.post(
        "/books",
        json={"title":"No Auth", "author": "Nobody", "year": 2000}
        # no headers -> no API key
    )
    assert response.status_code == 401

def test_get_missing_book_returns_404(auth_client):
    response = auth_client.get("/books/999")
    assert response.status_code == 404


def test_create_then_get(auth_client):
    # Create a book...
    create = auth_client.post(
        "/books",
        json={"title": "Refactoring", "author": "Martin Fowler", "year": 2018},
        # headers=AUTH,
    )
    book_id = create.json()["id"]
    # ...then fetch it back
    get = auth_client.get(f"/books/{book_id}")
    assert get.status_code == 200
    assert get.json()["author"] == "Martin Fowler"

def test_rate_limit_exceeds(auth_client):
    # The limit is 60/minute on GET /books, The first 5 should pass..
    for i in range(60):
        response = auth_client.get("/books")
        assert response.status_code == 200, f"request {i + 1} should succeed"
    
    # ... the 6th should be blocked with 429.
    response = auth_client.get("/books")
    assert response.status_code == 429