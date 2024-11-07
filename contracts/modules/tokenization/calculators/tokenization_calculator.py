from typing import Dict, Optional, List
import numpy as np
from datetime import datetime, timedelta

class TokenizationCalculator:
    """
    Калькулятор для расчета параметров токенизации
    """
    def __init__(self):
        self.MIN_TOKENIZATION_PERCENTAGE = 10
        self.MAX_TOKENIZATION_PERCENTAGE = 100
        self.TOKEN_DECIMALS = 6
        
    def calculate_tokenization(self,
                             business_value: float,
                             tokenization_percentage: float,
                             revenue_history: Optional[List[float]] = None) -> Dict:
        """
        Рассчитывает параметры токенизации бизнеса
        """
        if not self._validate_inputs(business_value, tokenization_percentage):
            raise ValueError("Invalid input parameters")
            
        tokenization_amount = business_value * (tokenization_percentage / 100)
        token_supply = self._calculate_token_supply(tokenization_amount)
        
        result = {
            "tokenization_amount": tokenization_amount,
            "token_supply": token_supply,
            "token_price": self._calculate_initial_token_price(tokenization_amount, token_supply),
            "projected_revenue": self._project_revenue(tokenization_amount, revenue_history),
            "staking_rewards": self._calculate_staking_rewards(token_supply)
        }
        
        return result
