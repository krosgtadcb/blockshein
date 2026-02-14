# 📡 GUÍA DE API - CryptoChain

## 🔗 Endpoints Disponibles

Todos los endpoints retornan JSON. El servidor corre en `http://localhost:5000`

---

## 🔐 AUTENTICACIÓN

### 1. Registrarse
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "mi_contraseña_segura"
  }'
```

**Respuesta:**
```json
{
  "message": "Usuario registrado exitosamente",
  "wallet_address": "a1b2c3d4e5f6g7h8"
}
```

### 2. Iniciar Sesión
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "usuario@example.com",
    "password": "mi_contraseña_segura"
  }'
```

**Respuesta:**
```json
{
  "message": "Sesión iniciada",
  "wallet_address": "a1b2c3d4e5f6g7h8",
  "email": "usuario@example.com"
}
```

### 3. Obtener Usuario Actual
```bash
curl -X GET http://localhost:5000/api/user \
  -b cookies.txt
```

**Respuesta:**
```json
{
  "email": "usuario@example.com",
  "wallet_address": "a1b2c3d4e5f6g7h8",
  "balance": 150.75
}
```

### 4. Cerrar Sesión
```bash
curl -X POST http://localhost:5000/api/logout \
  -b cookies.txt
```

---

## 💰 BILLETERA Y SALDO

### Obtener Saldo
```bash
curl -X GET "http://localhost:5000/api/balance/a1b2c3d4e5f6g7h8"
```

**Respuesta:**
```json
{
  "wallet_address": "a1b2c3d4e5f6g7h8",
  "balance": 150.75
}
```

---

## ⚒️ MINERÍA

### Minar un Bloque
```bash
curl -X POST http://localhost:5000/api/mine \
  -b cookies.txt
```

**Respuesta:**
```json
{
  "message": "Bloque minado exitosamente",
  "block": {
    "index": 5,
    "hash": "0000abc123def456...",
    "nonce": 42381,
    "transactions": [...]
  },
  "miner_reward": 10,
  "new_balance": 160.75
}
```

### Obtener Transacciones Pendientes
```bash
curl -X GET http://localhost:5000/api/pending-transactions
```

**Respuesta:**
```json
{
  "count": 3,
  "transactions": [
    {
      "sender": "usuario1",
      "receiver": "usuario2",
      "amount": 25.5,
      "commission": 0.51,
      "timestamp": 1234567890.123
    },
    ...
  ]
}
```

---

## 💸 TRANSACCIONES

### Enviar Criptomoneda
```bash
curl -X POST http://localhost:5000/api/transaction \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "receiver": "x7y8z9a0b1c2d3e4",
    "amount": 50
  }'
```

**Respuesta:**
```json
{
  "message": "Transacción creada",
  "transaction": {
    "sender": "a1b2c3d4e5f6g7h8",
    "receiver": "x7y8z9a0b1c2d3e4",
    "amount": 50,
    "commission": 1.0,
    "timestamp": 1234567890.123
  },
  "commission": 1.0
}
```

### Obtener Historial de Transacciones
```bash
curl -X GET "http://localhost:5000/api/history/a1b2c3d4e5f6g7h8"
```

**Respuesta:**
```json
{
  "history": [
    {
      "sender": "a1b2c3d4e5f6g7h8",
      "receiver": "x7y8z9a0b1c2d3e4",
      "amount": 50,
      "commission": 1.0,
      "timestamp": 1234567890.123,
      "block_index": 5
    },
    {
      "sender": "SISTEMA",
      "receiver": "a1b2c3d4e5f6g7h8",
      "amount": 10,
      "commission": 0,
      "timestamp": 1234567889.456,
      "block_index": 4
    }
  ]
}
```

---

## ⛓️ BLOCKCHAIN

### Obtener Toda la Cadena
```bash
curl -X GET http://localhost:5000/api/chain
```

**Respuesta:**
```json
{
  "length": 5,
  "is_valid": true,
  "chain": [
    {
      "index": 0,
      "timestamp": 1234567800.123,
      "hash": "0000abc123def456...",
      "previous_hash": "0",
      "nonce": 0,
      "transactions": []
    },
    {
      "index": 1,
      "timestamp": 1234567810.456,
      "hash": "0000def789ghi012...",
      "previous_hash": "0000abc123def456...",
      "nonce": 42381,
      "transactions": [...]
    }
  ]
}
```

### Obtener Estadísticas
```bash
curl -X GET http://localhost:5000/api/stats
```

**Respuesta:**
```json
{
  "total_blocks": 42,
  "total_users": 15,
  "total_miners": 8,
  "pending_transactions": 3,
  "total_balance": 1250.50,
  "difficulty": 4
}
```

---

## 🐍 EJEMPLOS EN PYTHON

### Instalación de requests
```bash
pip install requests
```

