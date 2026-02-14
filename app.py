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

# Inicializar blockchain con dificultad 99%
blockchain = Blockchain(difficulty=99)

# Almacenamiento de usuarios
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
    data = request.json
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    
    if data['email'] in users:
        return jsonify({'error': 'El usuario ya existe'}), 400
    
    wallet_address = str(uuid.uuid4())[:16]
    
    users[data['email']] = {
        'password': generate_password_hash(data['password']),
        'wallet_address': wallet_address,
        'created_at': str(__import__('datetime').datetime.now())
    }
    
    balances[wallet_address] = 0
    blockchain.balances[wallet_address] = 0
    
    save_users(users)
    save_balances(balances)
    
    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'wallet_address': wallet_address
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
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
    session.clear()
    return jsonify({'message': 'Sesión cerrada'}), 200

@app.route('/api/user', methods=['GET'])
def get_user():
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
    balance = blockchain.get_balance(wallet_address)
    return jsonify({'wallet_address': wallet_address, 'balance': balance}), 200

@app.route('/api/transaction', methods=['POST'])
def create_transaction():
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
    
    required = amount + (amount * 0.02)
    if blockchain.get_balance(sender) < required:
        return jsonify({'error': 'Saldo insuficiente'}), 400
    
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
    if 'wallet_address' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    miner_address = session['wallet_address']
    block = blockchain.mine_pending_transactions(miner_address)
    
    if block:
        # Obtener la recompensa del bloque minado
        mining_tx = next((tx for tx in block.transactions if tx['sender'] == 'SISTEMA'), None)
        mining_reward = mining_tx['amount'] if mining_tx else 0
        
        return jsonify({
            'message': 'Bloque minado exitosamente',
            'block': {
                'index': block.index,
                'hash': block.hash,
                'nonce': block.nonce,
                'transactions': block.transactions
            },
            'miner_reward': mining_reward,
            'new_balance': blockchain.get_balance(miner_address)
        }), 201
    else:
        return jsonify({'error': 'Error al minar'}), 500

@app.route('/api/pending-transactions', methods=['GET'])
def get_pending():
    return jsonify({
        'count': len(blockchain.pending_transactions),
        'transactions': [tx.to_dict() for tx in blockchain.pending_transactions]
    }), 200

@app.route('/api/history/<wallet_address>', methods=['GET'])
def get_history(wallet_address):
    history = blockchain.get_transaction_history(wallet_address)
    return jsonify({'history': history}), 200

