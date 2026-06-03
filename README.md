# Generador de Recetas con Inventario

Aplicacion web desarrollada con FastAPI que permite a los usuarios registrar ingredientes disponibles y generar recetas personalizadas mediante un modelo de lenguaje (LLM).

## Tecnologias utilizadas

- **Backend:** Python 3.11, FastAPI
- **Base de datos:** MySQL 8.0 con SQLAlchemy
- **Autenticacion:** JWT con python-jose y passlib
- **LLM:** OpenRouter API
- **Contenedores:** Docker y Docker Compose
- **Pruebas:** pytest

## Requisitos previos

- Docker y Docker Compose instalados
- Una clave de API de OpenRouter (https://openrouter.ai)

## Configuracion

1. Clonar el repositorio:

```bash
git clone <url-del-repositorio>
cd proyecto-recetas
```

2. Crear el archivo de variables de entorno:

```bash
cp .env.example .env
```

3. Editar el archivo `.env` con los valores reales, especialmente:
   - `SECRET_KEY`: una cadena aleatoria y segura
   - `OPENROUTER_API_KEY`: tu clave de API de OpenRouter
   - Credenciales de base de datos

## Ejecucion con Docker Compose

```bash
docker compose up --build -d
```

La aplicacion estara disponible en `http://localhost:8000`

La documentacion interactiva de la API estara en `http://localhost:8000/docs`

## Ejecucion local (desarrollo)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Pruebas unitarias

```bash
pip install -r requirements.txt
pytest
```

## Estructura del proyecto

```
proyecto-recetas/
├── app/
│   ├── main.py              # Punto de entrada de la aplicacion
│   ├── config.py            # Configuracion y variables de entorno
│   ├── database.py          # Conexion y sesion de base de datos
│   ├── models/
│   │   └── models.py        # Modelos SQLAlchemy (4 tablas)
│   ├── routers/
│   │   ├── auth_router.py   # Endpoints de autenticacion
│   │   ├── ingredientes_router.py
│   │   └── recetas_router.py
│   ├── services/
│   │   ├── auth.py          # Logica JWT y password hashing
│   │   └── llm_service.py   # Integracion con LLM
│   └── schemas/
│       └── schemas.py       # Esquemas Pydantic
├── tests/
│   └── test_app.py          # Pruebas unitarias (10+ pruebas)
├── templates/
│   └── index.html           # Interfaz de usuario
├── static/
│   └── favicon.ico
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── .env.example
└── requirements.txt
```

## Modelo de base de datos

- **usuarios**: id, nombre, email, hashed_password, creado_en
- **ingredientes**: id, nombre, cantidad, unidad, usuario_id, creado_en
- **recetas**: id, nombre_plato, ingredientes_json, pasos_json, tiempo_estimado, nivel_dificultad, usuario_id, creado_en
- **calificaciones**: id, estrellas, receta_id, usuario_id, creado_en

## Funcionalidades

1. Registro e inicio de sesion con JWT
2. CRUD completo de ingredientes del inventario personal
3. Generacion de recetas mediante LLM a partir del inventario
4. Historial de recetas generadas
5. Calificacion de recetas (1 a 5 estrellas)
6. Eliminacion de recetas del historial

## Despliegue en produccion

Para desplegar en un VPS con dominio y SSL usando Caddy:

1. Configurar DNS apuntando al servidor
2. Instalar Docker y Docker Compose en el VPS
3. Clonar el repositorio y configurar `.env`
4. Agregar Caddy como reverse proxy en `docker-compose.yml`
5. Ejecutar `docker compose up -d`

## Variables de entorno

Ver `.env.example` para la lista completa de variables requeridas.
