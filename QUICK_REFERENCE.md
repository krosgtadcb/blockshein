# 🎯 QUICK REFERENCE - CRYPTOCHAIN

## ⚡ INSTALAR EN 3 COMANDOS

```bash
pip install -r requirements.txt
python app.py
# Abre: http://localhost:5000
```

---

## 📊 COMPONENTES PRINCIPALES

```
┌─────────────┐
│  BLOCKCHAIN │ → blockchain.py (motor)
└─────────────┘

┌─────────────┐
│  SERVIDOR   │ → app.py (Flask)
└─────────────┘

┌─────────────┐
│  INTERFAZ   │ → HTML/CSS/JS en app.py
└─────────────┘
```

---

## 🎮 FUNCIONALIDADES

✅ **Autenticación**
- Registro de usuarios
- Login seguro
- Billetera automática

✅ **Minería**
- Proof of Work real
- Recompensa: 10 CC/bloque
- Dificultad ajustable

✅ **Transacciones**
- Envío entre usuarios
- Validación de saldo
- Comisión: 2%

✅ **Comisiones**
- Acumulación automática
- Distribución equitativa
- A TODOS los mineros

✅ **Blockchain**
- Cadena de bloques
- Validación de integridad
- Historial completo

---

## 💻 VERSIÓN RÁPIDA

Si quieres SOLO el blockchain sin web:

```python
from blockchain import Blockchain, Transaction

# Crear blockchain
bc = Blockchain(difficulty=4)

# Registrar usuario
bc.balances["alice"] = 0
bc.all_miners.add("alice")

# Minar
bc.mine_pending_transactions("alice")
print(bc.get_balance("alice"))  # 10

# Transacción
tx = Transaction("alice", "bob", 5)
bc.add_transaction(tx)

# Minar nuevamente (procesa transacción)
bc.mine_pending_transactions("alice")
print(bc.get_balance("alice"))  # ~14.975 (10 + recompensa + comisión)
print(bc.get_balance("bob"))    # 5

# Validar cadena
print(bc.is_chain_valid())  # True
```

---

## 🌐 VERSIÓN WEB (Recomendado)

```bash
python app.py
```

Luego abre `http://localhost:5000` y usa la interfaz gráfica.

---

## 📱 API REST

### Obtener saldo
```bash
curl http://localhost:5000/api/balance/wallet_id
```

### Minar
```bash
curl -X POST http://localhost:5000/api/mine \
  -b cookies.txt
```

### Enviar dinero
```bash
curl -X POST http://localhost:5000/api/transaction \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"receiver":"otro_id","amount":10}'
```

### Estadísticas
```bash
curl http://localhost:5000/api/stats
```

---

## 🔧 CAMBIAR PARÁMETROS

### Dificultad (blockchain.py)
```python
blockchain = Blockchain(difficulty=4)  # Cambiar 4
```

### Recompensa de minería (blockchain.py)
```python
self.mining_reward = 10  # Cambiar 10
```

### Comisión (blockchain.py)
```python
self.commission = amount * 0.02  # Cambiar 0.02
```

### Puerto (app.py)
```python
app.run(..., port=5000)  # Cambiar 5000
```

---

## 📊 ESTADÍSTICAS EN TIEMPO REAL

En la web, haz clic en **"Estadísticas"** para ver:
- Bloques minados
- Usuarios registrados
- Mineros activos
- Transacciones pendientes
- Saldo total de la red

---

## 🏆 EJEMPLO COMPLETO

### 1. Usuario A se registra
```
Email: alice@test.com
Contraseña: abc123
Wallet: a1b2c3d4e5f6
Saldo: 0
```

### 2. Usuario A mina un bloque
```
+10 CryptoChain
Saldo: 10
```

### 3. Usuario B se registra
```
Email: bob@test.com
Contraseña: xyz789
Wallet: x7y8z9a0b1c2
Saldo: 0
```

### 4. Usuario B mina un bloque
```
+10 CryptoChain
Saldo: 10
```

### 5. Usuario A envía 3 CC a B
```
A pierde: 3 + 0.06 (comisión 2%) = 3.06
B recibe: 3
Comisiones pendientes: 0.06
```

### 6. Usuario A mina otro bloque
```
A recibe: 10 (minería) + 0.03 (su parte de comisión)
B recibe: 0.03 (su parte de comisión)
Saldo A: 10 - 3.06 + 10 + 0.03 = 16.97
Saldo B: 10 + 3 + 0.03 = 13.03
```

---

## 🚨 ERRORES COMUNES

| Error | Solución |
|-------|----------|
| "Port 5000 already in use" | Cambiar puerto en app.py |
| "No module named 'flask'" | `pip install -r requirements.txt` |
| "ModuleNotFoundError: blockchain" | Asegúrate blockchain.py esté en misma carpeta |
| "Permission denied" (Mac) | `chmod +x app.py` |
| "ConnectionRefused" | `python app.py` no está corriendo |

---

