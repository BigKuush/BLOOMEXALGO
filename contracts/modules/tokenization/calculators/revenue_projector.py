from typing import List, Dict, Optional
from datetime import datetime, timedelta
import numpy as np

class RevenueProjector:
    """
    Проектор выручки для токенизированных бизнесов
    """
    def __init__(self):
        self.PROJECTION_PERIODS = {
            'monthly': 12,
            'quarterly': 4,
            'yearly': 5
        }
        self.RISK_LEVELS = {
            'low': 0.05,      # 5% волатильность
            'medium': 0.10,   # 10% волатильность
            'high': 0.15      # 15% волатильность
        }

    def project_revenue(self,
                       initial_revenue: float,
                       period: str = 'monthly',
                       risk_level: str = 'medium',
                       growth_rate: float = 0.05,
                       historical_data: Optional[List[float]] = None) -> Dict:
        """
        Проецирует будущую выручку бизнеса
        
        Args:
            initial_revenue: Начальная выручка
            period: Период проекции ('monthly', 'quarterly', 'yearly')
            risk_level: Уровень риска ('low', 'medium', 'high')
            growth_rate: Ожидаемый рост (по умолчанию 5%)
            historical_data: Исторические данные о выручке
        """
        if period not in self.PROJECTION_PERIODS:
            raise ValueError(f"Invalid period: {period}")
            
        if risk_level not in self.RISK_LEVELS:
            raise ValueError(f"Invalid risk level: {risk_level}")

        num_periods = self.PROJECTION_PERIODS[period]
        volatility = self.RISK_LEVELS[risk_level]

        # Корректируем рост на основе исторических данных
        if historical_data:
            historical_growth = self._calculate_historical_growth(historical_data)
            growth_rate = (growth_rate + historical_growth) / 2

        projections = self._generate_projections(
            initial_revenue,
            num_periods,
            growth_rate,
            volatility
        )

        return {
            'period': period,
            'risk_level': risk_level,
            'growth_rate': growth_rate,
            'projections': projections,
            'statistics': self._calculate_statistics(projections)
        }

    def _generate_projections(self,
                            initial_value: float,
                            num_periods: int,
                            growth_rate: float,
                            volatility: float) -> List[Dict]:
        """
        Генерирует проекции с учетом волатильности
        """
        projections = []
        current_value = initial_value

        for period in range(num_periods):
            # Добавляем случайную волатильность
            random_factor = np.random.normal(0, volatility)
            period_growth = growth_rate + random_factor
            
            # Рассчитываем новое значение
            current_value *= (1 + period_growth)
            
            projection = {
                'period': period + 1,
                'value': round(current_value, 2),
                'growth': round(period_growth * 100, 2),
                'timestamp': (datetime.now() + timedelta(days=30 * (period + 1))).isoformat()
            }
            
            projections.append(projection)

        return projections

    def _calculate_historical_growth(self, historical_data: List[float]) -> float:
        """
        Рассчитывает исторический рост
        """
        if len(historical_data) < 2:
            return 0.0
            
        growth_rates = []
        for i in range(1, len(historical_data)):
            rate = (historical_data[i] - historical_data[i-1]) / historical_data[i-1]
            growth_rates.append(rate)
            
        return np.mean(growth_rates)

    def _calculate_statistics(self, projections: List[Dict]) -> Dict:
        """
        Рассчитывает статистику по проекциям
        """
        values = [p['value'] for p in projections]
        growth_rates = [p['growth'] for p in projections]
        
        return {
            'min_value': round(min(values), 2),
            'max_value': round(max(values), 2),
            'mean_value': round(np.mean(values), 2),
            'median_value': round(np.median(values), 2),
            'std_dev': round(np.std(values), 2),
            'avg_growth': round(np.mean(growth_rates), 2),
            'volatility': round(np.std(growth_rates), 2)
        }

    def generate_report(self,
                       business_id: str,
                       projections: Dict,
                       additional_metrics: Optional[Dict] = None) -> Dict:
        """
        Генерирует отчет с проекциями и метриками
        """
        report = {
            'business_id': business_id,
            'generated_at': datetime.now().isoformat(),
            'projection_data': projections,
            'risk_assessment': self._assess_risk(projections),
        }

        if additional_metrics:
            report['additional_metrics'] = additional_metrics

        return report

    def _assess_risk(self, projections: Dict) -> Dict:
        """
        Оценивает риски на основе проекций
        """
        stats = projections['statistics']
        volatility = stats['volatility']
        
        risk_assessment = {
            'volatility_level': 'low' if volatility < 5 else 'medium' if volatility < 10 else 'high',
            'confidence_score': max(0, min(100, 100 - volatility * 5)),
            'risk_factors': []
        }

        # Анализ факторов риска
        if stats['std_dev'] / stats['mean_value'] > 0.2:
            risk_assessment['risk_factors'].append('High revenue variability')
            
        if stats['avg_growth'] < 0:
            risk_assessment['risk_factors'].append('Negative growth trend')

        return risk_assessment
