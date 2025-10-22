# -*- coding: utf-8 -*-
"""
Configuración local para GASTOS IA
Copia este archivo y configura tus API keys
"""

# 🥇 NOVITA AI (RECOMENDADO)
# Obtener en: https://api.novita.ai/
NOVITA_API_KEY = "tu-api-key-aquí"

# 🥈 GROQ (GRATIS)
# Obtener en: https://console.groq.com/
GROQ_API_KEY = ""

# 🥉 OPENAI (PREMIUM)
# Obtener en: https://platform.openai.com/
OPENAI_API_KEY = ""

# Configuración de la aplicación
SECRET_KEY = "gastos_app_secret_key_2025"
DATABASE_URL = "sqlite:///gastos.db"
UPLOAD_FOLDER = "uploads"
PORT = 5100
FLASK_ENV = "development"

def is_llm_configured():
    """
    Verifica si hay alguna API key configurada
    """
    return bool(
        (NOVITA_API_KEY and NOVITA_API_KEY != "tu-api-key-aquí") or
        (GROQ_API_KEY and GROQ_API_KEY != "tu-api-key-aquí") or
        (OPENAI_API_KEY and OPENAI_API_KEY != "tu-api-key-aquí")
    )

def get_configured_api():
    """
    Retorna la API configurada con prioridad
    Prioridad: NOVITA > GROQ > OPENAI
    """
    if NOVITA_API_KEY and NOVITA_API_KEY != "tu-api-key-aquí":
        return "novita"
    elif GROQ_API_KEY and GROQ_API_KEY != "tu-api-key-aquí":
        return "groq"
    elif OPENAI_API_KEY and OPENAI_API_KEY != "tu-api-key-aquí":
        return "openai"
    return None
