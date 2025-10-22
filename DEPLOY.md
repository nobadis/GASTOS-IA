# 🚀 Guía Rápida de Deploy a Railway

## Pre-requisitos
- Cuenta en [Railway.app](https://railway.app)
- Railway CLI instalado (opcional)

## Opción 1: Deploy desde GitHub (Recomendado)

### 1. Conectar Railway con GitHub
1. Ve a [railway.app/new](https://railway.app/new)
2. Selecciona "Deploy from GitHub repo"
3. Autoriza Railway para acceder a tus repos
4. Selecciona el repositorio `GASTOS-IA`

### 2. Configurar Variables de Entorno
En el dashboard de Railway, agrega estas variables:

```env
PORT=5100
FLASK_ENV=production
SECRET_KEY=gastos_app_secret_key_2025_railway
DATABASE_URL=sqlite:///gastos.db
UPLOAD_FOLDER=uploads

# Opcional - Para extracción IA
NOVITA_API_KEY=tu-api-key-real
```

### 3. Deploy Automático
Railway detectará automáticamente los archivos de configuración y hará el deploy.

## Opción 2: Deploy con Railway CLI

### 1. Instalar Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login
```bash
railway login
```

### 3. Inicializar Proyecto
```bash
railway init
```

### 4. Configurar Variables
```bash
railway variables set PORT=5100
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=gastos_app_secret_key_2025_railway
railway variables set NOVITA_API_KEY=tu-api-key
```

### 5. Deploy
```bash
railway up
```

## Verificación del Deploy

### 1. Ver Logs
```bash
railway logs
```

### 2. Verificar Base de Datos
Los logs deberían mostrar:
```
✅ Tabla de usuarios creada y usuarios por defecto insertados
```

### 3. Obtener URL
```bash
railway domain
```

## Usuarios de Prueba

Una vez deployado, puedes acceder con:
- **Admin**: `edurne` / `edurne`
- **User**: `paul` / `paul`

## Persistencia de Datos

Railway mantendrá:
- ✅ Base de datos SQLite
- ✅ Imágenes en `/uploads`
- ✅ Configuración de usuarios

## Solución de Problemas

### Error: "No such table"
La base de datos se crea automáticamente al iniciar. Si ves este error, verifica los logs de inicialización.

### Error: "Address already in use"
Railway asigna el puerto automáticamente. Asegúrate de usar `PORT` desde variables de entorno.

### Error: "API Key not found"
Verifica que `NOVITA_API_KEY` esté configurado correctamente en las variables de entorno.

## Comandos Útiles

```bash
# Ver estado
railway status

# Ver variables
railway variables

# Ver logs en tiempo real
railway logs --follow

# Conectar a la base de datos
railway connect

# Reiniciar servicio
railway restart
```

## Actualizar Deploy

Railway hace deploy automático con cada push a GitHub. Alternativamente:

```bash
git push origin main  # Deploy automático
# o
railway up            # Deploy manual
```

## Configuración Avanzada

### Custom Domain
En el dashboard de Railway:
1. Ve a Settings > Domains
2. Agrega tu dominio personalizado
3. Configura los DNS según las instrucciones

### Escalado
Railway escala automáticamente según el uso. Para configuración avanzada, ve a Settings > Resources.

## Soporte

Para más información, consulta:
- [Documentación Railway](https://docs.railway.app)
- [railway-config/railway-deploy.md](railway-config/railway-deploy.md)
- [README.md](README.md)
