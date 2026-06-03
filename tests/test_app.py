import json
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.services.llm_service import construir_prompt, parsear_respuesta
from app.services.auth import hash_password, verificar_password

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_hash_y_verificar_password():
    password = "contrasena_segura"
    hashed = hash_password(password)
    assert verificar_password(password, hashed)
    assert not verificar_password("contrasena_incorrecta", hashed)


def test_construir_prompt_contiene_ingredientes():
    ingredientes = [
        {"nombre": "Tomate", "cantidad": "3", "unidad": "unidades"},
        {"nombre": "Cebolla", "cantidad": "1", "unidad": "unidades"},
    ]
    prompt = construir_prompt(ingredientes)
    assert "Tomate" in prompt
    assert "Cebolla" in prompt
    assert "JSON" in prompt


def test_parsear_respuesta_valida():
    datos = {
        "nombre_plato": "Ensalada de tomate",
        "ingredientes": [{"nombre": "Tomate", "cantidad": "3", "unidad": "unidades"}],
        "pasos": ["Lavar los tomates", "Cortar en rodajas"],
        "tiempo_estimado": "10 minutos",
        "nivel_dificultad": "Facil",
    }
    resultado = parsear_respuesta(json.dumps(datos))
    assert resultado["nombre_plato"] == "Ensalada de tomate"
    assert len(resultado["pasos"]) == 2


def test_parsear_respuesta_con_texto_extra():
    datos = {
        "nombre_plato": "Sopa",
        "ingredientes": [{"nombre": "Zanahoria", "cantidad": "2", "unidad": "unidades"}],
        "pasos": ["Pelar", "Hervir"],
        "tiempo_estimado": "20 minutos",
        "nivel_dificultad": "Facil",
    }
    respuesta = "Aqui esta tu receta: " + json.dumps(datos) + " Espero que te guste."
    resultado = parsear_respuesta(respuesta)
    assert resultado["nombre_plato"] == "Sopa"


def test_parsear_respuesta_invalida_lanza_error():
    with pytest.raises(ValueError):
        parsear_respuesta("Este texto no contiene JSON valido")


def test_parsear_respuesta_campos_incompletos():
    datos_incompletos = {"nombre_plato": "Sopa"}
    with pytest.raises((ValueError, KeyError)):
        parsear_respuesta(json.dumps(datos_incompletos))


def test_registro_usuario():
    res = client.post("/auth/registro", json={
        "nombre": "Usuario Prueba",
        "email": "prueba@test.com",
        "password": "password123",
    })
    assert res.status_code == 201
    assert res.json()["email"] == "prueba@test.com"


def test_login_usuario():
    client.post("/auth/registro", json={
        "nombre": "Login Test",
        "email": "login@test.com",
        "password": "password123",
    })
    res = client.post("/auth/login", data={
        "username": "login@test.com",
        "password": "password123",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_ingredientes_requiere_autenticacion():
    res = client.get("/ingredientes")
    assert res.status_code == 401


def test_crear_ingrediente_autenticado():
    client.post("/auth/registro", json={
        "nombre": "Cocinero",
        "email": "cocinero@test.com",
        "password": "password123",
    })
    login_res = client.post("/auth/login", data={
        "username": "cocinero@test.com",
        "password": "password123",
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/ingredientes", json={
        "nombre": "Arroz",
        "cantidad": "500",
        "unidad": "gramos",
    }, headers=headers)
    assert res.status_code == 201
    assert res.json()["nombre"] == "Arroz"
