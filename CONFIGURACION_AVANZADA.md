# ⚙️ GUÍA AVANZADA - PERSONALIZACIÓN DEL BLOCKCHAIN

## 🎛️ Parámetros Configurables

### 1. Dificultad de Minería
En `app.py`, línea donde inicia blockchain:

```python
blockchain = Blockchain(difficulty=4)
```

**Cambiar dificultad:**
- `difficulty=3` → Minería más rápida (3-10 segundos)
- `difficulty=4` → Normal (10-30 segundos) ⭐
- `difficulty=5` → Más lenta (1-2 minutos)
- `difficulty=6` → Muy lenta (5-10 minutos)

### 2. Recompensa de Minería
En `blockchain.py`, clase `Blockchain.__init__`:

```python
self.mining_reward = 10  # Cambiar este valor
```

- `mining_reward = 5` → Menos cripto por bloque
- `mining_reward = 10` → Por defecto ⭐
- `mining_reward = 100` → Más cripto por bloque

### 3. Porcentaje de Comisión
En `blockchain.py`, clase `Transaction.__init__`:

```python
self.commission = amount * 0.02  # Cambiar 0.02 por otro valor
```

- `* 0.01` → 1% de comisión
- `* 0.02` → 2% de comisión ⭐
- `* 0.05` → 5% de comisión

### 4. Puerto del Servidor
En `app.py`, función `if __name__ == '__main__'`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

Cambiar `5000` por otro puerto (ej: 8000, 3000)

---

## 🔧 Ejemplos de Configuración

### Config 1: RED RÁPIDA (para pruebas)
```python
blockchain = Blockchain(difficulty=2)  # Muy rápido
mining_reward = 100  # Muchas monedas
commission = amount * 0.01  # 1%
```

### Config 2: RED REALISTA (similar a Bitcoin)
```python
blockchain = Blockchain(difficulty=6)  # Lento
mining_reward = 10  # Pocos coins
commission = amount * 0.02  # 2%
```

### Config 3: RED EDUCATIVA (equilibrada)
```python
blockchain = Blockchain(difficulty=4)  # Medio
mining_reward = 50  # Cantidad media
commission = amount * 0.05  # 5%
```

---

## 📊 Estadísticas de Performance

| Dificultad | Tiempo Promedio | CPU | Recomendación |
|-----------|-----------------|-----|---------------|
| 2 | 0.5-1s | Bajo | Pruebas rápidas |
| 3 | 3-5s | Bajo | Testing |
| 4 | 10-30s | Medio | Producción educativa ⭐ |
| 5 | 1-2min | Alto | Simulación realista |
| 6 | 5-10min | Muy Alto | Máxima seguridad |

---

## 🗄️ Base de Datos (Mejora Futura)

Para pasar de JSON a base de datos real:

```python
# Reemplazar:
# - users.json → PostgreSQL/MongoDB para usuarios
# - balances.json → Base de datos para saldos
# - Blockchain en memoria → Base de datos persistente
```

---

## 🔐 Mejoras de Seguridad

### Para Producción

1. **Usar HTTPS**
   ```python
   # Instalar: pip install pyopenssl
   app.run(ssl_context='adhoc')
   ```

2. **Variables de Entorno**
   ```python
   import os
   app.secret_key = os.environ.get('SECRET_KEY')
   ```

3. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: session['email'])
   ```

4. **Validación de Email**
   ```python
   from email_validator import validate_email
   validate_email(email)
   ```

---

## 📈 Monitoreo

### Ver logs en tiempo real
```bash
# En la consola, verás:
# [2024-XX-XX] Bloque minado: abc123...
# [2024-XX-XX] Transacción recibida: user -> user2
```

### Estadísticas de la red
```
GET /api/stats
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

## 🚀 Escalabilidad

### Problema: ¿Qué pasa con muchos usuarios?

**Solución 1: Usar bases de datos reales**
```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    wallet = db.Column(db.String(120))
    # ...
```

**Solución 2: Cacheo con Redis**
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

**Solución 3: Separar en múltiples servidores**
- Servidor 1: Blockchain
- Servidor 2: API
- Servidor 3: Web

---

## 💾 Persistencia de Blockchain

Para guardar blockchain en disco:

```python
import pickle

# Guardar
with open('blockchain.pkl', 'wb') as f:
    pickle.dump(blockchain, f)

# Cargar
with open('blockchain.pkl', 'rb') as f:
    blockchain = pickle.load(f)
```

---

## 🧪 Testing

Crear archivo `test_blockchain.py`:

```python
from blockchain import Blockchain, Transaction

def test_blockchain():
    bc = Blockchain(difficulty=2)
    
    # Test 1: Crear transacción
    tx = Transaction("user1", "user2", 10)
    assert bc.add_transaction(tx)
    
    # Test 2: Minar bloque
    block = bc.mine_pending_transactions("miner1")
    assert block is not None
    
    # Test 3: Validar cadena
    assert bc.is_chain_valid()
    
    print("✅ Todos los tests pasaron")

if __name__ == '__main__':
    test_blockchain()
```

Ejecutar:
```bash
python test_blockchain.py
```

---

## 📚 Recursos de Aprendizaje

- **Bitcoin Whitepaper**: https://bitcoin.org/bitcoin.pdf
- **Ethereum Yellow Paper**: https://ethereum.org/en/whitepaper/
- **Proof of Work**: https://en.wikipedia.org/wiki/Proof_of_work
- **Hashing SHA-256**: https://en.wikipedia.org/wiki/SHA-2

---

## 🎯 Próximos Pasos

1. ✅ **Blockchain básico** (ya hecho)
2. ⬜ Agregar firmas digitales (ECDSA)
3. ⬜ Implementar Smart Contracts
4. ⬜ Crear CLI para herramientas
5. ⬜ Agregar visualización de bloques
6. ⬜ Implementar consensus distribuido

---

**¡Gracias por usar CryptoChain! 🚀**
