from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class RewardType(Enum):
    STAKING = "STAKING"
    PERFORMANCE = "PERFORMANCE"
    REFERRAL = "REFERRAL"
    SPECIAL = "SPECIAL"

@dataclass
class RewardEvent:
    event_id: str
    reward_type: RewardType
    amount: float
    timestamp: datetime
    recipient: str
    pool_id: str
    status: str = "PENDING"
    metadata: Dict = None

class RewardDistributor:
    """
    Управление распределением наград за стейкинг
    """
    def __init__(self, algod_client):
        self.algod_client = algod_client
        self.reward_events: List[RewardEvent] = []
        self.distribution_history: Dict[str, List[RewardEvent]] = {}
        self.bonus_multipliers: Dict[str, float] = {
            'early_adopter': 1.2,    # +20% для ранних участников
            'large_stake': 1.15,     # +15% для крупных стейков
            'long_term': 1.25        # +25% для долгосрочного стейкинга
        }
        
    def calculate_rewards(self,
                        position_id: str,
                        staking_data: Dict,
                        additional_metrics: Optional[Dict] = None) -> Dict:
        """
        Рассчитывает награды для позиции стейкинга
        """
        base_reward = self._calculate_base_reward(staking_data)
        bonus_reward = self._calculate_bonuses(staking_data, additional_metrics)
        
        total_reward = base_reward + bonus_reward
        
        reward_breakdown = {
            'base_reward': base_reward,
            'bonus_reward': bonus_reward,
            'total_reward': total_reward,
            'calculation_time': datetime.now().isoformat(),
            'applied_multipliers': self._get_applied_multipliers(staking_data)
        }
        
        return reward_breakdown

    def distribute_rewards(self,
                         pool_id: str,
                         rewards_data: List[Dict]) -> List[RewardEvent]:
        """
        Распределяет награды между участниками пула
        """
        distributed_events = []
        
        for reward_data in rewards_data:
            event = RewardEvent(
                event_id=f"REW_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.reward_events)}",
                reward_type=RewardType(reward_data.get('type', 'STAKING')),
                amount=reward_data['amount'],
                timestamp=datetime.now(),
                recipient=reward_data['recipient'],
                pool_id=pool_id,
                metadata=reward_data.get('metadata', {})
            )
            
            # Попытка распределения награды
            if self._process_reward_distribution(event):
                event.status = "COMPLETED"
            else:
                event.status = "FAILED"
                
            self.reward_events.append(event)
            distributed_events.append(event)
            
            # Обновляем историю распределения
            if pool_id not in self.distribution_history:
                self.distribution_history[pool_id] = []
            self.distribution_history[pool_id].append(event)
            
        return distributed_events

    def _calculate_base_reward(self, staking_data: Dict) -> float:
        """
        Рассчитывает базовую награду
        """
        amount = staking_data['amount']
        rate = staking_data['reward_rate']
        days = staking_data.get('days', 0)
        
        return amount * (rate / 365) * days

    def _calculate_bonuses(self,
                         staking_data: Dict,
                         additional_metrics: Optional[Dict] = None) -> float:
        """
        Рассчитывает бонусные награды
        """
        bonus = 0.0
        base_reward = self._calculate_base_reward(staking_data)
        
        # Проверяем различные бонусные условия
        if self._is_early_adopter(staking_data):
            bonus += base_reward * (self.bonus_multipliers['early_adopter'] - 1)
            
        if self._is_large_stake(staking_data):
            bonus += base_reward * (self.bonus_multipliers['large_stake'] - 1)
            
        if self._is_long_term_staker(staking_data):
            bonus += base_reward * (self.bonus_multipliers['long_term'] - 1)
            
        return bonus

    def _process_reward_distribution(self, event: RewardEvent) -> bool:
        """
        Обрабатывает распределение награды
        """
        try:
            # Здесь будет логика взаимодействия с блокчейном
            # для отправки наград
            return True
        except Exception as e:
            event.metadata = {
                'error': str(e),
                'error_time': datetime.now().isoformat()
            }
            return False

    def get_distribution_history(self,
                               pool_id: Optional[str] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[RewardEvent]:
        """
        Получает историю распределения наград
        """
        if pool_id and pool_id not in self.distribution_history:
            return []
            
        events = self.distribution_history.get(pool_id, self.reward_events)
        
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]
            
        return sorted(events, key=lambda x: x.timestamp, reverse=True)

    def _is_early_adopter(self, staking_data: Dict) -> bool:
        """
        Проверяет, является ли стейкер ранним участником
        """
        start_time = datetime.fromisoformat(staking_data['start_time'])
        return (datetime.now() - start_time) <= timedelta(days=30)

    def _is_large_stake(self, staking_data: Dict) -> bool:
        """
        Проверяет, является ли стейк крупным
        """
        return staking_data['amount'] >= 10000  # Пример порога

    def _is_long_term_staker(self, staking_data: Dict) -> bool:
        """
        Проверяет, является ли стейкер долгосрочным
        """
        return staking_data.get('lock_period', 0) >= 180  # 180 дней

    def _get_applied_multipliers(self, staking_data: Dict) -> Dict:
        """
        Получает примененные множители для расчета наград
        """
        multipliers = {}
        
        if self._is_early_adopter(staking_data):
            multipliers['early_adopter'] = self.bonus_multipliers['early_adopter']
            
        if self._is_large_stake(staking_data):
            multipliers['large_stake'] = self.bonus_multipliers['large_stake']
            
        if self._is_long_term_staker(staking_data):
            multipliers['long_term'] = self.bonus_multipliers['long_term']
            
        return multipliers
