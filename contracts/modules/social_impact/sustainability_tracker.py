from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

class SustainabilityCategory(Enum):
    ENVIRONMENTAL = "ENVIRONMENTAL"
    SOCIAL = "SOCIAL"
    ECONOMIC = "ECONOMIC"
    GOVERNANCE = "GOVERNANCE"

class SustainabilityLevel(Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"

@dataclass
class SustainabilityMetrics:
    overall_score: float
    environmental_score: float
    social_score: float
    economic_score: float
    governance_score: float
    carbon_footprint: float
    resource_efficiency: float
    social_impact: float
    level: SustainabilityLevel

class SustainabilityTracker:
    """
    Отслеживание и анализ показателей устойчивого развития
    """
    def __init__(self):
        self.sustainability_history: Dict[str, List[Dict]] = {}
        self.category_weights = {
            SustainabilityCategory.ENVIRONMENTAL: 0.3,
            SustainabilityCategory.SOCIAL: 0.3,
            SustainabilityCategory.ECONOMIC: 0.2,
            SustainabilityCategory.GOVERNANCE: 0.2
        }
        
    def track_sustainability(self,
                           project_id: str,
                           current_data: Dict,
                           historical_data: Optional[List[Dict]] = None) -> SustainabilityMetrics:
        """
        Отслеживает и анализирует показатели устойчивости
        """
        # Расчет показателей по категориям
        environmental = self._calculate_environmental_metrics(current_data)
        social = self._calculate_social_metrics(current_data)
        economic = self._calculate_economic_metrics(current_data)
        governance = self._calculate_governance_metrics(current_data)
        
        # Расчет общего показателя
        overall_score = self._calculate_overall_score({
            SustainabilityCategory.ENVIRONMENTAL: environmental,
            SustainabilityCategory.SOCIAL: social,
            SustainabilityCategory.ECONOMIC: economic,
            SustainabilityCategory.GOVERNANCE: governance
        })
        
        # Расчет углеродного следа
        carbon_footprint = self._calculate_carbon_footprint(current_data)
        
        # Расчет эффективности использования ресурсов
        resource_efficiency = self._calculate_resource_efficiency(current_data)
        
        # Оценка социального воздействия
        social_impact = self._evaluate_social_impact(current_data)
        
        # Определение уровня устойчивости
        level = self._determine_sustainability_level(overall_score)
        
        metrics = SustainabilityMetrics(
            overall_score=overall_score,
            environmental_score=environmental,
            social_score=social,
            economic_score=economic,
            governance_score=governance,
            carbon_footprint=carbon_footprint,
            resource_efficiency=resource_efficiency,
            social_impact=social_impact,
            level=level
        )
        
        # Сохраняем данные
        self._store_sustainability_data(project_id, metrics)
        
        return metrics

    def _calculate_environmental_metrics(self, data: Dict) -> float:
        """
        Рассчитывает экологические показатели
        """
        metrics = data.get('environmental', {})
        
        # Анализируем различные экологические факторы
        carbon_score = metrics.get('carbon_efficiency', 0)
        waste_score = metrics.get('waste_management', 0)
        energy_score = metrics.get('energy_efficiency', 0)
        resource_score = metrics.get('resource_usage', 0)
        
        weights = {
            'carbon': 0.3,
            'waste': 0.2,
            'energy': 0.3,
            'resource': 0.2
        }
        
        return (
            carbon_score * weights['carbon'] +
            waste_score * weights['waste'] +
            energy_score * weights['energy'] +
            resource_score * weights['resource']
        )

    def _calculate_social_metrics(self, data: Dict) -> float:
        """
        Рассчитывает социальные показатели
        """
        metrics = data.get('social', {})
        
        community_impact = metrics.get('community_impact', 0)
        labor_practices = metrics.get('labor_practices', 0)
        human_rights = metrics.get('human_rights', 0)
        diversity = metrics.get('diversity_inclusion', 0)
        
        weights = {
            'community': 0.3,
            'labor': 0.25,
            'rights': 0.25,
            'diversity': 0.2
        }
        
        return (
            community_impact * weights['community'] +
            labor_practices * weights['labor'] +
            human_rights * weights['rights'] +
            diversity * weights['diversity']
        )

    def _calculate_economic_metrics(self, data: Dict) -> float:
        """
        Рассчитывает экономические показатели
        """
        metrics = data.get('economic', {})
        
        financial_sustainability = metrics.get('financial_sustainability', 0)
        market_presence = metrics.get('market_presence', 0)
        economic_impact = metrics.get('economic_impact', 0)
        innovation = metrics.get('innovation', 0)
        
        weights = {
            'financial': 0.3,
            'market': 0.2,
            'impact': 0.3,
            'innovation': 0.2
        }
        
        return (
            financial_sustainability * weights['financial'] +
            market_presence * weights['market'] +
            economic_impact * weights['impact'] +
            innovation * weights['innovation']
        )

    def _calculate_governance_metrics(self, data: Dict) -> float:
        """
        Рассчитывает показатели управления
        """
        metrics = data.get('governance', {})
        
        transparency = metrics.get('transparency', 0)
        accountability = metrics.get('accountability', 0)
        risk_management = metrics.get('risk_management', 0)
        compliance = metrics.get('compliance', 0)
        
        weights = {
            'transparency': 0.3,
            'accountability': 0.3,
            'risk': 0.2,
            'compliance': 0.2
        }
        
        return (
            transparency * weights['transparency'] +
            accountability * weights['accountability'] +
            risk_management * weights['risk'] +
            compliance * weights['compliance']
        )

    def _calculate_overall_score(self, category_scores: Dict[SustainabilityCategory, float]) -> float:
        """
        Рассчитывает общий показатель устойчивости
        """
        return sum(
            score * self.category_weights[category]
            for category, score in category_scores.items()
        )

    def _calculate_carbon_footprint(self, data: Dict) -> float:
        """
        Рассчитывает углеродный след
        """
        environmental = data.get('environmental', {})
        emissions = environmental.get('emissions', {})
        
        direct_emissions = emissions.get('direct', 0)
        indirect_emissions = emissions.get('indirect', 0)
        
        return direct_emissions + indirect_emissions

    def _calculate_resource_efficiency(self, data: Dict) -> float:
        """
        Рассчитывает эффективность использования ресурсов
        """
        resources = data.get('resource_usage', {})
        
        energy_efficiency = resources.get('energy_efficiency', 0)
        water_efficiency = resources.get('water_efficiency', 0)
        material_efficiency = resources.get('material_efficiency', 0)
        
        return np.mean([energy_efficiency, water_efficiency, material_efficiency])

    def _evaluate_social_impact(self, data: Dict) -> float:
        """
        Оценивает социальное воздействие
        """
        social = data.get('social_impact', {})
        
        community_benefit = social.get('community_benefit', 0)
        job_creation = social.get('job_creation', 0)
        skill_development = social.get('skill_development', 0)
        
        weights = {
            'community': 0.4,
            'jobs': 0.3,
            'skills': 0.3
        }
        
        return (
            community_benefit * weights['community'] +
            job_creation * weights['jobs'] +
            skill_development * weights['skills']
        )

    def _determine_sustainability_level(self, score: float) -> SustainabilityLevel:
        """
        Определяет уровень устойчивости на основе общего показателя
        """
        if score >= 0.8:
            return SustainabilityLevel.EXCELLENT
        elif score >= 0.6:
            return SustainabilityLevel.GOOD
        elif score >= 0.4:
            return SustainabilityLevel.FAIR
        else:
            return SustainabilityLevel.POOR

    def _store_sustainability_data(self, project_id: str, metrics: SustainabilityMetrics):
        """
        Сохраняет данные об устойчивости
        """
        if project_id not in self.sustainability_history:
            self.sustainability_history[project_id] = []
            
        self.sustainability_history[project_id].append({
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'overall_score': metrics.overall_score,
                'environmental_score': metrics.environmental_score,
                'social_score': metrics.social_score,
                'economic_score': metrics.economic_score,
                'governance_score': metrics.governance_score,
                'carbon_footprint': metrics.carbon_footprint,
                'resource_efficiency': metrics.resource_efficiency,
                'social_impact': metrics.social_impact,
                'level': metrics.level.value
            }
        })
