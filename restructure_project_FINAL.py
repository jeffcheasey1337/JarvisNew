# -*- coding: utf-8 -*-
"""
🏗️ JARVIS PROJECT RESTRUCTURING SCRIPT - ФИНАЛЬНАЯ ВЕРСИЯ
Полная реорганизация проекта в идеальную структуру

ИСПРАВЛЕНИЯ v2:
- Проверка на копирование файла в себя
- Пропуск файлов, которые уже на месте
"""

import os
import shutil
import sys
from pathlib import Path
import re

# Цвета для консоли
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_step(step_num, total, text):
    print(f"{Colors.BLUE}[{step_num}/{total}]{Colors.ENDC} {text}")

def print_success(text):
    print(f"  {Colors.GREEN}✓{Colors.ENDC} {text}")

def print_warning(text):
    print(f"  {Colors.YELLOW}⚠{Colors.ENDC} {text}")

def print_error(text):
    print(f"  {Colors.RED}✗{Colors.ENDC} {text}")

def print_info(text):
    print(f"  {Colors.BLUE}ℹ{Colors.ENDC} {text}")

class JarvisRestructure:
    """Класс для реструктуризации проекта JARVIS"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.backup_dir = self.root / "backup_before_restructure"
        
        # Маппинг старых файлов на новые
        self.file_mapping = {
            # Core files
            'core/speech_recognition.py': 'jarvis/core/speech/recognition.py',
            'core/speech_synthesis.py': 'jarvis/core/speech/synthesis.py',
            'core/nlp_processor.py': 'jarvis/core/nlp/processor.py',
            'core/memory_system.py': 'jarvis/core/memory/system.py',
            'core/learning_system.py': 'jarvis/core/learning/base.py',
            'core/autonomous_learning.py': 'jarvis/core/learning/autonomous.py',
            'core/continuous_learning.py': 'jarvis/core/learning/continuous.py',
            
            # Modules
            'modules/task_manager.py': 'jarvis/modules/tasks.py',
            'modules/calendar_manager.py': 'jarvis/modules/calendar.py',
            'modules/file_manager.py': 'jarvis/modules/files.py',
            'modules/system_control.py': 'jarvis/modules/system.py',
            'modules/web_search.py': 'jarvis/modules/search.py',
            
            # GUI
            'jarvis_gui_extended.py': 'jarvis/gui/main_window.py',
            
            # Main
            'main.py': 'jarvis/assistant.py',
            
            # Docs (только те, что нужно переместить)
            'ARCHITECTURE.md': 'docs/ARCHITECTURE.md',
            'QUICKSTART.md': 'docs/QUICKSTART.md',
            # README.md остаётся на месте - не копируем!
        }
        
        # Импорты для обновления
        self.import_replacements = {
            'from core.speech_recognition import': 'from jarvis.core.speech.recognition import',
            'from core.speech_synthesis import': 'from jarvis.core.speech.synthesis import',
            'from core.nlp_processor import': 'from jarvis.core.nlp.processor import',
            'from core.memory_system import': 'from jarvis.core.memory.system import',
            'from core.learning_system import': 'from jarvis.core.learning.base import',
            'from core.autonomous_learning import': 'from jarvis.core.learning.autonomous import',
            'from core.continuous_learning import': 'from jarvis.core.learning.continuous import',
            'from modules.task_manager import': 'from jarvis.modules.tasks import',
            'from modules.calendar_manager import': 'from jarvis.modules.calendar import',
            'from modules.file_manager import': 'from jarvis.modules.files import',
            'from modules.system_control import': 'from jarvis.modules.system import',
            'from modules.web_search import': 'from jarvis.modules.search import',
            'from jarvis_gui_extended import': 'from jarvis.gui.main_window import',
        }
    
    def create_backup(self):
        """Создание резервной копии"""
        print_step(1, 10, "Создание резервной копии...")
        
        if self.backup_dir.exists():
            print_warning(f"Резервная копия уже существует: {self.backup_dir}")
            response = input("  Перезаписать? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print_error("Отменено пользователем")
                return False
            shutil.rmtree(self.backup_dir)
        
        # Копируем важные папки
        important_dirs = ['core', 'modules', 'config', 'data']
        important_files = ['main.py', 'jarvis_gui_extended.py', 'requirements.txt', 'README.md']
        
        self.backup_dir.mkdir()
        
        for dir_name in important_dirs:
            src = self.root / dir_name
            if src.exists():
                shutil.copytree(src, self.backup_dir / dir_name)
                print_success(f"Скопирована папка: {dir_name}")
        
        for file_name in important_files:
            src = self.root / file_name
            if src.exists():
                shutil.copy2(src, self.backup_dir / file_name)
                print_success(f"Скопирован файл: {file_name}")
        
        print_success("Резервная копия создана!")
        return True
    
    def create_directory_structure(self):
        """Создание новой структуры папок"""
        print_step(2, 10, "Создание структуры папок...")
        
        # Список всех нужных директорий
        directories = [
            'docs',
            'config',
            'jarvis',
            'jarvis/core',
            'jarvis/core/speech',
            'jarvis/core/nlp',
            'jarvis/core/memory',
            'jarvis/core/learning',
            'jarvis/modules',
            'jarvis/gui',
            'jarvis/gui/widgets',
            'jarvis/utils',
            'data',
            'data/memory_db',
            'data/learning',
            'data/user',
            'models',
            'logs',
            'tests',
            'scripts',
        ]
        
        for dir_path in directories:
            full_path = self.root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Создана: {dir_path}/")
        
        print_success("Структура папок создана!")
    
    def move_files(self):
        """Перемещение файлов с проверкой"""
        print_step(3, 10, "Перемещение файлов...")
        
        for old_path, new_path in self.file_mapping.items():
            src = self.root / old_path
            dst = self.root / new_path
            
            # Проверка существования исходного файла
            if not src.exists():
                print_warning(f"Не найден: {old_path}")
                continue
            
            # Проверка - не копируем ли файл сам в себя
            try:
                if src.resolve() == dst.resolve():
                    print_info(f"Пропущен (уже на месте): {old_path}")
                    continue
            except:
                pass
            
            # Создание директории для целевого файла
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Копирование
            try:
                shutil.copy2(src, dst)
                print_success(f"{old_path} → {new_path}")
            except shutil.SameFileError:
                print_info(f"Пропущен (одинаковый файл): {old_path}")
            except Exception as e:
                print_error(f"Ошибка копирования {old_path}: {e}")
        
        print_success("Файлы перемещены!")
    
    def create_init_files(self):
        """Создание __init__.py файлов"""
        print_step(4, 10, "Создание __init__.py файлов...")
        
        init_locations = [
            'jarvis',
            'jarvis/core',
            'jarvis/core/speech',
            'jarvis/core/nlp',
            'jarvis/core/memory',
            'jarvis/core/learning',
            'jarvis/modules',
            'jarvis/gui',
            'jarvis/gui/widgets',
            'jarvis/utils',
            'tests',
        ]
        
        for location in init_locations:
            init_file = self.root / location / '__init__.py'
            if not init_file.exists():
                init_file.write_text('"""JARVIS module"""\n', encoding='utf-8')
                print_success(f"Создан: {location}/__init__.py")
            else:
                print_info(f"Уже существует: {location}/__init__.py")
    
    def create_main_entry_point(self):
        """Создание точки входа __main__.py"""
        print_step(5, 10, "Создание точки входа...")
        
        main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Just A Rather Very Intelligent System
Main entry point
"""

