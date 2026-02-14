# 🔧 SOLUCIÓN DE ERRORES - Python 3.14

## Error: AttributeError: module 'pkgutil' has no attribute 'get_loader'

Este error ocurre cuando Flask 2.3.0 no es compatible con Python 3.14.

### ✅ SOLUCIÓN RÁPIDA

Actualiza Flask a versión 3.0.0 o superior:

```bash
pip install --upgrade Flask==3.0.0
```

O actualiza todos:

```bash
pip install --upgrade -r requirements.txt
```

O instala las versiones correctas:

```bash
pip install Flask==3.0.0 Flask-CORS==4.0.0 Werkzeug==3.0.0
```

---

## Si aún no funciona, intenta esto:

### Opción 1: Crear virtualenv nuevo

```bash
# Eliminar virtualenv viejo
rm -rf .venv

# Crear nuevo
python -m venv .venv

# Activar
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Opción 2: Instalar directamente sin virtualenv

```bash
# Windows
python -m pip install --upgrade Flask==3.0.0 Werkzeug==3.0.0 Flask-CORS==4.0.0

# Mac/Linux
pip3 install --upgrade Flask==3.0.0 Werkzeug==3.0.0 Flask-CORS==4.0.0
```

### Opción 3: Usar Python 3.11 o 3.12 (más estable)

Si el error persiste, considera usar Python 3.11 o 3.12 que son más estables:

```bash
# Descargar desde https://www.python.org/downloads/
# Selecciona Python 3.11 o 3.12
```

---

## Versiones compatibles:

### Python 3.14 (más nuevo):
```
Flask==3.0.0+
Werkzeug==3.0.0+
```

### Python 3.12 / 3.13:
```
Flask==3.0.0+
Werkzeug==3.0.0+
```

### Python 3.11:
```
Flask==2.3.0 o Flask==3.0.0
Werkzeug==2.3.0 o Werkzeug==3.0.0
```

### Python 3.10:
```
Flask==2.3.0
Werkzeug==2.3.0
```

---

## Verificar versiones instaladas:

```bash
python --version
pip list | grep Flask
pip list | grep Werkzeug
```

Deberías ver:
```
Flask              3.0.0
Werkzeug           3.0.0
Flask-CORS         4.0.0
```

---

## En Render.com (si usas ese servicio):

Si desplegaste en Render.com, necesitas actualizar el archivo `requirements.txt`:

```
Flask==3.0.0
Flask-CORS==4.0.0
Werkzeug==3.0.0
```

Luego hacer push:
```bash
git add requirements.txt
git commit -m "Update Flask to 3.0.0 for Python 3.14 compatibility"
git push
```

---

## Si el problema sigue:

1. Copia este contenido exacto en `requirements.txt`:

```
Flask==3.0.0
Flask-CORS==4.0.0
Werkzeug==3.0.0
```

2. Ejecuta:

```bash
pip install --force-reinstall -r requirements.txt
```

3. Ejecuta la app:

```bash
python app.py
```

---

## Solución definitiva (si nada funciona):

```bash
# 1. Limpiar todo
pip uninstall Flask Werkzeug Flask-CORS -y

# 2. Instalar versiones más nuevas
pip install Flask==3.1.0 Werkzeug==3.1.0 Flask-CORS==4.0.0

# 3. Ejecutar
python app.py
```

---

**¡Debería funcionar ahora! 🚀**

Si aún tienes problemas, asegúrate de:
- ✅ Usar Python 3.11+ 
- ✅ Instalar Flask 3.0.0+
- ✅ Activar el virtualenv (si lo usas)
- ✅ Estar en la carpeta correcta
