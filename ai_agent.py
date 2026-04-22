import requests
import json
import re

def analizar_actividad(texto):
    prompt = f"""
Eres un asistente de gestión de actividades.

Analiza:
"{texto}"

Responde SOLO en JSON:

{{
  "titulo": "",
  "prioridad": "alta | media | baja",
  "categoria": "estudio | trabajo | personal",
  "sugerencia": ""
}}
"""

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "phi3:mini",
            "prompt": prompt,
            "stream": False
        })

        data = response.json()
        respuesta = data["response"]

        # Limpiar ```json ```
        respuesta = re.sub(r"```json|```", "", respuesta).strip()

        # Extraer JSON
        json_inicio = respuesta.find("{")
        json_fin = respuesta.rfind("}") + 1
        json_limpio = respuesta[json_inicio:json_fin]

        try:
            parsed = json.loads(json_limpio)

            # Validar campos mínimos
            return {
                "titulo": parsed.get("titulo", "Actividad"),
                "prioridad": parsed.get("prioridad", "media"),
                "categoria": parsed.get("categoria", "general"),
                "sugerencia": parsed.get("sugerencia", "Organizar mejor la tarea")
            }

        except:
            # Fallback si JSON falla
            return {
                "titulo": texto,
                "prioridad": "alta" if "mañana" in texto.lower() else "media",
                "categoria": "estudio" if "examen" in texto.lower() else "general",
                "sugerencia": "Revisar y planificar la actividad"
            }

    except Exception as e:
        return {"error": str(e)}