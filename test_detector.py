from fraud_detector import FraudDetector
import json


def test_basic_functionality():
    """Основне тестування детектора"""

    print("🧪 Тестування Fraud Detector")
    print("=" * 50)

    try:
        detector = FraudDetector()
    except FileNotFoundError:
        print("❌ Модель не знайдена. Спочатку запустіть: python train_model.py")
        return

    # Набір тестових запитів
    test_requests = [
        # Нормальні запити
        "показати мої замовлення",
        "пошук по категорії електроніка",
        "змінити персональні дані",
        "історія покупок за місяць",

        # Підозрілі, але можливо легітимні
        "пошук по слову 'select'",
        "товар з назвою <strong>важливий</strong>",

        # Явно фродові запити
        "' OR '1'='1",
        "<script>alert('hack')</script>",
        "admin' UNION SELECT password FROM users--",
        "../../../etc/passwd",
        "'; DROP TABLE products; --"
    ]

    print("Результати тестування:\n")

    for i, request_text in enumerate(test_requests, 1):
        print(f"🔍 Тест {i}:")
        result = detector.check_request(request_text)
        print("-" * 40)


def create_test_file():
    """Створює файл з тестовими випадками"""
    test_cases = [
        {"request": "показати мої замовлення", "expected_fraud": False},
        {"request": "' OR 1=1 --", "expected_fraud": True},
        {"request": "пошук товарів", "expected_fraud": False},
        {"request": "<script>alert('xss')</script>", "expected_fraud": True},
        {"request": "змінити пароль", "expected_fraud": False},
        {"request": "../admin/config.php", "expected_fraud": True},
        {"request": "контактна інформація", "expected_fraud": False},
    ]

    with open('data/test_requests.json', 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)

    print("📁 Створено файл data/test_requests.json")


def test_from_file():
    """Тестування з файлу тестових випадків"""
    try:
        with open('data/test_requests.json', 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print("Створюємо тестовий файл...")
        create_test_file()
        return test_from_file()

    print(f"\n📁 Тестування {len(test_cases)} випадків з файлу")
    print("=" * 50)

    detector = FraudDetector()
    correct = 0

    for case in test_cases:
        request_text = case['request']
        expected = case['expected_fraud']

        result = detector.predict(request_text)
        actual = result['is_fraud']

        if actual == expected:
            correct += 1
            status = "✅ ПРАВИЛЬНО"
        else:
            status = "❌ ПОМИЛКА"

        print(f"{status}: '{request_text}'")
        print(f"   Очікувалось: {expected}, Отримано: {actual}")
        print(f"   Ймовірність фроду: {result['fraud_probability']:.1%}")
        print()

    accuracy = correct / len(test_cases)
    print(f"📊 Загальна точність: {accuracy:.1%} ({correct}/{len(test_cases)})")


if __name__ == "__main__":
    test_basic_functionality()
    test_from_file()