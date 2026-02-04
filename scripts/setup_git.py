#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматической настройки Git репозитория без больших файлов
"""

import os
import shutil
import subprocess
import sys

def run_command(command, shell=True):
    """Выполнить команду и вернуть результат"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"✓ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка: {command}")
        print(f"  {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("АВТОМАТИЧЕСКАЯ НАСТРОЙКА GIT РЕПОЗИТОРИЯ")
    print("=" * 60)
    
    # Получить текущую директорию
    project_dir = os.getcwd()
    print(f"\n📁 Рабочая директория: {project_dir}")
    
    # Шаг 1: Удалить .git папку
    print("\n[1/8] Удаление старой истории Git...")
    git_dir = os.path.join(project_dir, '.git')
    if os.path.exists(git_dir):
        try:
            # Изменить атрибуты файлов на Windows
            if os.name == 'nt':
                os.system('attrib -r -h -s .git\\*.* /s /d')
            shutil.rmtree(git_dir)
            print("✓ Папка .git удалена")
        except Exception as e:
            print(f"⚠️  Не удалось удалить через Python: {e}")
            print("   Пробую через системную команду...")
            # Попробуем через команду
            if os.name == 'nt':  # Windows
                result = os.system('attrib -r -h -s .git\\*.* /s /d && rd /s /q .git')
                if result == 0:
                    print("✓ Папка .git удалена через cmd")
                else:
                    print("❌ ОШИБКА: Не удалось удалить .git")
                    print("   Закройте PyCharm и все программы, использующие проект,")
                    print("   затем вручную удалите папку .git и запустите скрипт снова.")
                    sys.exit(1)
            else:  # Linux/Mac
                os.system('rm -rf .git')
    else:
        print("ℹ Папка .git не найдена")
    
    # Шаг 2: Создать .gitignore
    print("\n[2/8] Создание .gitignore...")
    gitignore_content = """# Модели Vosk
models/vosk-model-ru/
models/*.bin
models/*.mdl

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/
*.egg

# Виртуальное окружение
venv/
env/
ENV/
.venv/

# IDE
.idea/
*.iml
.vscode/
*.swp
*.swo
*~

# Базы данных
*.db
*.sqlite3
data/memory_db/
*.sql

# Логи
*.log
logs/

# Временные файлы
*.tmp
*.temp
.DS_Store
Thumbs.db

# Конфигурация (если содержит секреты)
# config.py
# .env
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✓ Файл .gitignore создан")
    
    # Шаг 3: Создать README.md
    print("\n[3/8] Создание README.md...")
    readme_content = """# Jarvis Beta

Голосовой ассистент на базе Python с использованием Vosk для распознавания речи.

## 📋 Требования

- Python 3.8+
- Микрофон для голосового ввода

## 🚀 Установка

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/jeffcheasey1337/JarvisNew.git
cd JarvisNew
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Скачайте модель Vosk

**Важно!** Модель не включена в репозиторий из-за её размера.

1. Перейдите на https://alphacephei.com/vosk/models
2. Скачайте **vosk-model-ru** (русская модель)
3. Распакуйте архив
4. Поместите папку `vosk-model-ru` в директорию `models/`:
   ```
   JarvisNew/
   ├── models/
   │   └── vosk-model-ru/
   │       ├── am/
   │       ├── graph/
   │       ├── ivector/
   │       └── ...
   └── ...
   ```

## ▶️ Запуск

```bash
python main.py
```

## 📝 Структура проекта

```
JarvisNew/
├── models/          # Модели для распознавания речи (скачать отдельно)
├── data/            # Данные и базы данных
├── main.py          # Главный файл
└── README.md
```

## 🛠 Технологии

- Python
- Vosk (распознавание речи)
- PyAudio (работа с аудио)

## 📄 Лицензия

MIT License

## 👤 Автор

jeffcheasey1337
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✓ Файл README.md создан")
    
    # Шаг 4: Инициализировать Git
    print("\n[4/8] Инициализация нового Git репозитория...")
    run_command("git init")
    
    # Шаг 5: Добавить файлы
    print("\n[5/8] Добавление файлов...")
    run_command("git add .")
    
    # Проверить статус
    print("\n📊 Проверка добавленных файлов...")
    run_command("git status")
    
    # Проверить, что большие файлы не добавлены
    print("\n🔍 Проверка размеров файлов...")
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    large_files = []
    for filename in result.stdout.split('\n'):
        if filename.strip():
            filepath = os.path.join(project_dir, filename.strip())
            if os.path.exists(filepath) and os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                if size > 50_000_000:  # 50 MB
                    large_files.append((filename.strip(), size / 1_000_000))
    
    if large_files:
        print("\n⚠️  ВНИМАНИЕ! Обнаружены большие файлы:")
        for filename, size in large_files:
            print(f"   {filename}: {size:.2f} MB")
        print("\n❌ Остановка. Добавьте эти файлы в .gitignore!")
        print("\nДобавьте в .gitignore:")
        for filename, _ in large_files:
            print(f"   {filename}")
        sys.exit(1)
    else:
        print("✓ Больших файлов не обнаружено")
    
    # Шаг 6: Создать коммит
    print("\n[6/8] Создание первого коммита...")
    run_command('git commit -m "Initial commit: Clean repository without large model files"')
    
    # Шаг 7: Добавить remote
    print("\n[7/8] Добавление GitHub remote...")
    run_command("git remote add origin https://github.com/jeffcheasey1337/JarvisNew.git")
    
    # Шаг 8: Push
    print("\n[8/8] Отправка на GitHub...")
    print("\n⚠️  Сейчас будет выполнен ПРИНУДИТЕЛЬНЫЙ push (git push -f)")
    print("   Это перезапишет историю на GitHub!")
    
    response = input("\n❓ Продолжить? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y', 'да', 'д']:
        success = run_command("git push -f origin master")
        
        if success:
            print("\n" + "=" * 60)
            print("✅ УСПЕШНО! Репозиторий настроен и отправлен на GitHub!")
            print("=" * 60)
            print("\n📝 Следующие шаги:")
            print("   1. Проверьте репозиторий: https://github.com/jeffcheasey1337/JarvisNew")
            print("   2. Скачайте модель Vosk отдельно (см. README.md)")
            print("   3. Поместите модель в папку models/vosk-model-ru/")
        else:
            print("\n❌ Ошибка при push. Проверьте:")
            print("   - Подключение к интернету")
            print("   - Права доступа к репозиторию")
            print("   - Аутентификацию GitHub")
    else:
        print("\n⏸️  Push отменён. Вы можете выполнить его вручную:")
        print("   git push -f origin master")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
