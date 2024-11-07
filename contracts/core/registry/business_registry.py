from typing import Dict, Optional
from datetime import datetime

class Business:
    def __init__(self, owner: str, name: str, value: float):
        self.owner = owner
        self.name = name
        self.value = value
        self.tokenization_status = False
        self.created_at = datetime.now()
        self.token_address: Optional[str] = None
        self.metadata: Dict = {}

class BusinessRegistry:
    """
    Реестр токенизированных бизнесов
    """
    def __init__(self):
        self.businesses: Dict[str, Business] = {}
        
    def register_business(self, 
                         business_id: str, 
                         owner: str, 
                         name: str, 
                         value: float) -> Business:
        """Регистрирует новый бизнес"""
        if business_id in self.businesses:
            raise ValueError(f"Business {business_id} already registered")
            
        business = Business(owner, name, value)
        self.businesses[business_id] = business
        return business

    def get_business(self, business_id: str) -> Optional[Business]:
        """Получает информацию о бизнесе"""
        return self.businesses.get(business_id)

    def update_tokenization_status(self, 
                                 business_id: str, 
                                 token_address: str) -> bool:
        """Обновляет статус токенизации бизнеса"""
        business = self.get_business(business_id)
        if not business:
            return False
            
        business.tokenization_status = True
        business.token_address = token_address
        return True
