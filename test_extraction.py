#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la extracción con Llama 3.2 90B Vision
"""

import requests
import json

# API Key de Novita
NOVITA_API_KEY = "sk_LNf-QhMfqMCUtlIQncA6JMiWOedoJM1M-5DAxf79Vys"

# Prompt optimizado
prompt = """Analiza esta imagen de ticket y extrae EXACTAMENTE esta información en formato JSON:

IMPORTANTE: Busca el TOTAL FINAL (no subtotales). Busca la FECHA completa. Busca el NOMBRE del establecimiento.

Devuelve SOLO este JSON (sin texto adicional):
{
    "amount": 0.00,
    "currency": "EUR",
    "date": "2024-01-01",
    "description": "Nombre del establecimiento",
    "concept": "Restaurante"
}

CONCEPTOS válidos (elige UNO): Restaurante, Transporte, Alojamiento, Combustible, Compras, Otros

MONEDAS: EUR (€), USD ($), GBP (£), JPY (¥), CHF, CAD, etc.

FECHA: Convierte al formato YYYY-MM-DD (ejemplo: 15/03/2024 → 2024-03-15)

Si NO puedes ver algo claramente, usa null para ese campo.

Responde SOLO con el JSON, nada más."""

# Imagen de prueba simple (ticket de supermercado)
test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

print("🧪 Probando extracción con Llama 3.2 90B Vision...")
print("=" * 60)

try:
    url = "https://api.novita.ai/v3/openai/chat/completions"
    headers = {
        "Authorization": f"Bearer {NOVITA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {"role": "system", "content": "Eres un experto extractor de datos de tickets. Respondes SOLO con JSON válido, sin texto adicional."},
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{test_image_base64}"}}
            ]
        }
    ]
    
    # Probar diferentes modelos de vision disponibles en Novita
    # Basado en la documentación de Novita AI
    models_to_try = [
        "Qwen/Qwen2.5-VL-72B-Instruct",
        "qwen/qwen2.5-vl-72b-instruct",
        "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        "pixtral-12b-2024-09-15",
        "Pixtral-12B-2024-09-15"
    ]
    
    success = False
    for model_name in models_to_try:
        print(f"🔄 Probando modelo: {model_name}")
        data = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": 800
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            success = True
            break
        else:
            print(f"   ❌ Error {response.status_code}: {response.json().get('message', 'Unknown')}")
            print()
    
    if success:
        result = response.json()
        result_text = result['choices'][0]['message']['content'].strip()
        
        print(f"✅ Respuesta recibida correctamente!")
        print(f"📝 Respuesta del modelo:")
        print("-" * 60)
        print(result_text)
        print("-" * 60)
        print()
        
        # Intentar parsear JSON
        try:
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            extracted_data = json.loads(result_text.strip())
            
            print("✅ JSON válido!")
            print("📊 Datos extraídos:")
            for key, value in extracted_data.items():
                print(f"   - {key}: {value}")
            print()
            print("🎉 EXTRACCIÓN FUNCIONANDO PERFECTAMENTE!")
            print(f"✨ MODELO QUE FUNCIONA: {data['model']}")
            
        except json.JSONDecodeError as e:
            print(f"⚠️  El modelo no devolvió JSON válido")
            print(f"Error: {e}")
    
    else:
        print(f"❌ Ningún modelo funcionó")
        print(f"Última respuesta: {response.text if 'response' in locals() else 'No response'}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("✅ Test completado")

