# 💰 Gestor de Gastos Inteligente

Una aplicación web moderna y extremadamente user-friendly para gestionar gastos mediante captura de tickets con OCR automático.

## ✨ Características

- **📸 Captura de Tickets**: Toma fotos directamente o selecciona archivos
- **🤖 OCR Automático**: Extrae automáticamente importe, fecha y tipo de gasto
- **💱 Conversión de Monedas**: Soporte para múltiples monedas con conversión automática
- **🏷️ Categorización Inteligente**: Conceptos predeterminados y motivos personalizables
- **📱 Diseño Responsive**: Funciona perfectamente en móviles y escritorio
- **⚡ Interfaz Intuitiva**: Diseño moderno con UX optimizada para velocidad

## 🚀 Instalación Rápida

### Requisitos Previos

- Python 3.8 o superior
- Tesseract OCR

### Instalación de Tesseract

**Windows:**
1. Descarga Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instala el archivo .exe descargado
3. Asegúrate de que esté en el PATH del sistema

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### Instalación de la Aplicación

1. **Clona o descarga este repositorio**

2. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

3. **Ejecuta la aplicación (Mac):**
```bash
./iniciar_app.sh
```

O manualmente:
```bash
python3 app.py
```

4. **Abre tu navegador en:**
```
http://localhost:5100
```

## 📖 Guía de Uso

### 1. Añadir un Nuevo Gasto

1. **Toca el botón "+" en la parte inferior**
2. **Captura el ticket:**
   - 📷 **Tomar Foto**: Abre la cámara directamente
   - 📁 **Seleccionar Archivo**: Elige una imagen existente
3. **Revisa los datos extraídos:** La aplicación intentará extraer automáticamente:
   - Importe
   - Fecha
   - Tipo de establecimiento
4. **Completa los campos restantes:**
   - **Concepto**: Elige de la lista predeterminada
   - **Descripción**: Añade detalles adicionales
   - **Motivo**: Selecciona o crea un nuevo motivo
5. **Guarda el gasto**

### 2. Gestión de Monedas

- **Euros**: Campo principal para todos los gastos
- **Otra Moneda**: Campo opcional con conversión automática
- **Monedas Soportadas**: USD, GBP, JPY, CHF, CAD, AUD, CNY, MXN, BRL, ARS, COP, CLP, PEN, UYU

### 3. Conceptos y Motivos

**Conceptos Predeterminados:**
- Restaurante
- Transporte
- Alojamiento
- Combustible
- Compras
- Otros

**Motivos Inteligentes:**
- Se crean automáticamente según uses
- Sugerencias basadas en uso frecuente
- Autocompletado inteligente

### 4. Edición y Eliminación

- **Editar**: Toca el icono ✏️ en cualquier gasto
- **Eliminar**: Toca el icono 🗑️ con confirmación
- **Ver Imagen**: Toca la imagen en miniatura para ampliarla

## 🔧 Características Técnicas

### Backend (Python/Flask)
- **Flask**: Framework web ligero
- **SQLite**: Base de datos integrada
- **Pillow**: Procesamiento de imágenes
- **OpenCV**: Mejoras de imagen para OCR
- **Tesseract**: Reconocimiento óptico de caracteres

### Frontend (HTML/CSS/JavaScript)
- **Diseño Responsive**: CSS Grid y Flexbox
- **Progressive Web App**: Funciona offline
- **Interfaz Moderna**: Gradientes, sombras, transiciones
- **UX Optimizada**: Autocompletado, sugerencias inteligentes

### Funcionalidades Avanzadas
- **Procesamiento de Imágenes**: Compresión automática manteniendo legibilidad
- **OCR Multiidioma**: Español e inglés
- **Conversión de Monedas**: Tasas predeterminadas actualizables
- **Gestión de Estado**: Sincronización automática frontend-backend

## 📁 Estructura del Proyecto

```
GASTOS IA/
├── app.py                 # Servidor Flask principal
├── requirements.txt       # Dependencias Python
├── README.md             # Documentación
├── gastos.db             # Base de datos SQLite (se crea automáticamente)
├── templates/
│   └── index.html        # Interfaz de usuario
└── uploads/              # Imágenes de tickets (se crea automáticamente)
```

## 🛠️ Configuración Avanzada

### Tasas de Cambio
Las tasas de cambio están predefinidas en `app.py`. Para actualizarlas:

```python
EXCHANGE_RATES = {
    'USD': 1.09,  # Actualizar según tasas actuales
    'GBP': 0.87,
    # ... más monedas
}
```

### Conceptos Personalizados
Modifica los conceptos predeterminados en `app.py`:

```python
DEFAULT_CONCEPTS = [
    'Restaurante',
    'Transporte',
    'TuConceptoPersonalizado',
    # ... más conceptos
]
```

### Configuración de OCR
Para mejorar la precisión del OCR, puedes ajustar los parámetros en la función `process_image()`.

## 🚨 Solución de Problemas

### Error de Tesseract
```
TesseractNotFoundError: tesseract is not installed
```
**Solución**: Instala Tesseract OCR según las instrucciones de tu sistema operativo.

### Error de Puertos
```
Port 5000 is already in use
```
**Solución**: Cambia el puerto en `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Error de Permisos de Cámara
**Solución**: Asegúrate de permitir acceso a la cámara en tu navegador.

## 💡 Consejos de Uso

1. **Iluminación**: Toma fotos con buena iluminación para mejor OCR
2. **Calidad**: Mantén el ticket plano y enfocado
3. **Motivos**: Reutiliza motivos para mantener consistencia
4. **Backup**: La base de datos `gastos.db` contiene todos tus datos

## 🔄 Actualizaciones Futuras

- [ ] Integración con APIs de tasas de cambio en tiempo real
- [ ] Exportación a Excel/PDF
- [ ] Gráficos y estadísticas
- [ ] Sincronización en la nube
- [ ] Aplicación móvil nativa

## 🐛 Reportar Problemas

Si encuentras algún problema o tienes sugerencias, puedes:
1. Revisar la sección de solución de problemas
2. Verificar que todas las dependencias estén instaladas correctamente
3. Comprobar los logs de la aplicación

## 📄 Licencia

Este proyecto está bajo licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente.

---

**¡Disfruta gestionando tus gastos de forma inteligente! 💰✨** 