@app.route('/api/chain', methods=['GET'])
def get_chain():
    if not blockchain.is_chain_valid():
        return jsonify({'error': 'Blockchain inválida'}), 500
    
    return jsonify({
        'length': len(blockchain.chain),
        'is_valid': blockchain.is_chain_valid(),
        'chain': blockchain.get_chain_data()
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
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
    <title>BlockChain - Sistema de Mineria</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #1a1f3a;
            --secondary: #2d3561;
            --accent: #00d9ff;
            --accent-alt: #ff006e;
            --success: #00ff88;
            --warning: #ffa500;
            --danger: #ff0000;
            --text-light: #e0e0e0;
        }

        html, body {
            height: 100%;
            width: 100%;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, #0f1629 50%, var(--primary) 100%);
            color: var(--text-light);
            min-height: 100vh;
            overflow-x: hidden;
        }

        .navbar {
            background: rgba(26, 31, 58, 0.95);
            border-bottom: 2px solid var(--accent);
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), var(--accent-alt));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .nav-buttons {
            display: flex;
            gap: 1rem;
        }

        .nav-buttons button {
            background: linear-gradient(135deg, var(--accent), #00ccee);
            color: var(--primary);
            border: none;
            padding: 0.7rem 1.5rem;
            cursor: pointer;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            font-size: 0.95rem;
        }

        .nav-buttons button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0, 217, 255, 0.4);
        }

        .nav-buttons button:active {
            transform: translateY(-1px);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        .auth-section, .dashboard-section {
            display: none;
        }

        .auth-section.active, .dashboard-section.active {
            display: block;
        }

        .auth-container {
            max-width: 420px;
            margin: 4rem auto;
            background: rgba(45, 53, 97, 0.8);
            border: 2px solid var(--accent);
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 217, 255, 0.2);
            backdrop-filter: blur(10px);
        }

        .auth-container h2 {
            background: linear-gradient(135deg, var(--accent), var(--accent-alt));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1.5rem;
            text-align: center;
            font-size: 1.8rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.6rem;
            color: var(--accent);
            font-weight: 600;
            font-size: 0.95rem;
        }

        .form-group input {
            width: 100%;
            padding: 1rem;
            background: rgba(0, 217, 255, 0.08);
            border: 1.5px solid var(--accent);
            color: var(--text-light);
            border-radius: 8px;
            font-family: 'Segoe UI', sans-serif;
            transition: all 0.3s ease;
            font-size: 1rem;
        }

        .form-group input:focus {
            outline: none;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
            background: rgba(0, 217, 255, 0.15);
            border-color: var(--accent-alt);
        }

        button.btn {
            width: 100%;
            padding: 1.1rem;
            background: linear-gradient(135deg, var(--accent), #00ccee);
            color: var(--primary);
            border: none;
            border-radius: 8px;
            font-weight: 700;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        button.btn:hover {
            box-shadow: 0 10px 30px rgba(0, 217, 255, 0.4);
            transform: translateY(-2px);
        }

        button.btn:active {
            transform: translateY(0);
        }

        .toggle-auth {
            text-align: center;
            margin-top: 1.5rem;
            color: var(--text-light);
        }

        .toggle-auth button {
            background: none;
            border: none;
            color: var(--accent);
            cursor: pointer;
            text-decoration: underline;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
        }

        .alert {
            padding: 1.2rem;
            margin: 1rem 0;
            border-radius: 8px;
            display: none;
            border-left: 4px solid;
            font-weight: 500;
        }

        .alert.show {
            display: block;
            animation: slideDown 0.3s ease;
        }

        .alert.success {
            background: rgba(0, 255, 136, 0.1);
            border-left-color: var(--success);
            color: var(--success);
        }

        .alert.error {
            background: rgba(255, 0, 0, 0.1);
            border-left-color: var(--danger);
            color: var(--danger);
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
        }

        .card {
            background: rgba(45, 53, 97, 0.6);
            border: 2px solid rgba(0, 217, 255, 0.3);
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: var(--accent);
            box-shadow: 0 15px 50px rgba(0, 217, 255, 0.2);
            transform: translateY(-5px);
        }

        .card h3 {
            background: linear-gradient(135deg, var(--accent), var(--accent-alt));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid rgba(0, 217, 255, 0.3);
            padding-bottom: 1rem;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .card i {
            color: var(--accent);
        }

        .balance-display {
            font-size: 2.8rem;
            color: var(--success);
            font-weight: 700;
            margin: 1.5rem 0;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.4);
        }

        .wallet-address {
            color: var(--accent);
            font-size: 0.85rem;
            word-break: break-all;
            background: rgba(0, 217, 255, 0.08);
            padding: 1rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            border-left: 3px solid var(--accent);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .stat {
            background: rgba(0, 217, 255, 0.05);
            padding: 1.2rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid rgba(0, 217, 255, 0.2);
        }

        .stat-value {
            font-size: 1.8rem;
            color: var(--success);
            font-weight: 700;
        }

        .stat-label {
            color: var(--accent);
            font-size: 0.9rem;
            margin-top: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .transaction-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .transaction-form input {
            padding: 1rem;
            background: rgba(0, 217, 255, 0.08);
            border: 1.5px solid rgba(0, 217, 255, 0.3);
            color: var(--text-light);
            border-radius: 8px;
            transition: all 0.3s ease;
            font-size: 1rem;
        }

        .transaction-form input:focus {
            outline: none;
            box-shadow: 0 0 15px rgba(0, 217, 255, 0.4);
            border-color: var(--accent);
            background: rgba(0, 217, 255, 0.12);
        }

        .transaction-form button {
            padding: 1rem;
            background: linear-gradient(135deg, var(--accent-alt), #ff0066);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 700;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .transaction-form button:hover {
            box-shadow: 0 10px 30px rgba(255, 0, 110, 0.4);
            transform: translateY(-2px);
        }

        .mine-btn {
            padding: 1.3rem;
            background: linear-gradient(135deg, var(--success), #00dd77);
            color: var(--primary);
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 700;
            font-size: 1.05rem;
            transition: all 0.3s ease;
            margin-top: 1.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .mine-btn:hover:not(:disabled) {
            box-shadow: 0 15px 40px rgba(0, 255, 136, 0.4);
            transform: translateY(-3px);
        }

        .mine-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .history {
            margin-top: 1.5rem;
            max-height: 350px;
            overflow-y: auto;
        }

        .history::-webkit-scrollbar {
            width: 6px;
        }

        .history::-webkit-scrollbar-track {
            background: rgba(0, 217, 255, 0.1);
            border-radius: 10px;
        }

        .history::-webkit-scrollbar-thumb {
            background: var(--accent);
            border-radius: 10px;
        }

        .transaction {
            background: rgba(0, 217, 255, 0.08);
            padding: 1rem;
            margin: 0.8rem 0;
            border-radius: 8px;
            border-left: 4px solid var(--accent);
            transition: all 0.2s ease;
        }

        .transaction:hover {
            background: rgba(0, 217, 255, 0.12);
        }

        .transaction.sent {
            border-left-color: var(--accent-alt);
        }

        .transaction.received {
            border-left-color: var(--success);
        }

        .transaction i {
            margin-right: 0.5rem;
        }

        .transaction-info {
            font-size: 0.9rem;
            color: var(--accent);
            margin-top: 0.5rem;
        }

        .loading {
            text-align: center;
            color: var(--accent);
            font-weight: 600;
        }

        .loading i {
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .info-text {
            font-size: 0.85rem;
            color: var(--accent);
            margin-top: 1rem;
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            .logo {
                font-size: 1.4rem;
            }
            .card {
                padding: 1.8rem;
            }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">
            <i class="fas fa-cube"></i> BlockChain Mining
        </div>
        <div class="nav-buttons">
            <button onclick="showStats()">
                <i class="fas fa-chart-bar"></i> Estadisticas
            </button>
            <button id="logoutBtn" style="display:none;" onclick="logout()">
                <i class="fas fa-sign-out-alt"></i> Cerrar
            </button>
        </div>
    </div>

    <div class="container">
        <div id="authSection" class="auth-section active">
            <div class="auth-container">
                <h2><i class="fas fa-key"></i> <span id="authTitle">Iniciar Sesion</span></h2>
                <div id="alertBox" class="alert"></div>
                
                <form id="authForm">
                    <div class="form-group">
                        <label for="email"><i class="fas fa-envelope"></i> Correo Electronico</label>
                        <input type="email" id="email" required>
                    </div>
                    <div class="form-group">
                        <label for="password"><i class="fas fa-lock"></i> Contraseña</label>
                        <input type="password" id="password" required>
                    </div>
                    <button type="submit" class="btn" id="authBtn">Iniciar Sesion</button>
                </form>

                <div class="toggle-auth">
                    <p>No tienes cuenta? <button onclick="toggleAuth()">Registrate</button></p>
                </div>
            </div>
        </div>

        <div id="dashboardSection" class="dashboard-section">
            <div class="dashboard">
                <div class="card">
                    <h3><i class="fas fa-wallet"></i> Mi Billetera</h3>
                    <div class="balance-display" id="balanceDisplay">0.00</div>
                    <div class="wallet-address" id="walletAddress">Cargando...</div>
                    <button class="btn" onclick="refreshBalance()">
                        <i class="fas fa-sync-alt"></i> Actualizar
                    </button>
                </div>

                <div class="card">
                    <h3><i class="fas fa-hammer"></i> Mineria</h3>
                    <p style="color: var(--accent); margin-bottom: 1rem; font-size: 0.95rem;">
                        Resuelve el Proof of Work y gana recompensas aleatorias (5-50 coins)
                    </p>
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
                    <button class="mine-btn" id="mineBtn" onclick="mineBlock()">
                        <i class="fas fa-circle-notch"></i> Minar Bloque
                    </button>
                </div>

                <div class="card">
                    <h3><i class="fas fa-paper-plane"></i> Enviar</h3>
                    <div class="transaction-form">
                        <input type="text" id="receiverAddress" placeholder="Direccion del receptor">
                        <input type="number" id="amount" placeholder="Cantidad" min="0.1" step="0.1">
                        <button onclick="sendTransaction()">Enviar Fondos</button>
                    </div>
                    <p class="info-text">
                        <i class="fas fa-info-circle"></i> Se aplicara una comision del 2%
                    </p>
                </div>

                <div class="card">
                    <h3><i class="fas fa-history"></i> Historial</h3>
                    <div class="history" id="history">
                        <p class="loading">
                            <i class="fas fa-spinner"></i> Cargando historial...
                        </p>
                    </div>
                    <button class="btn" onclick="loadHistory()" style="margin-top: 1rem; padding: 0.8rem;">
                        <i class="fas fa-redo"></i> Actualizar
                    </button>
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
            document.getElementById('authTitle').textContent = isLoginMode ? 'Iniciar Sesion' : 'Registrarse';
            document.getElementById('authBtn').textContent = isLoginMode ? 'Iniciar Sesion' : 'Registrarse';
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
                        showAlert('Cuenta creada. Ahora inicia sesion.', 'success');
                        isLoginMode = true;
                        toggleAuth();
                        document.getElementById('authForm').reset();
                    }
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Error de conexion', 'error');
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
            showAlert('Sesion cerrada', 'success');
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
            mineBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Minando...';

            try {
                const response = await fetch('/api/mine', { method: 'POST' });
                const data = await response.json();

                if (response.ok) {
                    showAlert(`Bloque ${data.block.index} minado! Ganaste ${data.miner_reward.toFixed(2)} coins`, 'success');
                    refreshBalance();
                    loadBlockStats();
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Error al minar', 'error');
            } finally {
                mineBtn.disabled = false;
                mineBtn.innerHTML = '<i class="fas fa-circle-notch"></i> Minar Bloque';
            }
        }

        async function sendTransaction() {
            const receiver = document.getElementById('receiverAddress').value;
            const amount = parseFloat(document.getElementById('amount').value);

            if (!receiver || !amount || amount <= 0) {
                showAlert('Datos invalidos', 'error');
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
                    showAlert(`Enviado: ${amount} coins (Comision: ${data.commission.toFixed(4)})`, 'success');
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
                    historyDiv.innerHTML = '<p style="color: var(--accent); text-align: center;">Sin transacciones</p>';
                    return;
                }

                historyDiv.innerHTML = data.history.map(tx => {
                    const isSent = tx.sender === currentUser.wallet_address;
                    const other = isSent ? tx.receiver : tx.sender;
                    const type = isSent ? 'Enviado' : 'Recibido';
                    const className = isSent ? 'sent' : 'received';
                    const icon = isSent ? 'fa-arrow-right' : 'fa-arrow-left';

                    return `<div class="transaction ${className}">
                        <div>
                            <i class="fas ${icon}"></i>
                            <strong>${type}</strong>
                        </div>
                        <div class="transaction-info">${other.substring(0, 8)}...</div>
                        <div style="color: var(--success); font-weight: 700; margin-top: 0.5rem;">${tx.amount.toFixed(2)} coins</div>
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
                alert(`ESTADISTICAS DE LA RED

Bloques minados: ${data.total_blocks}
Usuarios: ${data.total_users}
Mineros activos: ${data.total_miners}
Transacciones pendientes: ${data.pending_transactions}
Balance total: ${data.total_balance.toFixed(2)} coins
Dificultad: ${data.difficulty}%
                `);
            } catch (error) {
                showAlert('Error al cargar estadisticas', 'error');
            }
        }

        window.addEventListener('load', async () => {
            const response = await fetch('/api/user');
            if (response.ok) {
                showDashboard();
                loadUserData();
            } else {
                showAuth();
            }
        });

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
    print("Iniciando servidor BlockChain...")
    print("Abre el navegador en: http://localhost:5000")
    print("Dificultad: 99%")
    print("Recompensa: ALEATORIA (5-50 coins)")
    app.run(debug=True, host='0.0.0.0', port=5000)
