# Deploy a Railway - GASTOS IA

## Pasos para deployar a Railway

### 1. Preparación del proyecto
- ✅ Tabla de usuarios creada con parent_admin
- ✅ Configuración de variables de entorno
- ✅ Archivos de configuración de Railway creados

### 2. Configuración en Railway

#### 2.1 Crear proyecto en Railway
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login en Railway
railway login

# Crear nuevo proyecto
railway new

# Conectar al proyecto
railway link
```

#### 2.2 Configurar variables de entorno
En el dashboard de Railway, configurar las siguientes variables:

```env
PORT=5100
FLASK_ENV=production
DATABASE_URL=sqlite:///gastos.db
SECRET_KEY=gastos_app_secret_key_2025_railway
UPLOAD_FOLDER=uploads
NOVITA_API_KEY=tu-api-key-real
GROQ_API_KEY=tu-api-key-real
OPENAI_API_KEY=tu-api-key-real
```

#### 2.3 Deploy
```bash
# Deploy a Railway
railway up
```

### 3. Estructura de usuarios

#### Usuarios por defecto:
- **edurne** (admin) - Sin parent_admin
- **paul** (user) - Parent admin: edurne

#### Tabla users:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    parent_admin TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Características del deploy

#### 4.1 Base de datos
- SQLite persistente en Railway
- Migraciones automáticas al iniciar
- Usuarios con parent_admin configurado

#### 4.2 Archivos estáticos
- Directorio uploads/ para imágenes
- Persistencia de archivos en Railway

#### 4.3 API Keys
- Configuración desde variables de entorno
- Soporte para Novita AI, Groq y OpenAI

### 5. Monitoreo y logs

#### 5.1 Logs en Railway
```bash
# Ver logs en tiempo real
railway logs

# Ver logs específicos
railway logs --service web
```

#### 5.2 Health check
- Endpoint: `/`
- Timeout: 100 segundos
- Restart policy: ON_FAILURE

### 6. Comandos útiles

```bash
# Ver estado del proyecto
railway status

# Ver variables de entorno
railway variables

# Conectar a la base de datos
railway connect

# Ver logs
railway logs

# Deploy
railway up
```

### 7. Troubleshooting

#### 7.1 Problemas comunes
- Verificar variables de entorno
- Revisar logs de Railway
- Verificar conectividad de base de datos

#### 7.2 Logs importantes
- Inicialización de base de datos
- Creación de usuarios
- Configuración de API keys
- Errores de autenticación

### 8. Seguridad

#### 8.1 Variables sensibles
- API keys en variables de entorno
- Secret key configurado
- Passwords en base de datos

#### 8.2 Acceso
- Autenticación requerida
- Roles de usuario y admin
- Parent admin configurado
