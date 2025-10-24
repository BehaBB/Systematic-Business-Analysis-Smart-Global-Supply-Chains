# 🔮 Предиктивная аналитика

## Модели прогнозирования

### 1. Прогноз времени доставки

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd

class DeliveryTimePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            random_state=42
        )
        self.features = [
            'distance_km', 'border_crossings', 'product_type_encoded',
            'season', 'weather_impact', 'customs_complexity',
            'vehicle_type', 'driver_experience'
        ]
    
    def prepare_features(self, df):
        """Подготовка признаков для модели"""
        features_df = pd.DataFrame()
        
        # Базовые признаки
        features_df['distance_km'] = df['distance_km']
        features_df['border_crossings'] = df['border_crossings']
        features_df['product_type_encoded'] = self.encode_product_type(df['product_type'])
        features_df['season'] = self.get_season(df['shipment_date'])
        features_df['weather_impact'] = self.calculate_weather_impact(df['route'])
        features_df['customs_complexity'] = df['customs_complexity']
        features_df['vehicle_type'] = df['vehicle_type']
        features_df['driver_experience'] = df['driver_experience_months']
        
        return features_df
    
    def train(self, historical_data):
        """Обучение модели на исторических данных"""
        X = self.prepare_features(historical_data)
        y = historical_data['actual_delivery_days']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Оценка модели
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"Train R²: {train_score:.3f}")
        print(f"Test R²: {test_score:.3f}")
        
        return self.model
    
    def predict(self, shipment_data):
        """Прогноз времени доставки для нового груза"""
        features = self.prepare_features(shipment_data)
        prediction = self.model.predict(features)
        
        # Доверительный интервал
        confidence_interval = self.calculate_confidence(prediction)
        
        return {
            'predicted_days': round(prediction[0], 1),
            'confidence_interval': confidence_interval,
            'features_importance': self.get_feature_importance()
        }
2. Прогнозирование спроса
python
from prophet import Prophet
import numpy as np

class DemandForecaster:
    def __init__(self):
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
    
    def prepare_time_series(self, sales_data):
        """Подготовка временных рядов для Prophet"""
        df = sales_data[['date', 'quantity']].copy()
        df.columns = ['ds', 'y']
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Добавление праздников
        russian_holidays = self.get_russian_holidays()
        chinese_holidays = self.get_chinese_holidays()
        
        self.model.add_country_holidays(country_name='RU')
        self.model.add_country_holidays(country_name='CN')
        
        return df
    
    def train(self, historical_sales):
        """Обучение модели прогнозирования спроса"""
        df = self.prepare_time_series(historical_sales)
        self.model.fit(df)
        
        return self.model
    
    def forecast(self, periods=30):
        """Прогноз спроса на указанный период"""
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
3. Анализ рисков
python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report

class RiskAnalyzer:
    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5
        )
    
    def prepare_risk_features(self, shipment_data):
        """Признаки для анализа рисков"""
        risk_features = pd.DataFrame()
        
        risk_features['delivery_time_variance'] = shipment_data['historical_delivery_std']
        risk_features['customs_delay_probability'] = shipment_data['customs_delay_rate']
        risk_features['weather_risk'] = shipment_data['weather_risk_score']
        risk_features['route_complexity'] = shipment_data['route_complexity_score']
        risk_features['product_sensitivity'] = shipment_data['product_sensitivity']
        risk_features['seasonal_risk'] = shipment_data['seasonal_risk_factor']
        
        return risk_features
    
    def train(self, historical_data):
        """Обучение модели классификации рисков"""
        X = self.prepare_risk_features(historical_data)
        y = historical_data['had_incident']  # 1 - был инцидент, 0 - не было
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        self.model.fit(X_train, y_train)
        
        # Оценка модели
        y_pred = self.model.predict(X_test)
        print(classification_report(y_test, y_pred))
        
        return self.model
    
    def assess_risk(self, shipment_data):
        """Оценка риска для конкретного груза"""
        features = self.prepare_risk_features(shipment_data)
        risk_probability = self.model.predict_proba(features)[0][1]
        
        risk_level = 'low'
        if risk_probability > 0.7:
            risk_level = 'high'
        elif risk_probability > 0.3:
            risk_level = 'medium'
        
        return {
            'risk_probability': round(risk_probability, 3),
            'risk_level': risk_level,
            'mitigation_recommendations': self.get_mitigation_strategies(risk_level)
        }
