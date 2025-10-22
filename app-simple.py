from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración básica
app.secret_key = os.getenv('SECRET_KEY', 'gastos_app_secret_key_2025')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
DATABASE = os.getenv('DATABASE_URL', 'gastos.db').replace('sqlite:///', '') if os.getenv('DATABASE_URL', '').startswith('sqlite:///') else os.getenv('DATABASE_URL', 'gastos.db')

# Crear directorio de uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ruta principal - healthcheck
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Autenticación simple
        if username == 'edurne' and password == 'edurne':
            session['user'] = {'username': 'edurne', 'role': 'admin'}
            return redirect('/')
        elif username == 'paul' and password == 'paul':
            session['user'] = {'username': 'paul', 'role': 'user'}
            return redirect('/')
        else:
            return render_template('login.html', error='Credenciales incorrectas')
    
    return render_template('login.html')

# Ruta de logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# API básica para gastos
@app.route('/api/gastos', methods=['GET'])
def get_gastos():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM gastos ORDER BY fecha DESC LIMIT 10')
        gastos = cursor.fetchall()
        conn.close()
        return jsonify(gastos)
    except:
        return jsonify([])

# Healthcheck específico
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'GASTOS IA is running'})

if __name__ == '__main__':
    # Inicializar base de datos básica
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Crear tabla de gastos si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                concepto TEXT,
                importe_eur REAL,
                imagen_path TEXT
            )
        ''')
        
        # Crear tabla de usuarios si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                parent_admin TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insertar usuarios por defecto si no existen
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO users (username, password, name, role, parent_admin) VALUES (?, ?, ?, ?, ?)', 
                          ('edurne', 'edurne', 'Edurne', 'admin', None))
            cursor.execute('INSERT INTO users (username, password, name, role, parent_admin) VALUES (?, ?, ?, ?, ?)', 
                          ('paul', 'paul', 'Paul', 'user', 'edurne'))
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
    
    # Iniciar aplicación
    port = int(os.getenv('PORT', 5100))
    print(f"🚀 Iniciando GASTOS IA en puerto {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
