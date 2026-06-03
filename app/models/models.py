from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    ingredientes = relationship("Ingrediente", back_populates="usuario", cascade="all, delete-orphan")
    recetas = relationship("Receta", back_populates="usuario", cascade="all, delete-orphan")


class Ingrediente(Base):
    __tablename__ = "ingredientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    cantidad = Column(String(50), nullable=False)
    unidad = Column(String(30), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="ingredientes")


class Receta(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre_plato = Column(String(200), nullable=False)
    ingredientes_json = Column(Text, nullable=False)
    pasos_json = Column(Text, nullable=False)
    tiempo_estimado = Column(String(50), nullable=False)
    nivel_dificultad = Column(String(30), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="recetas")
    calificaciones = relationship("Calificacion", back_populates="receta", cascade="all, delete-orphan")


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id = Column(Integer, primary_key=True, index=True)
    estrellas = Column(Integer, nullable=False)
    receta_id = Column(Integer, ForeignKey("recetas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    receta = relationship("Receta", back_populates="calificaciones")
