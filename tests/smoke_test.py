import os, io, sys
os.environ.update(SECRET_KEY="test-secret", MINIO_ROOT_USER="u", MINIO_ROOT_PASSWORD="p", DATABASE_URL="sqlite:///./test_tmp.db")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from core import storage

fake = MagicMock()
fake.bucket_exists.return_value = True
fake.presigned_get_object.side_effect = lambda b, o, expires: f"http://localhost:9000/{b}/{o}?sig=x"
storage.get_minio_client.cache_clear()
storage.get_minio_client = lambda: fake

from main import app
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100

with TestClient(app) as c:
    U = "/api/v1/users"
    r = c.post(f"{U}/", json={"username": "naomi", "email": "n@x.com", "password": "password123"}); assert r.status_code == 201, r.text
    assert "hashed_password" not in r.text and "password" not in r.json()
    assert c.post(f"{U}/", json={"username": "naomi", "email": "o@x.com", "password": "password123"}).status_code == 400
    assert c.post(f"{U}/token", data={"username": "naomi", "password": "mala"}).status_code == 401
    tok = c.post(f"{U}/token", data={"username": "naomi", "password": "password123"}).json()["access_token"]
    H = {"Authorization": f"Bearer {tok}"}
    assert c.get(f"{U}/").status_code == 401
    assert c.get(f"{U}/me", headers=H).json()["username"] == "naomi"
    # hash en BD
    from sqlmodel import Session, select
    from db.database import engine
    from models import Usuario
    with Session(engine) as s:
        h = s.exec(select(Usuario)).first().hashed_password
        assert h.startswith("$argon2"), h
    # avatar
    r = c.post(f"{U}/me/avatar", headers=H, files={"file": ("a.png", PNG, "image/png")}); assert r.status_code == 200, r.text
    assert r.json()["avatar_url"].startswith("http://localhost:9000/kiri/avatars/1/"), r.json()
    assert fake.put_object.called
    assert c.post(f"{U}/me/avatar", headers=H, files={"file": ("a.png", b"hola", "image/png")}).status_code == 415
    assert c.post(f"{U}/me/avatar", headers=H, files={"file": ("a.png", PNG + b"0" * 3_000_000, "image/png")}).status_code == 413
    assert c.delete(f"{U}/me/avatar", headers=H).status_code == 204 and fake.remove_object.called
    # segundo usuario no puede tocar al primero
    c.post(f"{U}/", json={"username": "otro", "email": "o@x.com", "password": "password123"})
    t2 = c.post(f"{U}/token", data={"username": "otro", "password": "password123"}).json()["access_token"]
    H2 = {"Authorization": f"Bearer {t2}"}
    assert c.put(f"{U}/1", headers=H2, json={"is_active": False}).status_code == 403
    assert c.put(f"{U}/2", headers=H2, json={"username": "naomi"}).status_code == 400
    # refrigeradores
    r = c.post("/api/v1/refrigeradores", headers=H, json={"nombre": "Principal", "ubicacion": "Cocina"}); assert r.status_code == 201, r.text
    r = c.post("/api/v1/refrigeradores/1/alimentos", headers=H, json={"nombre": "Leche", "tipo": "Lácteo", "cantidad": 2, "fecha_caducidad": "2026-12-01"}); assert r.status_code == 201, r.text
    assert len(c.get("/api/v1/refrigeradores/1", headers=H).json()["alimentos"]) == 1
    assert c.get("/api/v1/refrigeradores/1", headers=H2).status_code == 404
    # token manipulado
    assert c.get(f"{U}/me", headers={"Authorization": "Bearer " + tok[:-3] + "abc"}).status_code == 401
    assert c.delete(f"{U}/1", headers=H).status_code == 204
print("TODAS LAS PRUEBAS OK")
