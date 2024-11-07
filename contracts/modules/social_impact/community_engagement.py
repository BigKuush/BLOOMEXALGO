from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

class EngagementType(Enum):
    PARTICIPATION = "PARTICIPATION"
    FEEDBACK = "FEEDBACK"
    CONTRIBUTION = "CONTRIBUTION"
    GOVERNANCE = "GOVERNANCE"

class EngagementLevel(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INACTIVE = "INACTIVE"

@dataclass
class EngagementMetrics:
    active_participants: int
    engagement_rate: float
    feedback_score: float
    contribution_level: float
    governance_participation: float
    community_growth: float
    retention_rate: float

class CommunityManager:
    """
    Управление вовлеченностью сообщества
    """
    def __init__(self):
        self.engagement_history: Dict[str, List[Dict]] = {}
        self.activity_weights = {
            EngagementType.PARTICIPATION: 0.3,
            EngagementType.FEEDBACK: 0.2,
            EngagementType.CONTRIBUTION: 0.25,
            EngagementType.GOVERNANCE: 0.25
        }
        
    def analyze_engagement(self,
                         community_id: str,
                         current_data: Dict,
                         historical_data: Optional[List[Dict]] = None) -> EngagementMetrics:
        """
        Анализирует вовлеченность сообщества
        """
        # Подсчет активных участников
        active_users = self._count_active_participants(current_data)
        
        # Расчет уровня вовлеченности
        engagement_rate = self._calculate_engagement_rate(current_data)
        
        # Анализ обратной связи
        feedback = self._analyze_feedback(current_data)
        
        # Оценка уровня участия
        contribution = self._evaluate_contributions(current_data)
        
        # Анализ участия в управлении
        governance = self._analyze_governance_participation(current_data)
        
        # Расчет роста сообщества
        growth = self._calculate_community_growth(current_data, historical_data)
        
        # Расчет удержания
        retention = self._calculate_retention_rate(current_data, historical_data)
        
        metrics = EngagementMetrics(
            active_participants=active_users,
            engagement_rate=engagement_rate,
            feedback_score=feedback,
            contribution_level=contribution,
            governance_participation=governance,
            community_growth=growth,
            retention_rate=retention
        )
        
        # Сохраняем данные
        self._store_engagement_data(community_id, metrics)
        
        return metrics

    def _count_active_participants(self, data: Dict) -> int:
        """
        Подсчитывает количество активных участников
        """
        participants = set()
        
        # Учитываем различные типы активности
        for activity in data.get('activities', []):
            participants.add(activity.get('user_id'))
            
        return len(participants)

    def _calculate_engagement_rate(self, data: Dict) -> float:
        """
        Рассчитывает общий уровень вовлеченности
        """
        total_users = data.get('total_users', 1)  # Избегаем деления на ноль
        active_users = self._count_active_participants(data)
        
        return active_users / total_users if total_users > 0 else 0

    def _analyze_feedback(self, data: Dict) -> float:
        """
        Анализирует обратную связь от сообщества
        """
        feedback_data = data.get('feedback', {})
        
        # Анализируем различные аспекты обратной связи
        sentiment_score = feedback_data.get('sentiment_score', 0)
        response_rate = feedback_data.get('response_rate', 0)
        quality_score = feedback_data.get('quality_score', 0)
        
        return np.mean([sentiment_score, response_rate, quality_score])

    def _evaluate_contributions(self, data: Dict) -> float:
        """
        Оценивает уровень вклада участников
        """
        contributions = data.get('contributions', [])
        if not contributions:
            return 0.0
            
        # Оцениваем различные типы вкладов
        scores = []
        for contribution in contributions:
            score = contribution.get('impact_score', 0)
            weight = contribution.get('weight', 1)
            scores.append(score * weight)
            
        return np.mean(scores) if scores else 0.0

    def _analyze_governance_participation(self, data: Dict) -> float:
        """
        Анализирует участие в управлении
        """
        governance_data = data.get('governance', {})
        
        # Анализируем различные аспекты участия в управлении
        voting_rate = governance_data.get('voting_rate', 0)
        proposal_participation = governance_data.get('proposal_participation', 0)
        discussion_activity = governance_data.get('discussion_activity', 0)
        
        return np.mean([voting_rate, proposal_participation, discussion_activity])

    def _calculate_community_growth(self,
                                 current_data: Dict,
                                 historical_data: Optional[List[Dict]] = None) -> float:
        """
        Рассчитывает рост сообщества
        """
        if not historical_data:
            return 0.0
            
        current_size = current_data.get('total_users', 0)
        previous_size = historical_data[-1].get('total_users', current_size)
        
        if previous_size == 0:
            return 0.0
            
        return (current_size - previous_size) / previous_size

    def _calculate_retention_rate(self,
                                current_data: Dict,
                                historical_data: Optional[List[Dict]] = None) -> float:
        """
        Рассчитывает показатель удержания
        """
        if not historical_data:
            return 0.0
            
        previous_users = set(historical_data[-1].get('active_users', []))
        current_users = set(current_data.get('active_users', []))
        
        if not previous_users:
            return 0.0
            
        retained_users = len(previous_users.intersection(current_users))
        return retained_users / len(previous_users)

    def _store_engagement_data(self, community_id: str, metrics: EngagementMetrics):
        """
        Сохраняет данные о вовлеченности
        """
        if community_id not in self.engagement_history:
            self.engagement_history[community_id] = []
            
        self.engagement_history[community_id].append({
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'active_participants': metrics.active_participants,
                'engagement_rate': metrics.engagement_rate,
                'feedback_score': metrics.feedback_score,
                'contribution_level': metrics.contribution_level,
                'governance_participation': metrics.governance_participation,
                'community_growth': metrics.community_growth,
                'retention_rate': metrics.retention_rate
            }
        })
