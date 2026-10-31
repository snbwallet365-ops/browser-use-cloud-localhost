import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db
from app.security import encrypt_secret, decrypt_secret, mask_secret

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_crypto():
    raw = "sk-super-secret-12345"
    enc = encrypt_secret(raw)
    assert enc != raw
    assert decrypt_secret(enc) == raw
    assert "••••" in mask_secret(raw)
