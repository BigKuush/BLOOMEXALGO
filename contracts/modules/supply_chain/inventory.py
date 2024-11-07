from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

class InventoryStatus(Enum):
    IN_STOCK = "IN_STOCK"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    RESERVED = "RESERVED"
    EXPIRED = "EXPIRED"

class StorageType(Enum):
    AMBIENT = "AMBIENT"
    REFRIGERATED = "REFRIGERATED"
    FROZEN = "FROZEN"
    CONTROLLED = "CONTROLLED"

@dataclass
class InventoryItem:
    product_id: str
    quantity: float
    location: str
    storage_type: StorageType
    batch_number: str
    expiry_date: Optional[datetime]
    reorder_point: float
    optimal_quantity: float

class InventoryManager:
    """
    Управление запасами в цепочке поставок
    """
    def __init__(self):
        self.inventory: Dict[str, Dict[str, InventoryItem]] = {}  # location -> {product_id -> item}
        self.transactions: Dict[str, List[Dict]] = {}  # product_id -> transactions
        self.storage_conditions: Dict[str, Dict] = {}  # location -> conditions
        self.alerts: List[Dict] = []
        
    def add_inventory(self,
                     product_id: str,
                     location: str,
                     quantity: float,
                     storage_config: Dict) -> bool:
        """
        Добавление нового инвентаря
        """
        if location not in self.storage_conditions:
            return False
            
        # Проверяем соответствие условий хранения
        if not self._verify_storage_conditions(location, storage_config['storage_type']):
            return False
            
        inventory_key = f"{location}_{product_id}"
        
        # Создаем или обновляем запись инвентаря
        if inventory_key not in self.inventory:
            self.inventory[inventory_key] = InventoryItem(
                product_id=product_id,
                quantity=quantity,
                location=location,
                storage_type=StorageType(storage_config['storage_type']),
                batch_number=storage_config.get('batch_number', ''),
                expiry_date=storage_config.get('expiry_date'),
                reorder_point=storage_config.get('reorder_point', 0),
                optimal_quantity=storage_config.get('optimal_quantity', 0)
            )
        else:
            self.inventory[inventory_key].quantity += quantity
            
        # Записываем транзакцию
        self._record_transaction(
            product_id,
            'ADD',
            quantity,
            location,
            storage_config.get('batch_number', '')
        )
        
        # Проверяем необходимость оповещений
        self._check_inventory_alerts(inventory_key)
        
        return True

    def remove_inventory(self,
                        product_id: str,
                        location: str,
                        quantity: float,
                        reason: str) -> bool:
        """
        Удаление инвентаря
        """
        inventory_key = f"{location}_{product_id}"
        
        if inventory_key not in self.inventory:
            return False
            
        item = self.inventory[inventory_key]
        
        if item.quantity < quantity:
            return False
            
        item.quantity -= quantity
        
        # Записываем транзакцию
        self._record_transaction(
            product_id,
            'REMOVE',
            quantity,
            location,
            item.batch_number,
            reason
        )
        
        # Проверяем уровень запасов
        self._check_inventory_alerts(inventory_key)
        
        return True

    def _record_transaction(self,
                          product_id: str,
                          action: str,
                          quantity: float,
                          location: str,
                          batch_number: str,
                          reason: str = "") -> None:
        """
        Запись транзакции инвентаря
        """
        if product_id not in self.transactions:
            self.transactions[product_id] = []
            
        self.transactions[product_id].append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'quantity': quantity,
            'location': location,
            'batch_number': batch_number,
            'reason': reason
        })

    def _verify_storage_conditions(self, location: str, storage_type: str) -> bool:
        """
        Проверка соответствия условий хранения
        """
        conditions = self.storage_conditions.get(location, {})
        required_conditions = {
            'AMBIENT': {'temp_range': (15, 25), 'humidity_range': (30, 50)},
            'REFRIGERATED': {'temp_range': (2, 8), 'humidity_range': (40, 60)},
            'FROZEN': {'temp_range': (-25, -15), 'humidity_range': (60, 70)},
            'CONTROLLED': {'temp_range': (20, 22), 'humidity_range': (45, 55)}
        }
        
        if storage_type not in required_conditions:
            return False
            
        required = required_conditions[storage_type]
        current_temp = conditions.get('temperature', 20)
        current_humidity = conditions.get('humidity', 50)
        
        return (required['temp_range'][0] <= current_temp <= required['temp_range'][1] and
                required['humidity_range'][0] <= current_humidity <= required['humidity_range'][1])

    def _check_inventory_alerts(self, inventory_key: str) -> None:
        """
        Проверка и генерация оповещений об уровне запасов
        """
        item = self.inventory[inventory_key]
        
        # Проверка низкого уровня запасов
        if item.quantity <= item.reorder_point:
            self.alerts.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'LOW_STOCK',
                'product_id': item.product_id,
                'location': item.location,
                'current_quantity': item.quantity,
                'reorder_point': item.reorder_point
            })
            
        # Проверка срока годности
        if item.expiry_date and item.expiry_date - datetime.now() <= timedelta(days=30):
            self.alerts.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'EXPIRY_WARNING',
                'product_id': item.product_id,
                'location': item.location,
                'expiry_date': item.expiry_date.isoformat(),
                'quantity': item.quantity
            })

    def get_inventory_status(self, location: str, product_id: str) -> Optional[Dict]:
        """
        Получение статуса инвентаря
        """
        inventory_key = f"{location}_{product_id}"
        
        if inventory_key not in self.inventory:
            return None
            
        item = self.inventory[inventory_key]
        
        return {
            'product_id': item.product_id,
            'quantity': item.quantity,
            'location': item.location,
            'storage_type': item.storage_type.value,
            'batch_number': item.batch_number,
            'expiry_date': item.expiry_date.isoformat() if item.expiry_date else None,
            'status': self._calculate_status(item)
        }

    def _calculate_status(self, item: InventoryItem) -> InventoryStatus:
        """
        Расчет статуса инвентаря
        """
        if item.quantity == 0:
            return InventoryStatus.OUT_OF_STOCK
        elif item.quantity <= item.reorder_point:
            return InventoryStatus.LOW_STOCK
        elif item.expiry_date and item.expiry_date <= datetime.now():
            return InventoryStatus.EXPIRED
        else:
            return InventoryStatus.IN_STOCK

    def get_inventory_metrics(self, location: str) -> Dict:
        """
        Получение метрик инвентаря
        """
        location_items = [
            item for key, item in self.inventory.items()
            if item.location == location
        ]
        
        if not location_items:
            return {}
            
        total_value = sum(item.quantity for item in location_items)
        low_stock_items = len([
            item for item in location_items
            if item.quantity <= item.reorder_point
        ])
        
        return {
            'total_items': len(location_items),
            'total_value': total_value,
            'low_stock_items': low_stock_items,
            'storage_utilization': self._calculate_storage_utilization(location),
            'inventory_turnover': self._calculate_inventory_turnover(location)
        }

    def _calculate_storage_utilization(self, location: str) -> float:
        """
        Расчет использования складского пространства
        """
        # Упрощенный расчет
        total_capacity = self.storage_conditions[location].get('capacity', 1000)
        current_usage = sum(
            item.quantity
            for key, item in self.inventory.items()
            if item.location == location
        )
        
        return (current_usage / total_capacity) * 100

    def _calculate_inventory_turnover(self, location: str) -> float:
        """
        Расчет оборачиваемости запасов
        """
        # Упрощенный расчет за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        total_sales = sum(
            t['quantity']
            for transactions in self.transactions.values()
            for t in transactions
            if t['action'] == 'REMOVE'
            and t['location'] == location
            and datetime.fromisoformat(t['timestamp']) >= thirty_days_ago
        )
        
        average_inventory = np.mean([
            item.quantity
            for key, item in self.inventory.items()
            if item.location == location
        ])
        
        return total_sales / average_inventory if average_inventory > 0 else 0
