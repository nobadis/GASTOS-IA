# -*- coding: utf-8 -*-
"""
Configuración del Gestor de Gastos Inteligente
Puedes modificar estos valores según tus necesidades
"""

# Configuración del servidor
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000
DEBUG_MODE = True

# Configuración de archivos
UPLOAD_FOLDER = 'uploads'
DATABASE_FILE = 'gastos.db'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Configuración de imágenes
MAX_IMAGE_SIZE = (1200, 1200)  # (ancho, alto) en píxeles
IMAGE_QUALITY = 85  # Calidad JPEG (1-100)

# Tasas de conversión de monedas (EUR como base)
# Actualiza estos valores según las tasas actuales
EXCHANGE_RATES = {
    'USD': 1.09,      # Dólar Estadounidense
    'GBP': 0.87,      # Libra Esterlina
    'JPY': 161.50,    # Yen Japonés
    'CHF': 0.97,      # Franco Suizo
    'CAD': 1.49,      # Dólar Canadiense
    'AUD': 1.65,      # Dólar Australiano
    'NZD': 1.75,      # Dólar Neozelandés
    'HKD': 8.55,      # Dólar de Hong Kong
    'SGD': 1.45,      # Dólar de Singapur
    'CNY': 7.85,      # Yuan Chino
    'MYR': 4.85,      # Ringgit de Malasia
    'AED': 4.00,      # Dirham de Emiratos Árabes Unidos
    'BRL': 5.48,      # Real Brasileño
    'ARS': 350.00,    # Peso Argentino
    'MXN': 18.65,     # Peso Mexicano
    'COP': 4200.00,   # Peso Colombiano
    'CLP': 950.00,    # Peso Chileno
    'PEN': 3.75,      # Sol Peruano
    'UYU': 38.50,     # Peso Uruguayo
}

# Conceptos predeterminados
# Puedes añadir, quitar o modificar estos conceptos
DEFAULT_CONCEPTS = [
    'Restaurante',
    'Transporte',
    'Alojamiento',
    'Combustible',
    'Compras',
    'Entretenimiento',
    'Salud',
    'Educación',
    'Tecnología',
    'Otros'
]

# Configuración de OCR
OCR_LANGUAGES = 'spa+eng'  # Idiomas para Tesseract (español + inglés)
OCR_CONFIG = '--psm 6'      # Configuración de Tesseract

# Patrones de reconocimiento para diferentes tipos de tickets
ESTABLISHMENT_KEYWORDS = {
    'Restaurante': [
        'restaurante', 'bar', 'cafe', 'cafeteria', 'taberna', 'tapas', 
        'comida', 'menú', 'cena', 'almuerzo', 'desayuno', 'pizzeria',
        'hamburgueseria', 'marisqueria', 'asador', 'braseria'
    ],
    'Transporte': [
        'taxi', 'uber', 'cabify', 'metro', 'bus', 'tren', 'avión', 
        'vuelo', 'parking', 'aparcamiento', 'peaje', 'gasolina',
        'diesel', 'combustible', 'renfe', 'aena'
    ],
    'Alojamiento': [
        'hotel', 'hostal', 'apartamento', 'alojamiento', 'booking',
        'pension', 'resort', 'motel', 'b&b', 'airbnb'
    ],
    'Combustible': [
        'gasolina', 'diesel', 'combustible', 'repsol', 'cepsa', 
        'bp', 'shell', 'galp', 'petronor', 'carrefour'
    ],
    'Compras': [
        'supermercado', 'tienda', 'shop', 'centro comercial', 'farmacia',
        'mercadona', 'carrefour', 'dia', 'lidl', 'alcampo', 'corte inglés',
        'decathlon', 'ikea', 'mediamarkt'
    ],
    'Entretenimiento': [
        'cine', 'teatro', 'concierto', 'museo', 'parque', 'discoteca',
        'bar nocturno', 'bowling', 'casino', 'espectáculo'
    ],
    'Salud': [
        'farmacia', 'hospital', 'clinica', 'médico', 'dentista',
        'veterinario', 'óptica', 'fisioterapeuta'
    ],
    'Educación': [
        'universidad', 'colegio', 'instituto', 'academia', 'curso',
        'libro', 'material escolar', 'matrícula'
    ],
    'Tecnología': [
        'mediamarkt', 'fnac', 'apple', 'samsung', 'ordenador',
        'móvil', 'tablet', 'software', 'app store', 'google play'
    ]
}

# Configuración de patrones de reconocimiento de importes
AMOUNT_PATTERNS = [
    r'total[:\s]*€?(\d+[.,]\d{2})',
    r'importe[:\s]*€?(\d+[.,]\d{2})',
    r'€\s*(\d+[.,]\d{2})',
    r'(\d+[.,]\d{2})\s*€',
    r'(\d+[.,]\d{2})\s*eur',
    r'total[:\s]*(\d+[.,]\d{2})',
    r'suma[:\s]*€?(\d+[.,]\d{2})',
    r'cobrado[:\s]*€?(\d+[.,]\d{2})'
]

# Configuración de patrones de reconocimiento de fechas
DATE_PATTERNS = [
    r'(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})',
    r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
    r'(\d{1,2}\s+\w+\s+\d{4})',
    r'(\d{4}[/.-]\d{1,2}[/.-]\d{1,2})'
]

# Configuración de la interfaz
UI_THEME = {
    'primary_color': '#667eea',
    'secondary_color': '#764ba2',
    'success_color': '#28a745',
    'error_color': '#dc3545',
    'warning_color': '#ffc107',
    'info_color': '#17a2b8'
}

# Configuración de notificaciones
NOTIFICATION_DURATION = 3000  # Duración en milisegundos
SHOW_SUCCESS_NOTIFICATIONS = True
SHOW_ERROR_NOTIFICATIONS = True

# Configuración de respaldo automático
AUTO_BACKUP = True
BACKUP_INTERVAL_DAYS = 7
BACKUP_FOLDER = 'backups'

# Configuración de seguridad
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB

# Configuración de logs
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'gastos.log'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5 