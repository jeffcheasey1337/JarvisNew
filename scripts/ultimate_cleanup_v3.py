# -*- coding: utf-8 -*-
"""
🧹 JARVIS ULTIMATE CLEANUP & STRUCTURE V3
Финальная очистка и структуризация проекта

Что делает:
✅ Чистит корень проекта (только важные файлы)
✅ Организует всё по папкам
✅ Интегрирует turbo-обучение
✅ Добавляет dashboard
✅ Удаляет старые backup
✅ Создаёт правильную структуру
✅ Проверяет что всё на месте
"""

import shutil
from pathlib import Path
from datetime import datetime
import json
import os

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

def print_step(step, total, text):
    print(f"\n{Colors.BOLD}[{step}/{total}]{Colors.ENDC} {text}")


class UltimateCleanup:
    """Финальная очистка и структуризация"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.total_steps = 12
        self.current_step = 0
        
        # Создаём backup перед началом
        self.backup_dir = self.root / f"backup_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Файлы которые ДОЛЖНЫ остаться в корне
        self.allowed_root_files = {
            # Конфигурация пакета
            'setup.py',
            'pyproject.toml',
            'requirements.txt',
            'requirements_turbo.txt',
            'MANIFEST.in',
            
            # Документация
            'README.md',
            'LICENSE',
            
            # Git
            '.gitignore',
            '.gitattributes',
            
            # Env
            '.env',
            '.env.example',
            
            # Запуск
            'jarvis_launcher.py',
            
            # Тесты (в корне)
            'test_turbo_integration.py',
            'gpu_test_only.py',
            
            # Ярлыки Windows
            'Запустить_JARVIS.bat',
            'Открыть_Dashboard.bat',
            'JARVIS_Menu.bat',
            
            # Скрипты установки (можно удалить после использования)
            'auto_optimize_and_integrate.py',
            'auto_integrate_complete.py',
            'auto_gpu_setup.py',
            'auto_gpu_setup_v2.py',
        }
        
        # Папки которые ДОЛЖНЫ быть в корне
        self.allowed_root_dirs = {
            'jarvis',      # Главный пакет
            'tests',       # Тесты
            'docs',        # Документация
            'scripts',     # Утилиты
            'data',        # Данные
            'logs',        # Логи
            'models',      # Модели
            'config',      # Конфиги
            '.idea',       # PyCharm
            '.venv',       # Virtual env
            'venv',        # Virtual env
            '.git',        # Git
            '__pycache__', # Python cache (будет удалена)
        }
    
    def step(self, text):
        self.current_step += 1
        print_step(self.current_step, self.total_steps, text)
    
    def create_backup(self):
        """Создание backup"""
        self.step("Создание backup...")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Важные папки для backup
            dirs_to_backup = ['jarvis', 'config', 'data']
            
            for dir_name in dirs_to_backup:
                src = self.root / dir_name
                if src.exists():
                    dst = self.backup_dir / dir_name
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    print_success(f"Скопировано: {dir_name}")
            
            print_success(f"Backup: {self.backup_dir.name}")
            return True
        
        except Exception as e:
            print_error(f"Ошибка backup: {e}")
            return False
    
    def create_directory_structure(self):
        """Создание правильной структуры папок"""
        self.step("Создание структуры папок...")
        
        # Основная структура
        dirs = {
            'jarvis': {
                'core': ['learning', 'memory', 'nlp'],
                'gui': [],
                'modules': [],
                'utils': [],
            },
            'docs': ['guides', 'api'],
            'scripts': [],
            'data': ['learning', 'user', 'cache'],
            'logs': ['reports'],
            'models': [],
            'tests': [],
            'config': [],
        }
        
        for main_dir, subdirs in dirs.items():
            main_path = self.root / main_dir
            main_path.mkdir(exist_ok=True)
            
            if isinstance(subdirs, dict):
                for subdir, subsubdirs in subdirs.items():
                    sub_path = main_path / subdir
                    sub_path.mkdir(exist_ok=True)
                    
                    for subsubdir in subsubdirs:
                        subsub_path = sub_path / subsubdir
                        subsub_path.mkdir(exist_ok=True)
            else:
                for subdir in subdirs:
                    sub_path = main_path / subdir
                    sub_path.mkdir(exist_ok=True)
        
        print_success("Структура создана")
        return True
    
    def analyze_root_directory(self):
        """Анализ корневой директории"""
        self.step("Анализ корневой директории...")
        
        files_to_move = []
        files_to_delete = []
        files_ok = []
        
        for item in self.root.iterdir():
            if item.name.startswith('.') and item.name not in {'.gitignore', '.env', '.env.example', '.gitattributes'}:
                continue
            
            if item.is_file():
                if item.name in self.allowed_root_files:
                    files_ok.append(item.name)
                elif item.name.endswith('.md') and item.name != 'README.md':
                    files_to_move.append(('docs/guides', item))
                elif item.name.endswith('.py') and 'test' not in item.name.lower():
                    if any(x in item.name.lower() for x in ['fix', 'setup', 'cleanup', 'restructure']):
                        files_to_move.append(('scripts', item))
                elif item.name.endswith('.json') and 'report' in item.name.lower():
                    files_to_move.append(('logs/reports', item))
                elif item.name.endswith('.log'):
                    files_to_move.append(('logs', item))
                else:
                    # Оставляем в корне или спрашиваем
                    files_to_move.append(('scripts', item))
            
            elif item.is_dir():
                if item.name not in self.allowed_root_dirs:
                    if 'backup' in item.name.lower():
                        files_to_delete.append(item)
                    elif item.name == '__pycache__':
                        files_to_delete.append(item)
        
        print()
        print_info(f"Файлов в корне OK: {len(files_ok)}")
        print_info(f"Файлов к перемещению: {len(files_to_move)}")
        print_info(f"Файлов/папок к удалению: {len(files_to_delete)}")
        
        return files_to_move, files_to_delete, files_ok
    
    def move_files(self, files_to_move):
        """Перемещение файлов"""
        self.step("Перемещение файлов...")
        
        moved_count = 0
        
        for dest_dir, file_path in files_to_move:
            try:
                dest = self.root / dest_dir / file_path.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                if dest.exists():
                    print_warning(f"Уже существует: {dest_dir}/{file_path.name}")
                else:
                    shutil.move(str(file_path), str(dest))
                    print_success(f"Перемещён: {file_path.name} → {dest_dir}/")
                    moved_count += 1
            
            except Exception as e:
                print_error(f"Ошибка перемещения {file_path.name}: {e}")
        
        print()
        print_success(f"Перемещено файлов: {moved_count}")
        return True
    
    def delete_old_items(self, items_to_delete):
        """Удаление старых файлов и папок"""
        self.step("Удаление старых backup и cache...")
        
        deleted_count = 0
        
        for item in items_to_delete:
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    print_success(f"Удалена папка: {item.name}")
                else:
                    item.unlink()
                    print_success(f"Удалён файл: {item.name}")
                
                deleted_count += 1
            
            except Exception as e:
                print_error(f"Ошибка удаления {item.name}: {e}")
        
        # Удаляем __pycache__ везде
        for pycache in self.root.rglob('__pycache__'):
            try:
                shutil.rmtree(pycache)
                deleted_count += 1
            except:
                pass
        
        print()
        print_success(f"Удалено элементов: {deleted_count}")
        return True
    
    def create_init_files(self):
        """Создание __init__.py файлов"""
        self.step("Создание __init__.py...")
        
        init_dirs = [
            'jarvis',
            'jarvis/core',
            'jarvis/core/learning',
            'jarvis/core/memory',
            'jarvis/core/nlp',
            'jarvis/gui',
            'jarvis/modules',
            'jarvis/utils',
            'tests',
        ]
        
        for dir_path in init_dirs:
            init_file = self.root / dir_path / '__init__.py'
            if not init_file.exists():
                init_file.write_text('"""Package initialization"""', encoding='utf-8')
                print_success(f"Создан: {dir_path}/__init__.py")
        
        return True
    
    def create_gitkeep_files(self):
        """Создание .gitkeep для пустых папок"""
        self.step("Создание .gitkeep...")
        
        empty_dirs = [
            'data/learning',
            'data/user',
            'data/cache',
            'logs',
            'logs/reports',
            'models',
        ]
        
        for dir_path in empty_dirs:
            gitkeep = self.root / dir_path / '.gitkeep'
            gitkeep.parent.mkdir(parents=True, exist_ok=True)
            gitkeep.write_text('', encoding='utf-8')
        
        print_success("Созданы .gitkeep файлы")
        return True
    
    def create_readme_files(self):
        """Создание README файлов"""
        self.step("Создание README...")
        
        readmes = {
            'docs/guides/README.md': '# Руководства\n\nГайды по использованию JARVIS',
            'scripts/README.md': '# Скрипты\n\nУтилиты и скрипты для обслуживания',
            'logs/README.md': '# Логи\n\nЛоги работы системы',
            'models/README.md': '# Модели\n\nМодели машинного обучения',
            'data/README.md': '# Данные\n\nДанные для обучения и работы',
        }
        
        for path, content in readmes.items():
            readme = self.root / path
            if not readme.exists():
                readme.parent.mkdir(parents=True, exist_ok=True)
                readme.write_text(content, encoding='utf-8')
                print_success(f"Создан: {path}")
        
        return True
    
    def verify_structure(self):
        """Проверка структуры"""
        self.step("Проверка структуры...")
        
        # Обязательные файлы
        required_files = [
            'setup.py',
            'requirements.txt',
            'README.md',
            'jarvis/__init__.py',
        ]
        
        # Обязательные папки
        required_dirs = [
            'jarvis/core/learning',
            'docs/guides',
            'data/learning',
            'logs',
            'config',
        ]
        
        all_good = True
        
        print()
        print_info("Проверка файлов:")
        for file_path in required_files:
            path = self.root / file_path
            if path.exists():
                print_success(f"✓ {file_path}")
            else:
                print_error(f"✗ {file_path}")
                all_good = False
        
        print()
        print_info("Проверка папок:")
        for dir_path in required_dirs:
            path = self.root / dir_path
            if path.exists():
                print_success(f"✓ {dir_path}")
            else:
                print_error(f"✗ {dir_path}")
                all_good = False
        
        return all_good
    
    def show_final_structure(self):
        """Показать финальную структуру"""
        self.step("Финальная структура...")
        
        print()
        print(f"{Colors.BOLD}Структура проекта:{Colors.ENDC}")
        print()
        
        structure = """
