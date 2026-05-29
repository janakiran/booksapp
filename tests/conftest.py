import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_session

@pytest.fixture(name="session")
def session_fixture():
    # A brand-new in-memory database for EACH test - totally isolated.
    engine = create_engine(
        "sqlite://",                            # no file = in-memory
        connect_args={"check_same_thread":False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)        # create tables in the test DB.
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    # Override get_session so the app uses our TEST database, not books.db
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()            # undo the override after the test