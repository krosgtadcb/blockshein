# 🔗 CryptoChain - Sistema Blockchain Completo

Un sistema blockchain funcional con interfaz web, minería de bloques, transferencias de criptomoneda y distribución de comisiones entre mineros.

## ✨ Características

### 1. **Blockchain Completo**
- ✅ Implementación real de blockchain con Proof of Work (PoW)
- ✅ Sistema de hashing SHA-256
- ✅ Validación de cadena e integridad
- ✅ Bloques minables con dificultad ajustable

### 2. **Sistema de Autenticación**
- ✅ Registro de usuarios con contraseña encriptada
- ✅ Login seguro con sesiones
- ✅ Billetera única por usuario (dirección pública)

### 3. **Minería de Bloques**
- ✅ Algoritmo Proof of Work (PoW)
- ✅ Recompensa de 10 CryptoChain por bloque minado
- ✅ Dificultad ajustable (4 ceros iniciales por defecto)

### 4. **Sistema de Transacciones**
- ✅ Transferencias entre usuarios
- ✅ Validación de saldo
- ✅ Comisión automática del 2% por transacción

### 5. **Distribución de Comisiones**
- ✅ Cada transacción genera 2% de comisión
- ✅ Las comisiones se distribuyen EQUITATIVAMENTE entre todos los mineros
- ✅ Se acumulan y pagan en el próximo bloque minado

### 6. **Interfaz Web**
- ✅ Dashboard moderno con tema dark/neon
- ✅ Visualización de saldo en tiempo real
- ✅ Historial de transacciones
- ✅ Estadísticas de la red
- ✅ Responsive (funciona en móvil)

---

## 🚀 Instalación y Uso

### Paso 1: Instalar Python (si no lo tienes)
```bash
# En Windows
# Descarga desde https://www.python.org/downloads/
# Asegúrate de marcar "Add Python to PATH"

# En Mac
brew install python3

# En Linux
sudo apt-get install python3 python3-pip
```

### Paso 2: Clonar o descargar los archivos
```bash
# Coloca estos archivos en una carpeta:
# - blockchain.py
# - app.py
# - requirements.txt
```

### Paso 3: Instalar dependencias
```bash
cd ruta/a/la/carpeta
pip install -r requirements.txt
```

### Paso 4: Ejecutar el servidor
```bash
python app.py
```

### Paso 5: Abrir en navegador
```
http://localhost:5000
```

---

## 📖 Cómo Usar

### 1. **Crear una Cuenta**
- Haz clic en "Registrarse"
- Ingresa email y contraseña
- ¡Listo! Se crea tu billetera automáticamente

### 2. **Entrar a tu Cuenta**
- Ingresa email y contraseña
- Accede a tu dashboard

### 3. **Minar Bloques**
- Haz clic en el botón "Minar Bloque"
- El sistema calcula el Proof of Work
- Recibirás 10 CryptoChain cuando se complete

### 4. **Enviar Criptomoneda**
- En la tarjeta "Enviar Criptomoneda"
- Pega la dirección del receptor (de otro usuario)
- Ingresa la cantidad
- ¡Se aplica 2% de comisión automáticamente!

### 5. **Ver Historial**
- Tu historial de transacciones se actualiza automáticamente
- Puedes ver enviadas (↗️) y recibidas (↙️)

### 6. **Ver Estadísticas**
- Haz clic en "Estadísticas" en la barra superior
- Verás info de toda la red

---

## 🔑 Conceptos Clave

### **Blockchain**
Una cadena de bloques donde cada bloque contiene transacciones y referencia al bloque anterior.

### **Minería (Proof of Work)**
Resolver un problema matemático para agregar un bloque nuevo a la cadena. Requiere encontrar un número (nonce) tal que el hash del bloque comience con 4 ceros.

