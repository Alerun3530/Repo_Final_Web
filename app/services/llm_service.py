import json
import re
import httpx
from typing import List, Dict, Any
from app.config import settings


def construir_prompt(ingredientes: List[Dict[str, str]]) -> str:
    lista = "\n".join(
        f"- {ing['nombre']}: {ing['cantidad']} {ing['unidad']}"
        for ing in ingredientes
    )
    return (
        "Eres un chef profesional. Con los siguientes ingredientes disponibles, "
        "genera una receta completa. Responde UNICAMENTE con un objeto JSON valido "
        "sin texto adicional, con esta estructura exacta:\n"
        "{\n"
        '  "nombre_plato": "string",\n'
        '  "ingredientes": [{"nombre": "string", "cantidad": "string", "unidad": "string"}],\n'
        '  "pasos": ["string"],\n'
        '  "tiempo_estimado": "string",\n'
        '  "nivel_dificultad": "Facil | Intermedio | Dificil"\n'
        "}\n\n"
        f"Ingredientes disponibles:\n{lista}"
    )


def parsear_respuesta(respuesta_texto: str) -> Dict[str, Any]:
    texto = respuesta_texto.strip()
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if not match:
        raise ValueError("La respuesta del LLM no contiene un objeto JSON valido")
    datos = json.loads(match.group())
    campos = ["nombre_plato", "ingredientes", "pasos", "tiempo_estimado", "nivel_dificultad"]
    for campo in campos:
        if campo not in datos:
            raise ValueError(f"Campo requerido ausente en la respuesta: {campo}")
    return datos


async def generar_receta(ingredientes: List[Dict[str, str]]) -> Dict[str, Any]:
    prompt = construir_prompt(ingredientes)
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://recetas-app.com",
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        texto = data["choices"][0]["message"]["content"]
        return parsear_respuesta(texto)
