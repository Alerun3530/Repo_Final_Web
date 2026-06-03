from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str
    creado_en: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class IngredienteCreate(BaseModel):
    nombre: str
    cantidad: str
    unidad: str


class IngredienteOut(BaseModel):
    id: int
    nombre: str
    cantidad: str
    unidad: str
    creado_en: datetime

    class Config:
        from_attributes = True


class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = None
    cantidad: Optional[str] = None
    unidad: Optional[str] = None


class RecetaOut(BaseModel):
    id: int
    nombre_plato: str
    ingredientes_json: str
    pasos_json: str
    tiempo_estimado: str
    nivel_dificultad: str
    creado_en: datetime
    calificacion: Optional[int] = None

    class Config:
        from_attributes = True


class CalificacionCreate(BaseModel):
    estrellas: int


class CalificacionOut(BaseModel):
    id: int
    estrellas: int
    receta_id: int
    creado_en: datetime

    class Config:
        from_attributes = True
