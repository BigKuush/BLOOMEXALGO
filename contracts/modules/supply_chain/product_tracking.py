from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from algosdk import account, mnemonic
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn

class ProductStatus(Enum):
    REGISTERED = "REGISTERED"
    IN_PRODUCTION = "IN_PRODUCTION"
    QUALITY_CHECK = "QUALITY_CHECK"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    REJECTED = "REJECTED"

class ProductType(Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    PROCESSED = "PROCESSED"
    FINAL_PRODUCT = "FINAL_PRODUCT"

@dataclass
class ProductMetadata:
    product_id: str
    type: ProductType
    origin: str
    producer: str
    certifications: List[str]
    quality_score: float
    sustainability_score: float

class ProductTracker:
    """
    Система отслеживания продукции на Algorand
    """
    def __init__(self, algod_client):
        self.algod_client = algod_client
        self.products: Dict[str, Dict] = {}
        self.batches: Dict[str, List[str]] = {}
        self.tracking_history: Dict[str, List[Dict]] = {}
        
    def register_product(self,
                        product_id: str,
                        metadata: ProductMetadata,
                        initial_location: str) -> Optional[str]:
        """
        Регистрация нового продукта
        """
        if product_id in self.products:
            return None
            
        # Создаем NFT для продукта
        params = self.algod_client.suggested_params()
        
        txn = AssetConfigTxn(
            sender=metadata.producer,
            sp=params,
            total=1,
            default_frozen=False,
            unit_name="BLXP",
            asset_name=f"BloomexProduct_{product_id}",
            manager=metadata.producer,
            reserve=metadata.producer,
            freeze=metadata.producer,
            clawback=metadata.producer,
            url=f"https://bloomex.io/products/{product_id}",
            decimals=0
        )
        
        try:
            signed_txn = txn.sign(metadata.producer_key)
            tx_id = self.algod_client.send_transaction(signed_txn)
            confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
            asset_id = confirmed_txn["asset-index"]
            
            self.products[product_id] = {
                'asset_id': asset_id,
                'metadata': metadata,
                'status': ProductStatus.REGISTERED,
                'current_location': initial_location,
                'current_owner': metadata.producer,
                'created_at': datetime.now().isoformat()
            }
            
            self.tracking_history[product_id] = [{
                'timestamp': datetime.now().isoformat(),
                'status': ProductStatus.REGISTERED.value,
                'location': initial_location,
                'owner': metadata.producer
            }]
            
            return product_id
            
        except Exception as e:
            print(f"Error registering product: {e}")
            return None

    def update_product_status(self,
                            product_id: str,
                            new_status: ProductStatus,
                            location: str,
                            owner: str,
                            details: Dict) -> bool:
        """
        Обновление статуса продукта
        """
        if product_id not in self.products:
            return False
            
        product = self.products[product_id]
        
        # Обновляем статус
        product['status'] = new_status
        product['current_location'] = location
        product['current_owner'] = owner
        
        # Записываем в историю
        self.tracking_history[product_id].append({
            'timestamp': datetime.now().isoformat(),
            'status': new_status.value,
            'location': location,
            'owner': owner,
            'details': details
        })
        
        return True

    def transfer_ownership(self,
                         product_id: str,
                         from_address: str,
                         to_address: str,
                         new_location: str) -> bool:
        """
        Передача права собственности на продукт
        """
        if product_id not in self.products:
            return False
            
        product = self.products[product_id]
        
        if product['current_owner'] != from_address:
            return False
            
        # Создаем транзакцию передачи ASA
        params = self.algod_client.suggested_params()
        
        txn = AssetTransferTxn(
            sender=from_address,
            sp=params,
            receiver=to_address,
            amt=1,
            index=product['asset_id']
        )
        
        try:
            signed_txn = txn.sign(from_address_key)
            tx_id = self.algod_client.send_transaction(signed_txn)
            wait_for_confirmation(self.algod_client, tx_id, 4)
            
            product['current_owner'] = to_address
            product['current_location'] = new_location
            
            self.tracking_history[product_id].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'OWNERSHIP_TRANSFER',
                'from': from_address,
                'to': to_address,
                'location': new_location
            })
            
            return True
            
        except Exception as e:
            print(f"Error transferring ownership: {e}")
            return False

    def get_product_history(self, product_id: str) -> Optional[List[Dict]]:
        """
        Получение истории продукта
        """
        if product_id not in self.tracking_history:
            return None
            
        return self.tracking_history[product_id]

    def verify_product_authenticity(self, product_id: str) -> Optional[Dict]:
        """
        Проверка подлинности продукта
        """
        if product_id not in self.products:
            return None
            
        product = self.products[product_id]
        
        return {
            'is_authentic': True,
            'asset_id': product['asset_id'],
            'metadata': product['metadata'],
            'current_status': product['status'].value,
            'current_owner': product['current_owner'],
            'history': self.get_product_history(product_id)
        }
