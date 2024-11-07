from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

class ImpactCategory(Enum):
    ENVIRONMENTAL = "ENVIRONMENTAL"
    SOCIAL = "SOCIAL"
    ECONOMIC = "ECONOMIC"
    EDUCATIONAL = "EDUCATIONAL"
    HEALTHCARE = "HEALTHCARE"

class ImpactLevel(Enum):
    HIGH_POSITIVE = "HIGH_POSITIVE"
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    HIGH_NEGATIVE = "HIGH_NEGATIVE"

@dataclass
class ImpactMetrics:
    total_impact_score: float
    category_scores: Dict[ImpactCategory, float]
    beneficiaries_count: int
    community_engagement: float
    sustainability_score: float
    economic_value: float
    social_return: float

class ImpactAnalyzer:
    """
    Анализатор социального воздействия
    """
    def __init__(self):
        self.impact_history: Dict[str, List[Dict]] = {}
        self.category_weights = {
            ImpactCategory.ENVIRONMENTAL: 0.25,
            ImpactCategory.SOCIAL: 0.25,
            ImpactCategory.ECONOMIC: 0.2,
            ImpactCategory.EDUCATIONAL: 0.15,
            ImpactCategory.HEALTHCARE: 0.15
        }
        
    def analyze_impact(self,
                      project_id: str,
                      current_data: Dict,
                      historical_data: Optional[List[Dict]] = None) -> ImpactMetrics:
        """
        Проводит комплексный анализ социального воздействия
        """
        # Расчет показателей по категориям
        category_scores = self._calculate_category_scores(current_data)
        
        # Расчет общего показателя воздействия
        total_score = self._calculate_total_impact(category_scores)
        
        # Подсчет благополучателей
        beneficiaries = self._count_beneficiaries(current_data)
        
        # Расчет вовлеченности сообщества
        engagement = self._calculate_engagement(current_data)
        
        # Оценка устойчивости
        sustainability = self._calculate_sustainability(current_data)
        
        # Экономическая оценка
        economic_value = self._calculate_economic_value(current_data)
        
        # Расчет социального возврата на инвестиции
        social_return = self._calculate_social_return(current_data)
        
        metrics = ImpactMetrics(
            total_impact_score=total_score,
            category_scores=category_scores,
            beneficiaries_count=beneficiaries,
            community_engagement=engagement,
            sustainability_score=sustainability,
            economic_value=economic_value,
            social_return=social_return
        )
        
        # Сохраняем данные в историю
        self._store_impact_data(project_id, metrics)
        
        return metrics

    def _calculate_category_scores(self, data: Dict) -> Dict[ImpactCategory, float]:
        """
        Рассчитывает показатели по каждой категории воздействия
        """
        scores = {}
        
        for category in ImpactCategory:
            metrics = data.get(category.value.lower(), {})
            
            if category == ImpactCategory.ENVIRONMENTAL:
                scores[category] = self._calculate_environmental_score(metrics)
            elif category == ImpactCategory.SOCIAL:
                scores[category] = self._calculate_social_score(metrics)
            elif category == ImpactCategory.ECONOMIC:
                scores[category] = self._calculate_economic_score(metrics)
            elif category == ImpactCategory.EDUCATIONAL:
                scores[category] = self._calculate_educational_score(metrics)
            elif category == ImpactCategory.HEALTHCARE:
                scores[category] = self._calculate_healthcare_score(metrics)
                
        return scores

    def _calculate_total_impact(self, category_scores: Dict[ImpactCategory, float]) -> float:
        """
        Рассчитывает общий показатель воздействия
        """
        weighted_scores = [
            score * self.category_weights[category]
            for category, score in category_scores.items()
        ]
        return sum(weighted_scores)

    def _count_beneficiaries(self, data: Dict) -> int:
        """
        Подсчитывает количество благополучателей
        """
        direct = data.get('direct_beneficiaries', 0)
        indirect = data.get('indirect_beneficiaries', 0)
        return direct + indirect

    def _calculate_engagement(self, data: Dict) -> float:
        """
        Рассчитывает уровень вовлеченности сообщества
        """
        metrics = data.get('engagement_metrics', {})
        
        participation_rate = metrics.get('participation_rate', 0)
        feedback_score = metrics.get('feedback_score', 0)
        activity_level = metrics.get('activity_level', 0)
        
        return np.mean([participation_rate, feedback_score, activity_level])

    def _calculate_sustainability(self, data: Dict) -> float:
        """
        Оценивает устойчивость проекта
        """
        metrics = data.get('sustainability_metrics', {})
        
        environmental = metrics.get('environmental_sustainability', 0)
        financial = metrics.get('financial_sustainability', 0)
        social = metrics.get('social_sustainability', 0)
        
        return np.mean([environmental, financial, social])

    def _calculate_economic_value(self, data: Dict) -> float:
        """
        Рассчитывает экономическую ценность проекта
        """
        metrics = data.get('economic_metrics', {})
        
        direct_value = metrics.get('direct_economic_value', 0)
        indirect_value = metrics.get('indirect_economic_value', 0)
        cost_savings = metrics.get('cost_savings', 0)
        
        return direct_value + indirect_value + cost_savings

    def _calculate_social_return(self, data: Dict) -> float:
        """
        Рассчитывает социальный возврат на инвестиции (SROI)
        """
        total_benefits = self._calculate_economic_value(data)
        total_costs = data.get('total_costs', 1)  # Избегаем деления на ноль
        
        return total_benefits / total_costs if total_costs > 0 else 0

    def _store_impact_data(self, project_id: str, metrics: ImpactMetrics):
        """
        Сохраняет данные о воздействии в историю
        """
        if project_id not in self.impact_history:
            self.impact_history[project_id] = []
            
        self.impact_history[project_id].append({
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'total_score': metrics.total_impact_score,
                'category_scores': {k.value: v for k, v in metrics.category_scores.items()},
                'beneficiaries': metrics.beneficiaries_count,
                'engagement': metrics.community_engagement,
                'sustainability': metrics.sustainability_score,
                'economic_value': metrics.economic_value,
                'social_return': metrics.social_return
            }
        })
