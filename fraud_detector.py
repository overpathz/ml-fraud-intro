import numpy as np
import joblib
from datetime import datetime


class FraudDetector:
    """Детектор фродових запитів"""

    def __init__(self, model_path='models/fraud_model.joblib'):
        """Ініціалізація детектора"""
        try:
            self.model = joblib.load(model_path)
            print(f"✅ Модель завантажено з {model_path}")
        except FileNotFoundError:
            print(f"❌ Модель не знайдено: {model_path}")
            print("Спочатку навчіть модель: python train_model.py")
            raise

    def extract_features(self, text):
        """Витягує ознаки з тексту (повторює логіку з train_model.py)"""
        text = text.strip()
        text_lower = text.lower()

        sql_keywords = ['select', 'drop', 'insert', 'update', 'delete',
                        'union', 'where', 'from', 'table', 'database']
        html_js_patterns = ['script', 'iframe', 'img', 'svg', 'body',
                            'onload', 'onerror', 'alert', 'eval']
        path_patterns = ['../', './', 'etc/', 'windows/', 'system32']

        features = [
            len(text), text.count(' '), text.count("'"), text.count('"'),
            text.count('<'), text.count('>'), text.count('='),
            text.count(';'), text.count('-'), text.count('('), text.count('/'),
            sum([1 for word in sql_keywords if word in text_lower]),
            sum([1 for pattern in html_js_patterns if pattern in text_lower]),
            sum([1 for pattern in path_patterns if pattern in text_lower]),
        ]

        return features

    def predict(self, request_text, threshold=0.5):
        """Перевіряє запит на фрод"""
        features = np.array([self.extract_features(request_text)])

        # Отримуємо ймовірності
        probabilities = self.model.predict_proba(features)[0]
        fraud_probability = probabilities[1]

        # Визначення рівня ризику
        if fraud_probability < 0.3:
            risk_level = "НИЗЬКИЙ"
            emoji = "🟢"
        elif fraud_probability < 0.7:
            risk_level = "СЕРЕДНІЙ"
            emoji = "🟡"
        else:
            risk_level = "ВИСОКИЙ"
            emoji = "🔴"

        result = {
            'request': request_text,
            'is_fraud': fraud_probability > threshold,
            'fraud_probability': round(fraud_probability, 3),
            'normal_probability': round(probabilities[0], 3),
            'risk_level': risk_level,
            'emoji': emoji,
            'timestamp': datetime.now().isoformat()
        }

        return result

    def check_request(self, request_text, threshold=0.5, verbose=True):
        """Зручна функція для перевірки з виводом результатів"""
        result = self.predict(request_text, threshold)

        if verbose:
            print(f"{result['emoji']} Запит: '{request_text}'")
            print(f"📊 Ймовірність фроду: {result['fraud_probability']:.1%}")
            print(f"⚠️ Рівень ризику: {result['risk_level']}")
            print(f"✅ Результат: {'ФРОД' if result['is_fraud'] else 'БЕЗПЕЧНО'}")

        return result


# Глобальний детектор для використання в API
detector = None


def get_detector():
    """Повертає глобальний екземпляр детектора"""
    global detector
    if detector is None:
        detector = FraudDetector()
    return detector