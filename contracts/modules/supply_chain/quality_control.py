from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

class QualityStatus(Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    SATISFACTORY = "SATISFACTORY"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    REJECTED = "REJECTED"

class InspectionType(Enum):
    INITIAL = "INITIAL"
    ROUTINE = "ROUTINE"
    RANDOM = "RANDOM"
    COMPLAINT = "COMPLAINT"

@dataclass
class QualityMetrics:
    product_id: str
    inspection_date: datetime
    inspector: str
    inspection_type: InspectionType
    quality_score: float
    parameters: Dict[str, float]
    compliance_status: bool
    notes: str

class QualityController:
    """
    Система контроля качества продукции
    """
    def __init__(self):
        self.quality_records: Dict[str, List[QualityMetrics]] = {}
        self.quality_standards: Dict[str, Dict] = {}
        self.inspectors: Set[str] = set()
        self.compliance_history: Dict[str, List[Dict]] = {}
        
    def register_quality_standard(self,
                                product_type: str,
                                standards: Dict[str, float],
                                compliance_threshold: float) -> bool:
        """
        Регистрация стандартов качества для типа продукции
        """
        if product_type in self.quality_standards:
            return False
            
        self.quality_standards[product_type] = {
            'standards': standards,
            'threshold': compliance_threshold,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        return True

    def perform_quality_check(self,
                            product_id: str,
                            inspector: str,
                            inspection_type: InspectionType,
                            measurements: Dict[str, float],
                            notes: str = "") -> Optional[QualityMetrics]:
        """
        Проведение проверки качества
        """
        if inspector not in self.inspectors:
            return None
            
        # Рассчитываем показатели качества
        quality_score = self._calculate_quality_score(measurements)
        
        # Проверяем соответствие стандартам
        compliance_status = self._check_compliance(measurements)
        
        metrics = QualityMetrics(
            product_id=product_id,
            inspection_date=datetime.now(),
            inspector=inspector,
            inspection_type=inspection_type,
            quality_score=quality_score,
            parameters=measurements,
            compliance_status=compliance_status,
            notes=notes
        )
        
        # Сохраняем результаты
        if product_id not in self.quality_records:
            self.quality_records[product_id] = []
            
        self.quality_records[product_id].append(metrics)
        
        # Обновляем историю соответствия
        self._update_compliance_history(product_id, metrics)
        
        return metrics

    def _calculate_quality_score(self, measurements: Dict[str, float]) -> float:
        """
        Расчет общего показателя качества
        """
        scores = []
        weights = {
            'physical': 0.3,
            'chemical': 0.3,
            'biological': 0.2,
            'organoleptic': 0.2
        }
        
        for category, params in measurements.items():
            if isinstance(params, dict):
                category_score = np.mean(list(params.values()))
                scores.append(category_score * weights.get(category, 0.25))
                
        return sum(scores)

    def _check_compliance(self, measurements: Dict[str, float]) -> bool:
        """
        Проверка соответствия стандартам качества
        """
        for param, value in measurements.items():
            standard = self.quality_standards.get(param, {}).get('threshold', 0)
            if value < standard:
                return False
        return True

    def _update_compliance_history(self, product_id: str, metrics: QualityMetrics):
        """
        Обновление истории соответствия стандартам
        """
        if product_id not in self.compliance_history:
            self.compliance_history[product_id] = []
            
        self.compliance_history[product_id].append({
            'timestamp': metrics.inspection_date.isoformat(),
            'inspector': metrics.inspector,
            'type': metrics.inspection_type.value,
            'score': metrics.quality_score,
            'compliant': metrics.compliance_status
        })

    def get_quality_status(self, product_id: str) -> Optional[QualityStatus]:
        """
        Получение текущего статуса качества продукта
        """
        if product_id not in self.quality_records:
            return None
            
        latest_check = self.quality_records[product_id][-1]
        score = latest_check.quality_score
        
        if score >= 0.9:
            return QualityStatus.EXCELLENT
        elif score >= 0.8:
            return QualityStatus.GOOD
        elif score >= 0.7:
            return QualityStatus.SATISFACTORY
        elif score >= 0.6:
            return QualityStatus.NEEDS_IMPROVEMENT
        else:
            return QualityStatus.REJECTED

    def get_quality_history(self, product_id: str) -> Optional[List[Dict]]:
        """
        Получение истории проверок качества
        """
        if product_id not in self.quality_records:
            return None
            
        return [{
            'date': check.inspection_date.isoformat(),
            'inspector': check.inspector,
            'type': check.inspection_type.value,
            'score': check.quality_score,
            'compliant': check.compliance_status,
            'notes': check.notes
        } for check in self.quality_records[product_id]]

    def register_inspector(self, inspector_address: str, credentials: Dict) -> bool:
        """
        Регистрация инспектора качества
        """
        if inspector_address in self.inspectors:
            return False
            
        self.inspectors.add(inspector_address)
        return True

    def update_quality_standards(self,
                               product_type: str,
                               new_standards: Dict[str, float]) -> bool:
        """
        Обновление стандартов качества
        """
        if product_type not in self.quality_standards:
            return False
            
        self.quality_standards[product_type].update({
            'standards': new_standards,
            'last_updated': datetime.now().isoformat()
        })
        
        return True
