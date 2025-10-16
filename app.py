from flask import Flask, request, jsonify, render_template, send_from_directory, make_response, session, redirect, url_for, flash
from flask_cors import CORS
import sqlite3
import os
import base64
from PIL import Image
import pytesseract
import cv2
import numpy as np
import re
from datetime import datetime
import json
from io import BytesIO
import openai
from groq import Groq
from config import EXCHANGE_RATES as CONFIG_EXCHANGE_RATES  # Importar tasas desde config
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import pandas as pd
import tempfile
import zipfile
import shutil
from functools import wraps

app = Flask(__name__)
CORS(app)
app.secret_key = 'gastos_app_secret_key_2025'  # Clave secreta para sesiones

# Configuración
UPLOAD_FOLDER = 'uploads'
DATABASE = 'gastos.db'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Sistema de usuarios
USERS = {
    'paul': {'password': 'paul', 'role': 'user', 'name': 'Paul'},
    'edurne': {'password': 'edurne', 'role': 'admin', 'name': 'Edurne'}
}

def authenticate_user(username, password):
    """Verifica credenciales de usuario"""
    if username in USERS and USERS[username]['password'] == password:
        return USERS[username]
    return None

def is_admin():
    """Verifica si el usuario actual es admin"""
    return session.get('role') == 'admin'

