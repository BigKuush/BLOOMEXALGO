from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    total_value_locked: float
    daily_active_users: int
    transaction_volume: float
    average_stake_size: float
    stake_growth_rate: float
    yield_rate: float
    utilization_rate: float
    user_retention: float

class PerformanceAnalyzer:
    """
    Анализатор производительности платформы
    """
    def __init__(self):
        self.metrics_history: Dict[str, List[Dict]] = {}
        self.performance_thresholds = {
            'high': 0.8,    # 80% и выше
            'medium': 0.5,  # 50-80%
            'low': 0.3      # ниже 50%
        }

    def calculate_platform_metrics(self,
                                 current_data: Dict,
                                 historical_data: Optional[List[Dict]] = None) -> PerformanceMetrics:
        """
        Рассчитывает ключевые метрики производительности платформы
        """
        # Расчет TVL (Total Value Locked)
        tvl = self._calculate_tvl(current_data)
        
        # Расчет активных пользователей
        dau = self._calculate_daily_active_users(current_data)
        
        # Расчет объема транзакций
        volume = self._calculate_transaction_volume(current_data)
        
        # Расчет среднего размера стейка
        avg_stake = self._calculate_average_stake(current_data)
        
        # Расчет темпа роста стейкинга
        growth_rate = self._calculate_growth_rate(current_data, historical_data)
        
        # Расчет доходности
        yield_rate = self._calculate_yield_rate(current_data)
        
        # Расчет коэффициента использования
        utilization = self._calculate_utilization_rate(current_data)
        
        # Расчет удержания пользователей
        retention = self._calculate_user_retention(current_data, historical_data)
        
        metrics = PerformanceMetrics(
            total_value_locked=tvl,
            daily_active_users=dau,
            transaction_volume=volume,
            average_stake_size=avg_stake,
            stake_growth_rate=growth_rate,
            yield_rate=yield_rate,
            utilization_rate=utilization,
            user_retention=retention
        )
        
        # Сохраняем метрики в историю
        self._store_metrics(metrics)
        
        return metrics

    def _calculate_tvl(self, data: Dict) -> float:
        """
        Рассчитывает общую заблокированную стоимость
        """
        return sum(pool['total_staked'] for pool in data.get('pools', []))

    def _calculate_daily_active_users(self, data: Dict) -> int:
        """
        Рассчитывает количество активных пользователей за день
        """
        unique_users = set()
        for transaction in data.get('transactions', []):
            if (datetime.now() - transaction['timestamp']).days < 1:
                unique_users.add(transaction['user_address'])
        return len(unique_users)

    def _calculate_transaction_volume(self, data: Dict) -> float:
        """
        Рассчитывает объем транзакций
        """
        return sum(tx['amount'] for tx in data.get('transactions', []))

    def _calculate_average_stake(self, data: Dict) -> float:
        """
        Рассчитывает средний размер стейка
        """
        stakes = [position['amount'] for pool in data.get('pools', [])
                 for position in pool.get('positions', [])]
        return np.mean(stakes) if stakes else 0

    def _calculate_growth_rate(self,
                             current_data: Dict,
                             historical_data: Optional[List[Dict]] = None) -> float:
        """
        Рассчитывает темп роста стейкинга
        """
        if not historical_data:
            return 0.0
            
        current_tvl = self._calculate_tvl(current_data)
        previous_tvl = self._calculate_tvl(historical_data[-1])
        
        if previous_tvl == 0:
            return 0.0
            
        return (current_tvl - previous_tvl) / previous_tvl

    def _calculate_yield_rate(self, data: Dict) -> float:
        """
        Рассчитывает среднюю доходность
        """
        yields = [pool['reward_rate'] for pool in data.get('pools', [])]
        return np.mean(yields) if yields else 0

    def _calculate_utilization_rate(self, data: Dict) -> float:
        """
        Рассчитывает коэффициент использования
        """
        total_capacity = sum(pool.get('max_stake', 0) for pool in data.get('pools', []))
        if total_capacity == 0:
            return 0.0
            
        current_tvl = self._calculate_tvl(data)
        return current_tvl / total_capacity

    def _calculate_user_retention(self,
                                current_data: Dict,
                                historical_data: Optional[List[Dict]] = None) -> float:
        """
        Рассчитывает показатель удержания пользователей
        """
        if not historical_data:
            return 0.0
            
        # Получаем пользователей за предыдущий период
        previous_users = set(tx['user_address'] for tx in historical_data[-1].get('transactions', []))
        
        # Получаем активных пользователей текущего периода
        current_users = set(tx['user_address'] for tx in current_data.get('transactions', []))
        
        if not previous_users:
            return 0.0
            
        # Считаем процент оставшихся пользователей
        retained_users = len(previous_users.intersection(current_users))
        return retained_users / len(previous_users)

    def _store_metrics(self, metrics: PerformanceMetrics):
        """
        Сохраняет метрики в историю
        """
        timestamp = datetime.now().isoformat()
        
        metrics_dict = {
            'timestamp': timestamp,
            'tvl': metrics.total_value_locked,
            'dau': metrics.daily_active_users,
            'volume': metrics.transaction_volume,
            'avg_stake': metrics.average_stake_size,
            'growth_rate': metrics.stake_growth_rate,
            'yield_rate': metrics.yield_rate,
            'utilization': metrics.utilization_rate,
            'retention': metrics.user_retention
        }
        
        for metric_name, value in metrics_dict.items():
            if metric_name not in self.metrics_history:
                self.metrics_history[metric_name] = []
            self.metrics_history[metric_name].append({
                'timestamp': timestamp,
                'value': value
            })

    def get_performance_report(self,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict:
        """
        Генерирует отчет о производительности
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'metrics': {},
            'trends': {},
            'recommendations': []
        }

        # Собираем метрики за период
        for metric_name, history in self.metrics_history.items():
            filtered_data = [
                entry for entry in history
                if start_date <= datetime.fromisoformat(entry['timestamp']) <= end_date
            ]
            
            values = [entry['value'] for entry in filtered_data]
            if values:
                report['metrics'][metric_name] = {
                    'current': values[-1],
                    'average': np.mean(values),
                    'min': min(values),
                    'max': max(values)
                }
                
                # Анализируем тренды
                report['trends'][metric_name] = self._analyze_trend(values)

        # Генерируем рекомендации
        report['recommendations'] = self._generate_recommendations(report['metrics'], report['trends'])

        return report
