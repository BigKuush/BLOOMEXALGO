from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskCategory(Enum):
    MARKET = "MARKET"
    LIQUIDITY = "LIQUIDITY"
    OPERATIONAL = "OPERATIONAL"
    SMART_CONTRACT = "SMART_CONTRACT"
    REGULATORY = "REGULATORY"

@dataclass
class RiskMetrics:
    overall_risk: RiskLevel
    risk_score: float  # 0-100
    risk_breakdown: Dict[RiskCategory, float]
    var_daily: float  # Value at Risk (дневной)
    max_drawdown: float
    stress_test_results: Dict[str, float]
    risk_indicators: Dict[str, bool]

class RiskAssessor:
    """
    Анализатор и оценщик рисков платформы
    """
    def __init__(self):
        self.risk_history: Dict[str, List[Dict]] = {}
        self.risk_weights = {
            RiskCategory.MARKET: 0.3,
            RiskCategory.LIQUIDITY: 0.25,
            RiskCategory.OPERATIONAL: 0.2,
            RiskCategory.SMART_CONTRACT: 0.15,
            RiskCategory.REGULATORY: 0.1
        }
        self.risk_thresholds = {
            'var_limit': 0.15,  # 15% VaR предел
            'liquidity_min': 1000000,  # Минимальная ликвидность
            'concentration_max': 0.2,  # Максимальная концентрация 20%
            'volatility_threshold': 0.25  # Порог волатильности
        }

    def assess_risks(self,
                    current_data: Dict,
                    historical_data: Optional[List[Dict]] = None) -> RiskMetrics:
        """
        Проводит комплексную оценку рисков
        """
        # Оценка рисков по категориям
        market_risk = self._assess_market_risk(current_data, historical_data)
        liquidity_risk = self._assess_liquidity_risk(current_data)
        operational_risk = self._assess_operational_risk(current_data)
        smart_contract_risk = self._assess_smart_contract_risk(current_data)
        regulatory_risk = self._assess_regulatory_risk(current_data)

        # Расчет общего риск-скора
        risk_breakdown = {
            RiskCategory.MARKET: market_risk,
            RiskCategory.LIQUIDITY: liquidity_risk,
            RiskCategory.OPERATIONAL: operational_risk,
            RiskCategory.SMART_CONTRACT: smart_contract_risk,
            RiskCategory.REGULATORY: regulatory_risk
        }

        risk_score = self._calculate_overall_risk_score(risk_breakdown)
        overall_risk = self._determine_risk_level(risk_score)

        # Расчет VaR и других метрик
        var_daily = self._calculate_var(historical_data)
        max_drawdown = self._calculate_max_drawdown(historical_data)
        stress_test_results = self._run_stress_tests(current_data, historical_data)
        risk_indicators = self._check_risk_indicators(current_data)

        metrics = RiskMetrics(
            overall_risk=overall_risk,
            risk_score=risk_score,
            risk_breakdown=risk_breakdown,
            var_daily=var_daily,
            max_drawdown=max_drawdown,
            stress_test_results=stress_test_results,
            risk_indicators=risk_indicators
        )

        # Сохраняем оценку в историю
        self._store_risk_assessment(metrics)

        return metrics

    def _assess_market_risk(self,
                           current_data: Dict,
                           historical_data: Optional[List[Dict]] = None) -> float:
        """
        Оценивает рыночные риски
        """
        if not historical_data:
            return 0.5  # Средний риск при отсутствии данных

        # Расчет волатильности
        prices = [data.get('price', 0) for data in historical_data]
        volatility = np.std(np.diff(prices) / prices[:-1])

        # Расчет корреляции с рынком
        market_correlation = self._calculate_market_correlation(historical_data)

        # Оценка концентрации
        concentration = self._calculate_concentration(current_data)

        # Комбинируем факторы
        market_risk = (
            0.4 * min(1, volatility / self.risk_thresholds['volatility_threshold']) +
            0.3 * abs(market_correlation) +
            0.3 * min(1, concentration / self.risk_thresholds['concentration_max'])
        )

        return market_risk

    def _assess_liquidity_risk(self, current_data: Dict) -> float:
        """
        Оценивает риски ликвидности
        """
        liquidity = current_data.get('liquidity', 0)
        volume = current_data.get('volume_24h', 0)
        bid_ask_spread = current_data.get('spread', 0.01)

        # Нормализация метрик
        liquidity_score = min(1, liquidity / self.risk_thresholds['liquidity_min'])
        volume_score = min(1, volume / (liquidity * 0.1))  # Ожидаем 10% оборот
        spread_score = min(1, bid_ask_spread / 0.05)  # 5% максимальный спред

        # Комбинируем факторы
        liquidity_risk = (
            0.4 * (1 - liquidity_score) +
            0.3 * (1 - volume_score) +
            0.3 * spread_score
        )

        return liquidity_risk

    def _assess_operational_risk(self, current_data: Dict) -> float:
        """
        Оценивает операционные риски
        """
        # Проверяем различные операционные метрики
        uptime = current_data.get('system_uptime', 100) / 100
        error_rate = current_data.get('error_rate', 0)
        pending_operations = current_data.get('pending_operations', 0)
        
        # Нормализация метрик
        uptime_score = 1 - uptime
        error_score = min(1, error_rate / 0.01)  # 1% максимум ошибок
        pending_score = min(1, pending_operations / 1000)  # 1000 операций максимум

        # Комбинируем факторы
        operational_risk = (
            0.4 * uptime_score +
            0.4 * error_score +
            0.2 * pending_score
        )

        return operational_risk

    def _assess_smart_contract_risk(self, current_data: Dict) -> float:
        """
        Оценивает риски смарт-контрактов
        """
        # Проверяем метрики безопасности контрактов
        audit_score = current_data.get('audit_score', 0.5)
        vulnerability_count = current_data.get('vulnerabilities', 0)
        code_coverage = current_data.get('test_coverage', 0.8)

        # Нормализация метрик
        audit_risk = 1 - audit_score
        vulnerability_risk = min(1, vulnerability_count / 10)  # 10 уязвимостей максимум
        coverage_risk = 1 - code_coverage

        # Комбинируем факторы
        contract_risk = (
            0.4 * audit_risk +
            0.4 * vulnerability_risk +
            0.2 * coverage_risk
        )

        return contract_risk

    def _assess_regulatory_risk(self, current_data: Dict) -> float:
        """
        Оценивает регуляторные риски
        """
        # Проверяем соответствие регуляторным требованиям
        compliance_score = current_data.get('compliance_score', 0.8)
        regulatory_changes = current_data.get('regulatory_changes', 0)
        jurisdiction_risk = current_data.get('jurisdiction_risk', 0.3)

        # Комбинируем факторы
        regulatory_risk = (
            0.4 * (1 - compliance_score) +
            0.3 * min(1, regulatory_changes / 5) +  # 5 изменений максимум
            0.3 * jurisdiction_risk
        )

        return regulatory_risk

    def _calculate_var(self,
                      historical_data: Optional[List[Dict]] = None,
                      confidence_level: float = 0.95) -> float:
        """
        Рассчитывает Value at Risk
        """
        if not historical_data:
            return 0.0

        returns = self._calculate_returns([d.get('price', 0) for d in historical_data])
        return np.percentile(returns, (1 - confidence_level) * 100)

    def _calculate_max_drawdown(self, historical_data: Optional[List[Dict]] = None) -> float:
        """
        Рассчитывает максимальную просадку
        """
        if not historical_data:
            return 0.0

        prices = [d.get('price', 0) for d in historical_data]
        peak = prices[0]
        max_drawdown = 0.0

        for price in prices[1:]:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown

    def _run_stress_tests(self,
                         current_data: Dict,
                         historical_data: Optional[List[Dict]] = None) -> Dict[str, float]:
        """
        Проводит стресс-тестирование
        """
        results = {
            'market_crash': self._simulate_market_crash(current_data),
            'liquidity_crisis': self._simulate_liquidity_crisis(current_data),
            'high_volatility': self._simulate_high_volatility(current_data),
            'regulatory_event': self._simulate_regulatory_event(current_data)
        }
        return results

    def _check_risk_indicators(self, current_data: Dict) -> Dict[str, bool]:
        """
        Проверяет индикаторы риска
        """
        return {
            'high_volatility': current_data.get('volatility', 0) > self.risk_thresholds['volatility_threshold'],
            'low_liquidity': current_data.get('liquidity', 0) < self.risk_thresholds['liquidity_min'],
            'high_concentration': current_data.get('concentration', 0) > self.risk_thresholds['concentration_max'],
            'system_issues': current_data.get('error_rate', 0) > 0.01
        }

    def _calculate_overall_risk_score(self, risk_breakdown: Dict[RiskCategory, float]) -> float:
        """
        Рассчитывает общий риск-скор
        """
        return sum(risk * self.risk_weights[category] 
                  for category, risk in risk_breakdown.items()) * 100

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Определяет уровень риска на основе скора
        """
        if risk_score < 30:
            return RiskLevel.LOW
        elif risk_score < 60:
            return RiskLevel.MEDIUM
        elif risk_score < 80:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
