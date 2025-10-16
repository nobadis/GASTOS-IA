# 🚀 Guía Completa de Configuración de APIs

## 🏆 MEJORES OPCIONES (Precio vs Calidad)

### 1. 🥇 **LLAMA 3.3 70B - NOVITA AI** (RECOMENDADO)
- **💰 Precio**: $0.04 por millón de tokens (50x más barato que GPT-4)
- **⚡ Velocidad**: Muy rápida
- **🎯 Calidad**: Excelente para extracción de datos
- **🆓 Prueba**: $0.5 gratis para empezar

### 2. 🥈 **GROQ** (GRATIS)
- **💰 Precio**: $0.00 (completamente gratis)
- **⚡ Velocidad**: Súper rápida
- **🎯 Calidad**: Buena para extracción
- **🆓 Prueba**: Sin límites

### 3. 🥉 **OpenAI** (PREMIUM)
- **💰 Precio**: ~$5 por millón de tokens
- **⚡ Velocidad**: Buena
- **🎯 Calidad**: Excelente
- **🆓 Prueba**: $5 gratis inicial

---

## 📋 CONFIGURACIÓN PASO A PASO

### 🥇 **OPCIÓN 1: LLAMA 3.3 70B (Novita AI)**

#### **1. Crear cuenta**
- Ve a: https://api.novita.ai/
- Haz clic en "Sign Up"
- Completa el registro

#### **2. Obtener API Key**
- Una vez logueado, ve a "Settings" → "API Keys"
- Crea una nueva API key
- Copia la key (empieza con "nvta-...")

#### **3. Configurar en la app**
```python
# En config_api.py, descomenta y pega tu key:
NOVITA_API_KEY = "nvta-1234567890abcdef..."
```

#### **4. Costos estimados**
- **Extracción de ticket**: ~$0.0001 por ticket
- **1000 tickets**: ~$0.10
- **10,000 tickets**: ~$1.00

---

### 🥈 **OPCIÓN 2: GROQ (Gratis)**

#### **1. Crear cuenta**
- Ve a: https://console.groq.com/
- Haz clic en "Sign Up"
- Completa el registro

#### **2. Obtener API Key**
- Ve a "API Keys"
- Crea una nueva key
- Copia la key (empieza con "gsk_...")

#### **3. Configurar en la app**
```python
# En config_api.py, descomenta y pega tu key:
GROQ_API_KEY = "gsk_1234567890abcdef..."
```

#### **4. Límites**
- **Gratis**: 14,400 requests/día
- **Suficiente para**: Uso personal y pequeñas empresas

---

### 🥉 **OPCIÓN 3: OpenAI (Premium)**

#### **1. Crear cuenta**
- Ve a: https://platform.openai.com/
- Haz clic en "Sign Up"
- Añade método de pago

#### **2. Obtener API Key**
- Ve a "API Keys"
- Crea una nueva key
- Copia la key (empieza con "sk-...")

#### **3. Configurar en la app**
```python
# En config_api.py, descomenta y pega tu key:
OPENAI_API_KEY = "sk-1234567890abcdef..."
```

#### **4. Costos estimados**
- **Extracción de ticket**: ~$0.005 por ticket
- **1000 tickets**: ~$5.00
- **10,000 tickets**: ~$50.00

---

## 🔧 CONFIGURACIÓN FINAL

### **1. Editar config_api.py**
```python
# Descomenta la línea de tu API elegida:

# OPCIÓN 1: Novita AI (Recomendado)
NOVITA_API_KEY = "tu-api-key-aquí"

# OPCIÓN 2: Groq (Gratis)
# GROQ_API_KEY = "tu-api-key-aquí"

# OPCIÓN 3: OpenAI (Premium)
# OPENAI_API_KEY = "tu-api-key-aquí"
```

### **2. Reiniciar la aplicación**
```bash
# Detener la app (Ctrl+C)
# Volver a ejecutar:
python app.py
```

### **3. Verificar funcionamiento**
- Abre http://localhost:5000
- Toma foto de un ticket
- Deberías ver: "✅ Extracción con [API] completada"

---

## 🎯 RECOMENDACIONES

### **Para uso personal**
- **Opción 1**: GROQ (gratis)
- **Opción 2**: Novita AI (muy económico)

### **Para empresas pequeñas**
- **Opción 1**: Novita AI (mejor precio/calidad)
- **Opción 2**: GROQ (gratis hasta límites)

### **Para empresas grandes**
- **Opción 1**: Novita AI (muy económico)
- **Opción 2**: OpenAI (máxima precisión)

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### **Error: "Invalid API key"**
1. Verifica que copiaste la key completa
2. Verifica que no hay espacios extra
3. Verifica que la key no esté expirada

### **Error: "Rate limit exceeded"**
1. **Groq**: Espera a que se reinicie el límite diario
2. **Novita/OpenAI**: Recarga créditos

### **Error: "Connection failed"**
1. Verifica tu conexión a internet
2. Verifica que la URL base sea correcta
3. Reinicia la aplicación

---

## 💡 CONSEJOS DE OPTIMIZACIÓN

### **Para reducir costos**
1. Usa GROQ para desarrollo/pruebas
2. Usa Novita AI para producción
3. Configura límites de uso

### **Para mejorar precisión**
1. Usa imágenes con buena iluminación
2. Mantén los tickets planos
3. Usa OpenAI para casos críticos

### **Para mejorar velocidad**
1. Usa GROQ (más rápido)
2. Reduce el tamaño de las imágenes
3. Usa procesamiento en lote

---

## 🎉 ¡LISTO!

Con cualquiera de estas opciones configuradas, tu aplicación podrá:
- ✅ Extraer automáticamente importes de tickets
- ✅ Detectar fechas y descripciones
- ✅ Categorizar gastos automáticamente
- ✅ Procesar múltiples monedas
- ✅ Funcionar sin instalación de OCR

**¡Disfruta de tu gestor de gastos inteligente! 🚀** 