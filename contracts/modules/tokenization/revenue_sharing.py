from typing import Dict, List
from datetime import datetime

class RevenueShare:
    def __init__(self, business_id: str, total_revenue: float):
        self.business_id = business_id
        self.total_revenue = total_revenue
        self.distribution_date = datetime.now()
        self.distributions: Dict[str, float] = {}
        self.status = "pending"

class RevenueSharing:
    """
    Управление распределением выручки
    """
    def __init__(self):
        self.revenue_shares: List[RevenueShare] = []
        
    def create_revenue_share(self,
                           business_id: str,
                           total_revenue: float,
                           token_holders: Dict[str, int]) -> RevenueShare:
        """
        Создает новое распределение выручки
        """
        revenue_share = RevenueShare(business_id, total_revenue)
        
        # Рассчитываем распределение
        total_tokens = sum(token_holders.values())
        for holder, tokens in token_holders.items():
            share = (tokens / total_tokens) * total_revenue
            revenue_share.distributions[holder] = share
            
        self.revenue_shares.append(revenue_share)
        return revenue_share
        
    def process_distribution(self, revenue_share: RevenueShare) -> bool:
        """
        Обрабатывает распределение выручки
        """
        try:
            # Здесь будет логика отправки платежей
            revenue_share.status = "completed"
            return True
        except Exception as e:
            revenue_share.status = "failed"
            raise e
            
    def get_holder_revenue(self, 
                          holder_address: str,
                          business_id: Optional[str] = None) -> float:
        """
        Получает сумму выручки для держателя токенов
        """
        total_revenue = 0.0
        for share in self.revenue_shares:
            if business_id and share.business_id != business_id:
                continue
            total_revenue += share.distributions.get(holder_address, 0)
        return total_revenue


