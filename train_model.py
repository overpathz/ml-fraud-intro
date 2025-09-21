import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    """Завантажує дані з файлів"""

    # Читаємо нормальні запити
    with open('data/normal_requests.txt', 'r', encoding='utf-8') as f:
        normal_requests = [line.strip() for line in f if line.strip()]

    # Читаємо фродові запити
    with open('data/fraud_requests.txt', 'r', encoding='utf-8') as f:
        fraud_requests = [line.strip() for line in f if line.strip()]

    # Створюємо датасет
    data = []
    for req in normal_requests:
        data.append((req, 0))  # 0 = нормальний
    for req in fraud_requests:
        data.append((req, 1))  # 1 = фрод

    return data


def extract_features(text):
    """Витягує ознаки з тексту"""
    text = text.strip()
    text_lower = text.lower()

    # Ключові слова для різних типів атак
    sql_keywords = ['select', 'drop', 'insert', 'update', 'delete',
                    'union', 'where', 'from', 'table', 'database']

    html_js_patterns = ['script', 'iframe', 'img', 'svg', 'body',
                        'onload', 'onerror', 'alert', 'eval']

    path_patterns = ['../', './', 'etc/', 'windows/', 'system32']

    # Створюємо список ознак
    features = [
        len(text),  # довжина тексту
        text.count(' '),  # кількість пробілів
        text.count("'"),  # одинарні лапки
        text.count('"'),  # подвійні лапки
        text.count('<'),  # HTML теги початок
        text.count('>'),  # HTML теги кінець
        text.count('='),  # знаки рівності
        text.count(';'),  # крапка з комою
        text.count('-'),  # тире
        text.count('('),  # дужки
        text.count('/'),  # слеші

        # Підрахунок підозрілих паттернів
        sum([1 for word in sql_keywords if word in text_lower]),
        sum([1 for pattern in html_js_patterns if pattern in text_lower]),
        sum([1 for pattern in path_patterns if pattern in text_lower]),
    ]

    return features


def train_and_evaluate():
    """Навчає та оцінює модель"""

    print("📊 Завантаження даних...")
    data = load_data()

    # Підготовка даних
    texts = [item[0] for item in data]
    labels = [item[1] for item in data]

    print(f"Завантажено {len(texts)} записів:")
    print(f"  Нормальних: {labels.count(0)}")
    print(f"  Фродових: {labels.count(1)}")

    # Створення ознак
    print("🔧 Створення ознак...")
    features = [extract_features(text) for text in texts]
    X = np.array(features)
    y = np.array(labels)

    # Розділення на навчальну та тестову вибірки
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"📋 Train: {len(X_train)}, Test: {len(X_test)}")

    # Навчання моделі Random Forest
    print("🤖 Навчання моделі...")
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=10
    )
    model.fit(X_train, y_train)

    # Тестування моделі
    print("📈 Оцінка моделі...")
    y_pred = model.predict(X_test)

    print("\n=== РЕЗУЛЬТАТИ ===")
    print(classification_report(y_test, y_pred,
                                target_names=['Normal', 'Fraud']))

    # Створення та візуалізація матриці помилок
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Normal', 'Fraud'],
                yticklabels=['Normal', 'Fraud'])
    plt.title('Матриця помилок')
    plt.xlabel('Передбачено')
    plt.ylabel('Фактично')
    plt.savefig('confusion_matrix.png')
    print("📊 Матрицю помилок збережено: confusion_matrix.png")

    # Збереження навченої моделі
    joblib.dump(model, 'models/fraud_model.joblib')
    print("💾 Модель збережено: models/fraud_model.joblib")

    return model


if __name__ == "__main__":
    model = train_and_evaluate()