### **Comisiones Distribuidas**
```
Usuario A envía 100 CryptoChain a Usuario B
↓
Comisión = 100 × 2% = 2 CryptoChain
↓
Si hay 5 mineros en la red:
Cada minero recibe 2 ÷ 5 = 0.4 CryptoChain
↓
Cuando alguien mina el próximo bloque,
todos los mineros reciben sus comisiones
```

### **Billetera**
Tu dirección única en la red. Se crea automáticamente al registrarte. Ejemplo:
```
d3f42a1c9b7e
```

---

## 📊 Ejemplo de Uso Práctico

```
1. María se registra → Billetera: maria_wallet
2. Juan se registra → Billetera: juan_wallet
3. María mina 3 bloques → María tiene 30 CryptoChain
4. Juan mina 2 bloques → Juan tiene 20 CryptoChain
5. María envía 5 CryptoChain a Juan
   - Cantidad: 5
   - Comisión: 0.1
   - Total deducido de María: 5.1
   - Juan recibe: 5
   - Se acumulan 0.1 en comisiones
6. Alguien mina el siguiente bloque
   - Ese minero recibe 10 (recompensa) + su parte de comisiones
   - María recibe su parte de comisiones (0.05)
   - Juan recibe su parte de comisiones (0.05)
```

---

## 🔐 Seguridad

⚠️ **IMPORTANTE**: Este es un proyecto educativo. Para producción se necesitaría:
- Base de datos real (PostgreSQL, MongoDB)
- Validación de firmas digitales
- HTTPS obligatorio
- Rate limiting
- Protección contra ataques

---

## 📁 Estructura de Archivos

```
proyecto/
├── blockchain.py       # Motor de blockchain
├── app.py             # Servidor Flask + Frontend
├── requirements.txt   # Dependencias
├── users.json         # Datos de usuarios (se crea)
└── balances.json      # Saldos (se crea)
```

---

## 🛠️ Desarrollo y Debugging

### Ver blockchain completa
```
GET http://localhost:5000/api/chain
```

### Ver estadísticas de la red
```
GET http://localhost:5000/api/stats
```

### Ver historial de un usuario
```
GET http://localhost:5000/api/history/{wallet_address}
```

### Ver transacciones pendientes
```
GET http://localhost:5000/api/pending-transactions
```

---

## ❓ Preguntas Frecuentes

**P: ¿Cuánto tiempo tarda minar un bloque?**
R: Con dificultad 4, entre 5-30 segundos en una máquina normal.

**P: ¿Puedo cambiar la dificultad?**
R: Sí, en `blockchain.py` línea: `blockchain = Blockchain(difficulty=4)`

**P: ¿Puedo usar esto en la web real?**
R: No directamente. Necesitarías bases de datos reales y seguridad adicional.

**P: ¿Cómo se distribuyen las comisiones?**
R: Equitativamente entre TODOS los mineros registrados en la red.

---

## 📝 Notas de Desarrollo

- Las contraseñas se encriptan con Werkzeug
- Las sesiones se almacenan en servidor (Flask session)
- Los datos persisten en JSON (users.json, balances.json)
- El blockchain es en memoria (se reinicia al reiniciar el servidor)

---

## 🚨 Solución de Problemas

### Error: "Port 5000 is already in use"
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID {PID} /F

# Mac/Linux
lsof -i :5000
kill -9 {PID}
```

### Error: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Error: "Permission denied" (Mac/Linux)
```bash
chmod +x app.py
```

---

## 📞 Soporte

Si tienes problemas:
1. Verifica que Python 3.7+ esté instalado
2. Revisa que todas las dependencias estén instaladas
3. Comprueba que el puerto 5000 esté libre
4. Reinicia el servidor

---

## 🎓 Aprendizaje

Este proyecto enseña:
- Estructuras de datos (blockchain)
- Criptografía (hashing SHA-256)
- Conceptos de PoW (Proof of Work)
- Desarrollo backend (Flask)
- Desarrollo frontend (HTML/CSS/JS)
- Gestión de transacciones
- Sistemas de comisiones

---

**¡Disfruta minando! ⛓️💰**
