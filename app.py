from flask import Flask, request, jsonify
import logging
from fraud_detector import get_detector

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fraud_detection.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Статистика роботи системи
stats = {
    'total_requests': 0,
    'fraud_detected': 0
}


@app.route('/', methods=['GET'])
def home():
    """Головна сторінка API"""
    return jsonify({
        'message': '🛡️ Fraud Detection API',
        'version': '1.0',
        'endpoints': {
            'POST /check': 'Перевірити запит на фрод',
            'GET /stats': 'Статистика роботи системи'
        }
    })


@app.route('/check', methods=['POST'])
def check_fraud():
    """Основний endpoint для перевірки запитів"""
    try:
        data = request.get_json()

        if not data or 'request' not in data:
            return jsonify({'error': 'Відсутнє поле request'}), 400

        user_request = data.get('request', '')
        threshold = data.get('threshold', 0.5)

        # Перевіряємо запит через наш детектор
        detector = get_detector()
        result = detector.predict(user_request, threshold)

        # Оновлюємо статистику
        stats['total_requests'] += 1
        if result['is_fraud']:
            stats['fraud_detected'] += 1

        # Логування результатів
        log_msg = f"IP: {request.remote_addr}, Request: {user_request}, Fraud: {result['is_fraud']}"
        if result['is_fraud']:
            logging.warning(f"🚨 FRAUD DETECTED - {log_msg}")
        else:
            logging.info(f"✅ NORMAL REQUEST - {log_msg}")

        # Повертаємо результат
        return jsonify({
            'is_fraud': result['is_fraud'],
            'fraud_probability': result['fraud_probability'],
            'risk_level': result['risk_level'],
            'recommendation': 'БЛОКУВАТИ' if result['is_fraud'] else 'ДОЗВОЛИТИ',
            'message': 'Blocked' if result['is_fraud'] else 'Allowed'
        })

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Внутрішня помилка сервера'}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Статистика роботи системи"""
    fraud_rate = (stats['fraud_detected'] / stats['total_requests']
                  if stats['total_requests'] > 0 else 0)

    return jsonify({
        'total_requests': stats['total_requests'],
        'fraud_detected': stats['fraud_detected'],
        'normal_requests': stats['total_requests'] - stats['fraud_detected'],
        'fraud_rate_percent': round(fraud_rate * 100, 2)
    })


if __name__ == '__main__':
    print("🚀 Запуск Fraud Detection API...")
    print("📡 API доступний на: http://localhost:8095")
    print("📊 Статистика: http://localhost:8095/stats")

    app.run(debug=True, host='0.0.0.0', port=8095)