import sys
from jarvis.assistant import main

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n\\nЗавершение работы JARVIS...")
        print("До свидания, сэр.")
        sys.exit(0)
'''
        
        main_file = self.root / 'jarvis' / '__main__.py'
        main_file.write_text(main_content, encoding='utf-8')
        print_success("Создан jarvis/__main__.py")
    
    def update_imports(self):
        """Обновление импортов во всех файлах"""
        print_step(6, 10, "Обновление импортов...")
        
        python_files = list(self.root.glob('jarvis/**/*.py'))
        updated_count = 0
        
        for file_path in python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content
                
                # Применяем замены импортов
                for old_import, new_import in self.import_replacements.items():
                    content = content.replace(old_import, new_import)
                
                # Сохраняем если были изменения
                if content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                    print_success(f"Обновлены импорты: {file_path.relative_to(self.root)}")
                    updated_count += 1
            
            except Exception as e:
                print_error(f"Ошибка в {file_path}: {e}")
        
        if updated_count > 0:
            print_success(f"Импорты обновлены в {updated_count} файлах!")
        else:
            print_info("Импорты уже актуальны")
    
    def create_setup_py(self):
        """Создание setup.py"""
        print_step(7, 10, "Создание setup.py...")
        
        setup_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Читаем requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="jarvis-assistant",
    version="0.1.0",
    author="jeffcheasey1337",
    description="Personal AI Voice Assistant with Learning Capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeffcheasey1337/JarvisNew",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jarvis=jarvis.assistant:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jarvis": ["config/*.json"],
    },
)
'''
        
        setup_file = self.root / 'setup.py'
        setup_file.write_text(setup_content, encoding='utf-8')
        print_success("Создан setup.py")
    
    def create_documentation(self):
        """Создание дополнительной документации"""
        print_step(8, 10, "Создание документации...")
        
        # API.md
        api_doc = '''# JARVIS API Documentation

## Быстрый старт

```python
from jarvis.assistant import JarvisAssistant

# Создание экземпляра
jarvis = JarvisAssistant()

# Запуск
await jarvis.run()
```

## Core Components

### Speech Recognition
```python
from jarvis.core.speech.recognition import SpeechRecognizer

recognizer = SpeechRecognizer(config)
audio_data = await recognizer.listen()
text = await recognizer.recognize(audio_data)
```

### Speech Synthesis
```python
from jarvis.core.speech.synthesis import SpeechSynthesizer

synthesizer = SpeechSynthesizer(config)
await synthesizer.speak("Доброе утро, сэр")
```

### Memory System
```python
from jarvis.core.memory.system import MemorySystem

memory = MemorySystem(config)
await memory.store_memory("Важная информация", memory_type="fact")
results = await memory.recall_memory("запрос")
```

### Learning System
```python
from jarvis.core.learning.continuous import ContinuousLearning

learning = ContinuousLearning(config, memory, nlp)
await learning.start_continuous_learning()
```

## Modules

### Task Manager
```python
from jarvis.modules.tasks import TaskManager

tasks = TaskManager(memory)
response = await tasks.handle_command("Создай задачу купить молоко", entities)
```

### Web Search
```python
from jarvis.modules.search import WebSearch

search = WebSearch(config)
results = await search.search("новости ИИ", entities)
```

## GUI

```python
from jarvis.gui.main_window import launch_gui

gui = launch_gui(jarvis_instance)
```
'''
        
        api_file = self.root / 'docs' / 'API.md'
        api_file.write_text(api_doc, encoding='utf-8')
        print_success("Создан docs/API.md")
        
        # CHANGELOG.md
        changelog = '''# Changelog

## [0.1.0] - 2026-01-29

### Added
- ✨ Полная реорганизация проекта в модульную структуру
- 📦 Setup.py для установки как пакет
- 📚 Комплексная документация (API, Architecture, Quickstart)
- ✅ Организованная структура тестов
- 🔧 Правильная иерархия пакетов

### Changed
- 🏗️ Переход на модульную архитектуру jarvis/
- 📝 Обновлены все импорты на новые пути
- 📂 Логичная организация файлов по функциональности
- 🎯 Улучшена расширяемость и поддерживаемость

### Fixed
- 🐛 Исправлены пути импортов
- 📦 Правильная организация пакетов Python
- 🔍 Упрощена навигация по коду

### Technical
- Структура: `jarvis/core/`, `jarvis/modules/`, `jarvis/gui/`
- Точка входа: `python -m jarvis` или команда `jarvis`
- Установка: `pip install -e .`
'''
        
        changelog_file = self.root / 'docs' / 'CHANGELOG.md'
        changelog_file.write_text(changelog, encoding='utf-8')
        print_success("Создан docs/CHANGELOG.md")
    
    def update_gitignore(self):
        """Обновление .gitignore"""
        print_step(9, 10, "Обновление .gitignore...")
        
        gitignore_content = '''# JARVIS .gitignore

# Модели (большие файлы)
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
.pytest_cache/

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
data/learning/
data/user/
*.sql

# Логи
*.log
logs/

# Временные файлы
*.tmp
*.temp
.DS_Store
Thumbs.db

# Backup
backup_before_restructure/

# Конфигурация с секретами
.env
config/local.json

# OS
.DS_Store
Thumbs.db
'''
        
        gitignore_file = self.root / '.gitignore'
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        print_success("Обновлен .gitignore")
    
    def create_env_example(self):
        """Создание .env.example"""
        print_step(10, 10, "Создание .env.example...")
        
        env_example = '''# JARVIS Environment Variables Example
# Copy this file to .env and fill in your values

# API Keys (if needed in future)
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Paths
MODELS_PATH=models/
DATA_PATH=data/
LOGS_PATH=logs/

# Settings
DEBUG=false
LOG_LEVEL=INFO
'''
        
        env_file = self.root / '.env.example'
        env_file.write_text(env_example, encoding='utf-8')
        print_success("Создан .env.example")
    
    def cleanup_old_structure(self):
        """Очистка старой структуры (опционально)"""
        print("\n" + "="*70)
        print("Очистка старой структуры")
        print("="*70)
        
        response = input("\nУдалить старые файлы и папки? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print_warning("Старые файлы сохранены")
            return
        
        # Папки для удаления
        old_dirs = ['core', 'modules']
        old_files = [
            'main.py',
            'jarvis_gui.py',
            'jarvis_gui_extended.py',
            'integrate_extended_gui.py',
            'fix_voice_issues.py',
            'start_jarvis_gui.py',
            'test_voice_RU.py',
        ]
        
        for dir_name in old_dirs:
            dir_path = self.root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                try:
                    shutil.rmtree(dir_path)
                    print_success(f"Удалена папка: {dir_name}")
                except Exception as e:
                    print_error(f"Не удалось удалить {dir_name}: {e}")
        
        for file_name in old_files:
            file_path = self.root / file_name
            if file_path.exists():
                try:
                    file_path.unlink()
                    print_success(f"Удалён файл: {file_name}")
                except Exception as e:
                    print_error(f"Не удалось удалить {file_name}: {e}")
        
        print_success("Старая структура очищена!")
    
    def show_final_structure(self):
        """Показать финальную структуру"""
        print_header("НОВАЯ СТРУКТУРА ПРОЕКТА")
        
        structure_text = '''
jarvis/
├── 📄 README.md
├── 📄 setup.py                   # pip install -e .
├── 📄 requirements.txt
│
├── 📁 docs/                      # 📚 Документация
│   ├── ARCHITECTURE.md
│   ├── QUICKSTART.md
│   ├── API.md
│   └── CHANGELOG.md
│
├── 📁 config/                    # ⚙️ Конфигурация
│   ├── config.json
│   └── personality.json
│
├── 📁 jarvis/                    # 🤖 ОСНОВНОЙ КОД
│   ├── __init__.py
│   ├── __main__.py               # python -m jarvis
│   ├── assistant.py              # Главный класс
│   │
│   ├── core/                     # 🧠 Ядро
│   │   ├── speech/
│   │   │   ├── recognition.py
│   │   │   └── synthesis.py
│   │   ├── nlp/
│   │   │   └── processor.py
│   │   ├── memory/
│   │   │   └── system.py
│   │   └── learning/
│   │       ├── base.py
│   │       ├── autonomous.py
│   │       └── continuous.py
│   │
│   ├── modules/                  # 🔧 Функциональные модули
│   │   ├── tasks.py
│   │   ├── calendar.py
│   │   ├── files.py
│   │   ├── system.py
│   │   └── search.py
│   │
│   ├── gui/                      # 🖥️ Графический интерфейс
│   │   └── main_window.py
│   │
│   └── utils/                    # 🛠️ Утилиты
│
├── 📁 data/                      # 💾 Данные (не в git)
├── 📁 models/                    # 🎯 Модели (не в git)
├── 📁 logs/                      # 📝 Логи (не в git)
├── 📁 tests/                     # ✅ Тесты
└── 📁 scripts/                   # 🔨 Скрипты
        '''
        
        print(structure_text)
    
    def run(self):
        """Запуск полной реструктуризации"""
        print_header("JARVIS PROJECT RESTRUCTURING")
        
        print(f"{Colors.YELLOW}Этот скрипт полностью реорганизует проект!{Colors.ENDC}")
        print(f"{Colors.YELLOW}Будет создана резервная копия.{Colors.ENDC}\n")
        
        response = input("Продолжить? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print_error("Отменено пользователем")
            return False
        
        try:
            # Выполняем все шаги
            if not self.create_backup():
                return False
            
            self.create_directory_structure()
            self.move_files()
            self.create_init_files()
            self.create_main_entry_point()
            self.update_imports()
            self.create_setup_py()
            self.create_documentation()
            self.update_gitignore()
            self.create_env_example()
            
            print_header("РЕСТРУКТУРИЗАЦИЯ ЗАВЕРШЕНА!")
            
            print_success("✓ Резервная копия создана")
            print_success("✓ Новая структура создана")
            print_success("✓ Файлы перемещены")
            print_success("✓ Импорты обновлены")
            print_success("✓ Документация создана")
            
            self.show_final_structure()
            
            print("\n" + "="*70)
            print("СЛЕДУЮЩИЕ ШАГИ:")
            print("="*70)
            print("\n1. Установка пакета:")
            print("   pip install -e .")
            print("\n2. Запуск JARVIS:")
            print("   python -m jarvis")
            print("   # или просто:")
            print("   jarvis")
            print("\n3. Запуск тестов:")
            print("   pytest tests/")
            print("\n4. Если что-то сломалось:")
            print(f"   Восстановить из: {self.backup_dir}")
            
            # Опциональная очистка
            self.cleanup_old_structure()
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ПРОЕКТ УСПЕШНО РЕОРГАНИЗОВАН! 🎉{Colors.ENDC}")
            
            return True
            
        except Exception as e:
            print_error(f"Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            print(f"\n{Colors.YELLOW}Восстановите проект из резервной копии:{Colors.ENDC}")
            print(f"   {self.backup_dir}")
            return False


def main():
    """Главная функция"""
    restructure = JarvisRestructure()
    restructure.run()
    
    input("\n\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
