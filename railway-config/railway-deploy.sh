#!/bin/bash

# Script de deploy a Railway para GASTOS IA

echo "🚀 Iniciando deploy a Railway..."

# Verificar que Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI no está instalado"
    echo "📦 Instalando Railway CLI..."
    npm install -g @railway/cli
fi

# Verificar que estamos logueados
if ! railway whoami &> /dev/null; then
    echo "🔐 Iniciando sesión en Railway..."
    railway login
fi

# Crear proyecto si no existe
if [ ! -f ".railway/project.json" ]; then
    echo "📁 Creando nuevo proyecto en Railway..."
    railway new
fi

# Conectar al proyecto
echo "🔗 Conectando al proyecto..."
railway link

# Configurar variables de entorno
echo "⚙️ Configurando variables de entorno..."
railway variables set PORT=5100
railway variables set FLASK_ENV=production
railway variables set DATABASE_URL=sqlite:///gastos.db
railway variables set SECRET_KEY=gastos_app_secret_key_2025_railway
railway variables set UPLOAD_FOLDER=uploads

# Deploy
echo "🚀 Deployando aplicación..."
railway up

echo "✅ Deploy completado!"
echo "🌐 La aplicación estará disponible en:"
railway domain

echo "📊 Para ver logs:"
echo "railway logs"

echo "🔧 Para ver variables de entorno:"
echo "railway variables"