def get_current_user():
    """Obtiene el usuario actual de la sesión"""
    return session.get('username')

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            if request.is_json:
                return jsonify({'error': 'Autenticación requerida'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para rutas que requieren rol admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            if request.is_json:
                return jsonify({'error': 'Autenticación requerida'}), 401
            return redirect(url_for('login'))
        if not is_admin():
            if request.is_json:
                return jsonify({'error': 'Acceso denegado - se requiere rol admin'}), 403
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Configuración LLM desde archivo externo
try:
    from config_api import NOVITA_API_KEY, GROQ_API_KEY, OPENAI_API_KEY, is_llm_configured, get_configured_api
    print(f"🔑 API Keys cargadas - Novita: {'✅' if NOVITA_API_KEY and NOVITA_API_KEY != 'tu-api-key-aquí' else '❌'}")
    print(f"🔑 LLM configurado: {'✅' if is_llm_configured() else '❌'}")
except ImportError:
    print("📝 Para usar extracción automática con LLM, configura las API keys en config_api.py")
    NOVITA_API_KEY = None
    GROQ_API_KEY = None
    OPENAI_API_KEY = None
    def is_llm_configured(): return False
    def get_configured_api(): return None

# Inicializar clientes LLM
try:
    # Cliente Novita AI (Llama 3.3 70B) - Usar requests directamente
    if NOVITA_API_KEY and NOVITA_API_KEY != "tu-api-key-aquí":
        novita_client = "requests_direct"  # Marcador para usar requests
        print("✅ Cliente Novita configurado (usando requests directamente)")
    else:
        novita_client = None
    
    # Solo Novita por ahora
    groq_client = None
    openai.api_key = None
        
    print(f"🤖 Clientes finales - Novita: {'✅' if novita_client else '❌'}, Groq: {'✅' if groq_client else '❌'}, OpenAI: {'✅' if openai.api_key else '❌'}")
except Exception as e:
    print(f"❌ Error general inicializando clientes LLM: {e}")
    novita_client = None
    groq_client = None
    openai.api_key = None

# Usar tasas de conversión desde config.py (EUR como base)
EXCHANGE_RATES = CONFIG_EXCHANGE_RATES

def convert_to_eur(amount, from_currency):
    """Convertir cualquier moneda a EUR"""
    if not amount or amount == 0:
        return 0
    
    if from_currency == 'EUR' or not from_currency:
        return float(amount)
    
    # Obtener tasa de cambio
    from_rate = EXCHANGE_RATES.get(from_currency, 1)
    
    # Convertir a EUR
    eur_amount = float(amount) / from_rate
    
    print(f"🔄 Conversión automática: {amount} {from_currency} → {eur_amount:.2f} EUR (tasa: {from_rate})")
    
    return round(eur_amount, 2)

# Conceptos predeterminados
DEFAULT_CONCEPTS = [
    'Restaurante',
    'Transporte',
    'Alojamiento',
    'Combustible',
    'Compras',
    'Otros'
]

def init_db():
    """Inicializar la base de datos"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabla de gastos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            concepto TEXT NOT NULL,
            motivo TEXT,
            descripcion TEXT,
            importe_eur REAL NOT NULL,
            importe_otra_moneda REAL,
            moneda_otra TEXT,
            imagen_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de conceptos personalizados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conceptos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Tabla de motivos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS motivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            usado_veces INTEGER DEFAULT 0,
            ultimo_uso TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Insertar conceptos predeterminados
    for concept in DEFAULT_CONCEPTS:
        cursor.execute('INSERT OR IGNORE INTO conceptos (nombre) VALUES (?)', (concept,))
    
    # Migración: Agregar campo checkeado si no existe
    try:
        cursor.execute('ALTER TABLE gastos ADD COLUMN checkeado BOOLEAN DEFAULT FALSE')
        print("✅ Migración: Campo 'checkeado' añadido a la tabla gastos")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass  # La columna ya existe
        else:
            raise
    
    # Migración: Agregar campo usuario si no existe
    try:
        cursor.execute('ALTER TABLE gastos ADD COLUMN usuario TEXT DEFAULT "paul"')
        print("✅ Migración: Campo 'usuario' añadido a la tabla gastos")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass  # La columna ya existe
        else:
            raise
    
    # Tabla de detalles de viajes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS viaje_detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            motivo TEXT NOT NULL,
            importe_eur REAL NOT NULL,
            importe_original REAL NOT NULL,
            moneda_original TEXT NOT NULL DEFAULT 'EUR',
            cuadrado BOOLEAN DEFAULT FALSE,
            gasto_id INTEGER,
            usuario TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gasto_id) REFERENCES gastos (id)
        )
    ''')
    
    # Migración: Agregar campos de moneda a viaje_detalles si no existen
    try:
        cursor.execute('ALTER TABLE viaje_detalles ADD COLUMN importe_original REAL')
        cursor.execute('ALTER TABLE viaje_detalles ADD COLUMN moneda_original TEXT DEFAULT "EUR"')
        # Actualizar registros existentes
        cursor.execute('UPDATE viaje_detalles SET importe_original = importe_eur, moneda_original = "EUR" WHERE importe_original IS NULL')
        print("✅ Migración: Campos de moneda añadidos a viaje_detalles")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass  # Las columnas ya existen
        else:
            raise
    
    # Migración: Agregar campo detalle_cuadrado si no existe
    try:
        cursor.execute('ALTER TABLE gastos ADD COLUMN detalle_cuadrado BOOLEAN DEFAULT FALSE')
        print("✅ Migración: Campo 'detalle_cuadrado' añadido a la tabla gastos")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass  # La columna ya existe
        else:
            raise
    
    # Migración: Agregar campo activo a motivos si no existe
    try:
        cursor.execute('ALTER TABLE motivos ADD COLUMN activo BOOLEAN DEFAULT TRUE')
        print("✅ Migración: Campo 'activo' añadido a la tabla motivos")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass  # La columna ya existe
        else:
            raise
    
    conn.commit()
    conn.close()

def process_image(image_data):
    """Procesar imagen: comprimir y extraer texto"""
    try:
        # Decodificar imagen base64
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(BytesIO(image_bytes))
        
        # Comprimir imagen manteniendo legibilidad
        if image.mode in ('RGBA', 'LA'):
            image = image.convert('RGB')
        
        # Redimensionar si es muy grande
        max_size = (1200, 1200)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Guardar imagen comprimida
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ticket_{timestamp}.jpg'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image.save(filepath, 'JPEG', quality=85, optimize=True)
        
        # Extraer texto con OCR
        text = ""
        try:
            # Convertir a array numpy para OpenCV
            img_array = np.array(image)
            
            # Mejorar contraste para OCR
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Extraer texto
            text = pytesseract.image_to_string(enhanced, lang='spa+eng')
            
        except Exception as e:
            print(f"Error en OCR: {e}")
            text = ""
        
        # Usar LLM para mejorar extracción si está disponible
        if is_llm_configured():
            try:
                extracted_info = extract_with_llm(image_data, text)
                api_type = get_configured_api()
                if api_type == "novita":
                    print("✅ Extracción con Llama 3.3 70B (Novita AI) completada")
                elif api_type == "groq":
                    print("✅ Extracción con GROQ completada")
                elif api_type == "openai":
                    print("✅ Extracción con OpenAI completada")
                else:
                    print("✅ Extracción con LLM completada")
            except Exception as e:
                print(f"❌ Error en LLM: {e}")
                extracted_info = extract_ticket_info(text)
        else:
            if not text or len(text.strip()) < 5:
                print("⚠️  Sin OCR ni LLM disponibles - extracción muy limitada")
                print("💡 SOLUCIÓN RÁPIDA: Configura Llama 3.3 70B (súper económico) o GROQ (gratis) en config_api.py")
            else:
                print("ℹ️  Usando extracción básica (OCR solamente). Para mejor precisión, configura API keys en config_api.py")
            extracted_info = extract_ticket_info(text)
            
        # Mostrar información extraída en el log
        if extracted_info:
            print(f"📊 Información extraída: {extracted_info}")
        else:
            print("❌ No se pudo extraer información del ticket")
        
        return {
            'filename': filename,
            'text': text,
            'extracted_info': extracted_info
        }
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        return None

def extract_ticket_info(text):
    """Extraer información relevante del texto del ticket"""
    info = {}
    
    # Si no hay texto, intentar algunas extracciones básicas por defecto
    if not text or len(text.strip()) < 5:
        print("⚠️  Sin texto OCR disponible - usando fecha actual y conceptos por defecto")
        from datetime import datetime
        info['date'] = datetime.now().strftime('%Y-%m-%d')
        info['concept'] = 'Otros'
        return info
    
    # Buscar importes (patrones más amplios)
    amount_patterns = [
        r'total[:\s]*€?\s*(\d+[.,]\d{2})',
        r'importe[:\s]*€?\s*(\d+[.,]\d{2})',
        r'suma[:\s]*€?\s*(\d+[.,]\d{2})',
        r'€\s*(\d+[.,]\d{2})',
        r'(\d+[.,]\d{2})\s*€',
        r'(\d+[.,]\d{2})\s*eur',
        r'(\d+[.,]\d{2})\s*euros?',
        r'total[:\s]*(\d+[.,]\d{2})',
        r'(\d{1,3}[.,]\d{2})',  # Cualquier número con 2 decimales
    ]
    
    amounts_found = []
    for pattern in amount_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                amount = float(match.replace(',', '.'))
                if 0.01 <= amount <= 9999.99:  # Rango razonable
                    amounts_found.append(amount)
            except:
                continue
    
    if amounts_found:
        # Usar el mayor importe encontrado (usualmente el total)
        info['amount'] = max(amounts_found)
    
    # Buscar fechas (patrones más amplios)
    date_patterns = [
        r'(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})',
        r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
        r'(\d{1,2}\s+\w+\s+\d{4})',
        r'(\d{4}[/.-]\d{1,2}[/.-]\d{1,2})',
        r'(\d{2}[/.-]\d{2}[/.-]\d{4})'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                date_str = matches[0]
                # Intentar parsear la fecha
                from datetime import datetime
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y/%m/%d', '%Y-%m-%d']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        info['date'] = parsed_date.strftime('%Y-%m-%d')
                        break
                    except:
                        continue
                if 'date' in info:
                    break
            except:
                continue
    
    # Extraer posible descripción (líneas que contienen nombres de establecimiento)
    lines = text.split('\n')
    establishment_names = []
    
    for line in lines:
        line = line.strip()
        if len(line) > 3 and len(line) < 50:  # Longitud razonable para nombre
            # Evitar líneas que son solo números o fechas
            if not re.match(r'^[\d\s/.-]+$', line):
                establishment_names.append(line)
    
    if establishment_names:
        info['description'] = establishment_names[0]  # Primera línea relevante
    
    # Identificar tipo de establecimiento (patrones expandidos)
    establishment_keywords = {
        'Restaurante': [
            'restaurante', 'bar', 'cafe', 'cafeteria', 'taberna', 'tapas', 'comida', 'menú',
            'pizzeria', 'hamburgueseria', 'marisqueria', 'asador', 'braseria', 'cerveceria',
            'tasca', 'bistro', 'gastrobar', 'parrilla', 'cocina', 'burger', 'pizza'
        ],
        'Transporte': [
            'taxi', 'uber', 'cabify', 'metro', 'bus', 'tren', 'avión', 'vuelo', 'parking',
            'aparcamiento', 'peaje', 'renfe', 'aena', 'aeropuerto', 'estacion', 'transport'
        ],
        'Alojamiento': [
            'hotel', 'hostal', 'apartamento', 'alojamiento', 'booking', 'pension', 'resort',
            'motel', 'airbnb', 'hospedaje', 'lodge', 'inn'
        ],
        'Combustible': [
            'gasolina', 'diesel', 'combustible', 'repsol', 'cepsa', 'bp', 'shell', 'galp',
            'petronor', 'esso', 'fuel', 'gas', 'carburante'
        ],
        'Compras': [
            'supermercado', 'tienda', 'shop', 'centro comercial', 'farmacia', 'mercadona',
            'carrefour', 'dia', 'lidl', 'alcampo', 'corte inglés', 'market', 'store'
        ],
        'Entretenimiento': [
            'cine', 'teatro', 'concierto', 'museo', 'parque', 'discoteca', 'pub', 'club'
        ],
        'Salud': [
            'farmacia', 'hospital', 'clinica', 'médico', 'dentista', 'veterinario', 'óptica'
        ],
        'Tecnología': [
            'mediamarkt', 'fnac', 'apple', 'samsung', 'phone house', 'tech', 'electronics'
        ]
    }
    
    text_lower = text.lower()
    concept_scores = {}
    
    for concept, keywords in establishment_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
        if score > 0:
            concept_scores[concept] = score
    
    if concept_scores:
        # Elegir el concepto con mayor puntuación
        info['concept'] = max(concept_scores, key=concept_scores.get)
    
    return info

def extract_with_llm(image_data, ocr_text=""):
    """Extraer información usando Novita AI con modelo multimodal"""
    try:
        # Solo usar Novita AI
        if not novita_client:
            print("❌ Cliente Novita no disponible")
            return extract_ticket_info(ocr_text)
        
        # Preparar prompt específico para análisis de tickets
        prompt = """Analysez ce ticket d'achat et extrayez les informations exactes qui y apparaissent.

ÉTAPES À SUIVRE:
1. Identifiez le TOTAL à payer (le montant final le plus important, pas les sous-totaux)
2. Recherchez la DATE de la transaction (peut être au format DD/MM/YYYY, DD-MM-YYYY ou similaire)
3. Trouvez le NOM de l'établissement ou commerce
4. Classifiez le TYPE d'établissement

EXTRAYEZ ces champs:
- "amount": Seulement le nombre du total à payer (exemple: 15.50, 120.00)
- "currency": Code de 3 lettres de la devise (EUR, USD, GBP, JPY, etc.) - Si pas clair, utiliser "EUR"
- "date": Date au format YYYY-MM-DD (convertir DD/MM/YYYY en YYYY-MM-DD)
- "description": Nom exact de l'établissement qui apparaît sur le ticket
- "concept": Une de ces catégories exactes: Restaurante, Transporte, Alojamiento, Combustible, Supermercado, Farmacia, Tecnología, Ropa, Entretenimiento, Otros

EXEMPLES de conversion de date:
- 15/03/2024 → 2024-03-15
- 7/12/2023 → 2023-12-07

DÉTECTION DE DEVISE:
- Cherchez les symboles: €, $, £, ¥, CHF, CAD, etc.
- Cherchez le texte: "EUR", "USD", "GBP", "JPY", "CHF", etc.
- Si symbole € ou dit "EUR" → "EUR"
- Si symbole $ ou dit "USD" → "USD"
- Si symbole £ ou dit "GBP" → "GBP"
- Si symbole ¥ ou dit "JPY" → "JPY"
- Si pas clair, utiliser "EUR"

IMPORTANT: 
- Si vous ne voyez pas clairement une donnée, utilisez null
- Extrayez uniquement les informations qui apparaissent réellement sur le ticket
- Répondez UNIQUEMENT avec du JSON valide

Format de réponse:
{
    "amount": 15.50,
    "currency": "EUR",
    "date": "2024-03-15",
    "description": "Restaurante El Rincón",
    "concept": "Restaurante"
}"""
        
        try:
            # Usar requests directamente
            import requests
            
            url = "https://api.novita.ai/v3/openai/chat/completions"
            headers = {
                "Authorization": f"Bearer {NOVITA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Extraer solo la parte base64 de la imagen
            base64_image = image_data.split(',')[1] if ',' in image_data else image_data
            
            # Preparar mensaje con imagen usando modelo multimodal
            messages = [
                {"role": "system", "content": "Vous êtes un expert en analyse de tickets d'achat. Vous répondez uniquement avec du JSON valide."},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ]
            
            data = {
                "model": "qwen/qwen2.5-vl-72b-instruct",  # Modelo multimodal disponible en Novita AI
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                result_text = result['choices'][0]['message']['content'].strip()
                print(f"✅ Extracción con Qwen2.5-VL-72B (Novita AI) completada")
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return extract_ticket_info(ocr_text)
            
            # Parsear JSON
            try:
                # Limpiar respuesta si tiene texto adicional
                if '```json' in result_text:
                    result_text = result_text.split('```json')[1].split('```')[0]
                elif '```' in result_text:
                    result_text = result_text.split('```')[1].split('```')[0]
                
                extracted_data = json.loads(result_text)
                
                # Validar y convertir datos
                info = {}
                
                # Procesar amount
                if 'amount' in extracted_data and extracted_data['amount'] is not None:
                    try:
                        amount_val = float(extracted_data['amount'])
                        if amount_val > 0:  # Solo usar valores positivos
                            info['amount'] = amount_val
                    except (ValueError, TypeError):
                        print(f"⚠️ No se pudo convertir amount: {extracted_data['amount']}")
                
                # Procesar currency
                if 'currency' in extracted_data and extracted_data['currency'] is not None:
                    currency_val = str(extracted_data['currency']).strip().upper()
                    if currency_val and currency_val != 'NULL':
                        info['currency'] = currency_val
                
                # Procesar date
                if 'date' in extracted_data and extracted_data['date'] is not None:
                    date_val = str(extracted_data['date']).strip()
                    if date_val and date_val != 'null' and len(date_val) >= 8:
                        info['date'] = date_val
                
                # Procesar description
                if 'description' in extracted_data and extracted_data['description'] is not None:
                    desc_val = str(extracted_data['description']).strip()
                    if desc_val and desc_val != 'null' and desc_val != 'No disponible':
                        info['description'] = desc_val
                
                # Procesar concept
                if 'concept' in extracted_data and extracted_data['concept'] is not None:
                    concept_val = str(extracted_data['concept']).strip()
                    if concept_val and concept_val != 'null' and concept_val != 'Otros':
                        info['concept'] = concept_val
                
                print(f"📊 Información extraída por LLM: {info}")
                return info
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON del LLM: {e}")
                print(f"📝 Respuesta recibida: {result_text}")
                return extract_ticket_info(ocr_text)
                
        except Exception as e:
            print(f"❌ Error con Novita AI: {e}")
            return extract_ticket_info(ocr_text)
            
    except Exception as e:
        print(f"❌ Error general en extract_with_llm: {e}")
        return extract_ticket_info(ocr_text)

@app.route('/')
@login_required
def index():
    """Página principal"""
    return render_template('index.html', current_user=session.get('username'), is_admin=is_admin())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = authenticate_user(username, password)
        if user:
            session['username'] = username
            session['role'] = user['role']
            session['name'] = user['name']
            flash(f'Bienvenido, {user["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/api/current-user')
@login_required
def get_current_user_info():
    """Obtener información del usuario actual"""
    return jsonify({
        'username': session.get('username'),
        'name': session.get('name'),
        'role': session.get('role'),
        'is_admin': is_admin()
    })

@app.route('/api/users')
@admin_required
def get_users():
    """Obtener lista de usuarios (solo para admin)"""
    users_list = []
    for username, user_data in USERS.items():
        users_list.append({
            'username': username,
            'name': user_data['name'],
            'role': user_data['role']
        })
    return jsonify(users_list)

@app.route('/api/gastos', methods=['GET'])
@login_required
def get_gastos():
    """Obtener gastos según el rol del usuario"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Obtener parámetros de filtro
    filter_user = request.args.get('user')  # Para admin filtrar por usuario específico
    
    if is_admin():
        # Admin puede ver todos los gastos o filtrar por usuario
        if filter_user:
            cursor.execute('''
                SELECT id, fecha, concepto, motivo, descripcion, importe_eur, 
                       importe_otra_moneda, moneda_otra, imagen_path, checkeado, usuario, detalle_cuadrado
                FROM gastos WHERE usuario = ? ORDER BY fecha DESC, created_at DESC
            ''', (filter_user,))
        else:
            cursor.execute('''
                SELECT id, fecha, concepto, motivo, descripcion, importe_eur, 
                       importe_otra_moneda, moneda_otra, imagen_path, checkeado, usuario, detalle_cuadrado
                FROM gastos ORDER BY fecha DESC, created_at DESC
            ''')
    else:
        # Usuario normal solo ve sus propios gastos
        cursor.execute('''
            SELECT id, fecha, concepto, motivo, descripcion, importe_eur, 
                   importe_otra_moneda, moneda_otra, imagen_path, checkeado, usuario, detalle_cuadrado
            FROM gastos WHERE usuario = ? ORDER BY fecha DESC, created_at DESC
        ''', (get_current_user(),))
    
    gastos = cursor.fetchall()
    conn.close()
    
    gastos_list = []
    for gasto in gastos:
        gastos_list.append({
            'id': gasto[0],
            'fecha': gasto[1],
            'concepto': gasto[2],
            'motivo': gasto[3],
            'descripcion': gasto[4],
            'importe_eur': gasto[5],
            'importe_otra_moneda': gasto[6],
            'moneda_otra': gasto[7],
            'imagen_path': gasto[8],
            'checkeado': bool(gasto[9]),
            'usuario': gasto[10],
            'detalle_cuadrado': bool(gasto[11]) if len(gasto) > 11 else False
        })
    
    return jsonify(gastos_list)

@app.route('/api/process-image', methods=['POST'])
def process_image_only():
    """Procesar imagen sin guardar gasto - solo extraer información"""
    try:
        data = request.get_json()
        
        if 'image' not in data or not data['image']:
            return jsonify({'success': False, 'error': 'No se proporcionó imagen'})
        
        # Procesar imagen
        image_result = process_image(data['image'])
        
        if image_result:
            return jsonify({
                'success': True,
                'filename': image_result['filename'],
                'extracted_info': image_result['extracted_info'],
                'text': image_result['text']
            })
        else:
            return jsonify({'success': False, 'error': 'Error procesando imagen'})
            
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gastos', methods=['POST'])
@login_required
def add_gasto():
    """Añadir nuevo gasto"""
    try:
        data = request.get_json()
        
        # Manejar imagen (ya procesada o nueva)
        image_filename = None
        extracted_info = {}
        
        if 'processed_image_filename' in data and data['processed_image_filename']:
            # Usar imagen ya procesada
            image_filename = data['processed_image_filename']
        elif 'image' in data and data['image']:
            # Procesar nueva imagen
            image_result = process_image(data['image'])
            if image_result:
                image_filename = image_result['filename']
                extracted_info = image_result['extracted_info']
        
        # Usar información extraída como valores predeterminados
        fecha = data.get('fecha', extracted_info.get('date', datetime.now().strftime('%Y-%m-%d')))
        concepto = data.get('concepto', extracted_info.get('concept', ''))
        motivo = data.get('motivo', '')
        descripcion = data.get('descripcion', extracted_info.get('description', ''))
        importe_eur = data.get('importe_eur')
        if importe_eur is None:
            importe_eur = extracted_info.get('amount', 0) if 'amount' in extracted_info else 0
        
        # Convertir importe_eur a float si es string
        if isinstance(importe_eur, str):
            try:
                importe_eur = float(importe_eur) if importe_eur else 0
            except ValueError:
                importe_eur = 0
        
        # Asegurar que importe_eur no sea None
        if importe_eur is None:
            importe_eur = 0
        importe_otra_moneda = data.get('importe_otra_moneda')
        
        # Convertir importe_otra_moneda a float si es string
        if isinstance(importe_otra_moneda, str):
            try:
                importe_otra_moneda = float(importe_otra_moneda) if importe_otra_moneda else None
            except ValueError:
                importe_otra_moneda = None
        
        moneda_otra = data.get('moneda_otra')
        
        # CONVERSIÓN AUTOMÁTICA: Si hay moneda diferente a EUR, convertir automáticamente
        if importe_otra_moneda and moneda_otra and moneda_otra != 'EUR':
            # Convertir automáticamente a EUR
            auto_eur = convert_to_eur(importe_otra_moneda, moneda_otra)
            
            # Si no se proporcionó importe_eur o es 0, usar la conversión automática
            if not importe_eur or importe_eur == 0:
                importe_eur = auto_eur
                print(f"💱 Conversión automática aplicada: {importe_otra_moneda} {moneda_otra} = {importe_eur} EUR")
        
        # Si solo hay importe_eur pero no hay otra moneda, asegurar que moneda_otra sea None
        elif importe_eur and not importe_otra_moneda:
            moneda_otra = None
            importe_otra_moneda = None
        
        # Determinar usuario: admin puede crear para cualquier usuario, user solo para sí mismo
        target_user = data.get('usuario', get_current_user())
        if not is_admin() and target_user != get_current_user():
            return jsonify({'success': False, 'error': 'No autorizado para crear gastos de otro usuario'}), 403
        
        # Debug: Log de los datos procesados
        print(f"💰 Guardando gasto: EUR={importe_eur}, Otra={importe_otra_moneda}, Moneda={moneda_otra}")
        
        # Validar fecha
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            # Si la fecha extraída no es válida, usar fecha actual
            fecha = datetime.now().strftime('%Y-%m-%d')
        
        # Insertar en base de datos
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO gastos (fecha, concepto, motivo, descripcion, importe_eur, 
                              importe_otra_moneda, moneda_otra, imagen_path, checkeado, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (fecha, concepto, motivo, descripcion, importe_eur, 
              importe_otra_moneda, moneda_otra, image_filename, False, target_user))
        
        gasto_id = cursor.lastrowid
        
        # Actualizar motivo si se proporciona
        if motivo:
            cursor.execute('''
                INSERT OR REPLACE INTO motivos (nombre, usado_veces, ultimo_uso)
                VALUES (?, COALESCE((SELECT usado_veces FROM motivos WHERE nombre = ?), 0) + 1, ?)
            ''', (motivo, motivo, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'id': gasto_id,
            'extracted_info': extracted_info
        })
        
    except Exception as e:
        print(f"Error añadiendo gasto: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gastos/<int:gasto_id>', methods=['PUT'])
@login_required
def update_gasto(gasto_id):
    """Actualizar gasto existente"""
    try:
        data = request.get_json()
        
        # Verificar autorización: usuario solo puede editar sus propios gastos
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT usuario FROM gastos WHERE id = ?', (gasto_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'success': False, 'error': 'Gasto no encontrado'}), 404
        
        gasto_owner = result[0]
        if not is_admin() and gasto_owner != get_current_user():
            conn.close()
            return jsonify({'success': False, 'error': 'No autorizado para editar este gasto'}), 403
        
        # Manejar imagen
        image_filename = None
        if 'processed_image_filename' in data:
            # Usar imagen ya procesada
            image_filename = data['processed_image_filename']
        elif 'image' in data:
            # Procesar nueva imagen
            image_result = process_image(data['image'])
            if image_result:
                image_filename = image_result['filename']
        elif 'existing_image_filename' in data:
            # Mantener imagen existente
            image_filename = data['existing_image_filename']
        
        # Procesar importes con conversión automática
        importe_eur = data.get('importe_eur', 0)
        importe_otra_moneda = data.get('importe_otra_moneda')
        moneda_otra = data.get('moneda_otra')
        
        # Convertir tipos si es necesario
        if isinstance(importe_eur, str):
            try:
                importe_eur = float(importe_eur) if importe_eur else 0
            except ValueError:
                importe_eur = 0
        
        if isinstance(importe_otra_moneda, str):
            try:
                importe_otra_moneda = float(importe_otra_moneda) if importe_otra_moneda else None
            except ValueError:
                importe_otra_moneda = None
        
        # CONVERSIÓN AUTOMÁTICA: Si hay moneda diferente a EUR, convertir automáticamente
        if importe_otra_moneda and moneda_otra and moneda_otra != 'EUR':
            # Convertir automáticamente a EUR
            auto_eur = convert_to_eur(importe_otra_moneda, moneda_otra)
            
            # Si no se proporcionó importe_eur o es 0, usar la conversión automática
            if not importe_eur or importe_eur == 0:
                importe_eur = auto_eur
                print(f"💱 Conversión automática en UPDATE: {importe_otra_moneda} {moneda_otra} = {importe_eur} EUR")
        
        # Si solo hay importe_eur pero no hay otra moneda, asegurar que moneda_otra sea None
        elif importe_eur and not importe_otra_moneda:
            moneda_otra = None
            importe_otra_moneda = None
        
        # Actualizar con o sin imagen
        if image_filename:
            cursor.execute('''
                UPDATE gastos 
                SET fecha = ?, concepto = ?, motivo = ?, descripcion = ?, 
                    importe_eur = ?, importe_otra_moneda = ?, moneda_otra = ?, imagen_path = ?, checkeado = ?
                WHERE id = ?
            ''', (data['fecha'], data['concepto'], data['motivo'], data['descripcion'],
                  data['importe_eur'], data.get('importe_otra_moneda'), 
                  data.get('moneda_otra'), image_filename, data.get('checkeado', False), gasto_id))
        else:
            cursor.execute('''
                UPDATE gastos 
                SET fecha = ?, concepto = ?, motivo = ?, descripcion = ?, 
                    importe_eur = ?, importe_otra_moneda = ?, moneda_otra = ?, checkeado = ?
                WHERE id = ?
            ''', (data['fecha'], data['concepto'], data['motivo'], data['descripcion'],
                  data['importe_eur'], data.get('importe_otra_moneda'), 
                  data.get('moneda_otra'), data.get('checkeado', False), gasto_id))
        
        # Actualizar motivo si se proporciona
        if data.get('motivo'):
            cursor.execute('''
                INSERT OR REPLACE INTO motivos (nombre, usado_veces, ultimo_uso)
                VALUES (?, COALESCE((SELECT usado_veces FROM motivos WHERE nombre = ?), 0) + 1, ?)
            ''', (data['motivo'], data['motivo'], datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gastos/<int:gasto_id>', methods=['DELETE'])
@login_required
def delete_gasto(gasto_id):
    """Eliminar gasto"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar autorización: usuario solo puede eliminar sus propios gastos
        cursor.execute('SELECT imagen_path, usuario, detalle_cuadrado FROM gastos WHERE id = ?', (gasto_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'success': False, 'error': 'Gasto no encontrado'}), 404
        
        image_path, gasto_owner, detalle_cuadrado = result
        if not is_admin() and gasto_owner != get_current_user():
            conn.close()
            return jsonify({'success': False, 'error': 'No autorizado para eliminar este gasto'}), 403
        
        # Si el gasto está cuadrado con algún viaje, descuadrarlo automáticamente
        if detalle_cuadrado:
            cursor.execute('UPDATE viaje_detalles SET cuadrado = FALSE, gasto_id = NULL WHERE gasto_id = ?', (gasto_id,))
            print(f"✅ Gasto {gasto_id} descuadrado automáticamente al ser eliminado")
        
        # Eliminar archivo de imagen si existe
        if image_path:
            image_file_path = os.path.join(UPLOAD_FOLDER, image_path)
            if os.path.exists(image_file_path):
                os.remove(image_file_path)
        
        cursor.execute('DELETE FROM gastos WHERE id = ?', (gasto_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gastos/<int:gasto_id>/checkeado', methods=['PUT'])
@login_required
def update_checkeado(gasto_id):
    """Actualizar solo el estado checkeado de un gasto"""
    try:
        data = request.get_json()
        checkeado = data.get('checkeado', False)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar autorización: usuario solo puede actualizar sus propios gastos
        cursor.execute('SELECT usuario FROM gastos WHERE id = ?', (gasto_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'success': False, 'error': 'Gasto no encontrado'}), 404
        
        gasto_owner = result[0]
        if not is_admin() and gasto_owner != get_current_user():
            conn.close()
            return jsonify({'success': False, 'error': 'No autorizado para actualizar este gasto'}), 403
        
        # Actualizar solo el campo checkeado
        cursor.execute('UPDATE gastos SET checkeado = ? WHERE id = ?', (checkeado, gasto_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Gasto no encontrado'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conceptos', methods=['GET'])
def get_conceptos():
    """Obtener lista de conceptos"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT nombre FROM conceptos WHERE activo = TRUE ORDER BY nombre')
    conceptos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(conceptos)

@app.route('/api/motivos', methods=['GET'])
def get_motivos():
    """Obtener lista de motivos ordenados por uso (solo activos por defecto)"""
    solo_activos = request.args.get('solo_activos', 'true').lower() == 'true'
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if solo_activos:
        cursor.execute('SELECT nombre, activo FROM motivos WHERE activo = TRUE ORDER BY usado_veces DESC, ultimo_uso DESC')
    else:
        cursor.execute('SELECT nombre, activo FROM motivos ORDER BY activo DESC, usado_veces DESC, ultimo_uso DESC')
    
    motivos_data = cursor.fetchall()
    conn.close()
    
    # Si se pide todos, devolver con info de estado activo
    if not solo_activos:
        return jsonify([{'nombre': row[0], 'activo': bool(row[1])} for row in motivos_data])
    
    # Si solo activos, devolver solo nombres (backward compatibility)
    return jsonify([row[0] for row in motivos_data])

@app.route('/api/motivos', methods=['POST'])
def add_motivo():
    """Añadir nuevo motivo"""
    try:
        data = request.get_json()
        motivo = data.get('nombre', '').strip()
        
        if not motivo:
            return jsonify({'success': False, 'error': 'El motivo no puede estar vacío'}), 400
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute('SELECT nombre FROM motivos WHERE nombre = ?', (motivo,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Este motivo ya existe'}), 400
        
        # Insertar nuevo motivo (activo por defecto)
        cursor.execute('''
            INSERT INTO motivos (nombre, usado_veces, ultimo_uso, activo)
            VALUES (?, 0, ?, TRUE)
        ''', (motivo, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Motivo añadido correctamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/motivos/<motivo_nombre>', methods=['DELETE'])
def delete_motivo(motivo_nombre):
    """Eliminar motivo"""
    try:
        # Decodificar el nombre del motivo (por si tiene caracteres especiales)
        from urllib.parse import unquote
        motivo_nombre = unquote(motivo_nombre)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar si el motivo existe
        cursor.execute('SELECT nombre FROM motivos WHERE nombre = ?', (motivo_nombre,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Motivo no encontrado'}), 404
        
        # Verificar si el motivo está siendo usado en gastos
        cursor.execute('SELECT COUNT(*) FROM gastos WHERE motivo = ?', (motivo_nombre,))
        gastos_count = cursor.fetchone()[0]
        
        if gastos_count > 0:
            conn.close()
            return jsonify({
                'success': False, 
                'error': f'No se puede eliminar el motivo porque está siendo usado en {gastos_count} gasto(s). Elimina primero esos gastos o cambia su motivo.'
            }), 400
        
        # Eliminar el motivo
        cursor.execute('DELETE FROM motivos WHERE nombre = ?', (motivo_nombre,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Motivo eliminado correctamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/motivos/<motivo_nombre>/toggle-activo', methods=['PUT'])
def toggle_motivo_activo(motivo_nombre):
    """Activar o desactivar un motivo"""
    try:
        from urllib.parse import unquote
        motivo_nombre = unquote(motivo_nombre)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Obtener estado actual
        cursor.execute('SELECT activo FROM motivos WHERE nombre = ?', (motivo_nombre,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'success': False, 'error': 'Motivo no encontrado'}), 404
        
        # Cambiar estado
        nuevo_estado = not bool(result[0])
        cursor.execute('UPDATE motivos SET activo = ? WHERE nombre = ?', (nuevo_estado, motivo_nombre))
        
        conn.commit()
        conn.close()
        
        estado_texto = "activado" if nuevo_estado else "desactivado"
        return jsonify({'success': True, 'message': f'Viaje {estado_texto} correctamente', 'activo': nuevo_estado})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/convert-currency', methods=['POST'])
def convert_currency():
    """Convertir moneda"""
    try:
        data = request.get_json()
        amount = float(data['amount'])
        from_currency = data['from_currency']
        to_currency = data['to_currency']
        
        print(f"🔄 Conversión: {amount} {from_currency} → {to_currency}")
        
        if from_currency == to_currency:
            print(f"✅ Misma moneda, retornando: {amount}")
            return jsonify({'converted_amount': amount})
        
        # Obtener tasas de cambio
        from_rate = EXCHANGE_RATES.get(from_currency, 1)
        to_rate = EXCHANGE_RATES.get(to_currency, 1)
        
        print(f"📊 Tasas - {from_currency}: {from_rate}, {to_currency}: {to_rate}")
        
        # Convertir a EUR primero si no es EUR
        if from_currency != 'EUR':
            amount_eur = amount / from_rate
            print(f"💱 {amount} {from_currency} / {from_rate} = {amount_eur} EUR")
        else:
            amount_eur = amount
            print(f"💰 Ya en EUR: {amount_eur}")
        
        # Convertir de EUR a moneda destino
        if to_currency != 'EUR':
            converted_amount = amount_eur * to_rate
            print(f"💱 {amount_eur} EUR * {to_rate} = {converted_amount} {to_currency}")
        else:
            converted_amount = amount_eur
            print(f"💰 Resultado en EUR: {converted_amount}")
        
        final_amount = round(converted_amount, 2)
        print(f"✅ Resultado final: {final_amount} {to_currency}")
        
        return jsonify({'converted_amount': final_amount})
        
    except Exception as e:
        print(f"❌ Error en conversión: {e}")
        return jsonify({'error': str(e)}), 400

# ====================== ENDPOINTS DETALLES DE VIAJES ======================

@app.route('/api/viajes/<motivo>/detalles', methods=['GET'])
@login_required
def get_viaje_detalles(motivo):
    """Obtener detalles de un viaje específico"""
    try:
        from urllib.parse import unquote
        motivo = unquote(motivo)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Obtener detalles del viaje según el usuario - ordenados de más barato a más caro
        if is_admin():
            cursor.execute('''
                SELECT id, importe_eur, importe_original, moneda_original, cuadrado, gasto_id, usuario, created_at
                FROM viaje_detalles 
                WHERE motivo = ?
                ORDER BY importe_eur ASC, created_at DESC
            ''', (motivo,))
        else:
            cursor.execute('''
                SELECT id, importe_eur, importe_original, moneda_original, cuadrado, gasto_id, usuario, created_at
                FROM viaje_detalles 
                WHERE motivo = ? AND usuario = ?
                ORDER BY importe_eur ASC, created_at DESC
            ''', (motivo, get_current_user()))
        
        detalles = cursor.fetchall()
        
        # Obtener número total de gastos esperados (detalles del viaje)
        total_gastos_esperados = len(detalles)
        conn.close()
        
        detalles_list = []
        for detalle in detalles:
            detalles_list.append({
                'id': detalle[0],
                'importe_eur': detalle[1],
                'importe_original': detalle[2],
                'moneda_original': detalle[3],
                'cuadrado': bool(detalle[4]),
                'gasto_id': detalle[5],
                'usuario': detalle[6],
                'created_at': detalle[7]
            })
        
        # Devolver detalles con metadatos del viaje
        return jsonify({
            'detalles': detalles_list,
            'metadata': {
                'total_gastos_esperados': total_gastos_esperados,
                'motivo': motivo
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/viajes/<motivo>/detalles', methods=['POST'])
@login_required
def add_viaje_detalle(motivo):
    """Añadir nuevo detalle a un viaje"""
    try:
        from urllib.parse import unquote
        motivo = unquote(motivo)
        
        data = request.get_json()
        importe_original = float(data.get('importe_original', 0))
        moneda_original = data.get('moneda_original', 'EUR')
        
        if importe_original <= 0:
            return jsonify({'success': False, 'error': 'El importe debe ser mayor que 0'}), 400
        
        # Convertir a EUR si es necesario
        if moneda_original == 'EUR':
            importe_eur = importe_original
        else:
            importe_eur = convert_to_eur(importe_original, moneda_original)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO viaje_detalles (motivo, importe_eur, importe_original, moneda_original, cuadrado, usuario)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (motivo, importe_eur, importe_original, moneda_original, False, get_current_user()))
        
        detalle_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'id': detalle_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/viajes/detalles/<int:detalle_id>', methods=['DELETE'])
@login_required
def delete_viaje_detalle(detalle_id):
    """Eliminar detalle de viaje"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar autorización
        cursor.execute('SELECT usuario FROM viaje_detalles WHERE id = ?', (detalle_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'success': False, 'error': 'Detalle no encontrado'}), 404
        
        if not is_admin() and result[0] != get_current_user():
            conn.close()
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
        
        cursor.execute('DELETE FROM viaje_detalles WHERE id = ?', (detalle_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/viajes/todos-con-detalles', methods=['GET'])
@login_required
def get_todos_viajes_con_detalles():
    """Obtener todos los viajes que tienen detalles configurados (incluyendo los completamente cuadrados)"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        if is_admin():
            cursor.execute('''
                SELECT DISTINCT motivo, usuario
                FROM viaje_detalles 
                ORDER BY motivo, usuario
            ''')
        else:
            cursor.execute('''
                SELECT DISTINCT motivo
                FROM viaje_detalles 
                WHERE usuario = ?
                ORDER BY motivo
            ''', (get_current_user(),))
        
        resultados = cursor.fetchall()
        conn.close()
        
        viajes = []
        for resultado in resultados:
            if is_admin():
                viajes.append({
                    'motivo': resultado[0],
                    'usuario': resultado[1]
                })
            else:
                viajes.append({
                    'motivo': resultado[0]
                })
        
        return jsonify(viajes)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/viajes/resumen', methods=['GET'])
@login_required
def get_viajes_resumen():
    """Obtener resumen de viajes con detalles pendientes"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        if is_admin():
            cursor.execute('''
                SELECT 
                    motivo,
                    usuario,
                    COUNT(*) as total_detalles,
                    SUM(CASE WHEN cuadrado = 0 THEN 1 ELSE 0 END) as pendientes,
                    SUM(importe_eur) as total_importe,
                    SUM(CASE WHEN cuadrado = 0 THEN importe_eur ELSE 0 END) as importe_pendiente
                FROM viaje_detalles 
                GROUP BY motivo, usuario
                HAVING total_detalles > 0 AND importe_pendiente > 0
                ORDER BY motivo, usuario
            ''')
        else:
            cursor.execute('''
                SELECT 
                    motivo,
                    usuario,
                    COUNT(*) as total_detalles,
                    SUM(CASE WHEN cuadrado = 0 THEN 1 ELSE 0 END) as pendientes,
                    SUM(importe_eur) as total_importe,
                    SUM(CASE WHEN cuadrado = 0 THEN importe_eur ELSE 0 END) as importe_pendiente
                FROM viaje_detalles 
                WHERE usuario = ?
                GROUP BY motivo
                HAVING total_detalles > 0 AND importe_pendiente > 0
                ORDER BY motivo
            ''', (get_current_user(),))
        
        resultados = cursor.fetchall()
        conn.close()
        
        resumen = []
        for resultado in resultados:
            resumen.append({
                'motivo': resultado[0],
                'usuario': resultado[1],
                'total_detalles': resultado[2],
                'pendientes': resultado[3],
                'total_importe': resultado[4],
                'importe_pendiente': resultado[5]
            })
        
        return jsonify(resumen)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gastos/<int:gasto_id>/cuadrar', methods=['POST'])
@login_required
def cuadrar_gasto(gasto_id):
    """Cuadrar un gasto con un detalle de viaje"""
    try:
        data = request.get_json()
        detalle_id = data.get('detalle_id')
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar que el gasto existe y pertenece al usuario
        cursor.execute('SELECT usuario, motivo, importe_eur FROM gastos WHERE id = ?', (gasto_id,))
        gasto_result = cursor.fetchone()
        
        if not gasto_result:
            conn.close()
            return jsonify({'success': False, 'error': 'Gasto no encontrado'}), 404
        
        if not is_admin() and gasto_result[0] != get_current_user():
            conn.close()
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
        
        # Verificar que el detalle existe y no está cuadrado
        cursor.execute('SELECT motivo, importe_eur, cuadrado FROM viaje_detalles WHERE id = ?', (detalle_id,))
        detalle_result = cursor.fetchone()
        
        if not detalle_result:
            conn.close()
            return jsonify({'success': False, 'error': 'Detalle no encontrado'}), 404
        
        if detalle_result[2]:  # Ya está cuadrado
            conn.close()
            return jsonify({'success': False, 'error': 'Este detalle ya está cuadrado'}), 400
        
        # Verificar que el motivo coincide
        if gasto_result[1] != detalle_result[0]:
            conn.close()
            return jsonify({'success': False, 'error': 'El gasto y el detalle no pertenecen al mismo viaje'}), 400
        
        # Cuadrar
        cursor.execute('UPDATE viaje_detalles SET cuadrado = TRUE, gasto_id = ? WHERE id = ?', (gasto_id, detalle_id))
        cursor.execute('UPDATE gastos SET detalle_cuadrado = TRUE WHERE id = ?', (gasto_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gastos/<int:gasto_id>/descuadrar', methods=['POST'])
@login_required
def descuadrar_gasto(gasto_id):
    """Descuadrar un gasto"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar que el gasto existe y pertenece al usuario
        cursor.execute('SELECT usuario FROM gastos WHERE id = ?', (gasto_id,))
        gasto_result = cursor.fetchone()
        
        if not gasto_result:
            conn.close()
            return jsonify({'success': False, 'error': 'Gasto no encontrado'}), 404
        
        if not is_admin() and gasto_result[0] != get_current_user():
            conn.close()
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
        
        # Descuadrar
        cursor.execute('UPDATE viaje_detalles SET cuadrado = FALSE, gasto_id = NULL WHERE gasto_id = ?', (gasto_id,))
        cursor.execute('UPDATE gastos SET detalle_cuadrado = FALSE WHERE id = ?', (gasto_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gastos/<int:gasto_id>/buscar-cuadre', methods=['GET'])
@login_required
def buscar_cuadre_automatico(gasto_id):
    """Buscar automáticamente detalles de viaje que coincidan con el importe del gasto"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Obtener información del gasto
        cursor.execute('SELECT usuario, motivo, importe_eur FROM gastos WHERE id = ?', (gasto_id,))
        gasto_result = cursor.fetchone()
        
        if not gasto_result:
            conn.close()
            return jsonify({'success': False, 'error': 'Gasto no encontrado'}), 404
        
        if not is_admin() and gasto_result[0] != get_current_user():
            conn.close()
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
        
        usuario, motivo, importe_eur = gasto_result
        
        if not motivo:
            conn.close()
            return jsonify({'candidatos': []})
        
        # Buscar detalles no cuadrados con el mismo importe y motivo
        cursor.execute('''
            SELECT id, importe_eur, importe_original, moneda_original
            FROM viaje_detalles 
            WHERE motivo = ? AND usuario = ? AND cuadrado = FALSE AND ABS(importe_eur - ?) < 0.01
            ORDER BY created_at DESC
        ''', (motivo, usuario, importe_eur))
        
        candidatos = cursor.fetchall()
        conn.close()
        
        candidatos_list = []
        for candidato in candidatos:
            candidatos_list.append({
                'id': candidato[0],
                'importe_eur': candidato[1],
                'importe_original': candidato[2],
                'moneda_original': candidato[3]
            })
        
        return jsonify({'candidatos': candidatos_list})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir archivos de imagen"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/export/pdf', methods=['GET'])
@login_required
def export_pdf():
    """Exportar gastos filtrados a PDF"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        filter_user = request.args.get('user')  # Filtro de usuario para admin
        filter_viaje = request.args.get('viaje')  # Filtro de viaje
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Fechas requeridas'}), 400
        
        # Obtener gastos filtrados
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Construir consulta SQL con filtros dinámicos para PDF
        if is_admin():
            base_query = '''
                SELECT fecha, concepto, motivo, descripcion, importe_eur, importe_otra_moneda, moneda_otra, checkeado, usuario
                FROM gastos 
                WHERE fecha BETWEEN ? AND ?
            '''
            params = [fecha_inicio, fecha_fin]
            
            if filter_user:
                base_query += ' AND usuario = ?'
                params.append(filter_user)
            
            if filter_viaje:
                base_query += ' AND motivo = ?'
                params.append(filter_viaje)
            
            base_query += ' ORDER BY fecha DESC'
            cursor.execute(base_query, params)
        else:
            # Usuario normal solo puede exportar sus propios gastos
            base_query = '''
                SELECT fecha, concepto, motivo, descripcion, importe_eur, importe_otra_moneda, moneda_otra, checkeado, usuario
                FROM gastos 
                WHERE fecha BETWEEN ? AND ? AND usuario = ?
            '''
            params = [fecha_inicio, fecha_fin, get_current_user()]
            
            if filter_viaje:
                base_query += ' AND motivo = ?'
                params.append(filter_viaje)
            
            base_query += ' ORDER BY fecha DESC'
            cursor.execute(base_query, params)
        
        gastos = cursor.fetchall()
        conn.close()
        
        if not gastos:
            return jsonify({'error': 'No hay gastos en el rango seleccionado'}), 404
        
        # Crear PDF simple
        filename = f"gastos_{fecha_inicio}_{fecha_fin}.pdf"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Contenido del PDF
        story = []
        
        # Formatear fechas del período a dd/mm/yyyy
        def format_period_date(date_str):
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                return date_obj.strftime('%d/%m/%Y')
            except:
                return date_str
        
        fecha_inicio_formatted = format_period_date(fecha_inicio)
        fecha_fin_formatted = format_period_date(fecha_fin)
        
        # Título simple
        story.append(Paragraph("Reporte de Gastos", styles['Title']))
        story.append(Paragraph(f"Período: {fecha_inicio_formatted} - {fecha_fin_formatted}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Estadísticas básicas (sin promedio)
        total_gastos = len(gastos)
        total_importe = sum(gasto[4] for gasto in gastos)
        
        story.append(Paragraph(f"Total de tickets: {total_gastos}", styles['Normal']))
        story.append(Paragraph(f"Importe total: EUR {total_importe:.2f}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Tabla simple
        if is_admin():
            data = [['Fecha', 'Concepto', 'Viaje', 'Descripción', 'Importe EUR', 'Otra Moneda', 'Moneda', 'Checkeado', 'Usuario']]
        else:
            data = [['Fecha', 'Concepto', 'Viaje', 'Descripción', 'Importe EUR', 'Otra Moneda', 'Moneda', 'Checkeado']]
        
        # Función para formatear fechas a dd/mm/yyyy
        def format_date_for_pdf(date_str):
            if date_str:
                try:
                    # Convertir de YYYY-MM-DD a DD/MM/YYYY
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    return date_obj.strftime('%d/%m/%Y')
                except:
                    return date_str
            return date_str
        
        for gasto in gastos:
            fecha, concepto, motivo, descripcion, importe_eur, importe_otra_moneda, moneda_otra, checkeado, usuario = gasto
            fecha_formatted = format_date_for_pdf(fecha)
            motivo_text = motivo or '-'
            descripcion_text = descripcion or '-'
            checkeado_text = 'Si' if checkeado else 'No'
            
            # Formatear otras monedas
            importe_otra_text = f'{importe_otra_moneda:.2f}' if importe_otra_moneda else ''
            moneda_otra_text = moneda_otra or ''
            
            # Truncar texto largo
            if len(descripcion_text) > 25:
                descripcion_text = descripcion_text[:25] + '...'
            
            if is_admin():
                data.append([
                    fecha_formatted,
                    concepto,
                    motivo_text,
                    descripcion_text,
                    f'{importe_eur:.2f}',
                    importe_otra_text,
                    moneda_otra_text,
                    checkeado_text,
                    usuario
                ])
            else:
                data.append([
                    fecha_formatted,
                    concepto,
                    motivo_text,
                    descripcion_text,
                    f'{importe_eur:.2f}',
                    importe_otra_text,
                    moneda_otra_text,
                    checkeado_text
                ])
        
        # Crear tabla simple
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(table)
        
        # Generar PDF
        doc.build(story)
        
        # Leer archivo y enviarlo
        with open(filepath, 'rb') as f:
            pdf_data = f.read()
        
        # Limpiar archivo
        os.unlink(filepath)
        
        # Crear respuesta
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        print(f"Error exportando PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error generando PDF'}), 500

@app.route('/api/export/excel', methods=['GET'])
@login_required
def export_excel():
    """Exportar gastos filtrados a Excel"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        filter_user = request.args.get('user')  # Filtro de usuario para admin
        filter_viaje = request.args.get('viaje')  # Filtro de viaje
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Fechas requeridas'}), 400
        
        # Obtener gastos filtrados
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Construir consulta SQL con filtros dinámicos para Excel
        if is_admin():
            base_query = '''
                SELECT fecha, concepto, motivo, descripcion, importe_eur, importe_otra_moneda, moneda_otra, checkeado, usuario
                FROM gastos 
                WHERE fecha BETWEEN ? AND ?
            '''
            params = [fecha_inicio, fecha_fin]
            
            if filter_user:
                base_query += ' AND usuario = ?'
                params.append(filter_user)
            
            if filter_viaje:
                base_query += ' AND motivo = ?'
                params.append(filter_viaje)
            
            base_query += ' ORDER BY fecha DESC'
            cursor.execute(base_query, params)
        else:
            # Usuario normal solo puede exportar sus propios gastos
            base_query = '''
                SELECT fecha, concepto, motivo, descripcion, importe_eur, importe_otra_moneda, moneda_otra, checkeado, usuario
                FROM gastos 
                WHERE fecha BETWEEN ? AND ? AND usuario = ?
            '''
            params = [fecha_inicio, fecha_fin, get_current_user()]
            
            if filter_viaje:
                base_query += ' AND motivo = ?'
                params.append(filter_viaje)
            
            base_query += ' ORDER BY fecha DESC'
            cursor.execute(base_query, params)
        
        gastos = cursor.fetchall()
        conn.close()
        
        if not gastos:
            return jsonify({'error': 'No hay gastos en el rango seleccionado'}), 404
        
        # Crear DataFrame simple
        if is_admin():
            df = pd.DataFrame(gastos, columns=[
                'Fecha', 'Concepto', 'Motivo', 'Descripcion', 'Importe EUR', 'Importe Otra Moneda', 'Moneda', 'Checkeado', 'Usuario'
            ])
        else:
            df = pd.DataFrame(gastos, columns=[
                'Fecha', 'Concepto', 'Motivo', 'Descripcion', 'Importe EUR', 'Importe Otra Moneda', 'Moneda', 'Checkeado', 'Usuario'
            ])
            # Eliminar columna usuario para usuarios normales
            df = df.drop('Usuario', axis=1)
        
        # Convertir campo checkeado a texto legible
        df['Checkeado'] = df['Checkeado'].apply(lambda x: 'Si' if x else 'No')
        
        # Convertir valores nulos a cadenas vacías para las otras monedas
        df['Importe Otra Moneda'] = df['Importe Otra Moneda'].fillna('')
        df['Moneda'] = df['Moneda'].fillna('')
        df['Motivo'] = df['Motivo'].fillna('')
        df['Descripcion'] = df['Descripcion'].fillna('')
        
        # Formatear fechas a formato dd/mm/yyyy
        def format_date_for_excel(date_str):
            if date_str:
                try:
                    # Convertir de YYYY-MM-DD a DD/MM/YYYY
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    return date_obj.strftime('%d/%m/%Y')
                except:
                    return date_str
            return date_str
        
        df['Fecha'] = df['Fecha'].apply(format_date_for_excel)
        
        # Crear archivo Excel
        filename = f"gastos_{fecha_inicio}_{fecha_fin}.xlsx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Escribir archivo Excel simple
        df.to_excel(filepath, index=False, sheet_name='Gastos')
        
        # Leer archivo y enviarlo
        with open(filepath, 'rb') as f:
            excel_data = f.read()
        
        # Limpiar archivo
        os.unlink(filepath)
        
        # Crear respuesta
        response = make_response(excel_data)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        print(f"Error exportando Excel: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error generando Excel'}), 500

@app.route('/api/export/images', methods=['GET'])
@login_required
def export_images():
    """Exportar imágenes de gastos filtrados en un ZIP"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        filter_user = request.args.get('user')  # Filtro de usuario para admin
        filter_viaje = request.args.get('viaje')  # Filtro de viaje
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Fechas requeridas'}), 400
        
        # Obtener gastos filtrados que tienen imágenes
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Construir consulta SQL con filtros dinámicos para imágenes
        if is_admin():
            base_query = '''
                SELECT fecha, descripcion, imagen_path
                FROM gastos 
                WHERE fecha BETWEEN ? AND ? AND imagen_path IS NOT NULL AND imagen_path != ''
            '''
            params = [fecha_inicio, fecha_fin]
            
            if filter_user:
                base_query += ' AND usuario = ?'
                params.append(filter_user)
            
            if filter_viaje:
                base_query += ' AND motivo = ?'
                params.append(filter_viaje)
            
            base_query += ' ORDER BY fecha DESC'
            cursor.execute(base_query, params)
        else:
            # Usuario normal solo puede exportar sus propias imágenes
            base_query = '''
                SELECT fecha, descripcion, imagen_path
                FROM gastos 
                WHERE fecha BETWEEN ? AND ? AND imagen_path IS NOT NULL AND imagen_path != '' AND usuario = ?
            '''
            params = [fecha_inicio, fecha_fin, get_current_user()]
            
            if filter_viaje:
                base_query += ' AND motivo = ?'
                params.append(filter_viaje)
            
            base_query += ' ORDER BY fecha DESC'
            cursor.execute(base_query, params)
        
        gastos_con_imagenes = cursor.fetchall()
        conn.close()
        
        if not gastos_con_imagenes:
            return jsonify({'error': 'No hay imágenes en el rango seleccionado'}), 404
        
        # Crear archivo ZIP temporal
        zip_filename = f"imagenes_gastos_{fecha_inicio}_{fecha_fin}.zip"
        zip_filepath = os.path.join(UPLOAD_FOLDER, zip_filename)
        
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, (fecha, descripcion, imagen_path) in enumerate(gastos_con_imagenes):
                # Construir ruta completa de la imagen
                imagen_full_path = os.path.join(UPLOAD_FOLDER, imagen_path)
                
                # Verificar que la imagen existe
                if os.path.exists(imagen_full_path):
                    # Limpiar descripción para nombre de archivo
                    descripcion_clean = descripcion or f"Gasto_{i+1}"
                    # Remover caracteres no válidos para nombres de archivo
                    descripcion_clean = re.sub(r'[<>:"/\\|?*]', '_', descripcion_clean)
                    # Limitar longitud
                    if len(descripcion_clean) > 50:
                        descripcion_clean = descripcion_clean[:50]
                    
                    # Obtener extensión original
                    _, ext = os.path.splitext(imagen_path)
                    if not ext:
                        ext = '.jpg'  # Por defecto
                    
                    # Crear nombre de archivo: descripcion_fecha.ext
                    nuevo_nombre = f"{descripcion_clean}_{fecha}{ext}"
                    
                    # Añadir al ZIP
                    zipf.write(imagen_full_path, nuevo_nombre)
                    print(f"📷 Añadida imagen: {nuevo_nombre}")
        
        # Leer archivo ZIP
        with open(zip_filepath, 'rb') as f:
            zip_data = f.read()
        
        # Limpiar archivo temporal
        os.unlink(zip_filepath)
        
        # Crear respuesta
        response = make_response(zip_data)
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = f'attachment; filename={zip_filename}'
        
        print(f"✅ ZIP de imágenes generado: {len(gastos_con_imagenes)} imágenes")
        return response
        
    except Exception as e:
        print(f"Error exportando imágenes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error generando ZIP de imágenes'}), 500

@app.route('/api/export/zip', methods=['GET'])
@login_required
def export_zip():
    """Exportar gastos filtrados en un ZIP completo (PDF + Excel + Imágenes)"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        filter_user = request.args.get('user')  # Filtro de usuario para admin
        filter_viaje = request.args.get('viaje')  # Filtro de viaje
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Fechas requeridas'}), 400
        
        # Obtener gastos filtrados
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Construir consulta SQL con filtros dinámicos para ZIP
        if is_admin():
            base_query = '''
                SELECT fecha, concepto, motivo, descripcion, importe_eur, importe_otra_moneda, moneda_otra, checkeado, usuario, imagen_path
                FROM gastos 
                WHERE fecha BETWEEN ? AND ?
            '''
            params = [fecha_inicio, fecha_fin]
            
            if filter_user:
                base_query += ' AND usuario = ?'
                params.append(filter_user)
            
            if filter_viaje:
                base_query += ' AND motivo = ?'
                params.append(filter_viaje)
            
            base_query += ' ORDER BY fecha DESC'
            cursor.execute(base_query, params)
        else:
            # Usuario normal solo puede exportar sus propios gastos
            base_query = '''
                SELECT fecha, concepto, motivo, descripcion, importe_eur, importe_otra_moneda, moneda_otra, checkeado, usuario, imagen_path
                FROM gastos 
                WHERE fecha BETWEEN ? AND ? AND usuario = ?
            '''
            params = [fecha_inicio, fecha_fin, get_current_user()]
            
            if filter_viaje:
                base_query += ' AND motivo = ?'
                params.append(filter_viaje)
            
            base_query += ' ORDER BY fecha DESC'
            cursor.execute(base_query, params)
        
        gastos = cursor.fetchall()
        conn.close()
        
        if not gastos:
            return jsonify({'error': 'No se encontraron gastos en el rango de fechas especificado'}), 404
        
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 1. Generar PDF
            pdf_filename = f"gastos_{fecha_inicio}_{fecha_fin}.pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)
            
            # Crear documento PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("📊 Reporte de Gastos", title_style))
            story.append(Spacer(1, 20))
            
            # Información del reporte
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=10
            )
            # Formatear fechas del período a dd/mm/yyyy
            def format_period_date_zip(date_str):
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    return date_obj.strftime('%d/%m/%Y')
                except:
                    return date_str
            
            fecha_inicio_formatted = format_period_date_zip(fecha_inicio)
            fecha_fin_formatted = format_period_date_zip(fecha_fin)
            
            story.append(Paragraph(f"<b>Período:</b> {fecha_inicio_formatted} al {fecha_fin_formatted}", info_style))
            story.append(Paragraph(f"<b>Generado:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", info_style))
            if filter_user:
                story.append(Paragraph(f"<b>Usuario:</b> {filter_user}", info_style))
            story.append(Spacer(1, 20))
            
            # Tabla de gastos
            if is_admin():
                table_data = [['Fecha', 'Concepto', 'Viaje', 'Descripción', 'Importe EUR', 'Otra Moneda', 'Moneda', 'Usuario']]
            else:
                table_data = [['Fecha', 'Concepto', 'Viaje', 'Descripción', 'Importe EUR', 'Otra Moneda', 'Moneda']]
            
            # Función para formatear fechas a dd/mm/yyyy
            def format_date_for_zip_pdf(date_str):
                if date_str:
                    try:
                        # Convertir de YYYY-MM-DD a DD/MM/YYYY
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        return date_obj.strftime('%d/%m/%Y')
                    except:
                        return date_str
                return date_str
            
            for gasto in gastos:
                fecha, concepto, motivo, descripcion, importe_eur, importe_otra_moneda, moneda_otra, checkeado, usuario, imagen_path = gasto
                fecha_formatted = format_date_for_zip_pdf(fecha)
                
                                # Formatear otras monedas
                importe_otra_text = f'{importe_otra_moneda:.2f}' if importe_otra_moneda else ''
                moneda_otra_text = moneda_otra or ''
                
                if is_admin():
                    table_data.append([
                        fecha_formatted,
                        concepto or '',
                        motivo or '',
                        descripcion or '',
                        f"{importe_eur:.2f}" if importe_eur else '',
                        importe_otra_text,
                        moneda_otra_text,
                        usuario or ''
                    ])
                else:
                    table_data.append([
                        fecha_formatted,
                        concepto or '',
                        motivo or '',
                        descripcion or '',
                        f"{importe_eur:.2f}" if importe_eur else '',
                        importe_otra_text,
                        moneda_otra_text
                    ])
            
            # Ajustar anchos de columna según el número de columnas
            if is_admin():
                table = Table(table_data, colWidths=[0.8*inch, 1.2*inch, 1*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.8*inch])
            else:
                table = Table(table_data, colWidths=[0.8*inch, 1.2*inch, 1*inch, 1.8*inch, 0.8*inch, 0.8*inch, 0.6*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            
            # Calcular totales
            total_eur = sum(float(gasto[4]) for gasto in gastos if gasto[4])
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"<b>Total: {total_eur:.2f} €</b>", info_style))
            
            doc.build(story)
            
            # 2. Generar Excel
            excel_filename = f"gastos_{fecha_inicio}_{fecha_fin}.xlsx"
            excel_path = os.path.join(temp_dir, excel_filename)
            
            df_data = []
            for gasto in gastos:
                fecha, concepto, motivo, descripcion, importe_eur, importe_otra_moneda, moneda_otra, checkeado, usuario, imagen_path = gasto
                df_data.append({
                    'Fecha': fecha,
                    'Concepto': concepto or '',
                    'Motivo': motivo or '',
                    'Descripción': descripcion or '',
                    'Importe EUR': importe_eur or 0,
                    'Importe Otra Moneda': importe_otra_moneda if importe_otra_moneda is not None else '',
                    'Moneda': moneda_otra or '',
                    'Checkeado': 'Sí' if checkeado else 'No',
                    'Usuario': usuario or ''
                })
            
            df = pd.DataFrame(df_data)
            
            # Formatear fechas a formato dd/mm/yyyy
            def format_date_for_excel_zip(date_str):
                if date_str:
                    try:
                        # Convertir de YYYY-MM-DD a DD/MM/YYYY
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        return date_obj.strftime('%d/%m/%Y')
                    except:
                        return date_str
                return date_str
            
            df['Fecha'] = df['Fecha'].apply(format_date_for_excel_zip)
            
            df.to_excel(excel_path, index=False)
            
            # 3. Copiar imágenes
            images_dir = os.path.join(temp_dir, 'imagenes')
            os.makedirs(images_dir, exist_ok=True)
            
            images_copied = 0
            for gasto in gastos:
                imagen_path = gasto[9]  # imagen_path es el índice 9
                if imagen_path:
                    # Construir ruta completa de la imagen
                    imagen_full_path = os.path.join(UPLOAD_FOLDER, imagen_path)
                    
                    # Verificar que la imagen existe
                    if os.path.exists(imagen_full_path):
                        # Crear nombre único para la imagen
                        base_name = os.path.basename(imagen_path)
                        name, ext = os.path.splitext(base_name)
                        new_name = f"{gasto[0]}_{name}{ext}"  # fecha_nombreoriginal.ext
                        
                        dest_path = os.path.join(images_dir, new_name)
                        shutil.copy2(imagen_full_path, dest_path)
                        images_copied += 1
                        print(f"📷 Copiada imagen: {new_name}")
                    else:
                        print(f"⚠️ Imagen no encontrada: {imagen_full_path}")
            
            # 4. Crear ZIP final
            zip_filename = f"gastos_completo_{fecha_inicio}_{fecha_fin}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Agregar PDF
                zipf.write(pdf_path, pdf_filename)
                
                # Agregar Excel
                zipf.write(excel_path, excel_filename)
                
                # Agregar imágenes
                if images_copied > 0:
                    for root, dirs, files in os.walk(images_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.join('imagenes', file)
                            zipf.write(file_path, arc_name)
            
            # Leer ZIP para respuesta
            with open(zip_path, 'rb') as f:
                zip_data = f.read()
            
            # Crear respuesta
            response = make_response(zip_data)
            response.headers['Content-Type'] = 'application/zip'
            response.headers['Content-Disposition'] = f'attachment; filename={zip_filename}'
            
            print(f"✅ ZIP completo generado: {len(gastos)} gastos, {images_copied} imágenes")
            return response
            
        finally:
            # Limpiar directorio temporal
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"Error exportando ZIP completo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error generando ZIP completo'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5100) 