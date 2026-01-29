# -*- coding: utf-8 -*-
"""
Полная интеграция расширенного GUI с JARVIS
Исправляет все проблемы с отображением памяти
"""

import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def integrate_gui_with_main():
    """Интеграция GUI в main.py"""
    
    print("[1/3] Интеграция GUI в main.py...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверка, не добавлено ли уже
        if 'from jarvis_gui_extended import launch_gui' in content:
            print("  [ПРОПУЩЕНО] GUI уже интегрирован")
            return True
        
        # 1. Добавление импорта
        import_pos = content.find('import asyncio')
        if import_pos != -1:
            end_pos = content.find('\n', import_pos) + 1
            new_import = 'from jarvis_gui_extended import launch_gui\nimport threading\n'
            content = content[:end_pos] + new_import + content[end_pos:]
            print("  [OK] Импорт добавлен")
        
        # 2. Запуск GUI в main()
        main_func_pos = content.find('async def main():')
        if main_func_pos != -1:
            # Найти начало функции (после def main():)
            func_start = content.find('\n', main_func_pos) + 1
            
            # Добавить запуск GUI
            gui_code = '''    # Запуск расширенного GUI
    print("Запуск графического интерфейса...")
    gui = launch_gui()
    await asyncio.sleep(1)  # Даем GUI время запуститься
    
'''
            
            content = content[:func_start] + gui_code + content[func_start:]
            print("  [OK] Запуск GUI добавлен")
        
        # 3. Привязка GUI к JARVIS
        jarvis_init_pos = content.find('jarvis = JarvisAssistant()')
        if jarvis_init_pos != -1:
            end_pos = content.find('\n', jarvis_init_pos) + 1
            bind_code = '''    
    # Привязка GUI к JARVIS
    jarvis.gui = gui
    gui.jarvis = jarvis
    gui.add_log("=== JARVIS ИНИЦИАЛИЗИРОВАН ===")
    gui.add_log("Графический интерфейс подключен")
    
'''
            content = content[:end_pos] + bind_code + content[end_pos:]
            print("  [OK] Привязка GUI добавлена")
        
        # 4. Добавление методов в класс JarvisAssistant
        class_init = content.find('def __init__(self):')
        if class_init != -1:
            # Найти конец __init__
            next_def = content.find('\n    def ', class_init + 20)
            if next_def != -1:
                methods = '''
    def log_gui(self, message):
        """Логирование в GUI"""
        if hasattr(self, 'gui') and self.gui:
            self.gui.add_log(message)
    
    def update_gui_status(self, system, status):
        """Обновление статуса системы в GUI"""
        if hasattr(self, 'gui') and self.gui:
            self.gui.update_status(system, status)
    
'''
                content = content[:next_def] + methods + content[next_def:]
                print("  [OK] Методы GUI добавлены в класс")
        
        # Сохранить
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("  [ГОТОВО] main.py обновлен")
        return True
        
    except Exception as e:
        print(f"  [ОШИБКА] {e}")
        return False

def fix_continuous_learning():
    """Исправление continuous_learning для обновления GUI"""
    
    print("\n[2/3] Исправление continuous_learning.py...")
    
    try:
        with open('core/continuous_learning.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавить self.gui в __init__
        init_pos = content.find('def __init__(self, config, memory_system, nlp_processor):')
        if init_pos != -1:
            # Найти конец __init__
            next_def = content.find('\n    def ', init_pos + 100)
            if next_def != -1:
                if 'self.gui = None' not in content[init_pos:next_def]:
                    gui_init = '\n        # Ссылка на GUI\n        self.gui = None\n'
                    content = content[:next_def] + gui_init + content[next_def:]
                    print("  [OK] self.gui добавлен в __init__")
        
        # Найти метод _process_article и добавить обновление GUI
        process_article = content.find('async def _process_article')
        if process_article != -1:
            # Найти место где вызывается memory.store_memory
            store_pos = content.find('await self.memory.store_memory', process_article)
            if store_pos != -1:
                # Найти конец этого блока
                next_line = content.find('\n', store_pos + 100) + 1
                
                # Проверить, не добавлено ли уже
                if 'self.gui.add_log' not in content[store_pos:store_pos+300]:
                    gui_update = '''
                # Обновление GUI
                self.stats['knowledge_items'] += 1
                if self.gui:
                    self.gui.add_log(f"[ОБУЧЕНИЕ] Сохранена статья: {title[:50]}...")
                    self.gui.update_stat('memory_items', self.stats['knowledge_items'])
                
'''
                    content = content[:next_line] + gui_update + content[next_line:]
                    print("  [OK] Обновление GUI после сохранения добавлено")
        
        # Сохранить
        with open('core/continuous_learning.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("  [ГОТОВО] continuous_learning.py обновлен")
        return True
        
    except Exception as e:
        print(f"  [ОШИБКА] {e}")
        return False

def create_startup_script():
    """Создание скрипта запуска с GUI"""
    
    print("\n[3/3] Создание скрипта запуска...")
    
    script = '''# -*- coding: utf-8 -*-
"""
JARVIS - Запуск с графическим интерфейсом
"""

import asyncio
import sys

# Исправление кодировки
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    print("="*70)
    print("  J.A.R.V.I.S - Just A Rather Very Intelligent System")
    print("="*70)
    print()
    print("Запуск систем...")
    
    # Импорт основного модуля
    from main import main as jarvis_main
    
    # Запуск
    await jarvis_main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n\\nЗавершение работы JARVIS...")
        print("До свидания, сэр.")
'''
    
    try:
        with open('start_jarvis_gui.py', 'w', encoding='utf-8') as f:
            f.write(script)
        
        print("  [ГОТОВО] Создан start_jarvis_gui.py")
        return True
        
    except Exception as e:
        print(f"  [ОШИБКА] {e}")
        return False

def check_memory_system():
    """Проверка системы памяти"""
    
    print("\n" + "="*70)
    print("ПРОВЕРКА СИСТЕМЫ ПАМЯТИ")
    print("="*70)
    
    try:
        from core.memory_system import MemorySystem
        
        config = {'memory_db_path': 'data/memory_db'}
        memory = MemorySystem(config)
        
        all_data = memory.collection.get()
        total = len(all_data['ids'])
        
        print(f"\n✓ Система памяти работает")
        print(f"✓ Записей в БД: {total}")
        
        if total > 0:
            print(f"✓ Память НЕ пустая - GUI покажет данные!")
        else:
            print("⚠ Память пустая - запустите JARVIS для накопления знаний")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        return False

def main():
    print("="*70)
    print("  ИНТЕГРАЦИЯ РАСШИРЕННОГО GUI С JARVIS")
    print("="*70)
    print()
    print("Этот скрипт:")
    print("1. Добавит запуск GUI в main.py")
    print("2. Свяжет GUI с системой памяти")
    print("3. Настроит обновления в реальном времени")
    print("4. Создаст скрипт запуска")
    print()
    input("Нажмите Enter для продолжения...")
    print()
    
    success = True
    success &= integrate_gui_with_main()
    success &= fix_continuous_learning()
    success &= create_startup_script()
    
    check_memory_system()
    
    print()
    print("="*70)
    if success:
        print("✓ ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("="*70)
        print()
        print("Теперь запустите:")
        print("  python main.py")
        print()
        print("Или используйте удобный скрипт:")
        print("  python start_jarvis_gui.py")
        print()
        print("GUI покажет:")
        print("  ✓ ВСЕ записи в памяти (старые + новые)")
        print("  ✓ Статистику по типам и источникам")
        print("  ✓ Последние 10 записей с содержимым")
        print("  ✓ Real-time обновления при обучении")
        print()
    else:
        print("✗ ОШИБКА ПРИ ИНТЕГРАЦИИ")
        print("="*70)
        print()
        print("Проверьте структуру файлов и повторите")
    
    print()
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
