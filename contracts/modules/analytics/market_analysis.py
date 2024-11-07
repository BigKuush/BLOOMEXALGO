from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from enum import Enum

class MarketTrend(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    VOLATILE = "VOLATILE"

@dataclass
class MarketMetrics:
    volume_24h: float
    price_change_24h: float
    market_cap: float
    liquidity: float
    volatility: float
    trend: MarketTrend
    correlation_with_market: float

class MarketAnalyzer:
    """
    Анализатор рыночных данных и тенденций
    """
    def __init__(self):
        self.market_data_history: Dict[str, List[Dict]] = {}
        self.correlation_pairs: Dict[str, float] = {}
        self.trend_thresholds = {
            'volatility': 0.15,     # 15% порог волатильности
            'trend_strength': 0.1,  # 10% для определения тренда
            'liquidity': 1000000    # Минимальный порог ликвидности
        }

    def analyze_market(self,
                      token_id: str,
                      current_data: Dict,
                      historical_data: Optional[List[Dict]] = None) -> MarketMetrics:
        """
        Проводит комплексный анализ рынка для токена
        """
        # Расчет основных метрик
        volume_24h = self._calculate_24h_volume(current_data)
        price_change = self._calculate_price_change(current_data, historical_data)
        market_cap = self._calculate_market_cap(current_data)
        liquidity = self._calculate_liquidity(current_data)
        
        # Расчет волатильности и тренда
        volatility = self._calculate_volatility(historical_data)
        trend = self._determine_market_trend(historical_data)
        
        # Расчет корреляции с рынком
        correlation = self._calculate_market_correlation(token_id, historical_data)
        
        metrics = MarketMetrics(
            volume_24h=volume_24h,
            price_change_24h=price_change,
            market_cap=market_cap,
            liquidity=liquidity,
            volatility=volatility,
            trend=trend,
            correlation_with_market=correlation
        )
        
        # Сохраняем данные в историю
        self._store_market_data(token_id, metrics)
        
        return metrics

    def _calculate_24h_volume(self, data: Dict) -> float:
        """
        Рассчитывает объем торгов за последние 24 часа
        """
        current_time = datetime.now()
        volume = sum(
            tx['amount'] * tx['price']
            for tx in data.get('transactions', [])
            if current_time - tx['timestamp'] <= timedelta(hours=24)
        )
        return volume

    def _calculate_price_change(self,
                              current_data: Dict,
                              historical_data: Optional[List[Dict]] = None) -> float:
        """
        Рассчитывает изменение цены за 24 часа
        """
        if not historical_data:
            return 0.0
            
        current_price = current_data.get('price', 0)
        previous_price = historical_data[-1].get('price', current_price)
        
        if previous_price == 0:
            return 0.0
            
        return ((current_price - previous_price) / previous_price) * 100

    def _calculate_market_cap(self, data: Dict) -> float:
        """
        Рассчитывает рыночную капитализацию
        """
        total_supply = data.get('total_supply', 0)
        current_price = data.get('price', 0)
        return total_supply * current_price

    def _calculate_liquidity(self, data: Dict) -> float:
        """
        Рассчитывает ликвидность токена
        """
        buy_orders = sum(order['amount'] for order in data.get('buy_orders', []))
        sell_orders = sum(order['amount'] for order in data.get('sell_orders', []))
        return min(buy_orders, sell_orders)

    def _calculate_volatility(self, historical_data: Optional[List[Dict]] = None) -> float:
        """
        Рассчитывает волатильность на основе исторических данных
        """
        if not historical_data:
            return 0.0
            
        prices = [data.get('price', 0) for data in historical_data]
        if len(prices) < 2:
            return 0.0
            
        returns = np.diff(prices) / prices[:-1]
        return np.std(returns) * np.sqrt(365)  # Годовая волатильность

    def _determine_market_trend(self, historical_data: Optional[List[Dict]] = None) -> MarketTrend:
        """
        Определяет текущий тренд рынка
        """
        if not historical_data or len(historical_data) < 2:
            return MarketTrend.NEUTRAL
            
        prices = [data.get('price', 0) for data in historical_data]
        price_changes = np.diff(prices) / prices[:-1]
        
        avg_change = np.mean(price_changes)
        volatility = np.std(price_changes)
        
        if volatility > self.trend_thresholds['volatility']:
            return MarketTrend.VOLATILE
        elif avg_change > self.trend_thresholds['trend_strength']:
            return MarketTrend.BULLISH
        elif avg_change < -self.trend_thresholds['trend_strength']:
            return MarketTrend.BEARISH
        else:
            return MarketTrend.NEUTRAL

    def _calculate_market_correlation(self,
                                   token_id: str,
                                   historical_data: Optional[List[Dict]] = None) -> float:
        """
        Рассчитывает корреляцию с общим рынком
        """
        if not historical_data:
            return 0.0
            
        # Получаем данные рынка (например, индекс всего рынка)
        market_data = self._get_market_index_data(len(historical_data))
        
        # Рассчитываем корреляцию
        token_returns = self._calculate_returns([d.get('price', 0) for d in historical_data])
        market_returns = self._calculate_returns(market_data)
        
        if len(token_returns) != len(market_returns):
            return 0.0
            
        return float(np.corrcoef(token_returns, market_returns)[0, 1])

    def _calculate_returns(self, prices: List[float]) -> List[float]:
        """
        Рассчитывает доходность
        """
        return np.diff(prices) / prices[:-1]

    def _get_market_index_data(self, length: int) -> List[float]:
        """
        Получает данные рыночного индекса
        """
        # Здесь должна быть логика получения данных рыночного индекса
        # Временно возвращаем моковые данные
        return [100 + i for i in range(length)]

    def _store_market_data(self, token_id: str, metrics: MarketMetrics):
        """
        Сохраняет рыночные данные в историю
        """
        if token_id not in self.market_data_history:
            self.market_data_history[token_id] = []
            
        self.market_data_history[token_id].append({
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'volume': metrics.volume_24h,
                'price_change': metrics.price_change_24h,
                'market_cap': metrics.market_cap,
                'liquidity': metrics.liquidity,
                'volatility': metrics.volatility,
                'trend': metrics.trend.value,
                'correlation': metrics.correlation_with_market
            }
        })

    def get_market_analysis_report(self,
                                 token_id: str,
                                 period_days: int = 30) -> Dict:
        """
        Генерирует отчет по анализу рынка
        """
        if token_id not in self.market_data_history:
            return {}
            
        start_date = datetime.now() - timedelta(days=period_days)
        
        # Фильтруем данные за период
        period_data = [
            entry for entry in self.market_data_history[token_id]
            if datetime.fromisoformat(entry['timestamp']) >= start_date
        ]
        
        if not period_data:
            return {}
            
        return {
            'token_id': token_id,
            'period': {
                'start': start_date.isoformat(),
                'end': datetime.now().isoformat()
            },
            'market_metrics': self._calculate_period_metrics(period_data),
            'trend_analysis': self._analyze_trends(period_data),
            'liquidity_analysis': self._analyze_liquidity(period_data),
            'recommendations': self._generate_market_recommendations(period_data)
        }
