# -*- coding: utf-8 -*-
"""
Исправление предупреждения RuntimeWarning в task_manager.py
Заменяет asyncio.sleep(60) на time.sleep(60) в потоке
"""

import sys
import os

def fix_task_manager():
    """Исправление task_manager.py"""
    
    print("="*70)
    print("ИСПРАВЛЕНИЕ TASK_MANAGER.PY")
    print("="*70)
    print()
    print("Проблема: asyncio.sleep(60) без await в обычной функции")
    print("Решение: Заменить на time.sleep(60)")
    print()
    
    file_path = 'modules/task_manager.py'
    
    if not os.path.exists(file_path):
        print(f"[ОШИБКА] Файл не найден: {file_path}")
        return False
    
    # Читаем файл
    print(f"[1/3] Чтение {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие проблемы
    if 'asyncio.sleep(60)' not in content:
        print("[OK] Проблема уже исправлена или не найдена")
        return True
    
    print("[НАЙДЕНО] asyncio.sleep(60) в коде")
    
    # Исправляем
    print("[2/3] Применение исправления...")
    
    # Заменяем asyncio.sleep на time.sleep
    old_code = 'asyncio.sleep(60)'
    new_code = 'time.sleep(60)'
    
    content = content.replace(old_code, new_code)
    
    # Проверяем, что import time есть
    if 'import time' not in content:
        # Добавляем import после других импортов
        import_pos = content.find('import schedule')
        if import_pos != -1:
            # Найти конец строки
            end_line = content.find('\n', import_pos)
            # Вставить import time после
            content = content[:end_line+1] + 'import time\n' + content[end_line+1:]
            print("[ДОБАВЛЕНО] import time")
    
    print(f"[ИСПРАВЛЕНО] {old_code} -> {new_code}")
    
    # Сохраняем
    print("[3/3] Сохранение файла...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[ГОТОВО] Файл исправлен и сохранён")
    return True

def verify_fix():
    """Проверка исправления"""
    print()
    print("="*70)
    print("ПРОВЕРКА ИСПРАВЛЕНИЯ")
    print("="*70)
    print()
    
    file_path = 'modules/task_manager.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'import time': 'import time' in content,
        'time.sleep(60)': 'time.sleep(60)' in content,
        'asyncio.sleep(60) удалён': 'asyncio.sleep(60)' not in content
    }
    
    all_ok = True
    for check, result in checks.items():
        status = "[OK]" if result else "[ОШИБКА]"
        print(f"  {status} {check}")
        if not result:
            all_ok = False
    
    print()
    if all_ok:
        print("[УСПЕХ] Все проверки пройдены!")
        print()
        print("Предупреждение RuntimeWarning больше не появится.")
    else:
        print("[ПРОБЛЕМА] Некоторые проверки не прошли")
    
    return all_ok

def main():
    print("="*70)
    print("  ИСПРАВЛЕНИЕ RUNTIME WARNING В TASK_MANAGER")
    print("="*70)
    print()
    print("Это исправит предупреждение:")
    print('  "RuntimeWarning: coroutine \'sleep\' was never awaited"')
    print()
    input("Нажмите Enter для продолжения...")
    print()
    
    success = fix_task_manager()
    
    if success:
        verify_fix()
    
    print()
    print("="*70)
    if success:
        print("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
        print("="*70)
        print()
        print("Теперь можно запускать JARVIS без предупреждений:")
        print("  python main.py")
    else:
        print("ОШИБКА")
        print("="*70)
    
    print()
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
