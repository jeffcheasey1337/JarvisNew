#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 QUICK INSTALL - Автоматический установщик Enhanced Learning System
Запустите этот скрипт для быстрой интеграции улучшенной системы обучения
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

class EnhancedLearningInstaller:
    """Установщик Enhanced Learning System"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.jarvis_dir = self.base_dir / "jarvis"
        self.learning_dir = self.jarvis_dir / "core" / "learning"
        self.backup_dir = self.base_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.files_to_install = {
            'enhanced_learning.py': self.base_dir / 'jarvis' / 'core' / 'learning' / 'enhanced_learning.py',
            'integration.py': self.base_dir / 'jarvis' / 'core' / 'learning' / 'integration.py',
        }
        
        self.assistant_file = self.jarvis_dir / "assistant.py"
        
    def print_header(self):
        """Печать заголовка"""
        print("\n" + "="*70)
        print(" "*15 + "🧠 ENHANCED LEARNING SYSTEM")
        print(" "*20 + "Автоустановка")
        print("="*70 + "\n")
    
    def check_prerequisites(self) -> bool:
        """Проверка предварительных условий"""
        print("🔍 Проверка системы...")
        print()
        
        # Проверяем наличие директории jarvis
        if not self.jarvis_dir.exists():
            print(f"❌ Директория JARVIS не найдена: {self.jarvis_dir}")
            print("   Убедитесь что скрипт запущен из корня проекта")
            return False
        print(f"✓ Директория JARVIS найдена: {self.jarvis_dir}")
        
        # Проверяем learning директорию
        if not self.learning_dir.exists():
            print(f"⚠️  Директория learning не найдена, создаю...")
            self.learning_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Директория learning: {self.learning_dir}")
        
        # Проверяем assistant.py
        if not self.assistant_file.exists():
            print(f"❌ Файл assistant.py не найден: {self.assistant_file}")
            return False
        print(f"✓ Файл assistant.py найден")
        
        print()
        return True
    
    def create_backup(self):
        """Создание резервной копии"""
        print("💾 Создание резервной копии...")
        print()
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Бэкап assistant.py
        if self.assistant_file.exists():
            backup_assistant = self.backup_dir / "assistant.py"
            shutil.copy2(self.assistant_file, backup_assistant)
            print(f"✓ Создан бэкап: {backup_assistant}")
        
        # Бэкап существующих файлов learning
        for file in self.learning_dir.glob("*.py"):
            backup_file = self.backup_dir / file.name
            shutil.copy2(file, backup_file)
            print(f"✓ Создан бэкап: {backup_file}")
        
        print()
        print(f"📁 Все бэкапы сохранены в: {self.backup_dir}")
        print()
    
    def install_files(self) -> bool:
        """Установка файлов"""
        print("📦 Установка файлов Enhanced Learning...")
        print()
        
        # Проверяем наличие исходных файлов
        for name, source in self.files_to_install.items():
            if not source.exists():
                print(f"❌ Исходный файл не найден: {source}")
                return False
        
        # Копируем файлы
        for name, source in self.files_to_install.items():
            dest = self.learning_dir / name
            
            # Проверяем, не один ли это и тот же файл
            if source.resolve() == dest.resolve():
                print(f"✓ Файл уже установлен: {name}")
                continue
            
            shutil.copy2(source, dest)
            print(f"✓ Установлен: {name}")
        
        print()
        return True
    
    def patch_assistant(self) -> bool:
        """Патчинг assistant.py"""
        print("🔧 Патчинг assistant.py...")
        print()
        
        try:
            # Читаем файл
            content = self.assistant_file.read_text(encoding='utf-8')
            
            # Проверяем, не пропатчен ли уже
            if 'SmartContinuousLearning' in content or 'patch_jarvis_assistant' in content:
                print("⚠️  assistant.py уже пропатчен, пропускаю...")
                print()
                return True
            
            # Ищем импорты
            import_section_end = content.find('\n\n')
            if import_section_end == -1:
                import_section_end = content.find('class')
            
            # Добавляем импорт
            patch_import = "\n# Enhanced Learning System integration\nfrom jarvis.core.learning.integration import patch_jarvis_assistant\npatch_jarvis_assistant()\n"
            
            patched_content = content[:import_section_end] + patch_import + content[import_section_end:]
            
            # Сохраняем
            self.assistant_file.write_text(patched_content, encoding='utf-8')
            
            print("✓ assistant.py успешно пропатчен")
            print()
            return True
            
        except Exception as e:
            print(f"❌ Ошибка патчинга: {e}")
            print()
            return False
    
    def verify_installation(self) -> bool:
        """Проверка установки"""
        print("✅ Проверка установки...")
        print()
        
        all_ok = True
        
        # Проверяем файлы
        for name in self.files_to_install.keys():
            file_path = self.learning_dir / name
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"✓ {name} ({size} bytes)")
            else:
                print(f"❌ {name} не найден")
                all_ok = False
        
        # Проверяем патч
        content = self.assistant_file.read_text(encoding='utf-8')
        if 'SmartContinuousLearning' in content or 'patch_jarvis_assistant' in content:
            print(f"✓ assistant.py пропатчен")
        else:
            print(f"⚠️  assistant.py не содержит патч")
            all_ok = False
        
        print()
        return all_ok
    
    def print_summary(self, success: bool):
        """Печать итогов"""
        print("="*70)
        if success:
            print("🎉 УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
        else:
            print("⚠️  УСТАНОВКА ЗАВЕРШЕНА С ПРЕДУПРЕЖДЕНИЯМИ")
        print("="*70)
        print()
        
        if success:
            print("📋 Что дальше:")
            print()
            print("  1. Перезапустите JARVIS:")
            print("     python jarvis/assistant.py")
            print()
            print("  2. Проверьте логи:")
            print("     tail -f jarvis.log | grep 'Enhanced'")
            print()
            print("  3. Через 5-10 минут проверьте качество:")
            print("     grep 'КАЧЕСТВО' jarvis.log")
            print()
            print("📖 Документация:")
            print(f"     {self.base_dir / 'ENHANCED_LEARNING_GUIDE.md'}")
            print()
            print("🧪 Запустить тесты:")
            print(f"     python {self.base_dir / 'test_enhanced_learning.py'}")
            print()
        else:
            print("⚠️  Обнаружены проблемы. Проверьте:")
            print()
            print("  1. Все ли файлы на месте")
            print("  2. Логи установки выше")
            print("  3. Права доступа к файлам")
            print()
        
        print(f"💾 Резервные копии сохранены в:")
        print(f"   {self.backup_dir}")
        print()
    
    def run(self):
        """Запуск установки"""
        self.print_header()
        
        # Проверка системы
        if not self.check_prerequisites():
            print("❌ Установка прервана")
            return False
        
        # Создание бэкапов
        self.create_backup()
        
        # Установка файлов
        if not self.install_files():
            print("❌ Установка прервана")
            return False
        
        # Патчинг assistant.py
        if not self.patch_assistant():
            print("⚠️  Патчинг не выполнен, но файлы установлены")
            print("    Вы можете добавить патч вручную")
        
        # Проверка
        success = self.verify_installation()
        
        # Итоги
        self.print_summary(success)
        
        return success


def main():
    """Точка входа"""
    installer = EnhancedLearningInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
