# -*- coding: utf-8 -*-
"""
🧹 JARVIS ULTIMATE CLEANUP - ИДЕАЛЬНО ЧИСТЫЙ КОРЕНЬ
Финальная очистка с перемещением ВСЕХ файлов из корня в правильные места

Корень проекта будет содержать ТОЛЬКО:
- README.md
- LICENSE
- requirements.txt
- setup.py
- pyproject.toml
- MANIFEST.in
- .gitignore
- .env.example
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"  {Colors.GREEN}✓{Colors.ENDC} {text}")

def print_warning(text):
    print(f"  {Colors.YELLOW}⚠{Colors.ENDC} {text}")

def print_error(text):
    print(f"  {Colors.RED}✗{Colors.ENDC} {text}")

def print_info(text):
    print(f"  {Colors.BLUE}ℹ{Colors.ENDC} {text}")


class UltimateCleanup:
    """Идеальная очистка корня проекта JARVIS"""
    
    def __init__(self):
        self.root = Path.cwd()
        
        # ТОЛЬКО эти файлы остаются в корне
        self.allowed_root_files = {
            'README.md',
            'LICENSE',
            'requirements.txt',
            'setup.py',
            'pyproject.toml',
            'MANIFEST.in',
            '.gitignore',
            '.env',
            '.env.example',
        }
        
        # Разрешённые папки в корне
        self.allowed_root_dirs = {
            'jarvis',
            'docs',
            'config',
            'data',
            'models',
            'logs',
            'tests',
            'scripts',
        }
        
        # Папки для удаления
        self.dirs_to_delete = {
            'backup_before_restructure',
            'backup_20260129_172010',
            'core',
            'modules',
            '__pycache__',
            '.pytest_cache',
        }
        
        # Карта перемещения файлов: {паттерн: целевая_папка}
        self.file_mapping = {
            '*.md': self._decide_md_destination,  # Функция решает куда
            '*.py': self._decide_py_destination,   # Функция решает куда
            '*.json': self._decide_json_destination, # Функция решает куда
            '*.log': 'logs/',
        }
    
    def _decide_md_destination(self, filename):
        """Решает куда переместить MD файл"""
        main_docs = {'ARCHITECTURE.md', 'QUICKSTART.md', 'API.md', 
                    'CHANGELOG.md', 'CONTRIBUTING.md', 'INSTALLATION.md'}
        
        if filename == 'README.md':
            return None  # Остаётся в корне
        elif filename in main_docs:
            return 'docs/'
        else:
            return 'docs/guides/'
    
    def _decide_py_destination(self, filename):
        """Решает куда переместить Python файл"""
        # setup.py остаётся в корне
        if filename == 'setup.py':
            return None
        
        # Скрипты очистки, реструктуризации и т.д.
        script_patterns = ['cleanup', 'restructure', 'setup_', 'fix_', 
                          'integrate_', 'start_', 'download_']
        
        for pattern in script_patterns:
            if pattern in filename.lower():
                return 'scripts/'
        
        # Тесты
        if filename.startswith('test_'):
            return 'tests/'
        
        # Всё остальное - в scripts
        return 'scripts/'
    
    def _decide_json_destination(self, filename):
        """Решает куда переместить JSON файл"""
        # Отчёты о реструктуризации
        if 'REPORT' in filename or 'report' in filename:
            return 'logs/reports/'
        
        # Конфигурация
        if 'config' in filename.lower() or 'settings' in filename.lower():
            return 'config/'
        
        # Данные пользователя
        if 'user' in filename.lower() or 'profile' in filename.lower():
            return 'data/user/'
        
        # Данные обучения
        if 'learning' in filename.lower() or 'stats' in filename.lower():
            return 'data/learning/'
        
        # По умолчанию - в data
        return 'data/'
    
    def create_required_structure(self):
        """Создание необходимой структуры папок"""
        print_header("📁 СОЗДАНИЕ СТРУКТУРЫ ПАПОК")
        
        required_dirs = [
            'docs',
            'docs/guides',
            'docs/examples',
            'config',
            'scripts',
            'scripts/deployment',
            'tests',
            'tests/fixtures',
            'data',
            'data/user',
            'data/learning',
            'data/memory_db',
            'data/templates',
            'models',
            'logs',
            'logs/reports',
        ]
        
        for dir_path in required_dirs:
            full_path = self.root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                print_success(f"Создана: {dir_path}/")
    
    def analyze_root(self):
        """Анализ файлов в корне"""
        print_header("📊 АНАЛИЗ КОРНЯ ПРОЕКТА")
        
        root_files = [f for f in self.root.iterdir() 
                     if f.is_file() and not f.name.startswith('.')]
        
        to_keep = []
        to_move = []
        
        for file_path in root_files:
            if file_path.name in self.allowed_root_files:
                to_keep.append(file_path.name)
            else:
                to_move.append(file_path.name)
        
        print(f"\n  {Colors.GREEN}✅ Остаются в корне ({len(to_keep)}):{Colors.ENDC}")
        for name in sorted(to_keep):
            print(f"      📄 {name}")
        
        print(f"\n  {Colors.YELLOW}📦 Будут перемещены ({len(to_move)}):{Colors.ENDC}")
        for name in sorted(to_move):
            print(f"      📄 {name}")
        
        return to_move
    
    def move_files_from_root(self):
        """Перемещение файлов из корня"""
        print_header("🔄 ПЕРЕМЕЩЕНИЕ ФАЙЛОВ ИЗ КОРНЯ")
        
        root_files = [f for f in self.root.iterdir() 
                     if f.is_file() and not f.name.startswith('.')]
        
        moved_count = 0
        
        for file_path in root_files:
            # Пропускаем разрешённые файлы
            if file_path.name in self.allowed_root_files:
                continue
            
            # Определяем куда переместить
            destination = None
            
            # Проверяем по расширению
            ext = file_path.suffix
            if ext == '.md':
                destination = self._decide_md_destination(file_path.name)
            elif ext == '.py':
                destination = self._decide_py_destination(file_path.name)
            elif ext == '.json':
                destination = self._decide_json_destination(file_path.name)
            elif ext == '.log':
                destination = 'logs/'
            
            # Если не определили - в scripts
            if destination is None and file_path.name not in self.allowed_root_files:
                continue  # Остаётся в корне
            
            if destination:
                # Создаём целевую папку
                dest_dir = self.root / destination
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                # Перемещаем файл
                dest_path = dest_dir / file_path.name
                try:
                    if not dest_path.exists():
                        shutil.move(file_path, dest_path)
                        print_success(f"{file_path.name} → {destination}")
                        moved_count += 1
                    else:
                        print_warning(f"Уже существует: {destination}{file_path.name}")
                        file_path.unlink()  # Удаляем дубликат
                except Exception as e:
                    print_error(f"Ошибка при перемещении {file_path.name}: {e}")
        
        print(f"\n  Перемещено файлов: {Colors.BOLD}{moved_count}{Colors.ENDC}")
    
    def delete_old_directories(self):
        """Удаление старых директорий"""
        print_header("🗑️ УДАЛЕНИЕ СТАРЫХ ПАПОК")
        
        for dir_name in self.dirs_to_delete:
            # Поддержка wildcards
            if '*' in dir_name:
                import glob
                matching_dirs = glob.glob(str(self.root / dir_name))
                for dir_path in matching_dirs:
                    try:
                        shutil.rmtree(dir_path)
                        print_success(f"Удалена: {Path(dir_path).name}/")
                    except Exception as e:
                        print_error(f"Не удалось удалить {dir_path}: {e}")
            else:
                dir_path = self.root / dir_name
                if dir_path.exists():
                    try:
                        shutil.rmtree(dir_path)
                        print_success(f"Удалена: {dir_name}/")
                    except Exception as e:
                        print_error(f"Не удалось удалить {dir_name}: {e}")
    
    def fix_data_templates(self):
        """Исправление data/templates/"""
        print_header("🔧 ИСПРАВЛЕНИЕ DATA/TEMPLATES/")
        
        templates_dir = self.root / 'data' / 'templates'
        
        if not templates_dir.exists():
            templates_dir.mkdir(parents=True)
            print_success("Создана: data/templates/")
        
        # Удаляем неправильные файлы
        if templates_dir.exists():
            for item in templates_dir.iterdir():
                if item.name not in ['user_profile.example.json', 'config.example.json', '.gitkeep']:
                    try:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                        print_success(f"Удалено из templates/: {item.name}")
                    except Exception as e:
                        print_error(f"Ошибка: {e}")
        
        # Создаём правильные примеры
        examples = {
            'user_profile.example.json': {
                "name": "User",
                "preferences": {},
                "created_at": "2026-01-29"
            },
            'config.example.json': {
                "setting": "value",
                "example": "configuration"
            }
        }
        
        for filename, content in examples.items():
            file_path = templates_dir / filename
            if not file_path.exists():
                file_path.write_text(json.dumps(content, indent=2, ensure_ascii=False), 
                                   encoding='utf-8')
                print_success(f"Создан: data/templates/{filename}")
    
    def create_gitkeep_files(self):
        """Создание .gitkeep для пустых папок"""
        print_header("📌 СОЗДАНИЕ .GITKEEP")
        
        empty_dirs = [
            'data',
            'data/memory_db',
            'data/learning',
            'data/user',
            'models',
            'logs',
            'logs/reports',
        ]
        
        for dir_path in empty_dirs:
            gitkeep = self.root / dir_path / '.gitkeep'
            gitkeep.parent.mkdir(parents=True, exist_ok=True)
            if not gitkeep.exists():
                gitkeep.touch()
                print_success(f"Создан: {dir_path}/.gitkeep")
    
    def create_readme_files(self):
        """Создание README в важных папках"""
        print_header("📝 СОЗДАНИЕ README")
        
        readmes = {
            'models/README.md': '''# Модели для JARVIS

## Vosk модель для русского языка

Скачайте модель отсюда:
https://alphacephei.com/vosk/models

Рекомендуется: `vosk-model-ru-0.42`

Распакуйте в: `models/vosk-model-ru/`
''',
            'logs/README.md': '''# Логи JARVIS

Все логи автоматически сохраняются в этой директории.

## Структура:

- `jarvis_YYYYMMDD.log` - основные логи
- `errors_YYYYMMDD.log` - логи ошибок
- `reports/` - отчёты о реструктуризации и других операциях
''',
            'logs/reports/README.md': '''# Отчёты

Здесь хранятся JSON отчёты о различных операциях:
- Реструктуризация проекта
- Очистка
- Миграции
- И другие системные операции
''',
            'docs/guides/README.md': '''# Гайды и руководства

Вспомогательные руководства по работе с проектом.

## Основная документация

См. корневую папку `docs/` для основной документации.
''',
            'scripts/README.md': '''# Скрипты

Вспомогательные скрипты для:
- Настройки окружения
- Очистки проекта
- Реструктуризации
- Автоматизации задач
''',
        }
        
        for filepath, content in readmes.items():
            full_path = self.root / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if not full_path.exists():
                full_path.write_text(content, encoding='utf-8')
                print_success(f"Создан: {filepath}")
    
    def verify_root_cleanliness(self):
        """Проверка чистоты корня"""
        print_header("✅ ПРОВЕРКА КОРНЯ")
        
        root_items = list(self.root.iterdir())
        
        # Файлы в корне
        root_files = [f.name for f in root_items if f.is_file() and not f.name.startswith('.')]
        
        # Папки в корне
        root_dirs = [d.name for d in root_items if d.is_dir() and not d.name.startswith('.')]
        
        # Проверка файлов
        unexpected_files = [f for f in root_files if f not in self.allowed_root_files]
        
        # Проверка папок
        unexpected_dirs = [d for d in root_dirs if d not in self.allowed_root_dirs]
        
        all_clean = len(unexpected_files) == 0 and len(unexpected_dirs) == 0
        
        if all_clean:
            print(f"\n  {Colors.GREEN}{Colors.BOLD}🎉 Корень проекта идеально чист!{Colors.ENDC}")
        else:
            if unexpected_files:
                print(f"\n  {Colors.RED}❌ Лишние файлы в корне:{Colors.ENDC}")
                for f in unexpected_files:
                    print(f"      📄 {f}")
            
            if unexpected_dirs:
                print(f"\n  {Colors.RED}❌ Лишние папки в корне:{Colors.ENDC}")
                for d in unexpected_dirs:
                    print(f"      📁 {d}/")
        
        return all_clean
    
    def show_final_structure(self):
        """Показать финальную структуру"""
        print_header("📊 ФИНАЛЬНАЯ СТРУКТУРА")
        
        print(f"\n{Colors.BOLD}📁 Корень проекта:{Colors.ENDC}")
        print()
        
        # Файлы
        root_files = sorted([f.name for f in self.root.iterdir() 
                           if f.is_file() and not f.name.startswith('.')])
        for f in root_files:
            print(f"    📄 {f}")
        
        print()
        
        # Папки
        root_dirs = sorted([d.name for d in self.root.iterdir() 
                          if d.is_dir() and not d.name.startswith('.')])
        for d in root_dirs:
            if d in self.allowed_root_dirs:
                print(f"    📁 {d}/")
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}Структура идеальна!{Colors.ENDC}")
    
    def run(self):
        """Запуск полной очистки"""
        print_header("🧹 ULTIMATE CLEANUP - ЧИСТЫЙ КОРЕНЬ")
        
        print(f"{Colors.YELLOW}Этот скрипт очистит корень проекта!{Colors.ENDC}")
        print(f"{Colors.YELLOW}Все файлы будут правильно организованы.{Colors.ENDC}\n")
        
        # Анализ
        files_to_move = self.analyze_root()
        
        if not files_to_move:
            print(f"\n{Colors.GREEN}Корень уже чист!{Colors.ENDC}")
            return True
        
        print()
        response = input(f"{Colors.BOLD}Начать очистку? (yes/no): {Colors.ENDC}").strip().lower()
        if response not in ['yes', 'y']:
            print_error("Отменено")
            return False
        
        try:
            # Шаг 1: Создание структуры
            self.create_required_structure()
            
            # Шаг 2: Перемещение файлов из корня
            self.move_files_from_root()
            
            # Шаг 3: Удаление старых папок
            self.delete_old_directories()
            
            # Шаг 4: Исправление data/templates
            self.fix_data_templates()
            
            # Шаг 5: .gitkeep файлы
            self.create_gitkeep_files()
            
            # Шаг 6: README файлы
            self.create_readme_files()
            
            # Шаг 7: Проверка
            is_clean = self.verify_root_cleanliness()
            
            # Шаг 8: Показать результат
            self.show_final_structure()
            
            # Финал
            print_header("✅ ОЧИСТКА ЗАВЕРШЕНА!")
            
            if is_clean:
                print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Корень проекта идеально организован! 🎉{Colors.ENDC}")
            else:
                print(f"\n{Colors.YELLOW}⚠ Остались лишние файлы - проверьте вручную{Colors.ENDC}")
            
            print(f"\n{Colors.CYAN}Следующие шаги:{Colors.ENDC}")
            print(f"  1. pip install -e .")
            print(f"  2. python -m jarvis")
            print(f"  3. pytest tests/")
            
            return True
            
        except Exception as e:
            print_error(f"Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Главная функция"""
    cleanup = UltimateCleanup()
    cleanup.run()
    
    input("\n\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
