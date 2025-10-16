# 🚀 SOLUCIÓN RÁPIDA: Configurar GROQ (5 minutos)

## ¿Por qué GROQ?
- ✅ **Completamente GRATIS**
- ✅ **Muy rápido**
- ✅ **Extracción automática precisa**
- ✅ **Sin instalar nada**

## 📋 Pasos (5 minutos):

### 1. Crear cuenta GROQ
- Ve a: **https://console.groq.com/**
- Haz clic en "Sign Up"
- Regístrate con tu email
- Verifica tu email

### 2. Crear API Key
- Una vez logueado, ve a "API Keys"
- Haz clic en "Create API Key"
- Copia la key que aparece (empieza con "gsk_...")

### 3. Configurar en la app
- Abre el archivo `config_api.py`
- Busca la línea: `GROQ_API_KEY = "tu-api-key-aquí"`
- Reemplaza `"tu-api-key-aquí"` con tu key real
- Guarda el archivo

### 4. ¡Listo!
- Reinicia la app: `python app.py`
- Ahora podrás extraer datos automáticamente de los tickets

## 🎯 Ejemplo de configuración:
```python
# En config_api.py
GROQ_API_KEY = "gsk_1234567890abcdef..."  # ← Tu key aquí
```

## 🔧 Si tienes problemas:
1. Verifica que copiaste la key completa (empieza con "gsk_")
2. Verifica que no hay espacios extra
3. Reinicia la aplicación después de configurar

## 🆘 Alternativa: Instalar Tesseract
Si prefieres no usar LLM, sigue las instrucciones en `instalar_tesseract.md` 