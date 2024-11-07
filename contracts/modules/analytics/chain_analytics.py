from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from enum import Enum

class ChainStatus(Enum):
    OPTIMAL = "OPTIMAL"
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class BottleneckType(Enum):
    CAPACITY = "CAPACITY"
    DELAY = "DELAY"
    QUALITY = "QUALITY"
    COST = "COST"

@dataclass
class ChainMetrics:
    efficiency_score: float
    throughput: float
    cycle_time: float
    bottlenecks: List[Dict]
    quality_metrics: Dict[str, float]
    cost_metrics: Dict[str, float]
    sustainability_score: float

class ChainAnalytics:
    """
    Анализатор цепочки поставок
    """
    def __init__(self):
        self.chain_history: Dict[str, List[Dict]] = {}
        self.performance_thresholds = {
            'efficiency_min': 0.7,    # Минимальная эффективность
            'quality_min': 0.8,       # Минимальное качество
            'delay_max': 48,          # Максимальная задержка (часы)
            'cost_variance_max': 0.15 # Максимальное отклонение затрат
        }

    def analyze_chain(self,
                     chain_id: str,
                     current_data: Dict,
                     historical_data: Optional[List[Dict]] = None) -> ChainMetrics:
        """
        Проводит комплексный анализ цепочки поставок
        """
        # Расчет основных метрик
        efficiency = self._calculate_efficiency(current_data)
        throughput = self._calculate_throughput(current_data)
        cycle_time = self._calculate_cycle_time(current_data)
        
        # Анализ узких мест
        bottlenecks = self._identify_bottlenecks(current_data)
        
        # Анализ качества и затрат
        quality_metrics = self._analyze_quality(current_data)
        cost_metrics = self._analyze_costs(current_data, historical_data)
        
        # Оценка устойчивости
        sustainability = self._calculate_sustainability(current_data)
        
        metrics = ChainMetrics(
            efficiency_score=efficiency,
            throughput=throughput,
            cycle_time=cycle_time,
            bottlenecks=bottlenecks,
            quality_metrics=quality_metrics,
            cost_metrics=cost_metrics,
            sustainability_score=sustainability
        )
        
        # Сохраняем данные в историю
        self._store_chain_data(chain_id, metrics)
        
        return metrics

    def _calculate_efficiency(self, data: Dict) -> float:
        """
        Рассчитывает общую эффективность цепочки
        """
        # Анализируем различные факторы эффективности
        time_efficiency = self._calculate_time_efficiency(data)
        resource_efficiency = self._calculate_resource_efficiency(data)
        cost_efficiency = self._calculate_cost_efficiency(data)
        
        # Взвешенная оценка
        return (
            0.4 * time_efficiency +
            0.3 * resource_efficiency +
            0.3 * cost_efficiency
        )

    def _calculate_throughput(self, data: Dict) -> float:
        """
        Рассчитывает пропускную способность цепочки
        """
        total_volume = sum(node.get('volume', 0) for node in data.get('nodes', []))
        time_period = data.get('time_period', 24)  # в часах
        
        return total_volume / time_period if time_period > 0 else 0

    def _calculate_cycle_time(self, data: Dict) -> float:
        """
        Рассчитывает время полного цикла
        """
        nodes = data.get('nodes', [])
        if not nodes:
            return 0
            
        total_time = sum(node.get('processing_time', 0) for node in nodes)
        return total_time

    def _identify_bottlenecks(self, data: Dict) -> List[Dict]:
        """
        Определяет узкие места в цепочке
        """
        bottlenecks = []
        nodes = data.get('nodes', [])
        
        for node in nodes:
            bottleneck_types = []
            
            # Проверка пропускной способности
            if node.get('utilization', 0) > 0.9:  # 90% загрузка
                bottleneck_types.append(BottleneckType.CAPACITY)
                
            # Проверка задержек
            if node.get('delay', 0) > self.performance_thresholds['delay_max']:
                bottleneck_types.append(BottleneckType.DELAY)
                
            # Проверка качества
            if node.get('quality_score', 1) < self.performance_thresholds['quality_min']:
                bottleneck_types.append(BottleneckType.QUALITY)
                
            # Проверка затрат
            if node.get('cost_variance', 0) > self.performance_thresholds['cost_variance_max']:
                bottleneck_types.append(BottleneckType.COST)
                
            if bottleneck_types:
                bottlenecks.append({
                    'node_id': node.get('id'),
                    'node_type': node.get('type'),
                    'bottleneck_types': [bt.value for bt in bottleneck_types],
                    'severity': len(bottleneck_types) / 4  # 0.25 - 1.0
                })
                
        return sorted(bottlenecks, key=lambda x: x['severity'], reverse=True)

    def _analyze_quality(self, data: Dict) -> Dict[str, float]:
        """
        Анализирует метрики качества
        """
        nodes = data.get('nodes', [])
        if not nodes:
            return {}
            
        quality_metrics = {
            'average_quality': np.mean([node.get('quality_score', 1) for node in nodes]),
            'min_quality': min([node.get('quality_score', 1) for node in nodes]),
            'defect_rate': np.mean([node.get('defect_rate', 0) for node in nodes]),
            'compliance_rate': np.mean([node.get('compliance_rate', 1) for node in nodes])
        }
        
        return quality_metrics

    def _analyze_costs(self,
                      current_data: Dict,
                      historical_data: Optional[List[Dict]] = None) -> Dict[str, float]:
        """
        Анализирует структуру затрат
        """
        nodes = current_data.get('nodes', [])
        if not nodes:
            return {}
            
        # Текущие затраты
        total_cost = sum(node.get('cost', 0) for node in nodes)
        operating_costs = sum(node.get('operating_cost', 0) for node in nodes)
        logistics_costs = sum(node.get('logistics_cost', 0) for node in nodes)
        
        cost_metrics = {
            'total_cost': total_cost,
            'operating_cost_ratio': operating_costs / total_cost if total_cost > 0 else 0,
            'logistics_cost_ratio': logistics_costs / total_cost if total_cost > 0 else 0,
        }
        
        # Анализ тренда, если есть исторические данные
        if historical_data:
            historical_costs = [
                sum(node.get('cost', 0) for node in period.get('nodes', []))
                for period in historical_data
            ]
            cost_metrics['cost_trend'] = (
                (total_cost - historical_costs[-1]) / historical_costs[-1]
                if historical_costs else 0
            )
            
        return cost_metrics

    def _calculate_sustainability(self, data: Dict) -> float:
        """
        Рассчитывает показатель устойчивости цепочки
        """
        nodes = data.get('nodes', [])
        if not nodes:
            return 0
            
        # Факторы устойчивости
        environmental_scores = [node.get('environmental_score', 0.5) for node in nodes]
        social_scores = [node.get('social_score', 0.5) for node in nodes]
        resilience_scores = [node.get('resilience_score', 0.5) for node in nodes]
        
        return np.mean([
            np.mean(environmental_scores),
            np.mean(social_scores),
            np.mean(resilience_scores)
        ])

    def _store_chain_data(self, chain_id: str, metrics: ChainMetrics):
        """
        Сохраняет данные анализа в историю
        """
        if chain_id not in self.chain_history:
            self.chain_history[chain_id] = []
            
        self.chain_history[chain_id].append({
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'efficiency': metrics.efficiency_score,
                'throughput': metrics.throughput,
                'cycle_time': metrics.cycle_time,
                'bottlenecks': metrics.bottlenecks,
                'quality': metrics.quality_metrics,
                'costs': metrics.cost_metrics,
                'sustainability': metrics.sustainability_score
            }
        })

    def get_chain_analysis_report(self,
                                chain_id: str,
                                period_days: int = 30) -> Dict:
        """
        Генерирует отчет по анализу цепочки поставок
        """
        if chain_id not in self.chain_history:
            return {}
            
        start_date = datetime.now() - timedelta(days=period_days)
        
        # Фильтруем данные за период
        period_data = [
            entry for entry in self.chain_history[chain_id]
            if datetime.fromisoformat(entry['timestamp']) >= start_date
        ]
        
        if not period_data:
            return {}
            
        return {
            'chain_id': chain_id,
            'period': {
                'start': start_date.isoformat(),
                'end': datetime.now().isoformat()
            },
            'performance_summary': self._calculate_period_performance(period_data),
            'bottleneck_analysis': self._analyze_period_bottlenecks(period_data),
            'quality_trends': self._analyze_quality_trends(period_data),
            'cost_analysis': self._analyze_cost_trends(period_data),
            'recommendations': self._generate_chain_recommendations(period_data)
        }
