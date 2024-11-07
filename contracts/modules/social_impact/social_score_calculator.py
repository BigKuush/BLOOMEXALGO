from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

class ScoreCategory(Enum):
    COMMUNITY_IMPACT = "COMMUNITY_IMPACT"
    SOCIAL_BENEFIT = "SOCIAL_BENEFIT"
    INCLUSION = "INCLUSION"
    EDUCATION = "EDUCATION"
    EMPOWERMENT = "EMPOWERMENT"

class ScoreLevel(Enum):
    EXCEPTIONAL = "EXCEPTIONAL"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    DEVELOPING = "DEVELOPING"
    LIMITED = "LIMITED"

@dataclass
class SocialScore:
    total_score: float
    category_scores: Dict[ScoreCategory, float]
    impact_level: ScoreLevel
    beneficiary_reach: int
    community_growth: float
    engagement_quality: float
    sustainability_factor: float

class SocialScoreCalculator:
    """
    Калькулятор социального скоринга
    """
    def __init__(self):
        self.score_history: Dict[str, List[Dict]] = {}
        self.category_weights = {
            ScoreCategory.COMMUNITY_IMPACT: 0.25,
            ScoreCategory.SOCIAL_BENEFIT: 0.25,
            ScoreCategory.INCLUSION: 0.2,
            ScoreCategory.EDUCATION: 0.15,
            ScoreCategory.EMPOWERMENT: 0.15
        }
        
    def calculate_social_score(self,
                             project_id: str,
                             current_data: Dict,
                             historical_data: Optional[List[Dict]] = None) -> SocialScore:
        """
        Рассчитывает комплексный социальный скоринг
        """
        # Расчет показателей по категориям
        category_scores = self._calculate_category_scores(current_data)
        
        # Расчет общего показателя
        total_score = self._calculate_total_score(category_scores)
        
        # Определение уровня воздействия
        impact_level = self._determine_impact_level(total_score)
        
        # Анализ охвата благополучателей
        beneficiary_reach = self._calculate_beneficiary_reach(current_data)
        
        # Расчет роста сообщества
        community_growth = self._calculate_community_growth(current_data, historical_data)
        
        # Оценка качества вовлеченности
        engagement_quality = self._evaluate_engagement_quality(current_data)
        
        # Расчет фактора устойчивости
        sustainability = self._calculate_sustainability_factor(current_data)
        
        score = SocialScore(
            total_score=total_score,
            category_scores=category_scores,
            impact_level=impact_level,
            beneficiary_reach=beneficiary_reach,
            community_growth=community_growth,
            engagement_quality=engagement_quality,
            sustainability_factor=sustainability
        )
        
        # Сохраняем данные
        self._store_score_data(project_id, score)
        
        return score

    def _calculate_category_scores(self, data: Dict) -> Dict[ScoreCategory, float]:
        """
        Рассчитывает показатели по каждой категории
        """
        scores = {}
        
        for category in ScoreCategory:
            if category == ScoreCategory.COMMUNITY_IMPACT:
                scores[category] = self._calculate_community_impact(data)
            elif category == ScoreCategory.SOCIAL_BENEFIT:
                scores[category] = self._calculate_social_benefit(data)
            elif category == ScoreCategory.INCLUSION:
                scores[category] = self._calculate_inclusion_score(data)
            elif category == ScoreCategory.EDUCATION:
                scores[category] = self._calculate_education_score(data)
            elif category == ScoreCategory.EMPOWERMENT:
                scores[category] = self._calculate_empowerment_score(data)
                
        return scores

    def _calculate_community_impact(self, data: Dict) -> float:
        """
        Рассчитывает показатель воздействия на сообщество
        """
        impact_data = data.get('community_impact', {})
        
        direct_impact = impact_data.get('direct_impact', 0)
        indirect_impact = impact_data.get('indirect_impact', 0)
        long_term_effect = impact_data.get('long_term_effect', 0)
        
        weights = {
            'direct': 0.4,
            'indirect': 0.3,
            'long_term': 0.3
        }
        
        return (
            direct_impact * weights['direct'] +
            indirect_impact * weights['indirect'] +
            long_term_effect * weights['long_term']
        )

    def _calculate_social_benefit(self, data: Dict) -> float:
        """
        Рассчитывает показатель социальной пользы
        """
        benefit_data = data.get('social_benefit', {})
        
        quality_of_life = benefit_data.get('quality_of_life', 0)
        economic_benefit = benefit_data.get('economic_benefit', 0)
        social_capital = benefit_data.get('social_capital', 0)
        
        weights = {
            'quality': 0.4,
            'economic': 0.3,
            'social': 0.3
        }
        
        return (
            quality_of_life * weights['quality'] +
            economic_benefit * weights['economic'] +
            social_capital * weights['social']
        )

    def _calculate_inclusion_score(self, data: Dict) -> float:
        """
        Рассчитывает показатель инклюзивности
        """
        inclusion_data = data.get('inclusion', {})
        
        diversity = inclusion_data.get('diversity', 0)
        accessibility = inclusion_data.get('accessibility', 0)
        participation = inclusion_data.get('participation', 0)
        
        weights = {
            'diversity': 0.35,
            'accessibility': 0.35,
            'participation': 0.3
        }
        
        return (
            diversity * weights['diversity'] +
            accessibility * weights['accessibility'] +
            participation * weights['participation']
        )

    def _calculate_education_score(self, data: Dict) -> float:
        """
        Рассчитывает образовательный показатель
        """
        education_data = data.get('education', {})
        
        knowledge_transfer = education_data.get('knowledge_transfer', 0)
        skill_development = education_data.get('skill_development', 0)
        awareness = education_data.get('awareness', 0)
        
        weights = {
            'knowledge': 0.35,
            'skills': 0.35,
            'awareness': 0.3
        }
        
        return (
            knowledge_transfer * weights['knowledge'] +
            skill_development * weights['skills'] +
            awareness * weights['awareness']
        )

    def _calculate_empowerment_score(self, data: Dict) -> float:
        """
        Рассчитывает показатель расширения возможностей
        """
        empowerment_data = data.get('empowerment', {})
        
        autonomy = empowerment_data.get('autonomy', 0)
        capacity_building = empowerment_data.get('capacity_building', 0)
        leadership = empowerment_data.get('leadership', 0)
        
        weights = {
            'autonomy': 0.35,
            'capacity': 0.35,
            'leadership': 0.3
        }
        
        return (
            autonomy * weights['autonomy'] +
            capacity_building * weights['capacity'] +
            leadership * weights['leadership']
        )

    def _calculate_total_score(self, category_scores: Dict[ScoreCategory, float]) -> float:
        """
        Рассчитывает общий социа��ьный скоринг
        """
        return sum(
            score * self.category_weights[category]
            for category, score in category_scores.items()
        )

    def _determine_impact_level(self, score: float) -> ScoreLevel:
        """
        Определяет уровень социального воздействия
        """
        if score >= 0.85:
            return ScoreLevel.EXCEPTIONAL
        elif score >= 0.7:
            return ScoreLevel.STRONG
        elif score >= 0.5:
            return ScoreLevel.MODERATE
        elif score >= 0.3:
            return ScoreLevel.DEVELOPING
        else:
            return ScoreLevel.LIMITED

    def _calculate_beneficiary_reach(self, data: Dict) -> int:
        """
        Рассчитывает охват благополучателей
        """
        reach_data = data.get('beneficiary_reach', {})
        
        direct_beneficiaries = reach_data.get('direct', 0)
        indirect_beneficiaries = reach_data.get('indirect', 0)
        
        return direct_beneficiaries + indirect_beneficiaries

    def _calculate_community_growth(self,
                                 current_data: Dict,
                                 historical_data: Optional[List[Dict]] = None) -> float:
        """
        Рассчитывает рост сообщества
        """
        if not historical_data:
            return 0.0
            
        current_size = current_data.get('community_size', 0)
        previous_size = historical_data[-1].get('community_size', current_size)
        
        if previous_size == 0:
            return 0.0
            
        return (current_size - previous_size) / previous_size

    def _evaluate_engagement_quality(self, data: Dict) -> float:
        """
        Оценивает качество вовлеченности
        """
        engagement_data = data.get('engagement', {})
        
        participation_rate = engagement_data.get('participation_rate', 0)
        feedback_quality = engagement_data.get('feedback_quality', 0)
        interaction_depth = engagement_data.get('interaction_depth', 0)
        
        return np.mean([participation_rate, feedback_quality, interaction_depth])

    def _calculate_sustainability_factor(self, data: Dict) -> float:
        """
        Рассчитывает фактор устойчивости
        """
        sustainability_data = data.get('sustainability', {})
        
        financial = sustainability_data.get('financial', 0)
        operational = sustainability_data.get('operational', 0)
        social = sustainability_data.get('social', 0)
        
        weights = {
            'financial': 0.35,
            'operational': 0.35,
            'social': 0.3
        }
        
        return (
            financial * weights['financial'] +
            operational * weights['operational'] +
            social * weights['social']
        )

    def _store_score_data(self, project_id: str, score: SocialScore):
        """
        Сохраняет данные о социальном скоринге
        """
        if project_id not in self.score_history:
            self.score_history[project_id] = []
            
        self.score_history[project_id].append({
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'total_score': score.total_score,
                'category_scores': {k.value: v for k, v in score.category_scores.items()},
                'impact_level': score.impact_level.value,
                'beneficiary_reach': score.beneficiary_reach,
                'community_growth': score.community_growth,
                'engagement_quality': score.engagement_quality,
                'sustainability_factor': score.sustainability_factor
            }
        })
