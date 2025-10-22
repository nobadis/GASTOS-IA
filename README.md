# 💰 GASTOS IA - Sistema Inteligente de Gestión de Gastos

Sistema avanzado de gestión de gastos con extracción automática de datos mediante IA (Novita AI - Qwen2.5-VL-72B).

## 🚀 Características Principales

- **Extracción Automática con IA**: Procesa imágenes de tickets y extrae datos automáticamente
- **Gestión de Usuarios**: Sistema de usuarios con roles (admin/user) y parent_admin
- **Gestión de Viajes**: Organiza gastos en grupos/viajes
- **Cuadre Automático**: Reconcilia gastos con gastos esperados
- **Conversión de Monedas**: Soporte para múltiples monedas
- **Exportación**: PDF, Excel y ZIP de imágenes
- **Multiusuario**: Soporte para múltiples usuarios con diferentes roles
- **Interfaz Moderna**: UI/UX intuitiva y responsive

## 📋 Requisitos

- Python 3.9+
- Flask
- SQLite
- Novita AI API Key (opcional, para extracción automática)

## 🔧 Instalación Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/nobadis/GASTOS-IA.git
cd GASTOS-IA
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar API Keys (opcional)
Crear archivo `config_api.py`:
```python
NOVITA_API_KEY = "tu-api-key"
GROQ_API_KEY = ""  # Opcional
OPENAI_API_KEY = ""  # Opcional

def is_llm_configured():
    return bool(NOVITA_API_KEY and NOVITA_API_KEY != "tu-api-key-aquí")

def get_configured_api():
    if NOVITA_API_KEY and NOVITA_API_KEY != "tu-api-key-aquí":
        return "novita"
    return None
```

### 4. Ejecutar la aplicación
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5100`

## 🌐 Deploy a Railway

### Opción 1: Deploy Automático
```bash
./railway-config/railway-deploy.sh
```

### Opción 2: Deploy Manual
```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Crear proyecto
railway new

# 4. Configurar variables de entorno
railway variables set PORT=5100
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=tu-secret-key
railway variables set NOVITA_API_KEY=tu-api-key

# 5. Deploy
railway up
```

### Variables de Entorno Necesarias
- `PORT`: Puerto de la aplicación (por defecto: 5100)
- `FLASK_ENV`: Entorno (production/development)
- `SECRET_KEY`: Clave secreta de Flask
- `NOVITA_API_KEY`: API Key de Novita AI (opcional)
- `DATABASE_URL`: URL de la base de datos (por defecto: sqlite:///gastos.db)

Ver más detalles en [railway-config/railway-deploy.md](railway-config/railway-deploy.md)

## 👥 Usuarios por Defecto

- **Admin**: `edurne` / `edurne`
- **User**: `paul` / `paul` (parent_admin: edurne)

## 📂 Estructura del Proyecto

```
GASTOS-IA/
├── app.py                    # Aplicación principal Flask
├── config.py                 # Configuración de la aplicación
├── requirements.txt          # Dependencias Python
├── README.md                 # Este archivo
├── railway.json              # Configuración Railway
├── railway.toml              # Configuración Railway alternativa
├── nixpacks.toml            # Configuración de build
├── templates/               # Plantillas HTML
│   ├── index.html           # Interfaz principal
│   └── login.html           # Página de login
├── static/                  # Archivos estáticos
├── uploads/                 # Imágenes de tickets
├── docs/                    # Documentación
│   ├── GROQ_SETUP.md
│   ├── GUIA_API_SETUP.md
│   └── instalar_tesseract.md
└── railway-config/          # Configuración Railway
    ├── railway-deploy.md
    ├── railway-deploy.sh
    └── railway-variables.env
```

## 🔑 API Endpoints

- `GET /` - Página principal (requiere autenticación)
- `POST /login` - Login de usuario
- `GET /logout` - Logout de usuario
- `GET /api/gastos` - Listar gastos
- `POST /api/gastos` - Crear gasto
- `PUT /api/gastos/:id` - Actualizar gasto
- `DELETE /api/gastos/:id` - Eliminar gasto
- `POST /api/process-image` - Procesar imagen con IA
- `GET /api/conceptos` - Listar conceptos
- `GET /api/motivos` - Listar viajes/grupos

## 🤖 Integración con IA

El sistema utiliza Novita AI con el modelo Qwen2.5-VL-72B para:
- Extraer fechas de tickets
- Identificar importes y monedas
- Reconocer descripciones
- Clasificar conceptos automáticamente

## 📊 Base de Datos

SQLite con las siguientes tablas:
- `users` - Usuarios del sistema con parent_admin
- `gastos` - Gastos registrados
- `conceptos` - Conceptos/categorías personalizados
- `motivos` - Viajes/grupos de gastos
- `viaje_detalles` - Gastos esperados por viaje

## 🛡️ Seguridad

- Autenticación requerida para todas las rutas
- Roles de usuario (admin/user)
- Parent admin configurado para cada usuario
- API Keys en variables de entorno
- Secret key para sesiones Flask

## 📝 Licencia

Este proyecto es privado y está protegido por derechos de autor.

## 👤 Autor

Paul Victor Graitec

## 🆘 Soporte

Para soporte o consultas, contactar al administrador del sistema.