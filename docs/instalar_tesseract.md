# 📸 Instalación de Tesseract OCR para Windows

## ¿Qué es Tesseract?
Tesseract es el software de reconocimiento óptico de caracteres (OCR) que permite extraer texto de las imágenes de tickets automáticamente.

## 🚀 Instalación Rápida

### 1. Descargar Tesseract
- Ve a: https://github.com/UB-Mannheim/tesseract/wiki
- Descarga la versión más reciente para Windows (archivo .exe)

### 2. Instalar
1. **Ejecuta el archivo .exe descargado**
2. **Durante la instalación, IMPORTANTE:**
   - ✅ Marca la casilla **"Add Tesseract to PATH"**
   - ✅ Selecciona instalar idiomas adicionales (especialmente Spanish)
3. **Completa la instalación**

### 3. Verificar Instalación
1. **Abre Command Prompt o PowerShell**
2. **Escribe:** `tesseract --version`
3. **Si funciona**, verás la versión instalada
4. **Si no funciona**, necesitas añadir Tesseract al PATH manualmente

## 🔧 Solución de Problemas

### Error: "tesseract is not installed"

**Opción A: Reinstalar con PATH**
1. Desinstala Tesseract
2. Reinstala marcando "Add to PATH"
3. Reinicia tu computadora

**Opción B: Añadir PATH manualmente**
1. Encuentra donde se instaló Tesseract (usualmente `C:\Program Files\Tesseract-OCR`)
2. Copia la ruta completa
3. Añade la ruta al PATH de Windows:
   - Presiona `Win + R`, escribe `sysdm.cpl`
   - Ve a "Advanced" → "Environment Variables"
   - En "System Variables", encuentra "Path" y haz clic en "Edit"
   - Haz clic en "New" y pega la ruta de Tesseract
   - Haz clic en "OK" en todas las ventanas
4. Reinicia tu computadora

## 📱 ¿Qué pasa si no instalo Tesseract?

**La aplicación seguirá funcionando**, pero:
- ❌ No podrá extraer texto de las imágenes automáticamente
- ❌ Tendrás que escribir manualmente el importe, fecha y descripción
- ✅ Todas las demás funciones funcionarán normalmente

## 🤖 Alternativa: Usar LLM sin OCR

Si no quieres instalar Tesseract, puedes:
1. Configurar una API key en `config_api.py`
2. El LLM intentará extraer información directamente de la imagen
3. Resultado: extracción automática sin necesidad de OCR

## 🆘 Ayuda Adicional

Si tienes problemas:
1. Reinicia la aplicación después de instalar Tesseract
2. Verifica que el comando `tesseract --version` funciona en Command Prompt
3. Si sigue sin funcionar, usa la opción de LLM configurando las API keys

## 🎯 Instalación Exitosa

Cuando esté correctamente instalado:
- ✅ La aplicación mostrará "Tesseract OCR encontrado" en los logs
- ✅ Podrás hacer fotos y extraer texto automáticamente
- ✅ La extracción de datos será mucho más precisa 