Метрики качества моделей
Точность прогнозов
python
model_metrics = {
    'delivery_time_predictor': {
        'r_squared': 0.87,
        'mae_days': 0.4,
        'rmse_days': 0.6,
        'coverage_95pct': 0.92
    },
    'demand_forecaster': {
        'mape': 0.15,
        'mase': 0.8,
        'r_squared': 0.82
    },
    'risk_analyzer': {
        'accuracy': 0.89,
        'precision': 0.85,
        'recall': 0.82,
        'f1_score': 0.83
    }
}
Примеры прогнозов
Прогноз времени доставки
python
sample_prediction = {
    'route': 'Harbin → Ulan-Ude',
    'predicted_days': 4.2,
    'confidence_interval': [3.8, 4.6],
    'key_factors': [
        {'factor': 'distance', 'impact': 0.35},
        {'factor': 'customs', 'impact': 0.25},
        {'factor': 'weather', 'impact': 0.20}
    ]
}
Прогноз спроса на электронику
python
demand_forecast = {
    'product_category': 'electronics',
    'next_30_days': {
        'predicted_volume': 1450,
        'confidence_lower': 1320,
        'confidence_upper': 1580,
        'trend': 'increasing',
        'seasonal_peak': '2024-02-15'
    }
}
Интеграция с бизнес-процессами
Автоматические рекомендации
python
def generate_recommendations(shipment_data):
    """Генерация рекомендаций на основе прогнозов"""
    delivery_prediction = delivery_predictor.predict(shipment_data)
    risk_assessment = risk_analyzer.assess_risk(shipment_data)
    
    recommendations = []
    
    if risk_assessment['risk_level'] == 'high':
        recommendations.append({
            'type': 'risk_mitigation',
            'priority': 'high',
            'action': 'Увеличить страховое покрытие',
            'reason': 'Высокая вероятность инцидентов'
        })
    
    if delivery_prediction['predicted_days'] > 5:
        recommendations.append({
            'type': 'logistics_optimization', 
            'priority': 'medium',
            'action': 'Рассмотреть альтернативный маршрут',
            'reason': 'Прогнозируемое время доставки превышает целевое'
        })
    
    return recommendations
Мониторинг точности моделей
python
class ModelMonitor:
    def __init__(self):
        self.performance_history = []
    
    def track_prediction_accuracy(self, prediction, actual):
        """Отслеживание точности прогнозов"""
        error = abs(prediction - actual)
        self.performance_history.append({
            'timestamp': pd.Timestamp.now(),
            'prediction': prediction,
            'actual': actual,
            'error': error
        })
        
        # Автоматическое переобучение при ухудшении точности
        if self.detected_performance_degradation():
            self.trigger_retraining()
Визуализация прогнозов
Дашборд предиктивной аналитики
text
┌─────────────────────────────────────────────────────────┐
│ Predictive Analytics Dashboard             [🔄 Update] │
├─────────────────────────────────────────────────────────┤
│ 📈 Delivery Time Forecast                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Actual: 4.1d ────┤                                 │ │
│ │ Predicted: 4.2d ─┼─────┤                           │ │
│ │ Confidence: [3.8-4.6]d                              │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 📊 Demand Forecast - Electronics                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 1600 ┤         █████████▊                           │ │
│ │ 1500 ┤       ██████████████▋                        │ │
│ │ 1400 ┤     ███████████████████▌                     │ │
│ │ 1300 ┤   ███████████████████████▍                   │ │
│ │ 1200 ┤ ███████████████████████████▊                 │ │
│ │     └──────────────────────────────────────────────── │
│ │      Jan   Feb   Mar   Apr   May   Jun               │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ ⚠️ Risk Assessment                                      │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ High Risk: 12% of shipments                         │ │
│ │ Medium Risk: 23% of shipments                       │ │
│ │ Low Risk: 65% of shipments                          │ │
│ │                                                     │ │
│ │ Top Risk Factors:                                   │ │
│ │ • Customs delays (35%)                              │ │
│ │ • Weather conditions (28%)                          │ │
│ │ • Route complexity (22%)                            │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
text

