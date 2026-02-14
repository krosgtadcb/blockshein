import hashlib
import json
import time
import random
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional

class Block:
    """Representa un bloque en la blockchain"""
    
    def __init__(self, index: int, timestamp: float, transactions: List[Dict], 
                 previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calcula el hash SHA-256 del bloque"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 4):
        """Realiza Proof of Work (PoW) minando el bloque"""
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Bloque minado: {self.hash}")


class Transaction:
    """Representa una transacción"""
    
    def __init__(self, sender: str, receiver: str, amount: float, timestamp: Optional[float] = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp or time.time()
        self.commission = amount * 0.02  # Comisión del 2%
    
    def to_dict(self) -> Dict:
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'commission': self.commission,
            'timestamp': self.timestamp
        }


class Blockchain:
    """Implementa la blockchain con minería y gestión de transacciones"""
    
    def __init__(self, difficulty: int = 99):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        self.balances: Dict[str, float] = defaultdict(float)
        self.all_miners: set = set()  # Registro de todos los mineros
        
        # Crear bloque génesis
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Crea el primer bloque de la blockchain"""
        genesis_block = Block(0, time.time(), [], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Retorna el último bloque de la cadena"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Añade una transacción pendiente si es válida"""
        if not self.is_valid_transaction(transaction):
            return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def is_valid_transaction(self, transaction: Transaction) -> bool:
        """Valida que la transacción sea válida"""
        # El minero (sistema) no necesita suficiente saldo
        if transaction.sender == "SISTEMA":
            return transaction.amount > 0
        
        # Las transacciones normales deben tener saldo suficiente
        required_amount = transaction.amount + transaction.commission
        return self.balances[transaction.sender] >= required_amount
    
    def mine_pending_transactions(self, miner_address: str) -> Optional[Block]:
        """Mina las transacciones pendientes y añade el bloque a la cadena"""
        
        # Registrar minero
        self.all_miners.add(miner_address)
        
        # Recompensa aleatoria entre 5 y 50
        mining_reward = random.uniform(5, 50)
        
        # Recompensa de minería para el minero
        mining_transaction = Transaction("SISTEMA", miner_address, mining_reward)
        self.pending_transactions.insert(0, mining_transaction)
        
        # Distribuir comisiones a todos los mineros
        total_commission = sum(tx.commission for tx in self.pending_transactions 
                              if tx.sender != "SISTEMA")
        
        if total_commission > 0 and len(self.all_miners) > 0:
            commission_per_miner = total_commission / len(self.all_miners)
            for miner in self.all_miners:
                commission_tx = Transaction(
                    "COMISIONES",
                    miner,
                    commission_per_miner
                )
                self.pending_transactions.append(commission_tx)
        
        # Crear nuevo bloque
        new_block = Block(
            len(self.chain),
            time.time(),
            [tx.to_dict() for tx in self.pending_transactions],
            self.get_latest_block().hash
        )
        
        # Minar el bloque
        new_block.mine_block(self.difficulty)
        
        # Actualizar balances
        for tx_dict in new_block.transactions:
            tx = Transaction(
                tx_dict['sender'],
                tx_dict['receiver'],
                tx_dict['amount']
            )
            
            if tx.sender != "SISTEMA" and tx.sender != "COMISIONES":
                self.balances[tx.sender] -= tx.amount
                self.balances[tx.sender] -= tx.commission
            else:
                self.balances[tx.sender] -= 0  # SISTEMA no pierde saldo
            
            self.balances[tx.receiver] += tx.amount
        
        # Añadir bloque a la cadena
        self.chain.append(new_block)
        
        # Limpiar transacciones pendientes
        self.pending_transactions = []
        
        return new_block
    
    def get_balance(self, address: str) -> float:
        """Obtiene el saldo de una dirección"""
        return self.balances[address]
    
    def get_transaction_history(self, address: str) -> List[Dict]:
        """Obtiene el historial de transacciones de una dirección"""
        history = []
        for block in self.chain:
            for tx_dict in block.transactions:
                if tx_dict['sender'] == address or tx_dict['receiver'] == address:
                    tx_dict['block_index'] = block.index
                    history.append(tx_dict)
        return history
    
    def is_chain_valid(self) -> bool:
        """Valida la integridad de toda la blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verificar hash del bloque actual
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verificar hash anterior
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Verificar Proof of Work
            if not current_block.hash.startswith('0' * self.difficulty):
                return False
        
        return True
    
    def get_chain_data(self) -> List[Dict]:
        """Retorna toda la cadena en formato serializable"""
        return [{
            'index': block.index,
            'timestamp': block.timestamp,
            'hash': block.hash,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'transactions': block.transactions
        } for block in self.chain]