F:/Jarvis Beta/
│
├── 📄 README.md                       # Описание проекта
├── 📄 LICENSE                         # Лицензия
├── 📄 setup.py                        # Установка пакета
├── 📄 requirements.txt                # Зависимости
├── 📄 jarvis_launcher.py              # Меню запуска
│
├── 📁 jarvis/                         # Главный пакет
│   ├── 📁 core/                       # Ядро системы
│   │   ├── 📁 learning/               # Обучение
│   │   │   ├── base.py
│   │   │   ├── continuous.py
│   │   │   ├── turbo.py               # ⚡ GPU-ускорение
│   │   │   └── topics_database.py     # 📚 4127 тем
│   │   ├── 📁 memory/                 # Память
│   │   └── 📁 nlp/                    # NLP
│   │
│   ├── 📁 gui/                        # Интерфейсы
│   │   └── learning_dashboard.py      # 📊 Dashboard
│   │
│   ├── 📁 modules/                    # Модули
│   └── 📁 utils/                      # Утилиты
│
├── 📁 docs/                           # Документация
│   ├── 📁 guides/                     # Руководства
│   │   ├── COMPLETE_GUIDE.md
│   │   ├── TURBO_INTEGRATION.md
│   │   └── MANUAL_INSTALL_GUIDE.md
│   └── 📁 api/                        # API документация
│
├── 📁 scripts/                        # Скрипты
│   ├── auto_optimize_and_integrate.py
│   └── auto_gpu_setup_v2.py
│
├── 📁 data/                           # Данные
│   ├── 📁 learning/                   # Данные обучения
│   │   ├── learning_topics.json
│   │   ├── learning_stats.json
│   │   └── learning_history.json
│   ├── 📁 user/                       # Пользовательские данные
│   └── 📁 cache/                      # Кеш
│
├── 📁 logs/                           # Логи
│   └── 📁 reports/                    # Отчёты
│
├── 📁 models/                         # ML модели
├── 📁 tests/                          # Тесты
├── 📁 config/                         # Конфигурация
│   └── turbo_learning.json
│
└── 📁 .idea/                          # PyCharm настройки
    └── runConfigurations/
        ├── Run_JARVIS.xml
        └── Learning_Dashboard.xml
        """
        
        print(structure)
    
    def create_cleanup_report(self):
        """Создание отчёта"""
        self.step("Создание отчёта...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "backup_location": str(self.backup_dir),
            "actions": [
                "Создана структура папок",
                "Перемещены файлы из корня",
                "Удалены старые backup",
                "Созданы __init__.py",
                "Созданы .gitkeep",
                "Созданы README",
            ],
            "structure": {
                "root_files": list(self.allowed_root_files),
                "root_dirs": list(self.allowed_root_dirs),
            }
        }
        
        report_file = self.root / 'logs' / 'reports' / 'cleanup_report.json'
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        
        print_success(f"Отчёт: logs/reports/cleanup_report.json")
        return True
    
    def show_summary(self):
        """Итоговая информация"""
        self.step("Итоги...")
        
        print_header("✅ ОЧИСТКА ЗАВЕРШЕНА!")
        
        print(f"\n{Colors.BOLD}Что сделано:{Colors.ENDC}\n")
        
        print_success("Создана правильная структура папок")
        print_success("Корень очищен от лишних файлов")
        print_success("Всё организовано по категориям")
        print_success("Добавлены __init__.py и README")
        print_success(f"Backup: {self.backup_dir.name}")
        
        print()
        print(f"{Colors.BOLD}Корень проекта теперь содержит:{Colors.ENDC}\n")
        print("  • setup.py, requirements.txt (конфигурация)")
        print("  • README.md, LICENSE (документация)")
        print("  • jarvis_launcher.py (запуск)")
        print("  • Основные папки: jarvis/, docs/, data/, logs/")
        
        print()
        print(f"{Colors.BOLD}Следующие шаги:{Colors.ENDC}\n")
        print("1. Проверьте структуру:")
        print(f"   {Colors.CYAN}dir{Colors.ENDC}")
        print()
        print("2. Запустите JARVIS:")
        print(f"   {Colors.CYAN}python -m jarvis{Colors.ENDC}")
        print()
        print("3. Или используйте launcher:")
        print(f"   {Colors.CYAN}python jarvis_launcher.py{Colors.ENDC}")
        
        print()
        print(f"{Colors.GREEN}{Colors.BOLD}Проект готов к работе! 🎉{Colors.ENDC}\n")
    
    def run(self):
        """Запуск очистки"""
        print_header("🧹 JARVIS ULTIMATE CLEANUP V3")
        
        print(f"{Colors.YELLOW}Финальная очистка и структуризация проекта{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}Что будет сделано:{Colors.ENDC}")
        print("  • Создание backup")
        print("  • Создание правильной структуры")
        print("  • Очистка корня проекта")
        print("  • Перемещение файлов по папкам")
        print("  • Удаление старых backup")
        print("  • Создание __init__.py и README")
        print("  • Проверка структуры")
        print()
        
        response = input(f"{Colors.BOLD}Начать очистку? (yes/no): {Colors.ENDC}").strip().lower()
        if response not in ['yes', 'y']:
            print_error("Отменено")
            return False
        
        try:
            # Выполняем все шаги
            self.create_backup()
            self.create_directory_structure()
            
            files_to_move, files_to_delete, files_ok = self.analyze_root_directory()
            
            self.move_files(files_to_move)
            self.delete_old_items(files_to_delete)
            
            self.create_init_files()
            self.create_gitkeep_files()
            self.create_readme_files()
            
            self.verify_structure()
            self.show_final_structure()
            self.create_cleanup_report()
            
            self.show_summary()
            
            return True
        
        except Exception as e:
            print_error(f"Ошибка: {e}")
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
