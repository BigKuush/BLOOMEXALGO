from typing import Dict, Optional
from datetime import datetime
from algosdk.future.transaction import AssetConfigTxn

class BusinessToken:
    def __init__(self, 
                 business_id: str,
                 token_name: str,
                 total_supply: int,
                 decimals: int = 6):
        self.business_id = business_id
        self.token_name = token_name
        self.token_symbol = f"BLX{business_id[:4].upper()}"
        self.total_supply = total_supply
        self.decimals = decimals
        self.created_at = datetime.now()
        self.asset_id: Optional[int] = None
        self.metadata: Dict = {}

class BusinessTokenization:
    """
    Управление токенизацией бизнеса
    """
    def __init__(self, algod_client):
        self.algod_client = algod_client
        self.tokens: Dict[str, BusinessToken] = {}
        
    def create_business_token(self,
                            business_id: str,
                            owner_address: str,
                            business_value: float,
                            tokenization_percentage: float) -> BusinessToken:
        """
        Создает токен для бизнеса
        """
        if business_id in self.tokens:
            raise ValueError(f"Token for business {business_id} already exists")
            
        # Рассчитываем параметры токена
        total_supply = int(business_value * tokenization_percentage * 10**6)
        token_name = f"BloomexBusiness{business_id}"
        
        token = BusinessToken(
            business_id=business_id,
            token_name=token_name,
            total_supply=total_supply
        )
        
        # Создаем ASA (Algorand Standard Asset)
        params = self.algod_client.suggested_params()
        txn = AssetConfigTxn(
            sender=owner_address,
            sp=params,
            total=total_supply,
            default_frozen=False,
            unit_name=token.token_symbol,
            asset_name=token_name,
            manager=owner_address,
            reserve=owner_address,
            freeze=owner_address,
            clawback=owner_address,
            decimals=token.decimals
        )
        
        # Сохраняем информацию о токене
        self.tokens[business_id] = token
        return token
        
    def get_token_info(self, business_id: str) -> Optional[BusinessToken]:
        """
        Получает информацию о токене бизнеса
        """
        return self.tokens.get(business_id)
        
    def calculate_token_distribution(self,
                                   business_id: str,
                                   investors: Dict[str, float]) -> Dict[str, int]:
        """
        Рассчитывает распределение токенов между инвесторами
        """
        token = self.get_token_info(business_id)
        if not token:
            raise ValueError(f"Token for business {business_id} not found")
            
        total_investment = sum(investors.values())
        distribution = {}
        
        for investor, amount in investors.items():
            percentage = amount / total_investment
            tokens_amount = int(token.total_supply * percentage)
            distribution[investor] = tokens_amount
            
        return distribution