### Script Completo
```python
import requests
import json

# Configuración
BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

# 1. Registrarse
def register(email, password):
    response = SESSION.post(f"{BASE_URL}/api/register", json={
        "email": email,
        "password": password
    })
    return response.json()

# 2. Iniciar sesión
def login(email, password):
    response = SESSION.post(f"{BASE_URL}/api/login", json={
        "email": email,
        "password": password
    })
    return response.json()

# 3. Obtener usuario actual
def get_user():
    response = SESSION.get(f"{BASE_URL}/api/user")
    return response.json()

# 4. Obtener saldo
def get_balance(wallet_address):
    response = SESSION.get(f"{BASE_URL}/api/balance/{wallet_address}")
    return response.json()

# 5. Enviar transacción
def send_transaction(receiver, amount):
    response = SESSION.post(f"{BASE_URL}/api/transaction", json={
        "receiver": receiver,
        "amount": amount
    })
    return response.json()

# 6. Minar bloque
def mine_block():
    response = SESSION.post(f"{BASE_URL}/api/mine")
    return response.json()

# 7. Obtener historial
def get_history(wallet_address):
    response = SESSION.get(f"{BASE_URL}/api/history/{wallet_address}")
    return response.json()

# 8. Obtener estadísticas
def get_stats():
    response = SESSION.get(f"{BASE_URL}/api/stats")
    return response.json()

# 9. Obtener blockchain completa
def get_chain():
    response = SESSION.get(f"{BASE_URL}/api/chain")
    return response.json()

# EJEMPLO DE USO
if __name__ == "__main__":
    print("=== CryptoChain API Demo ===\n")
    
    # Registrar usuario
    print("1. Registrando usuario...")
    result = register("demo@example.com", "password123")
    print(json.dumps(result, indent=2))
    wallet = result.get("wallet_address")
    
    # Iniciar sesión
    print("\n2. Iniciando sesión...")
    result = login("demo@example.com", "password123")
    print(json.dumps(result, indent=2))
    
    # Obtener usuario
    print("\n3. Obteniendo datos del usuario...")
    result = get_user()
    print(json.dumps(result, indent=2))
    
    # Minar bloque
    print("\n4. Minando bloque...")
    result = mine_block()
    print(json.dumps(result, indent=2))
    
    # Ver saldo
    print("\n5. Verificando saldo...")
    result = get_balance(wallet)
    print(json.dumps(result, indent=2))
    
    # Obtener estadísticas
    print("\n6. Estadísticas de la red...")
    result = get_stats()
    print(json.dumps(result, indent=2))
    
    print("\n✅ Demo completado!")
```

---

## 🧪 TESTING CON cURL

### Script Bash Automatizado
```bash
#!/bin/bash

BASE_URL="http://localhost:5000"
EMAIL="test@example.com"
PASSWORD="test123"

echo "=== CryptoChain API Testing ==="

# Registrar
echo -e "\n📝 Registrando usuario..."
curl -X POST $BASE_URL/api/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}"

# Iniciar sesión
echo -e "\n\n🔐 Iniciando sesión..."
curl -X POST $BASE_URL/api/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}"

# Ver usuario
echo -e "\n\n👤 Datos del usuario..."
curl -X GET $BASE_URL/api/user \
  -b cookies.txt

# Minar
echo -e "\n\n⚒️  Minando bloque..."
curl -X POST $BASE_URL/api/mine \
  -b cookies.txt

# Estadísticas
echo -e "\n\n📊 Estadísticas..."
curl -X GET $BASE_URL/api/stats

echo -e "\n\n✅ Testing completado!"
```

---

## 📋 CÓDIGOS DE ESTADO HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 500 | Server Error - Error del servidor |

---

## 🔄 FLUJO COMPLETO DE EJEMPLO

```
1. POST /api/register
   → Crear usuario y billetera

2. POST /api/login
   → Iniciar sesión

3. POST /api/mine (usuario A)
   → Obtiene 10 CryptoChain

4. POST /api/mine (usuario B)
   → Obtiene 10 CryptoChain

5. POST /api/transaction (usuario A → usuario B, 5 CC)
   → Transacción creada (comisión 0.1 CC)

6. POST /api/mine (usuario A)
   → Bloque minado
   → Usuario A: +10 (recompensa) +0.05 (comisión)
   → Usuario B: +0.05 (comisión)

7. GET /api/history/{wallet_A}
   → Ver todas las transacciones
```

---

## ⚡ OPTIMIZACIONES

### Hacer Multiple Requests
```python
import concurrent.futures

def mine_multiple_blocks(n_blocks):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(mine_block) for _ in range(n_blocks)]
        return [f.result() for f in futures]
```

### Esperar Bloques Pendientes
```python
def wait_for_blocks_to_mine(timeout=300):
    import time
    start = time.time()
    while time.time() - start < timeout:
        stats = get_stats()
        if stats['pending_transactions'] == 0:
            return True
        time.sleep(5)
    return False
```

---

**¡Listo para integrar! 🚀**
