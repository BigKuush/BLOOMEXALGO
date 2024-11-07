from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

class StakingStatus(Enum):
    ACTIVE = "ACTIVE"
    UNSTAKING = "UNSTAKING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

@dataclass
class StakingPosition:
    investor_address: str
    amount: float
    start_time: datetime
    lock_period: int  # в днях
    status: StakingStatus
    reward_rate: float
    accumulated_rewards: float = 0.0
    last_claim_time: Optional[datetime] = None

class StakingPool:
    """
    Пул стейкинга для определенного бизнеса/продукта
    """
    def __init__(self, 
                 pool_id: str,
                 business_id: str,
                 min_stake: float,
                 max_stake: float,
                 base_reward_rate: float):
        self.pool_id = pool_id
        self.business_id = business_id
        self.min_stake = min_stake
        self.max_stake = max_stake
        self.base_reward_rate = base_reward_rate
        self.total_staked = 0.0
        self.positions: Dict[str, StakingPosition] = {}
        self.created_at = datetime.now()
        self.metadata: Dict = {}

class StakingManager:
    """
    Управление стейкингом и пулами
    """
    def __init__(self, algod_client):
        self.algod_client = algod_client
        self.pools: Dict[str, StakingPool] = {}
        self.lock_period_multipliers = {
            30: 1.0,   # 30 дней - базовая ставка
            90: 1.2,   # 90 дней - +20% к базовой ставке
            180: 1.5,  # 180 дней - +50% к базовой ставке
            360: 2.0   # 360 дней - +100% к базовой ставке
        }

    def create_pool(self,
                   business_id: str,
                   min_stake: float,
                   max_stake: float,
                   base_reward_rate: float) -> StakingPool:
        """
        Создает новый пул стейкинга
        """
        pool_id = f"POOL_{business_id}_{datetime.now().strftime('%Y%m%d')}"
        pool = StakingPool(
            pool_id=pool_id,
            business_id=business_id,
            min_stake=min_stake,
            max_stake=max_stake,
            base_reward_rate=base_reward_rate
        )
        self.pools[pool_id] = pool
        return pool

    def stake(self,
             pool_id: str,
             investor_address: str,
             amount: float,
             lock_period: int) -> StakingPosition:
        """
        Создает новую позицию стейкинга
        """
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} not found")
            
        pool = self.pools[pool_id]
        
        if amount < pool.min_stake or amount > pool.max_stake:
            raise ValueError(f"Amount must be between {pool.min_stake} and {pool.max_stake}")
            
        if lock_period not in self.lock_period_multipliers:
            raise ValueError(f"Invalid lock period. Must be one of {list(self.lock_period_multipliers.keys())}")

        # Рассчитываем награду с учетом периода блокировки
        reward_rate = pool.base_reward_rate * self.lock_period_multipliers[lock_period]

        position = StakingPosition(
            investor_address=investor_address,
            amount=amount,
            start_time=datetime.now(),
            lock_period=lock_period,
            status=StakingStatus.ACTIVE,
            reward_rate=reward_rate
        )

        pool.positions[investor_address] = position
        pool.total_staked += amount
        
        return position

    def unstake(self, pool_id: str, investor_address: str) -> Dict:
        """
        Запускает процесс вывода средств из стейкинга
        """
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} not found")
            
        pool = self.pools[pool_id]
        position = pool.positions.get(investor_address)
        
        if not position:
            raise ValueError(f"No staking position found for {investor_address}")

        # Проверяем, прошел ли период блокировки
        lock_end_time = position.start_time + timedelta(days=position.lock_period)
        if datetime.now() < lock_end_time:
            raise ValueError(f"Lock period not ended. Ends at {lock_end_time}")

        # Рассчитываем финальные награды
        final_rewards = self._calculate_rewards(position)
        
        position.status = StakingStatus.UNSTAKING
        pool.total_staked -= position.amount

        return {
            'principal': position.amount,
            'rewards': final_rewards,
            'total': position.amount + final_rewards
        }

    def _calculate_rewards(self, position: StakingPosition) -> float:
        """
        Рассчитывает награды за стейкинг
        """
        if position.status != StakingStatus.ACTIVE:
            return 0.0

        time_staked = datetime.now() - (position.last_claim_time or position.start_time)
        days_staked = time_staked.days

        # Базовый расчет наград
        rewards = position.amount * (position.reward_rate / 365) * days_staked
        
        return round(rewards, 6)

    def get_pool_stats(self, pool_id: str) -> Dict:
        """
        Получает статистику пула
        """
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} not found")
            
        pool = self.pools[pool_id]
        
        active_positions = sum(1 for p in pool.positions.values() 
                             if p.status == StakingStatus.ACTIVE)
        
        return {
            'total_staked': pool.total_staked,
            'active_positions': active_positions,
            'avg_stake': pool.total_staked / active_positions if active_positions > 0 else 0,
            'created_at': pool.created_at,
            'min_stake': pool.min_stake,
            'max_stake': pool.max_stake,
            'base_reward_rate': pool.base_reward_rate
        }
