# Установка JARVIS

## Требования

- Python 3.8+
- Микрофон
- 4GB RAM

## Шаги установки

### 1. Клонирование
```bash
git clone https://github.com/jeffcheasey1337/JarvisNew.git
cd JarvisNew
```

### 2. Виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Зависимости
```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Модели
```bash
python scripts/download_models.py
```

### 5. Запуск
```bash
jarvis
```
