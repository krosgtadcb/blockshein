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

blockchain = Blockchain(difficulty=99)

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

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Silk Road - Blockchain Mining</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            background: #0a0e27;
            color: #e0e0e0;
            line-height: 1.6;
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            padding: 40px 0 20px;
            border-bottom: 1px solid #1a1f3a;
            margin-bottom: 40px;
        }

        .title {
            font-size: 28px;
            font-weight: normal;
            letter-spacing: 4px;
            color: #fff;
            margin-bottom: 5px;
            text-transform: uppercase;
        }

        .subtitle {
            font-size: 12px;
            color: #666;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        nav {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            padding-top: 20px;
        }

        nav button {
            background: none;
            border: none;
            color: #999;
            font-size: 12px;
            cursor: pointer;
            letter-spacing: 1px;
            transition: color 0.3s;
            text-transform: uppercase;
            font-family: 'Monaco', monospace;
        }

        nav button:hover {
            color: #fff;
        }

        nav button#logoutBtn {
            display: none;
        }

        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
        }

        .section {
            background: #0f1434;
            border: 1px solid #1a1f3a;
            padding: 30px;
        }

        .section h2 {
            font-size: 14px;
            font-weight: normal;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #fff;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px solid #1a1f3a;
        }

        .auth-section, .dashboard-content {
            display: none;
        }

        .auth-section.active, .dashboard-content.active {
            display: block;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            font-size: 11px;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 8px;
        }

        .form-group input {
            width: 100%;
            background: #0a0e27;
            border: 1px solid #1a1f3a;
            color: #e0e0e0;
            padding: 12px;
            font-family: 'Monaco', monospace;
            font-size: 12px;
            transition: border-color 0.3s;
        }

        .form-group input:focus {
            outline: none;
            border-color: #666;
            background: #0f1434;
        }

        button {
            background: #0a0e27;
            border: 1px solid #1a1f3a;
            color: #e0e0e0;
            padding: 12px 20px;
            cursor: pointer;
            font-size: 11px;
            letter-spacing: 1px;
            text-transform: uppercase;
            font-family: 'Monaco', monospace;
            transition: all 0.3s;
        }

        button:hover {
            border-color: #666;
            color: #fff;
        }

        button:active {
            background: #1a1f3a;
        }

        .btn-large {
            width: 100%;
            padding: 15px;
            margin-top: 20px;
        }

        .toggle-auth {
            text-align: center;
            margin-top: 20px;
            font-size: 11px;
        }

        .toggle-auth button {
            background: none;
            border: none;
            color: #666;
            padding: 0;
            text-decoration: underline;
        }

        .toggle-auth button:hover {
            color: #999;
        }

        .alert {
            padding: 12px;
            margin-bottom: 20px;
            border-left: 2px solid;
            font-size: 11px;
            display: none;
        }

        .alert.show {
            display: block;
        }

        .alert.success {
            background: rgba(0, 255, 100, 0.1);
            border-left-color: #00ff64;
            color: #00ff64;
        }

        .alert.error {
            background: rgba(255, 0, 0, 0.1);
            border-left-color: #ff0000;
            color: #ff0000;
        }

        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
        }

        @media (max-width: 768px) {
            .dashboard, .content {
                grid-template-columns: 1fr;
            }

            .section {
                padding: 20px;
            }

            nav {
                gap: 15px;
                flex-wrap: wrap;
            }
        }

        .stat-item {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #1a1f3a;
        }

        .stat-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }

        .stat-label {
            font-size: 11px;
            color: #666;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 16px;
            color: #fff;
            font-weight: normal;
        }

        .history {
            max-height: 400px;
            overflow-y: auto;
        }

        .tx-item {
            padding: 12px 0;
            border-bottom: 1px solid #1a1f3a;
            font-size: 11px;
        }

        .tx-item:last-child {
            border-bottom: none;
        }

        .tx-type {
            color: #666;
            margin-bottom: 3px;
        }

        .tx-amount {
            color: #fff;
            font-weight: normal;
        }

        .tx-address {
            color: #666;
            font-size: 10px;
            margin-top: 3px;
            word-break: break-all;
        }

        .mining-status {
            margin-top: 20px;
            padding: 15px;
            background: #0a0e27;
            border: 1px solid #1a1f3a;
            text-align: center;
            font-size: 11px;
            color: #666;
            display: none;
        }

        .mining-status.active {
            display: block;
            color: #00ff64;
            border-color: #1a1f3a;
        }

        .spinner {
            display: inline-block;
            width: 12px;
            height: 12px;
            border: 1px solid #666;
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .box {
            background: #0a0e27;
            border: 1px solid #1a1f3a;
            padding: 15px;
            text-align: center;
        }

        .box-label {
            font-size: 10px;
            color: #666;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .box-value {
            font-size: 18px;
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1 class="title">Silk Road</h1>
            <p class="subtitle">Blockchain Mining Network</p>
            <nav>
                <button onclick="showStats()">Stats</button>
                <button onclick="showAbout()">About</button>
                <button id="logoutBtn" onclick="logout()">Logout</button>
            </nav>
        </header>

        <div id="authSection" class="auth-section active">
            <div class="content">
                <div class="section">
                    <h2>Sign In</h2>
                    <div id="alertBox" class="alert"></div>
                    <form id="authForm">
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="email" required>
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" id="password" required>
                        </div>
                        <button type="submit" class="btn-large" id="authBtn">Sign In</button>
                    </form>
                    <div class="toggle-auth">
                        <p>No account? <button onclick="toggleAuth()">Sign Up</button></p>
                    </div>
                </div>
            </div>
        </div>

        <div id="dashboardSection" class="dashboard-content">
            <div class="dashboard">
                <div class="section">
                    <h2>Wallet</h2>
                    <div class="stat-item">
                        <div class="stat-label">Balance</div>
                        <div class="stat-value" id="balanceDisplay">0.00</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Address</div>
                        <div class="stat-value" id="walletAddress" style="font-size: 11px; word-break: break-all;">-</div>
                    </div>
                    <button class="btn-large" onclick="refreshBalance()">Refresh</button>
                </div>

                <div class="section">
                    <h2>Mining</h2>
                    <div class="grid-2">
                        <div class="box">
                            <div class="box-label">Blocks</div>
                            <div class="box-value" id="blockCount">0</div>
                        </div>
                        <div class="box">
                            <div class="box-label">Pending</div>
                            <div class="box-value" id="pendingCount">0</div>
                        </div>
                    </div>
                    <button class="btn-large" id="mineBtn" onclick="mineBlock()">Start Mining</button>
                    <div class="mining-status" id="miningStatus">
                        <span class="spinner"></span>Mining...
                    </div>
                </div>

                <div class="section">
                    <h2>Send Coins</h2>
                    <div class="form-group">
                        <label>Recipient Address</label>
                        <input type="text" id="receiverAddress" placeholder="">
                    </div>
                    <div class="form-group">
                        <label>Amount</label>
                        <input type="number" id="amount" placeholder="0.00" step="0.1">
                    </div>
                    <button class="btn-large" onclick="sendTransaction()">Send</button>
                    <p style="font-size: 10px; color: #666; margin-top: 15px; text-transform: uppercase; letter-spacing: 1px;">
                        Network Fee: 2%
                    </p>
                </div>

                <div class="section">
                    <h2>Transaction History</h2>
                    <div class="history" id="history">
                        <p style="color: #666; text-align: center; padding: 20px 0;">Loading...</p>
                    </div>
                    <button class="btn-large" onclick="loadHistory()">Reload</button>
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
            document.getElementById('authBtn').textContent = isLoginMode ? 'Sign In' : 'Sign Up';
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
                        showAlert('Account created. Please sign in.', 'success');
                        isLoginMode = true;
                        document.getElementById('authBtn').textContent = 'Sign In';
                        document.getElementById('authForm').reset();
                    }
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Connection error', 'error');
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
            showAlert('Logged out', 'success');
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
                console.error('Error:', error);
            }
        }

        async function refreshBalance() {
            if (!currentUser) return;
            try {
                const response = await fetch(`/api/balance/${currentUser.wallet_address}`);
                const data = await response.json();
                document.getElementById('balanceDisplay').textContent = data.balance.toFixed(2);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function loadBlockStats() {
            try {
                const response = await fetch('/api/chain');
                const data = await response.json();
                document.getElementById('blockCount').textContent = data.length;
            } catch (error) {
                console.error('Error:', error);
            }

            try {
                const response = await fetch('/api/pending-transactions');
                const data = await response.json();
                document.getElementById('pendingCount').textContent = data.count;
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function mineBlock() {
            const mineBtn = document.getElementById('mineBtn');
            const status = document.getElementById('miningStatus');
            mineBtn.disabled = true;
            mineBtn.style.opacity = '0.5';
            status.classList.add('active');

            try {
                const response = await fetch('/api/mine', { method: 'POST' });
                const data = await response.json();

                if (response.ok) {
                    showAlert(`Block ${data.block.index} mined! Reward: ${data.miner_reward.toFixed(2)} coins`, 'success');
                    refreshBalance();
                    loadBlockStats();
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Mining error', 'error');
            } finally {
                mineBtn.disabled = false;
                mineBtn.style.opacity = '1';
                status.classList.remove('active');
            }
        }

        async function sendTransaction() {
            const receiver = document.getElementById('receiverAddress').value;
            const amount = parseFloat(document.getElementById('amount').value);

            if (!receiver || !amount || amount <= 0) {
                showAlert('Invalid data', 'error');
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
                    showAlert(`Sent: ${amount} coins (Fee: ${data.commission.toFixed(4)})`, 'success');
                    document.getElementById('receiverAddress').value = '';
                    document.getElementById('amount').value = '';
                    loadBlockStats();
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Send error', 'error');
            }
        }

        async function loadHistory() {
            if (!currentUser) return;
            try {
                const response = await fetch(`/api/history/${currentUser.wallet_address}`);
                const data = await response.json();
                const historyDiv = document.getElementById('history');

                if (data.history.length === 0) {
                    historyDiv.innerHTML = '<p style="color: #666; text-align: center; padding: 20px 0;">No transactions</p>';
                    return;
                }

                historyDiv.innerHTML = data.history.map(tx => {
                    const isSent = tx.sender === currentUser.wallet_address;
                    const other = isSent ? tx.receiver : tx.sender;
                    const type = isSent ? 'SENT' : 'RECEIVED';

                    return `<div class="tx-item">
                        <div class="tx-type">${type}</div>
                        <div class="tx-amount">${tx.amount.toFixed(2)} coins</div>
                        <div class="tx-address">${other.substring(0, 12)}...</div>
                    </div>`;
                }).join('');
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function showStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    alert(`NETWORK STATISTICS

Blocks: ${data.total_blocks}
Users: ${data.total_users}
Miners: ${data.total_miners}
Pending TX: ${data.pending_transactions}
Total Balance: ${data.total_balance.toFixed(2)} coins
Difficulty: ${data.difficulty}%`);
                });
        }

        function showAbout() {
            alert(`SILK ROAD
Blockchain Mining Network

Difficulty: 99%
Network Fee: 2%
Block Reward: 5-50 coins (random)

The Silk Road. The ancient network of trade routes connecting East and West. 
Today, reimagined as a modern blockchain network for distributed mining.`);
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
            if (currentUser && !document.getElementById('miningStatus').classList.contains('active')) {
                refreshBalance();
                loadBlockStats();
            }
        }, 15000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("Silk Road - Blockchain Mining Network")
    print("http://localhost:5000")
    print("Difficulty: 99%")
    print("Mining started...")
    app.run(debug=True, host='0.0.0.0', port=5000)
