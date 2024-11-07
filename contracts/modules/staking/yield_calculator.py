from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

@dataclass
class YieldMetrics:
    apy: float  # Annual Percentage Yield
    apr: float  # Annual Percentage Rate
    daily_rate: float
    total_return: float
    risk_adjusted_return: float
    volatility: float
    sharpe_ratio: float

class YieldCalculator:
    """
    Калькулятор доходности для стейкинга
    """
    def __init__(self):
        self.RISK_FREE_RATE = 0.03  # 3% годовых (условная безрисковая ставка)
        self.COMPOUNDING_FREQUENCY = {
            'daily': 365,
            'weekly': 52,
            'monthly': 12,
            'quarterly': 4,
            'yearly': 1
        }
        
    def calculate_yield_metrics(self,
                              principal: float,
                              reward_rate: float,
                              lock_period: int,
                              compounding_period: str = 'daily',
                              historical_data: Optional[List[float]] = None) -> YieldMetrics:
        """
        Рассчитывает метрики доходности
        
        Args:
            principal: Сумма стейкинга
            reward_rate: Годовая ставка вознаграждения
            lock_period: Период блокировки в днях
            compounding_period: Периодичность начисления
            historical_data: Исторические данные о доходности
        """
        if compounding_period not in self.COMPOUNDING_FREQUENCY:
            raise ValueError(f"Invalid compounding period: {compounding_period}")

        # Расчет базовых метрик
        apr = reward_rate
        apy = self._calculate_apy(reward_rate, compounding_period)
        daily_rate = reward_rate / 365
        
        # Расчет общей доходности
        total_return = self._calculate_total_return(
            principal,
            reward_rate,
            lock_period,
            compounding_period
        )
        
        # Расчет метрик риска
        volatility = self._calculate_volatility(historical_data) if historical_data else 0
        risk_adjusted_return = self._calculate_risk_adjusted_return(apy, volatility)
        sharpe_ratio = self._calculate_sharpe_ratio(apy, volatility)
        
        return YieldMetrics(
            apy=round(apy * 100, 2),
            apr=round(apr * 100, 2),
            daily_rate=round(daily_rate * 100, 4),
            total_return=round(total_return, 2),
            risk_adjusted_return=round(risk_adjusted_return * 100, 2),
            volatility=round(volatility * 100, 2),
            sharpe_ratio=round(sharpe_ratio, 2)
        )

    def _calculate_apy(self, rate: float, compounding_period: str) -> float:
        """
        Рассчитывает годовую процентную доходность с учетом компаундинга
        """
        n = self.COMPOUNDING_FREQUENCY[compounding_period]
        return (1 + rate/n)**n - 1

    def _calculate_total_return(self,
                              principal: float,
                              rate: float,
                              days: int,
                              compounding_period: str) -> float:
        """
        Рассчитывает общую доходность за период
        """
        n = self.COMPOUNDING_FREQUENCY[compounding_period]
        t = days / 365  # Конвертируем дни в годы
        
        return principal * ((1 + rate/n)**(n*t) - 1)

    def _calculate_volatility(self, historical_data: List[float]) -> float:
        """
        Рассчитывает волатильность на основе исторических данных
        """
        if len(historical_data) < 2:
            return 0
            
        returns = np.diff(historical_data) / historical_data[:-1]
        return np.std(returns)

    def _calculate_risk_adjusted_return(self, return_rate: float, volatility: float) -> float:
        """
        Рассчитывает доходность с учетом риска
        """
        if volatility == 0:
            return return_rate
        return return_rate / (1 + volatility)

    def _calculate_sharpe_ratio(self, return_rate: float, volatility: float) -> float:
        """
        Рассчитывает коэффициент Шарпа
        """
        if volatility == 0:
            return 0
        return (return_rate - self.RISK_FREE_RATE) / volatility

    def project_yields(self,
                      principal: float,
                      reward_rate: float,
                      lock_period: int,
                      compounding_period: str = 'daily') -> Dict[str, List[Dict]]:
        """
        Проецирует доходность на весь период стейкинга
        """
        projections = []
        current_value = principal
        daily_projections = []
        
        n = self.COMPOUNDING_FREQUENCY[compounding_period]
        daily_rate = reward_rate / 365
        
        for day in range(lock_period + 1):
            if compounding_period == 'daily':
                current_value *= (1 + daily_rate)
            else:
                # Для других периодов используем пропорциональное начисление
                period_rate = reward_rate / n
                if day % (365 // n) == 0:
                    current_value *= (1 + period_rate)
                    
            projection = {
                'day': day,
                'value': round(current_value, 2),
                'yield': round(current_value - principal, 2),
                'yield_percentage': round((current_value - principal) / principal * 100, 2)
            }
            daily_projections.append(projection)
            
            # Добавляем ключевые точки для графика
            if day == 0 or day == lock_period or day % 30 == 0:
                projections.append(projection)
                
        return {
            'daily_projections': daily_projections,
            'key_points': projections
        }

    def calculate_optimal_compound_period(self,
                                       reward_rate: float,
                                       lock_period: int) -> Dict[str, Dict]:
        """
        Рассчитывает оптимальный период компаундинга
        """
        results = {}
        
        for period in self.COMPOUNDING_FREQUENCY.keys():
            apy = self._calculate_apy(reward_rate, period)
            results[period] = {
                'apy': round(apy * 100, 2),
                'frequency': self.COMPOUNDING_FREQUENCY[period],
                'effective_rate': round((apy - reward_rate) * 100, 2)  # Дополнительная доходность
            }
            
        # Определяем оптимальный период
        optimal = max(results.items(), key=lambda x: x[1]['apy'])
        
        return {
            'periods': results,
            'optimal_period': optimal[0],
            'optimal_metrics': optimal[1]
        }
