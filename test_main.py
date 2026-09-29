from fastapi.testclient import TestClient
import pytest
from httpx import AsyncClient,ASGITransport
from unittest.mock import patch
from main import app,fetch_ext
import requests

test=TestClient(app)

def test_login_invalid():
    resp=test.post("/auth/token",json={"username":"hello","password":"12"})

    assert resp.status_code==401
    assert resp.json()["detail"]=="Invalid credentials"

@pytest.mark.asyncio
async def test_login_valid():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test.com") as c:
        resp=await c.post("/auth/token",json={"username":"admin","password":"1234"})
        assert resp.status_code==200
        assert resp.json()["access_token"]

def test_protected_route_no_token():
    client=test.get("/v1/completions")
    assert client.status_code==401
    
def test_with_token():
    log=test.post("/auth/token",json={"username":"admin","password":"1234"})
    token=log.json()["access_token"]
    resp=test.get("/v1/completions",headers={"Authorization":f"Bearer {token}"})
    assert resp.status_code==200
    


def test_rate_limit_exceed():
    log=test.post("/auth/token",json={"username":"admin","password":"1234"}) 
    token=log.json()["access_token"]
    headers={"Authorization":f"Bearer {token}"}

    for i in range(6):
        resp=test.get("/v1/completions",headers=headers)
    assert resp.status_code==429


@patch("main.requests.get")
def test_fetch_ext(m):
    mock={"status":"success"}
    m.return_value.json.return_value=mock

    resp=fetch_ext()
    assert resp==mock
    m.assert_called_once_with("https://api.com/data")

