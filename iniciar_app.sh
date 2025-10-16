#!/bin/bash

# Script para iniciar la aplicación de Gestión de Gastos en Mac
# Puerto: 5100

echo "🚀 Iniciando aplicación de Gestión de Gastos..."
echo ""

# Cambiar al directorio de la aplicación
cd "$(dirname "$0")"

# 1. Matar procesos en puerto 5100
echo "🔍 Verificando puerto 5100..."
PORT_PID=$(lsof -ti:5100)

if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  Puerto 5100 en uso. Liberando..."
    kill -9 $PORT_PID 2>/dev/null
    sleep 2
    echo "✅ Puerto 5100 liberado"
else
    echo "✅ Puerto 5100 disponible"
fi

# 2. Verificar que Python3 está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python3 no está instalado"
    exit 1
fi

echo "✅ Python3 detectado: $(python3 --version)"

# 3. Verificar que Tesseract está disponible
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  ADVERTENCIA: Tesseract OCR no está instalado"
    echo "   Para instalarlo: brew install tesseract"
else
    echo "✅ Tesseract OCR detectado"
fi

# 4. Verificar dependencias Python
echo ""
echo "🔧 Verificando dependencias..."
python3 -c "import flask, PIL, pytesseract, cv2, requests, flask_cors, reportlab, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependencias faltantes..."
    pip3 install --user -q Flask Pillow pytesseract opencv-python requests flask-cors openai groq reportlab pandas openpyxl 2>/dev/null
    echo "✅ Dependencias instaladas"
else
    echo "✅ Todas las dependencias disponibles"
fi

# 5. Inicializar base de datos si no existe
if [ ! -f "gastos.db" ]; then
    echo "📊 Inicializando base de datos..."
fi

# 6. Iniciar aplicación
echo ""
echo "🚀 Iniciando servidor Flask en puerto 5100..."
echo ""

# Ejecutar la aplicación
python3 app.py 2>&1 &
APP_PID=$!

# Esperar a que la aplicación inicie
sleep 3

# Verificar que la aplicación está corriendo
if ps -p $APP_PID > /dev/null 2>&1; then
    echo "✅ Aplicación iniciada correctamente (PID: $APP_PID)"
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "   🎉 APLICACIÓN FUNCIONANDO EN PUERTO 5100"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    echo "📍 Acceso:"
    echo "   • Local:      http://localhost:5100"
    echo "   • Red local:  http://$(ipconfig getifaddr en0):5100"
    echo ""
    echo "👥 Usuarios:"
    echo "   • paul / paul      (usuario normal)"
    echo "   • edurne / edurne  (administrador)"
    echo ""
    echo "⚙️  Control:"
    echo "   • Ver logs:   tail -f nohup.out"
    echo "   • Detener:    kill $APP_PID"
    echo "   • O ejecuta:  lsof -ti:5100 | xargs kill -9"
    echo ""
    echo "═══════════════════════════════════════════════════════"
else
    echo "❌ ERROR: La aplicación no pudo iniciar"
    echo "   Revisa el archivo de logs para más detalles"
    exit 1
fi


