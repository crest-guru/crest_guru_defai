import sqlite3
import os
from typing import Dict, Any
from pathlib import Path
from eth_account import Account
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Changes, Bip44Coins
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / 'data' / 'wallets.db'

def init_db():
    """Initialize database and create tables"""
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            user_address TEXT PRIMARY KEY,
            safe_address TEXT NOT NULL,
            cobo_address TEXT,
            agent_address TEXT,
            agent_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection with row factory"""
    if not DB_PATH.exists():
        init_db()
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def generate_agent_wallet(index: int) -> tuple[str, str]:
    """Generate agent wallet from mnemonic
    
    Args:
        index: Index for derivation path
        
    Returns:
        tuple[str, str]: (address, private_key)
    """
    mnemonic = os.getenv('AGENT_MNEMONIC')
    if not mnemonic:
        raise ValueError("AGENT_MNEMONIC not set in environment")
        
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_def = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    bip44_acc = bip44_def.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    bip44_addr = bip44_acc.AddressIndex(index)
    
    private_key = bip44_addr.PrivateKey().Raw().ToHex()
    address = Account.from_key(private_key).address
    return address, private_key

def create_wallet_record(user_address: str, safe_address: str) -> None:
    """Create new wallet record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM wallets")
        index = cursor.fetchone()[0]
        
        agent_address, agent_key = generate_agent_wallet(index)
        
        cursor.execute("""
            INSERT INTO wallets (
                user_address,
                safe_address,
                cobo_address,
                agent_address,
                agent_key,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_address,
            safe_address,
            None,
            agent_address,
            agent_key,
            datetime.utcnow()
        ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_wallet(user_address: str) -> Dict[str, Any]:
    """Get wallet data for user"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM wallets WHERE user_address = ?", 
            (user_address,)
        )
        wallet = cursor.fetchone()
        
        if not wallet:
            raise ValueError(f"No wallet found for {user_address}")
            
        return {
            'safe_address': wallet['safe_address'],
            'cobo_address': wallet['cobo_address'],
            'agent_address': wallet['agent_address'],
            'agent_key': wallet['agent_key']
        }
        
    except Exception as e:
        print(f"[Database] Error getting wallet: {str(e)}")
        raise
    finally:
        conn.close()

def update_cobo_address(user_address: str, cobo_address: str) -> None:
    """Update Cobo address"""
    print(f"Updating Cobo address for user {user_address}")  
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE wallets 
            SET cobo_address = ?
            WHERE user_address = ?
        """, (cobo_address, user_address))
        
        if cursor.rowcount == 0:
            raise ValueError(f"No wallet found for {user_address}")
            
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating Cobo address: {e}")  
        raise e
    finally:
        conn.close() 