from flask import Flask, request, jsonify, render_template_string, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import timedelta
from blockchain import Blockchain, Transaction
import uuid

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura_aqui'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app)

# Inicializar blockchain
blockchain = Blockchain(difficulty=4)

# Almacenamiento de usuarios (en producción usarías una BD real)
users_file = 'users.json'
balances_file = 'balances.json'

def load_users():
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(users_file, 'w') as f:
        json.dump(users, f)

def load_balances():
    if os.path.exists(balances_file):
        with open(balances_file, 'r') as f:
            return json.load(f)
    return {}

def save_balances(balances):
    with open(balances_file, 'w') as f:
        json.dump(balances, f)

users = load_users()
balances = load_balances()

# ============ RUTAS DE AUTENTICACIÓN ============

@app.route('/api/register', methods=['POST'])
def register():
    """Registra un nuevo usuario"""
    data = request.json
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    
    if data['email'] in users:
        return jsonify({'error': 'El usuario ya existe'}), 400
    
    # Generar dirección única para la criptomoneda
    wallet_address = str(uuid.uuid4())[:16]
    
    users[data['email']] = {
        'password': generate_password_hash(data['password']),
        'wallet_address': wallet_address,
        'created_at': str(__import__('datetime').datetime.now())
    }
    
    balances[wallet_address] = 0  # Saldo inicial 0
    blockchain.balances[wallet_address] = 0
    
    save_users(users)
    save_balances(balances)
    
    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'wallet_address': wallet_address
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    """Inicia sesión de un usuario"""
    data = request.json
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    
    user = users.get(data['email'])
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    session.permanent = True
    session['email'] = data['email']
    session['wallet_address'] = user['wallet_address']
    
    return jsonify({
        'message': 'Sesión iniciada',
        'wallet_address': user['wallet_address'],
        'email': data['email']
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    """Cierra la sesión del usuario"""
    session.clear()
    return jsonify({'message': 'Sesión cerrada'}), 200

@app.route('/api/user', methods=['GET'])
def get_user():
    """Obtiene información del usuario actual"""
    if 'email' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    wallet_address = session.get('wallet_address')
    return jsonify({
        'email': session['email'],
        'wallet_address': wallet_address,
        'balance': blockchain.get_balance(wallet_address)
    }), 200

# ============ RUTAS DE BLOCKCHAIN ============

@app.route('/api/balance/<wallet_address>', methods=['GET'])
def get_balance(wallet_address):
    """Obtiene el saldo de una dirección"""
    balance = blockchain.get_balance(wallet_address)
    return jsonify({'wallet_address': wallet_address, 'balance': balance}), 200

@app.route('/api/transaction', methods=['POST'])
def create_transaction():
    """Crea una nueva transacción"""
    if 'wallet_address' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.json
    sender = session['wallet_address']
    receiver = data.get('receiver')
    amount = float(data.get('amount', 0))
    
    if not receiver or amount <= 0:
        return jsonify({'error': 'Datos de transacción inválidos'}), 400
    
    if sender == receiver:
        return jsonify({'error': 'No puedes enviar a tu propia dirección'}), 400
    
    # Verificar saldo
    required = amount + (amount * 0.02)
    if blockchain.get_balance(sender) < required:
        return jsonify({'error': 'Saldo insuficiente'}), 400
    
    # Crear transacción
    transaction = Transaction(sender, receiver, amount)
    if blockchain.add_transaction(transaction):
        return jsonify({
            'message': 'Transacción creada',
            'transaction': transaction.to_dict(),
            'commission': transaction.commission
        }), 201
    else:
        return jsonify({'error': 'Transacción inválida'}), 400

@app.route('/api/mine', methods=['POST'])
def mine_block():
    """Mina un nuevo bloque"""
    if 'wallet_address' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    miner_address = session['wallet_address']
    
    # Minar bloque
    block = blockchain.mine_pending_transactions(miner_address)
    
    if block:
        return jsonify({
            'message': 'Bloque minado exitosamente',
            'block': {
                'index': block.index,
                'hash': block.hash,
                'nonce': block.nonce,
                'transactions': block.transactions
            },
            'miner_reward': blockchain.mining_reward,
            'new_balance': blockchain.get_balance(miner_address)
        }), 201
    else:
        return jsonify({'error': 'Error al minar'}), 500

@app.route('/api/pending-transactions', methods=['GET'])
def get_pending():
    """Obtiene las transacciones pendientes"""
    return jsonify({
        'count': len(blockchain.pending_transactions),
        'transactions': [tx.to_dict() for tx in blockchain.pending_transactions]
    }), 200

@app.route('/api/history/<wallet_address>', methods=['GET'])
def get_history(wallet_address):
    """Obtiene el historial de transacciones de una dirección"""
    history = blockchain.get_transaction_history(wallet_address)
    return jsonify({'history': history}), 200

@app.route('/api/chain', methods=['GET'])
def get_chain():
    """Obtiene la blockchain completa"""
    if not blockchain.is_chain_valid():
        return jsonify({'error': 'Blockchain inválida'}), 500
    
    return jsonify({
        'length': len(blockchain.chain),
        'is_valid': blockchain.is_chain_valid(),
        'chain': blockchain.get_chain_data()
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas del sistema"""
    total_miners = len(blockchain.all_miners)
    total_balance = sum(blockchain.balances.values())
    total_blocks = len(blockchain.chain)
    
    return jsonify({
        'total_blocks': total_blocks,
        'total_users': len(users),
        'total_miners': total_miners,
        'pending_transactions': len(blockchain.pending_transactions),
        'total_balance': total_balance,
        'difficulty': blockchain.difficulty
    }), 200

# ============ SERVIR FRONTEND ============

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CryptoChain - Sistema de Blockchain</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0f0f1e 0%, #1a0a2e 100%);
            color: #00ff88;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .navbar {
            background: rgba(0, 0, 0, 0.8);
            border-bottom: 2px solid #00ff88;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: #ff00ff;
            text-shadow: 0 0 10px #ff00ff;
        }

        .nav-buttons button {
            background: #00ff88;
            color: #000;
            border: none;
            padding: 0.7rem 1.5rem;
            margin-left: 1rem;
            cursor: pointer;
            border-radius: 4px;
            font-weight: bold;
            transition: all 0.3s;
        }

        .nav-buttons button:hover {
            background: #ff00ff;
            color: #fff;
            box-shadow: 0 0 20px #ff00ff;
        }

        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }

        .auth-section, .dashboard-section {
            display: none;
        }

        .auth-section.active, .dashboard-section.active {
            display: block;
        }

        .auth-container {
            max-width: 400px;
            margin: 5rem auto;
            background: rgba(20, 10, 40, 0.9);
            border: 2px solid #00ff88;
            padding: 3rem;
            border-radius: 8px;
            box-shadow: 0 0 40px rgba(0, 255, 136, 0.3);
        }

        .auth-container h2 {
            color: #ff00ff;
            margin-bottom: 1.5rem;
            text-align: center;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #00ff88;
            font-weight: bold;
        }

        .form-group input {
            width: 100%;
            padding: 0.8rem;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            color: #00ff88;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }

        .form-group input:focus {
            outline: none;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
            background: rgba(0, 255, 136, 0.2);
        }

        button.btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
            color: #000;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s;
        }

        button.btn:hover {
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.6);
            transform: translateY(-2px);
        }

        .toggle-auth {
            text-align: center;
            margin-top: 1rem;
            color: #00ff88;
        }

        .toggle-auth button {
            background: none;
            border: none;
            color: #ff00ff;
            cursor: pointer;
            text-decoration: underline;
            font-family: 'Courier New', monospace;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }

        .card {
            background: rgba(20, 10, 40, 0.8);
            border: 2px solid #00ff88;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.2);
        }

        .card h3 {
            color: #ff00ff;
            margin-bottom: 1rem;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 0.5rem;
        }

        .balance-display {
            font-size: 2.5rem;
            color: #00ff88;
            font-weight: bold;
            margin: 1rem 0;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
        }

        .wallet-address {
            color: #00ccff;
            font-size: 0.9rem;
            word-break: break-all;
            background: rgba(0, 255, 136, 0.1);
            padding: 0.8rem;
            border-radius: 4px;
            margin: 1rem 0;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-top: 1rem;
        }

        .stat {
            background: rgba(0, 255, 136, 0.1);
            padding: 1rem;
            border-radius: 4px;
            text-align: center;
        }

        .stat-value {
            font-size: 1.5rem;
            color: #00ff88;
            font-weight: bold;
        }

        .stat-label {
            color: #00ccff;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }

        .transaction-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-top: 1rem;
        }

        .transaction-form input {
            padding: 0.8rem;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            color: #00ff88;
            border-radius: 4px;
        }

        .transaction-form button {
            padding: 0.8rem;
            background: linear-gradient(135deg, #ff00ff 0%, #ff0088 100%);
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }

        .transaction-form button:hover {
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.6);
        }

        .mine-btn {
            padding: 1.2rem;
            background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
            color: #000;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1.1rem;
            transition: all 0.3s;
            margin-top: 1rem;
        }

        .mine-btn:hover {
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.6);
            transform: translateY(-3px);
        }

        .mine-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .history {
            margin-top: 1rem;
            max-height: 300px;
            overflow-y: auto;
        }

        .transaction {
            background: rgba(0, 255, 136, 0.1);
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 4px;
            border-left: 3px solid #00ff88;
        }

        .transaction.sent {
            border-left-color: #ff0088;
        }

        .transaction.received {
            border-left-color: #00ff88;
        }

        .alert {
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
            display: none;
        }

        .alert.show {
            display: block;
        }

        .alert.success {
            background: rgba(0, 255, 136, 0.2);
            border: 1px solid #00ff88;
            color: #00ff88;
        }

        .alert.error {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff0000;
            color: #ff0000;
        }

        .loading {
            text-align: center;
            color: #00ff88;
        }

        .loading::after {
            content: '...';
            animation: dots 1.5s infinite;
        }

        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            .logo {
                font-size: 1.4rem;
            }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">⛓️ CryptoChain</div>
        <div class="nav-buttons">
            <button onclick="showStats()">📊 Estadísticas</button>
            <button id="logoutBtn" style="display:none;" onclick="logout()">Cerrar Sesión</button>
        </div>
    </div>

    <div class="container">
        <!-- SECCIÓN DE AUTENTICACIÓN -->
        <div id="authSection" class="auth-section active">
            <div class="auth-container">
                <h2 id="authTitle">Iniciar Sesión</h2>
                <div id="alertBox" class="alert"></div>
                
                <form id="authForm">
                    <div class="form-group">
                        <label for="email">Correo Electrónico</label>
                        <input type="email" id="email" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Contraseña</label>
                        <input type="password" id="password" required>
                    </div>
                    <button type="submit" class="btn" id="authBtn">Iniciar Sesión</button>
                </form>

                <div class="toggle-auth">
                    <p>¿No tienes cuenta? <button onclick="toggleAuth()">Registrarse</button></p>
                </div>
            </div>
        </div>

        <!-- SECCIÓN DEL DASHBOARD -->
        <div id="dashboardSection" class="dashboard-section">
            <div class="dashboard">
                <!-- TARJETA DE BILLETERA -->
                <div class="card">
                    <h3>💰 Mi Billetera</h3>
                    <div class="balance-display" id="balanceDisplay">0</div>
                    <div class="wallet-address" id="walletAddress"></div>
                    <button class="btn" onclick="refreshBalance()">Actualizar Saldo</button>
                </div>

                <!-- TARJETA DE MINERÍA -->
                <div class="card">
                    <h3>⚒️ Minería</h3>
                    <p>Mina nuevos bloques y gana recompensas</p>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-value" id="blockCount">0</div>
                            <div class="stat-label">Bloques</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" id="pendingCount">0</div>
                            <div class="stat-label">Pendientes</div>
                        </div>
                    </div>
                    <button class="mine-btn" id="mineBtn" onclick="mineBlock()">Minar Bloque</button>
                </div>

                <!-- TARJETA DE TRANSACCIONES -->
                <div class="card">
                    <h3>💸 Enviar Criptomoneda</h3>
                    <div class="transaction-form">
                        <input type="text" id="receiverAddress" placeholder="Dirección del receptor">
                        <input type="number" id="amount" placeholder="Cantidad" min="0.1" step="0.1">
                        <button onclick="sendTransaction()">Enviar</button>
                    </div>
                    <p style="font-size: 0.9rem; color: #00ccff; margin-top: 1rem;">*Comisión del 2% se distribuye entre mineros</p>
                </div>

                <!-- HISTORIAL DE TRANSACCIONES -->
                <div class="card">
                    <h3>📋 Historial</h3>
                    <div class="history" id="history">
                        <p style="color: #00ccff;">Cargando historial...</p>
                    </div>
                    <button class="btn" onclick="loadHistory()" style="margin-top: 1rem;">Actualizar</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let isLoginMode = true;
        let currentUser = null;

        function showAlert(message, type = 'success') {
            const alertBox = document.getElementById('alertBox');
            alertBox.textContent = message;
            alertBox.className = `alert show ${type}`;
            setTimeout(() => alertBox.classList.remove('show'), 4000);
        }

        function toggleAuth() {
            isLoginMode = !isLoginMode;
            document.getElementById('authTitle').textContent = isLoginMode ? 'Iniciar Sesión' : 'Registrarse';
            document.getElementById('authBtn').textContent = isLoginMode ? 'Iniciar Sesión' : 'Registrarse';
        }

        document.getElementById('authForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const endpoint = isLoginMode ? '/api/login' : '/api/register';

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert(data.message, 'success');
                    if (isLoginMode) {
                        currentUser = { email, walletAddress: data.wallet_address };
                        showDashboard();
                        loadUserData();
                    } else {
                        showAlert('Cuenta creada. Ahora inicia sesión.', 'success');
                        isLoginMode = true;
                        toggleAuth();
                        document.getElementById('authForm').reset();
                    }
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Error de conexión', 'error');
            }
        });

        function showDashboard() {
            document.getElementById('authSection').classList.remove('active');
            document.getElementById('dashboardSection').classList.add('active');
            document.getElementById('logoutBtn').style.display = 'block';
        }

        function showAuth() {
            document.getElementById('dashboardSection').classList.remove('active');
            document.getElementById('authSection').classList.add('active');
            document.getElementById('logoutBtn').style.display = 'none';
        }

        async function logout() {
            await fetch('/api/logout', { method: 'POST' });
            currentUser = null;
            document.getElementById('authForm').reset();
            isLoginMode = true;
            showAuth();
            showAlert('Sesión cerrada', 'success');
        }

        async function loadUserData() {
            try {
                const response = await fetch('/api/user');
                if (response.ok) {
                    const data = await response.json();
                    currentUser = data;
                    document.getElementById('walletAddress').textContent = data.wallet_address;
                    refreshBalance();
                    loadBlockStats();
                    loadHistory();
                }
            } catch (error) {
                console.error('Error loading user data:', error);
            }
        }

        async function refreshBalance() {
            if (!currentUser) return;
            try {
                const response = await fetch(`/api/balance/${currentUser.wallet_address}`);
                const data = await response.json();
                document.getElementById('balanceDisplay').textContent = data.balance.toFixed(2);
            } catch (error) {
                console.error('Error refreshing balance:', error);
            }
        }

        async function loadBlockStats() {
            try {
                const response = await fetch('/api/chain');
                const data = await response.json();
                document.getElementById('blockCount').textContent = data.length;
            } catch (error) {
                console.error('Error loading stats:', error);
            }

            try {
                const response = await fetch('/api/pending-transactions');
                const data = await response.json();
                document.getElementById('pendingCount').textContent = data.count;
            } catch (error) {
                console.error('Error loading pending:', error);
            }
        }

        async function mineBlock() {
            const mineBtn = document.getElementById('mineBtn');
            mineBtn.disabled = true;
            mineBtn.textContent = 'Minando...';

            try {
                const response = await fetch('/api/mine', { method: 'POST' });
                const data = await response.json();

                if (response.ok) {
                    showAlert(`¡Bloque ${data.block.index} minado! +${data.miner_reward} CryptoChain`, 'success');
                    refreshBalance();
                    loadBlockStats();
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Error al minar', 'error');
            } finally {
                mineBtn.disabled = false;
                mineBtn.textContent = 'Minar Bloque';
            }
        }

        async function sendTransaction() {
            const receiver = document.getElementById('receiverAddress').value;
            const amount = parseFloat(document.getElementById('amount').value);

            if (!receiver || !amount || amount <= 0) {
                showAlert('Datos inválidos', 'error');
                return;
            }

            try {
                const response = await fetch('/api/transaction', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ receiver, amount })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert(`Enviado: ${amount} CryptoChain (Comisión: ${data.commission.toFixed(4)})`, 'success');
                    document.getElementById('receiverAddress').value = '';
                    document.getElementById('amount').value = '';
                    loadBlockStats();
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Error al enviar', 'error');
            }
        }

        async function loadHistory() {
            if (!currentUser) return;
            try {
                const response = await fetch(`/api/history/${currentUser.wallet_address}`);
                const data = await response.json();
                const historyDiv = document.getElementById('history');

                if (data.history.length === 0) {
                    historyDiv.innerHTML = '<p style="color: #00ccff;">Sin transacciones</p>';
                    return;
                }

                historyDiv.innerHTML = data.history.map(tx => {
                    const isSent = tx.sender === currentUser.wallet_address;
                    const other = isSent ? tx.receiver : tx.sender;
                    const type = isSent ? 'Enviado' : 'Recibido';
                    const className = isSent ? 'sent' : 'received';
                    const symbol = isSent ? '↗️' : '↙️';

                    return `<div class="transaction ${className}">
                        <div><strong>${symbol} ${type}</strong></div>
                        <div style="font-size: 0.9rem; color: #00ccff;">${other.substring(0, 8)}...</div>
                        <div><strong>${tx.amount.toFixed(2)} CC</strong></div>
                    </div>`;
                }).join('');
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }

        async function showStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                alert(`
📊 ESTADÍSTICAS DE LA RED:

Bloques: ${data.total_blocks}
Usuarios: ${data.total_users}
Mineros: ${data.total_miners}
Transacciones pendientes: ${data.pending_transactions}
Balance total: ${data.total_balance.toFixed(2)} CryptoChain
Dificultad: ${data.difficulty}
                `);
            } catch (error) {
                showAlert('Error al cargar estadísticas', 'error');
            }
        }

        // Cargar datos del usuario al cargar la página
        window.addEventListener('load', async () => {
            const response = await fetch('/api/user');
            if (response.ok) {
                showDashboard();
                loadUserData();
            } else {
                showAuth();
            }
        });

        // Actualizar datos cada 10 segundos
        setInterval(() => {
            if (currentUser) {
                refreshBalance();
                loadBlockStats();
            }
        }, 10000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("🚀 Iniciando servidor CryptoChain...")
    print("📍 Abre el navegador en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
