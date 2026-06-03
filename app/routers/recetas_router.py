import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Receta, Ingrediente, Calificacion, Usuario
from app.schemas.schemas import RecetaOut, CalificacionCreate, CalificacionOut
from app.routers.auth_router import get_current_user
from app.services.llm_service import generar_receta

router = APIRouter(prefix="/recetas", tags=["Recetas"])


@router.post("/generar", response_model=RecetaOut, status_code=status.HTTP_201_CREATED)
async def generar_receta_endpoint(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    ingredientes = db.query(Ingrediente).filter(Ingrediente.usuario_id == usuario.id).all()
    if not ingredientes:
        raise HTTPException(status_code=400, detail="No tienes ingredientes registrados en tu inventario")
    lista = [{"nombre": i.nombre, "cantidad": i.cantidad, "unidad": i.unidad} for i in ingredientes]
    datos = await generar_receta(lista)
    receta = Receta(
        nombre_plato=datos["nombre_plato"],
        ingredientes_json=json.dumps(datos["ingredientes"], ensure_ascii=False),
        pasos_json=json.dumps(datos["pasos"], ensure_ascii=False),
        tiempo_estimado=datos["tiempo_estimado"],
        nivel_dificultad=datos["nivel_dificultad"],
        usuario_id=usuario.id,
    )
    db.add(receta)
    db.commit()
    db.refresh(receta)
    return receta


@router.get("", response_model=List[RecetaOut])
def listar_recetas(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    recetas = db.query(Receta).filter(Receta.usuario_id == usuario.id).order_by(Receta.creado_en.desc()).all()
    for receta in recetas:
        cal = db.query(Calificacion).filter(
            Calificacion.receta_id == receta.id,
            Calificacion.usuario_id == usuario.id
        ).first()
        receta.calificacion = cal.estrellas if cal else None
    return recetas


@router.get("/{receta_id}", response_model=RecetaOut)
def obtener_receta(receta_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    receta = db.query(Receta).filter(Receta.id == receta_id, Receta.usuario_id == usuario.id).first()
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return receta


@router.delete("/{receta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_receta(receta_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    receta = db.query(Receta).filter(Receta.id == receta_id, Receta.usuario_id == usuario.id).first()
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    db.delete(receta)
    db.commit()


@router.post("/{receta_id}/calificar", response_model=CalificacionOut, status_code=status.HTTP_201_CREATED)
def calificar_receta(receta_id: int, datos: CalificacionCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    if not (1 <= datos.estrellas <= 5):
        raise HTTPException(status_code=400, detail="La calificacion debe estar entre 1 y 5 estrellas")
    receta = db.query(Receta).filter(Receta.id == receta_id, Receta.usuario_id == usuario.id).first()
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    calificacion = db.query(Calificacion).filter(
        Calificacion.receta_id == receta_id,
        Calificacion.usuario_id == usuario.id
    ).first()
    if calificacion:
        calificacion.estrellas = datos.estrellas
    else:
        calificacion = Calificacion(estrellas=datos.estrellas, receta_id=receta_id, usuario_id=usuario.id)
        db.add(calificacion)
    db.commit()
    db.refresh(calificacion)
    return calificacion