## 📈 DIFÍCULTAD vs TIEMPO

| Dificultad | Tiempo Promedio | Caso de Uso |
|-----------|-----------------|------------|
| 2 | < 1 segundo | Pruebas |
| 3 | 3-5 segundos | Testing |
| 4 | 10-30 segundos | Normal ⭐ |
| 5 | 1-2 minutos | Realista |
| 6 | 5-10 minutos | Máxima seguridad |

---

## 💰 FLUJO DE DINERO

```
USUARIO MINA:         Alice mina
  └─ +10 CC           Alice: 10

USUARIO ENVÍA:        Alice → Bob: 5 CC
  ├─ Receptor +5      Bob: 5
  ├─ Comisión 0.1     Comisiones: 0.1
  └─ Alice -5.1       Alice: 4.9

SIGUIENTE MINERÍA:    Carol mina
  ├─ Carol +10        Carol: 10
  ├─ Alice +0.05      Alice: 4.95
  └─ Bob +0.05        Bob: 5.05
```

---

## 🔐 ARCHIVOS GENERADOS

```
users.json       ← Usuarios y contraseñas (encriptadas)
balances.json    ← Backup de saldos (JSON)
__pycache__/     ← Cache Python (ignorar)
```

---

## 📖 DOCUMENTACIÓN RÁPIDA

| Archivo | Contenido | Tamaño |
|---------|----------|--------|
| INICIO_RAPIDO.md | Empezar en 5 min | 4KB |
| README.md | Manual completo | 7KB |
| ARQUITECTURA_FLUJOS.md | Diagramas visuales | 24KB |
| API_ENDPOINTS.md | Referencia API | 9KB |
| CONFIGURACION_AVANZADA.md | Personalización | 5KB |

---

## 🎯 CHECKLIST

- [ ] Python 3.7+ instalado
- [ ] `pip install -r requirements.txt`
- [ ] `python app.py` sin errores
- [ ] Navegador: http://localhost:5000
- [ ] Registrar usuario de prueba
- [ ] Minar un bloque
- [ ] Ver saldo aumentó en 10
- [ ] Crear segundo usuario
- [ ] Enviar dinero entre usuarios
- [ ] Ver comisiones distribuidas

---

## 🌍 CASOS DE USO

```
┌─────────────────┐
│   EDUCACIÓN     │ → Enseñar blockchain
├─────────────────┤
│   PRUEBAS       │ → Entender cómo funciona
├─────────────────┤
│ EXPERIMENTACIÓN │ → Crear variantes
├─────────────────┤
│  INTEGRACIÓN    │ → Conectar con otros sistemas
├─────────────────┤
│  PRODUCCIÓN*    │ → *Necesita mejoras de seguridad
└─────────────────┘
```

---

## 🚀 PRÓXIMOS PASOS

1. **Domina lo básico** (1 semana)
   - Usa la interfaz
   - Entiende los flujos
   - Lee la documentación

2. **Personaliza** (1 semana)
   - Cambia parámetros
   - Agrega nuevas funciones
   - Experimenta con dificultad

3. **Integra** (2 semanas)
   - Crea scripts de automatización
   - Conecta con APIs externas
   - Construye herramientas

4. **Mejora** (continuo)
   - Seguridad
   - Base de datos real
   - Mejor interfaz
   - Distribución

---

## 💡 TIPS PRO

1. 🔑 Abre dos navegadores para probar con 2 usuarios
2. ⚡ Dificultad=2 para testing rápido
3. 📊 Usa `/api/stats` para monitoreo
4. 🔄 Actualiza saldo manualmente si es necesario
5. 💾 Guarda users.json antes de experimentar
6. 🧪 Prueba en incógnito para usuarios nuevos
7. 📱 La API funciona desde cualquier cliente

---

## 📞 SOPORTE RÁPIDO

**¿Cómo inicio?**
→ Lee INICIO_RAPIDO.md (5 min)

**¿Cómo funciona?**
→ Lee ARQUITECTURA_FLUJOS.md

**¿Qué puedo hacer?**
→ Lee README.md

**¿Cómo integro?**
→ Lee API_ENDPOINTS.md

**¿Cómo cambio cosas?**
→ Lee CONFIGURACION_AVANZADA.md

---

## ✨ RESUMEN

```
🎯 OBJETIVO: Sistema blockchain completo ✅

✅ Motor blockchain         (blockchain.py)
✅ Servidor web            (app.py)
✅ Interfaz gráfica        (HTML+CSS+JS)
✅ Autenticación           (usuarios + passwords)
✅ Minería real            (Proof of Work)
✅ Transacciones           (entre usuarios)
✅ Comisiones              (distribuidas)
✅ API REST                (para integrar)
✅ Documentación           (9 archivos)

ESTADO: Completo y funcional 🚀
```

---

**¡Listo para empezar! ⛓️💰🚀**

Ejecuta:
```bash
pip install -r requirements.txt
python app.py
```

Luego abre: http://localhost:5000
