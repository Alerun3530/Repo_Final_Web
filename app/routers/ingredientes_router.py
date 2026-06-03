from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Ingrediente, Usuario
from app.schemas.schemas import IngredienteCreate, IngredienteOut, IngredienteUpdate
from app.routers.auth_router import get_current_user

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])


@router.get("", response_model=List[IngredienteOut])
def listar_ingredientes(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return db.query(Ingrediente).filter(Ingrediente.usuario_id == usuario.id).all()


@router.post("", response_model=IngredienteOut, status_code=status.HTTP_201_CREATED)
def crear_ingrediente(datos: IngredienteCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    if not datos.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre del ingrediente no puede estar vacio")
    ingrediente = Ingrediente(**datos.model_dump(), usuario_id=usuario.id)
    db.add(ingrediente)
    db.commit()
    db.refresh(ingrediente)
    return ingrediente


@router.put("/{ingrediente_id}", response_model=IngredienteOut)
def actualizar_ingrediente(ingrediente_id: int, datos: IngredienteUpdate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    ingrediente = db.query(Ingrediente).filter(
        Ingrediente.id == ingrediente_id, Ingrediente.usuario_id == usuario.id
    ).first()
    if not ingrediente:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(ingrediente, campo, valor)
    db.commit()
    db.refresh(ingrediente)
    return ingrediente


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ingrediente(ingrediente_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    ingrediente = db.query(Ingrediente).filter(
        Ingrediente.id == ingrediente_id, Ingrediente.usuario_id == usuario.id
    ).first()
    if not ingrediente:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    db.delete(ingrediente)
    db.commit()
