from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

class ShipmentStatus(Enum):
    PLANNED = "PLANNED"
    IN_TRANSIT = "IN_TRANSIT"
    DELAYED = "DELAYED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class TransportType(Enum):
    ROAD = "ROAD"
    RAIL = "RAIL"
    AIR = "AIR"
    SEA = "SEA"

@dataclass
class ShipmentDetails:
    shipment_id: str
    origin: str
    destination: str
    transport_type: TransportType
    carrier: str
    estimated_delivery: datetime
    actual_delivery: Optional[datetime]
    products: List[str]
    conditions: Dict[str, float]

class LogisticsManager:
    """
    Управление логистикой в цепочке поставок
    """
    def __init__(self):
        self.shipments: Dict[str, ShipmentDetails] = {}
        self.routes: Dict[str, List[Dict]] = {}
        self.carriers: Dict[str, Dict] = {}
        self.tracking_data: Dict[str, List[Dict]] = {}
        
    def create_shipment(self,
                       shipment_id: str,
                       origin: str,
                       destination: str,
                       products: List[str],
                       transport_config: Dict) -> Optional[str]:
        """
        Создание новой поставки
        """
        if shipment_id in self.shipments:
            return None
            
        # Проверяем перевозчика
        carrier = transport_config.get('carrier')
        if carrier not in self.carriers:
            return None
            
        # Рассчитываем оптимальный маршрут
        route = self._calculate_optimal_route(
            origin,
            destination,
            transport_config.get('transport_type')
        )
        
        if not route:
            return None
            
        # Создаем детали поставки
        shipment = ShipmentDetails(
            shipment_id=shipment_id,
            origin=origin,
            destination=destination,
            transport_type=TransportType(transport_config['transport_type']),
            carrier=carrier,
            estimated_delivery=self._calculate_eta(route),
            actual_delivery=None,
            products=products,
            conditions=transport_config.get('conditions', {})
        )
        
        self.shipments[shipment_id] = shipment
        self.routes[shipment_id] = route
        
        # Инициализируем отслеживание
        self.tracking_data[shipment_id] = [{
            'timestamp': datetime.now().isoformat(),
            'status': ShipmentStatus.PLANNED.value,
            'location': origin,
            'notes': 'Shipment created'
        }]
        
        return shipment_id

    def update_shipment_status(self,
                             shipment_id: str,
                             status: ShipmentStatus,
                             location: str,
                             notes: str = "") -> bool:
        """
        Обновление статуса поставки
        """
        if shipment_id not in self.shipments:
            return False
            
        shipment = self.shipments[shipment_id]
        
        # Обновляем статус и местоположение
        self.tracking_data[shipment_id].append({
            'timestamp': datetime.now().isoformat(),
            'status': status.value,
            'location': location,
            'notes': notes
        })
        
        # Если доставлено, обновляем actual_delivery
        if status == ShipmentStatus.DELIVERED:
            shipment.actual_delivery = datetime.now()
            
        return True

    def _calculate_optimal_route(self,
                               origin: str,
                               destination: str,
                               transport_type: str) -> Optional[List[Dict]]:
        """
        Расчет оптимального маршрута
        """
        # Здесь должна быть логика расчета маршрута
        # Пример упрощенного маршрута
        return [
            {'point': origin, 'eta': datetime.now()},
            {'point': destination, 'eta': datetime.now() + timedelta(days=2)}
        ]

    def _calculate_eta(self, route: List[Dict]) -> datetime:
        """
        Расчет ожидаемого времени прибытия
        """
        return route[-1]['eta']

    def register_carrier(self,
                        carrier_id: str,
                        details: Dict,
                        capabilities: List[TransportType]) -> bool:
        """
        Регистрация перевозчика
        """
        if carrier_id in self.carriers:
            return False
            
        self.carriers[carrier_id] = {
            'details': details,
            'capabilities': [c.value for c in capabilities],
            'rating': 5.0,
            'active': True,
            'registered_at': datetime.now().isoformat()
        }
        
        return True

    def get_shipment_status(self, shipment_id: str) -> Optional[Dict]:
        """
        Получение текущего статуса поставки
        """
        if shipment_id not in self.shipments:
            return None
            
        shipment = self.shipments[shipment_id]
        current_status = self.tracking_data[shipment_id][-1]
        
        return {
            'shipment_id': shipment_id,
            'current_status': current_status['status'],
            'current_location': current_status['location'],
            'origin': shipment.origin,
            'destination': shipment.destination,
            'carrier': shipment.carrier,
            'estimated_delivery': shipment.estimated_delivery.isoformat(),
            'actual_delivery': shipment.actual_delivery.isoformat() if shipment.actual_delivery else None,
            'products': shipment.products
        }

    def get_tracking_history(self, shipment_id: str) -> Optional[List[Dict]]:
        """
        Получение истории отслеживания поставки
        """
        if shipment_id not in self.tracking_data:
            return None
            
        return self.tracking_data[shipment_id]

    def calculate_delivery_metrics(self, carrier_id: str) -> Optional[Dict]:
        """
        Расчет метрик доставки для перевозчика
        """
        if carrier_id not in self.carriers:
            return None
            
        completed_shipments = [
            s for s in self.shipments.values()
            if s.carrier == carrier_id and s.actual_delivery
        ]
        
        if not completed_shipments:
            return None
            
        # Рассчитываем метрики
        on_time_deliveries = len([
            s for s in completed_shipments
            if s.actual_delivery <= s.estimated_delivery
        ])
        
        total_deliveries = len(completed_shipments)
        
        return {
            'total_deliveries': total_deliveries,
            'on_time_rate': on_time_deliveries / total_deliveries,
            'average_delay': self._calculate_average_delay(completed_shipments),
            'performance_score': self._calculate_performance_score(completed_shipments)
        }

    def _calculate_average_delay(self, shipments: List[ShipmentDetails]) -> float:
        """
        Расчет среднего времени задержки
        """
        delays = [
            (s.actual_delivery - s.estimated_delivery).total_seconds() / 3600
            for s in shipments
            if s.actual_delivery > s.estimated_delivery
        ]
        
        return np.mean(delays) if delays else 0.0

    def _calculate_performance_score(self, shipments: List[ShipmentDetails]) -> float:
        """
        Расчет показателя эффективности
        """
        scores = []
        for shipment in shipments:
            # Учитываем своевременность доставки
            on_time = 1.0 if shipment.actual_delivery <= shipment.estimated_delivery else 0.5
            scores.append(on_time)
            
        return np.mean(scores) if scores else 0.0
