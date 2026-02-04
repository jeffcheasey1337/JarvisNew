# -*- coding: utf-8 -*-
"""
🧹 JARVIS PERFECT CLEANUP & ORGANIZATION
Финальная очистка и правильная организация проекта

Этот скрипт:
1. Удаляет весь "срач" из корня
2. Оставляет только правильные файлы в правильных местах
3. Создаёт идеально чистую структуру
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

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


class PerfectCleanup:
    """Идеальная очистка проекта JARVIS"""
    
    def __init__(self):
        self.root = Path.cwd()
        
        # Файлы, которые ДОЛЖНЫ остаться в корне
        self.root_files_to_keep = {
            'README.md',
            'LICENSE',
            'requirements.txt',
            'setup.py',
            'pyproject.toml',
            'MANIFEST.in',
            '.gitignore',
            '.env',
            '.env.example',
            'RESTRUCTURE_REPORT.json',
        }
        
        # Папки, которые ДОЛЖНЫ существовать
        self.valid_directories = {
            'jarvis',
            'docs',
            'config',
            'data',
            'models',
            'logs',
            'tests',
            'scripts',
        }
        
        # Вложенные структуры
        self.nested_valid_dirs = {
            'docs/guides',
            'docs/examples',
        }
        
        # Папки для полного удаления
        self.dirs_to_delete = {
            'backup_before_restructure',
            'backup_20260129_172010',
            'core',
            'modules',
            '__pycache__',
            '.pytest_cache',
            '*.egg-info',
        }
        
        # Файлы для удаления из корня
        self.files_to_delete_patterns = [
            'fix_*.py',
            'restructure_*.py',
            'ultimate_restructure.py',
            'integrate_*.py',
            'start_*.py',
            'test_*.py',
            '*.log',
            'jarvis_gui*.py',
        ]
    
    def analyze_current_mess(self):
        """Анализ текущего беспорядка"""
        print_header("📊 АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ")
        
        root_items = list(self.root.iterdir())
        
        # Файлы в корне
        root_files = [f for f in root_items if f.is_file() and not f.name.startswith('.')]
        # Папки в корне
        root_dirs = [d for d in root_items if d.is_dir() and not d.name.startswith('.')]
        
        print(f"\n  📁 Папок в корне: {Colors.BOLD}{len(root_dirs)}{Colors.ENDC}")
        for d in sorted(root_dirs):
            status = "✅ нужна" if d.name in self.valid_directories else "❌ лишняя"
            print(f"    {status} - {d.name}/")
        
        print(f"\n  📄 Файлов в корне: {Colors.BOLD}{len(root_files)}{Colors.ENDC}")
        for f in sorted(root_files)[:20]:
            status = "✅ нужен" if f.name in self.root_files_to_keep else "❌ лишний"
            print(f"    {status} - {f.name}")
        
        if len(root_files) > 20:
            print(f"    ... и ещё {len(root_files) - 20} файлов")
        
        return root_files, root_dirs
    
    def fix_data_templates_mess(self):
        """Исправление беспорядка в data/templates/"""
        print_header("🔧 ИСПРАВЛЕНИЕ DATA/TEMPLATES/")
        
        templates_dir = self.root / 'data' / 'templates'
        
        if not templates_dir.exists():
            print_info("data/templates/ не существует - пропускаем")
            return
        
        # Удаляем всё из data/templates/ - это была ошибка
        try:
            shutil.rmtree(templates_dir)
            templates_dir.mkdir(parents=True)
            print_success("Очищена data/templates/")
            
            # Создаём только нужные примеры
            example_files = {
                'user_profile.example.json': '{\n  "name": "User",\n  "preferences": {}\n}\n',
                'config.example.json': '{\n  "setting": "value"\n}\n',
            }
            
            for filename, content in example_files.items():
                file_path = templates_dir / filename
                file_path.write_text(content, encoding='utf-8')
                print_success(f"Создан: data/templates/{filename}")
        
        except Exception as e:
            print_error(f"Ошибка: {e}")
    
    def move_setup_to_root(self):
        """Перемещение setup.py обратно в корень"""
        print_header("📦 ПЕРЕМЕЩЕНИЕ SETUP.PY")
        
        setup_in_scripts = self.root / 'scripts' / 'setup.py'
        setup_in_root = self.root / 'setup.py'
        
        if setup_in_scripts.exists() and not setup_in_root.exists():
            shutil.move(setup_in_scripts, setup_in_root)
            print_success("setup.py перемещён в корень")
        elif setup_in_root.exists():
            print_info("setup.py уже в корне")
            # Удаляем дубликат
            if setup_in_scripts.exists():
                setup_in_scripts.unlink()
                print_success("Удалён дубликат setup.py из scripts/")
    
    def delete_old_directories(self):
        """Удаление старых директорий"""
        print_header("🗑️ УДАЛЕНИЕ СТАРЫХ ПАПОК")
        
        for dir_pattern in self.dirs_to_delete:
            # Поддержка wildcards
            if '*' in dir_pattern:
                import glob
                matching_dirs = glob.glob(str(self.root / dir_pattern))
                for dir_path in matching_dirs:
                    try:
                        shutil.rmtree(dir_path)
                        print_success(f"Удалена: {Path(dir_path).name}/")
                    except Exception as e:
                        print_error(f"Не удалось удалить {dir_path}: {e}")
            else:
                dir_path = self.root / dir_pattern
                if dir_path.exists():
                    try:
                        shutil.rmtree(dir_path)
                        print_success(f"Удалена: {dir_pattern}/")
                    except Exception as e:
                        print_error(f"Не удалось удалить {dir_pattern}: {e}")
    
    def cleanup_root_files(self):
        """Очистка лишних файлов из корня"""
        print_header("🧹 ОЧИСТКА КОРНЕВЫХ ФАЙЛОВ")
        
        root_files = [f for f in self.root.iterdir() if f.is_file()]
        deleted_count = 0
        
        for file_path in root_files:
            # Пропускаем нужные файлы
            if file_path.name in self.root_files_to_keep:
                continue
            
            # Пропускаем скрытые файлы
            if file_path.name.startswith('.'):
                continue
            
            # Проверяем паттерны для удаления
            should_delete = False
            for pattern in self.files_to_delete_patterns:
                import fnmatch
                if fnmatch.fnmatch(file_path.name, pattern):
                    should_delete = True
                    break
            
            if should_delete:
                try:
                    file_path.unlink()
                    print_success(f"Удалён: {file_path.name}")
                    deleted_count += 1
                except Exception as e:
                    print_error(f"Не удалось удалить {file_path.name}: {e}")
        
        print(f"\n  Удалено файлов: {Colors.BOLD}{deleted_count}{Colors.ENDC}")
    
    def organize_guides(self):
        """Организация гайдов в docs/guides/"""
        print_header("📚 ОРГАНИЗАЦИЯ ГАЙДОВ")
        
        guides_dir = self.root / 'docs' / 'guides'
        guides_dir.mkdir(parents=True, exist_ok=True)
        
        # Файлы-гайды, которые нужно переместить в docs/guides/
        guide_files = [
            'NEW_STRUCTURE_GUIDE.md',
            'RESTRUCTURE_CHECKLIST.md',
        ]
        
        # Основные файлы документации, которые остаются в docs/
        main_docs = {
            'ARCHITECTURE.md',
            'QUICKSTART.md',
            'API.md',
            'CHANGELOG.md',
            'CONTRIBUTING.md',
            'INSTALLATION.md',
            'README.md',
        }
        
        moved_count = 0
        
        # Перемещаем гайды из корня в docs/guides/
        for guide_name in guide_files:
            src = self.root / guide_name
            if src.exists():
                dst = guides_dir / guide_name
                shutil.move(src, dst)
                print_success(f"Перемещён: {guide_name} → docs/guides/")
                moved_count += 1
        
        # Перемещаем гайды из docs/ в docs/guides/
        docs_dir = self.root / 'docs'
        if docs_dir.exists():
            for md_file in docs_dir.glob('*.md'):
                # Пропускаем основные файлы документации
                if md_file.name in main_docs:
                    continue
                
                # Перемещаем остальные MD файлы в guides
                dst = guides_dir / md_file.name
                if not dst.exists():
                    shutil.move(md_file, dst)
                    print_success(f"Перемещён: {md_file.name} → docs/guides/")
                    moved_count += 1
        
        # Создаём README для папки guides
        guides_readme = guides_dir / 'README.md'
        if not guides_readme.exists():
            content = '''# Гайды и руководства JARVIS

Эта папка содержит различные руководства по работе с проектом.

## Доступные гайды:

- **NEW_STRUCTURE_GUIDE.md** - Подробное описание новой структуры проекта
- **RESTRUCTURE_CHECKLIST.md** - Чеклист для проверки после реорганизации

## Основная документация

Основная документация проекта находится в корневой папке `docs/`:
- `ARCHITECTURE.md` - Архитектура системы
- `QUICKSTART.md` - Быстрый старт
- `API.md` - API документация
- `INSTALLATION.md` - Инструкции по установке
- `CONTRIBUTING.md` - Руководство для контрибьюторов
'''
            guides_readme.write_text(content, encoding='utf-8')
            print_success("Создан: docs/guides/README.md")
        
        print(f"\n  Перемещено гайдов: {Colors.BOLD}{moved_count}{Colors.ENDC}")
    
    def verify_jarvis_structure(self):
        """Проверка структуры jarvis/"""
        print_header("✅ ПРОВЕРКА СТРУКТУРЫ JARVIS/")
        
        required_structure = {
            'jarvis/__init__.py': 'файл',
            'jarvis/__main__.py': 'файл',
            'jarvis/assistant.py': 'файл',
            'jarvis/core/': 'папка',
            'jarvis/core/speech/recognition.py': 'файл',
            'jarvis/core/speech/synthesis.py': 'файл',
            'jarvis/core/nlp/processor.py': 'файл',
            'jarvis/core/memory/system.py': 'файл',
            'jarvis/core/learning/base.py': 'файл',
            'jarvis/modules/': 'папка',
            'jarvis/modules/tasks.py': 'файл',
            'jarvis/modules/calendar.py': 'файл',
            'jarvis/gui/': 'папка',
            'jarvis/gui/main_window.py': 'файл',
            'jarvis/utils/': 'папка',
        }
        
        all_good = True
        for path, item_type in required_structure.items():
            full_path = self.root / path
            
            if item_type == 'файл':
                if full_path.exists() and full_path.is_file():
                    print_success(f"✓ {path}")
                else:
                    print_error(f"✗ Отсутствует: {path}")
                    all_good = False
            elif item_type == 'папка':
                if full_path.exists() and full_path.is_dir():
                    print_success(f"✓ {path}")
                else:
                    print_error(f"✗ Отсутствует: {path}")
                    all_good = False
        
        return all_good
    
    def create_missing_essentials(self):
        """Создание недостающих важных файлов"""
        print_header("📝 СОЗДАНИЕ НЕДОСТАЮЩИХ ФАЙЛОВ")
        
        # LICENSE
        license_file = self.root / 'LICENSE'
        if not license_file.exists():
            license_content = '''MIT License

Copyright (c) 2026 jeffcheasey1337

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
            license_file.write_text(license_content, encoding='utf-8')
            print_success("Создан LICENSE")
        
        # models/README.md
        models_readme = self.root / 'models' / 'README.md'
        if not models_readme.exists():
            models_readme.parent.mkdir(parents=True, exist_ok=True)
            content = '''# Модели для JARVIS

## Vosk модель для русского языка

Скачайте модель отсюда:
https://alphacephei.com/vosk/models

Рекомендуется: `vosk-model-ru-0.42`

Распакуйте в:
```
models/vosk-model-ru/
```
'''
            models_readme.write_text(content, encoding='utf-8')
            print_success("Создан models/README.md")
        
        # logs/README.md
        logs_readme = self.root / 'logs' / 'README.md'
        if not logs_readme.exists():
            logs_readme.parent.mkdir(parents=True, exist_ok=True)
            content = '''# Логи JARVIS

Все логи сохраняются в этой директории.

Форматы:
- `jarvis_YYYYMMDD.log` - основные логи
- `errors_YYYYMMDD.log` - ошибки
'''
            logs_readme.write_text(content, encoding='utf-8')
            print_success("Создан logs/README.md")
    
    def show_final_structure(self):
        """Показать финальную структуру"""
        print_header("📊 ФИНАЛЬНАЯ СТРУКТУРА")
        
        print("\n✅ В корне проекта:")
        root_files = sorted([f.name for f in self.root.iterdir() if f.is_file() and not f.name.startswith('.')])
        for f in root_files:
            print(f"    📄 {f}")
        
        print("\n✅ Директории:")
        root_dirs = sorted([d.name for d in self.root.iterdir() if d.is_dir() and not d.name.startswith('.')])
        for d in root_dirs:
            if d in self.valid_directories:
                print(f"    📁 {d}/")
                
                # Показываем содержимое docs/
                if d == 'docs':
                    docs_dir = self.root / 'docs'
                    print(f"        📚 Документация:")
                    for doc_file in sorted(docs_dir.glob('*.md')):
                        print(f"            📄 {doc_file.name}")
                    
                    guides_dir = docs_dir / 'guides'
                    if guides_dir.exists():
                        guide_count = len(list(guides_dir.glob('*.md')))
                        print(f"        📁 guides/ ({guide_count} гайдов)")
        
        print(f"\n{Colors.GREEN}Проект идеально организован!{Colors.ENDC}")
    
    def run(self):
        """Запуск очистки"""
        print_header("🧹 JARVIS PERFECT CLEANUP")
        
        print(f"{Colors.YELLOW}Этот скрипт удалит весь 'срач' и оставит только нужные файлы!{Colors.ENDC}\n")
        
        # Анализ
        self.analyze_current_mess()
        
        print()
        response = input(f"{Colors.BOLD}Начать очистку? (yes/no): {Colors.ENDC}").strip().lower()
        if response not in ['yes', 'y']:
            print_error("Отменено")
            return False
        
        try:
            # Шаг 1: Исправление data/templates/
            self.fix_data_templates_mess()
            
            # Шаг 2: setup.py в корень
            self.move_setup_to_root()
            
            # Шаг 3: Удаление старых папок
            self.delete_old_directories()
            
            # Шаг 4: Очистка корневых файлов
            self.cleanup_root_files()
            
            # Шаг 5: Организация гайдов
            self.organize_guides()
            
            # Шаг 6: Создание недостающих файлов
            self.create_missing_essentials()
            
            # Шаг 7: Проверка структуры
            structure_ok = self.verify_jarvis_structure()
            
            # Шаг 8: Показать результат
            self.show_final_structure()
            
            # Финал
            print_header("✅ ОЧИСТКА ЗАВЕРШЕНА!")
            
            if structure_ok:
                print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Проект JARVIS идеально организован! 🎉{Colors.ENDC}")
            else:
                print(f"\n{Colors.YELLOW}⚠ Некоторые файлы отсутствуют - проверьте структуру{Colors.ENDC}")
            
            print(f"\n{Colors.CYAN}Следующие шаги:{Colors.ENDC}")
            print(f"  1. pip install -e .")
            print(f"  2. python -m jarvis")
            
            return True
            
        except Exception as e:
            print_error(f"Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Главная функция"""
    cleanup = PerfectCleanup()
    cleanup.run()
    
    input("\n\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