## ⚠️ **Создаем analytics/risk-analysis.md:**

```markdown
# ⚠️ Анализ рисков

## Категории рисков

### 1. Операционные риски
```python
operational_risks = {
    'customs_delays': {
        'probability': 0.15,
        'impact': 'high',
        'mitigation': 'Предварительная подготовка документов',
        'monitoring_metric': 'customs_clearance_time'
    },
    'weather_disruptions': {
        'probability': 0.08, 
        'impact': 'medium',
        'mitigation': 'Альтернативные маршруты',
        'monitoring_metric': 'weather_alert_count'
    },
    'vehicle_breakdowns': {
        'probability': 0.05,
        'impact': 'high',
        'mitigation': 'Регулярное техобслуживание',
        'monitoring_metric': 'breakdown_incidents'
    }
}
2. Финансовые риски
python
financial_risks = {
    'currency_fluctuation': {
        'probability': 0.25,
        'impact': 'medium',
        'mitigation': 'Хеджирование валютных рисков',
        'exposure_usd': 500000
    },
    'customs_duty_changes': {
        'probability': 0.10,
        'impact': 'high', 
        'mitigation': 'Мониторинг законодательства',
        'exposure_usd': 250000
    },
    'fuel_price_volatility': {
        'probability': 0.30,
        'impact': 'medium',
        'mitigation': 'Долгосрочные контракты',
        'exposure_usd': 150000
    }
}
3. Риски качества
python
quality_risks = {
    'temperature_violations': {
        'probability': 0.03,
        'impact': 'high',
        'mitigation': 'Двойные датчики температуры',
        'sla_requirement': '99.5% compliance'
    },
    'damage_during_transit': {
        'probability': 0.02,
        'impact': 'high',
        'mitigation': 'Специальная упаковка',
        'insurance_coverage': 'full_value'
    },
    'documentation_errors': {
        'probability': 0.12,
        'impact': 'medium',
        'mitigation': 'AI проверка документов',
        'auto_verification_rate': '85%'
    }
}
Матрица рисков
Оценка вероятности и воздействия
text
       ▲
 Impact│
       │
  High │ customs_delays     vehicle_breakdowns
       │ temperature_violations
       │
Medium │ weather_disruptions  currency_fluctuation
       │ documentation_errors fuel_price_volatility
       │
  Low  │ minor_paperwork_issues
       │
       └───────────────────────────►
        Low     Medium    High   Probability
Метрики мониторинга рисков
Ключевые индикаторы рисков
python
risk_metrics = {
    'customs_risk_index': {
        'formula': '(delayed_shipments / total_shipments) * average_delay_hours',
        'threshold': 2.0,
        'current_value': 1.8,
        'trend': 'decreasing'
    },
    'temperature_risk_score': {
        'formula': 'temperature_violations * severity_weight',
        'threshold': 5.0,
        'current_value': 2.3, 
        'trend': 'stable'
    },
    'financial_risk_exposure': {
        'formula': 'sum(currency_exposure + duty_exposure + fuel_exposure)',
        'threshold': 1000000,
        'current_value': 900000,
        'trend': 'increasing'
    }
}
Процесс управления рисками
1. Идентификация рисков
python
def identify_risks(shipment_data):
    """Автоматическая идентификация рисков для груза"""
    risks = []
    
    # Анализ маршрута
    if shipment_data['route_complexity'] > 0.7:
        risks.append('complex_route_risk')
    
    # Анализ товара
    if shipment_data['product_sensitivity'] == 'high':
        risks.append('sensitive_goods_risk')
    
    # Сезонный анализ
    if shipment_data['season'] == 'winter':
        risks.append('wather_risk')
    
    return risks
2. Оценка рисков
python
def assess_risk_level(risk_type, shipment_context):
    """Оценка уровня риска"""
    base_probability = risk_database[risk_type]['probability']
    context_multiplier = calculate_context_multiplier(shipment_context)
    
    final_probability = base_probability * context_multiplier
    impact = risk_database[risk_type]['impact']
    
    return {
        'risk_type': risk_type,
        'probability': final_probability,
        'impact': impact,
        'risk_score': final_probability * impact_weight[impact]
    }
