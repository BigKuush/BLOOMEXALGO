from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from algosdk import account, mnemonic
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn

class ChainStatus(Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"

class ParticipantRole(Enum):
    FARMER = "FARMER"
    PROCESSOR = "PROCESSOR"
    DISTRIBUTOR = "DISTRIBUTOR"
    RETAILER = "RETAILER"

@dataclass
class ChainParticipant:
    address: str
    role: ParticipantRole
    reputation_score: float
    active_contracts: List[str]
    certification: Dict[str, str]

class SupplyChainManager:
    """
    Управление цепочкой поставок на Algorand
    """
    def __init__(self, algod_client):
        self.algod_client = algod_client
        self.participants: Dict[str, ChainParticipant] = {}
        self.active_chains: Dict[str, Dict] = {}
        self.contracts: Dict[str, Dict] = {}
        
    def register_participant(self,
                           address: str,
                           role: ParticipantRole,
                           certification: Dict[str, str]) -> bool:
        """
        Регистрация нового участника цепочки
        """
        if address in self.participants:
            return False
            
        participant = ChainParticipant(
            address=address,
            role=role,
            reputation_score=1.0,
            active_contracts=[],
            certification=certification
        )
        
        self.participants[address] = participant
        return True

    def create_supply_chain(self,
                          chain_id: str,
                          participants: List[str],
                          config: Dict) -> Optional[str]:
        """
        Создание новой цепочки поставок
        """
        if chain_id in self.active_chains:
            return None
            
        # Проверяем всех участников
        for address in participants:
            if address not in self.participants:
                return None
                
        # Создаем ASA для отслеживания
        params = self.algod_client.suggested_params()
        
        txn = AssetConfigTxn(
            sender=config['creator_address'],
            sp=params,
            total=1000000,
            default_frozen=False,
            unit_name="BLEX",
            asset_name=f"BloomexChain_{chain_id}",
            manager=config['creator_address'],
            reserve=config['creator_address'],
            freeze=config['creator_address'],
            clawback=config['creator_address'],
            url="https://bloomex.io",
            decimals=0
        )
        
        # Подписываем и отправляем транзакцию
        signed_txn = txn.sign(config['creator_key'])
        tx_id = self.algod_client.send_transaction(signed_txn)
        
        # Ждем подтверждения
        try:
            confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
            asset_id = confirmed_txn["asset-index"]
            
            self.active_chains[chain_id] = {
                'asset_id': asset_id,
                'participants': participants,
                'status': ChainStatus.ACTIVE,
                'config': config,
                'created_at': datetime.now().isoformat()
            }
            
            return chain_id
            
        except Exception as e:
            print(f"Error creating supply chain: {e}")
            return None

    def update_participant_reputation(self,
                                   address: str,
                                   score_delta: float) -> bool:
        """
        Обновление репутации участника
        """
        if address not in self.participants:
            return False
            
        participant = self.participants[address]
        new_score = participant.reputation_score + score_delta
        
        # Ограничиваем score диапазоном [0, 5]
        participant.reputation_score = max(0, min(5, new_score))
        return True

    def get_chain_status(self, chain_id: str) -> Optional[Dict]:
        """
        Получение статуса цепочки поставок
        """
        if chain_id not in self.active_chains:
            return None
            
        chain = self.active_chains[chain_id]
        
        return {
            'status': chain['status'].value,
            'participants': [
                {
                    'address': addr,
                    'role': self.participants[addr].role.value,
                    'reputation': self.participants[addr].reputation_score
                }
                for addr in chain['participants']
            ],
            'asset_id': chain['asset_id'],
            'created_at': chain['created_at']
        }

    def get_participant_info(self, address: str) -> Optional[Dict]:
        """
        Получение информации об участнике
        """
        if address not in self.participants:
            return None
            
        participant = self.participants[address]
        
        return {
            'role': participant.role.value,
            'reputation': participant.reputation_score,
            'contracts': participant.active_contracts,
            'certification': participant.certification
        }
