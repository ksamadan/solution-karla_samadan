import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app

@pytest_asyncio.fixture
async def test_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    TestingSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestingSessionLocal() as session:
        yield session

    await engine.dispose()

@pytest_asyncio.fixture
async def client(test_session):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_create_ticket(client):
    payload = {
        "title": "Problem with login",
        "description": "User cannot log in",
        "status": "open",
        "priority": "high",
        "assignee": "karla",
    }

    response = await client.post("/tickets", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Problem with login"
    assert data["status"] == "open"
    assert data["priority"] == "high"
    assert data["assignee"] == "karla"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_tickets(client):
    payload = {
        "title": "Printer does not work",
        "description": "The office printer is not responding",
        "status": "open",
        "priority": "medium",
        "assignee": "ana",
    }

    await client.post("/tickets", json=payload)

    response = await client.get("/tickets")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Printer does not work"
    assert data[0]["status"] == "open"
    assert data[0]["priority"] == "medium"

@pytest.mark.asyncio
async def test_patch_ticket(client):
    create_payload = {
        "title": "Payment issue",
        "description": "Customer payment failed",
        "status": "open",
        "priority": "low",
        "assignee": "marko",
    }

    create_response = await client.post("/tickets", json=create_payload)
    ticket_id = create_response.json()["id"]

    update_payload = {
        "status": "closed",
        "priority": "high",
    }

    response = await client.patch(f"/tickets/{ticket_id}", json=update_payload)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == ticket_id
    assert data["status"] == "closed"
    assert data["priority"] == "high"

@pytest.mark.asyncio
async def test_search_tickets(client):
    payload = {
        "title": "Internet connection problem",
        "description": "Wi-Fi is not working",
        "status": "open",
        "priority": "high",
        "assignee": "iva",
    }

    await client.post("/tickets", json=payload)

    response = await client.get("/tickets/search?q=Internet")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Internet connection problem"