3. Планирование мер
python
def generate_mitigation_plan(identified_risks):
    """Генерация плана mitigation мер"""
    mitigation_plan = []
    
    for risk in identified_risks:
        if risk['risk_score'] > 0.7:
            mitigation_plan.append({
                'risk': risk['risk_type'],
                'action': risk_database[risk['risk_type']]['mitigation'],
                'priority': 'high',
                'responsible': 'logistics_manager'
            })
        elif risk['risk_score'] > 0.3:
            mitigation_plan.append({
                'risk': risk['risk_type'],
                'action': risk_database[risk['risk_type']]['mitigation'],
                'priority': 'medium', 
                'responsible': 'operations_team'
            })
    
    return mitigation_plan
Отчетность по рискам
Еженедельный отчет о рисках
python
weekly_risk_report = {
    'period': '2024-01-15 to 2024-01-21',
    'high_risk_incidents': 3,
    'medium_risk_incidents': 12,
    'risk_exposure_change': '+5%',
    'top_risks': [
        {'risk': 'customs_delays', 'incidents': 8, 'avg_delay_hours': 6.2},
        {'risk': 'weather_disruptions', 'incidents': 3, 'avg_delay_hours': 4.5},
        {'risk': 'documentation_errors', 'incidents': 5, 'resolution_hours': 2.1}
    ],
    'mitigation_effectiveness': {
        'customs_pre_check': 0.85,
        'alternative_routes': 0.92,
        'ai_document_verification': 0.78
    }
}
Дашборд мониторинга рисков
text
┌─────────────────────────────────────────────────────────┐
│ Risk Monitoring Dashboard                  [📅 Weekly] │
├─────────────────────────────────────────────────────────┤
│ 📊 Risk Overview                                        │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│ │      3      │ │     12      │ │    +5%      │         │
│ │ High Risk   │ │ Medium Risk │ │ Exposure    │         │
│ │ Incidents   │ │ Incidents   │ │ Change      │         │
│ └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                         │
│ ⚠️ Top Risks This Week                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Risk           │ Incidents │ Avg Impact │ Trend     │ │
│ ├────────────────┼───────────┼────────────┼───────────┤ │
│ │ Customs Delays │     8     │   6.2h     │ 🔴 Up     │ │
│ │ Weather        │     3     │   4.5h     │ 🟡 Stable │ │
│ │ Documentation  │     5     │   2.1h     │ 🟢 Down   │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 🛡️ Mitigation Effectiveness                            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Measure                  │ Effectiveness │ Target   │ │
│ ├──────────────────────────┼───────────────┼──────────┤ │
│ │ Customs Pre-Check        │     85%       │   90%    │ │
│ │ Alternative Routes       │     92%       │   95%    │ │
│ │ AI Document Verification │     78%       │   85%    │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
Процесс эскалации
Уровни эскалации
python
escalation_levels = {
    'level_1': {
        'condition': 'risk_score > 0.7',
        'action': 'Уведомление менеджера',
        'timeframe': 'immediately'
    },
    'level_2': {
        'condition': 'risk_score > 0.8 OR multiple_high_risks',
        'action': 'Эскалация директору',
        'timeframe': 'within_1_hour'
    },
    'level_3': {
        'condition': 'risk_score > 0.9 OR critical_incident',
        'action': 'Создание crisis team',
        'timeframe': 'within_15_minutes'
    }
}
Автоматические уведомления
python
def trigger_risk_alert(risk_assessment):
    """Триггер уведомлений о рисках"""
    if risk_assessment['risk_score'] > 0.7:
        send_alert(
            recipient='logistics_managers',
            title='High Risk Alert',
            message=f"High risk detected for shipment {risk_assessment['shipment_id']}",
            priority='high'
        )
    
    if risk_assessment['risk_score'] > 0.9:
        send_alert(
            recipient='directors',
            title='Critical Risk Alert', 
            message='Immediate attention required',
            priority='critical'
        )

