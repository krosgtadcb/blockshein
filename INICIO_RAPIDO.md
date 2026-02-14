# ⚡ INICIO RÁPIDO - 5 MINUTOS

## Paso 1: Descargar Python (2 minutos)
Si no lo tienes instalado:

**Windows**: https://www.python.org/downloads/
- Descarga "Windows installer"
- Durante la instalación, marca **"Add Python to PATH"**

**Mac**: 
```bash
brew install python3
```

**Linux**:
```bash
sudo apt-get install python3 python3-pip
```

---

## Paso 2: Descargar los Archivos (1 minuto)
Descargar estos 4 archivos a una carpeta (ej: `MiBlockchain/`):
- `blockchain.py`
- `app.py`
- `requirements.txt`
- `README.md` (opcional, pero útil)

---

## Paso 3: Instalar Dependencias (1 minuto)

### Windows/Mac/Linux:
```bash
cd MiBlockchain
pip install -r requirements.txt
```

O si tienes problemas:
```bash
pip install Flask==2.3.0 Flask-CORS==4.0.0 Werkzeug==2.3.0
```

---

## Paso 4: Ejecutar (1 minuto)

```bash
python app.py
```

Deberías ver:
```
🚀 Iniciando servidor CryptoChain...
📍 Abre el navegador en: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

---

## Paso 5: Abrir en Navegador (inmediato)

Abre tu navegador y ve a:
```
http://localhost:5000
```

---

## ✅ ¡LISTO!

Ahora puedes:

### 1. **Registrarte**
   - Haz clic en "Registrarse"
   - Pon tu email y contraseña
   - ¡Se crea tu billetera automáticamente!

### 2. **Minar Bloques**
   - Haz clic en "Minar Bloque"
   - Espera a que termine (10-30 segundos)
   - ¡Ganas 10 CryptoChain!

### 3. **Enviar Dinero**
   - Crea otro usuario (otra pestaña, incógnito)
   - Copia su dirección de billetera
   - En tu cuenta, pega la dirección
   - Pon la cantidad
   - ¡Se cobra 2% de comisión automáticamente!

### 4. **Ver Historial**
   - Tu historial se actualiza en tiempo real
   - Puedes ver quién te envió dinero

---

## 🆘 PROBLEMAS COMUNES

### ❌ "Port 5000 is already in use"
Otro programa usa el puerto. Solución:

**Windows (Command Prompt como Admin):**
```bash
netstat -ano | findstr :5000
taskkill /PID XXXX /F
```

**Mac/Linux:**
```bash
lsof -i :5000
kill -9 XXXX
```

### ❌ "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### ❌ "Python not found"
Python no está instalado o no está en PATH. Reinstálalo desde https://www.python.org/

### ❌ "Permission denied" (Mac/Linux)
```bash
chmod +x app.py
```

---

## 🎮 PRIMEROS PASOS

### Crear 2 usuarios y hacer transacciones:

1. **Usuario A**: Registrarse con email `a@test.com`
2. **Usuario B**: Registrarse con email `b@test.com` (otra pestaña)
3. **Usuario A**: Mina 3 bloques → Obtiene 30 CryptoChain
4. **Usuario B**: Mina 2 bloques → Obtiene 20 CryptoChain
5. **Usuario A**: Envía 10 CryptoChain a Usuario B
   - B recibe 10
   - A se queda sin 10.2 (10 + 2% comisión)
   - Se acumula 0.2 en comisiones
6. Alguien mina → Las comisiones se distribuyen a todos
7. Ambos ven en su historial la transacción

---

## 📊 QUÉ PASA CUANDO ENVÍAS DINERO

```
Tú envías 100 CryptoChain
        ↓
  Se calcula comisión: 2 CryptoChain
        ↓
Tu saldo: -102 CryptoChain
Saldo del otro: +100 CryptoChain
        ↓
Las 2 CryptoChain se distribuyen entre todos los mineros
cuando alguien mina el próximo bloque
```

---

## 📈 CÓMO FUNCIONAN LAS COMISIONES

Imaginemos 3 mineros (A, B, C):

1. **Usuario X** envía 50 CC a Usuario Y
   - Comisión = 1 CC
   - Se guarda esperando

2. **Usuario Z** envía 200 CC a Usuario Q
   - Comisión = 4 CC
   - Total acumulado = 5 CC

3. **Minero A** mina un bloque
   - Recibe: 10 (recompensa) + 5/3 = 11.67 CC
   - **Minero B** recibe: 5/3 = 1.67 CC
   - **Minero C** recibe: 5/3 = 1.67 CC

---

## 💡 CONSEJOS

✅ **Abre 2 navegadores** (o 2 pestañas incógnito) para probar con 2 usuarios

✅ **Mina algunos bloques** antes de enviar dinero

✅ **Haz transacciones** para que los mineros ganen comisiones

✅ **Actualiza el saldo** regularmente con el botón "Actualizar Saldo"

✅ **Mira el historial** para ver todas tus transacciones

---

## 📚 PRÓXIMOS PASOS

Después de probar lo básico:

1. Lee `README.md` para entender mejor cómo funciona
2. Lee `API_ENDPOINTS.md` si quieres automatizar
3. Lee `CONFIGURACION_AVANZADA.md` para personalizar

---

## 🎯 OBJETIVO LOGRADO

Ahora tienes un **blockchain funcional completo** con:
- ✅ Usuarios y autenticación
- ✅ Billeteras individuales
- ✅ Minería real (Proof of Work)
- ✅ Transacciones entre usuarios
- ✅ Comisiones automáticas
- ✅ Distribución de ganancias a mineros
- ✅ Interfaz web bonita

---

## 📞 ¿NECESITAS AYUDA?

Verifica:
1. Python está instalado: `python --version`
2. Las dependencias: `pip list | grep Flask`
3. El puerto 5000 no está en uso
4. Abre http://localhost:5000 en navegador

---

**¡Disfruta minando! 🚀⛓️💰**

*Próxima vez: Agrega Firebase para persistencia real*
