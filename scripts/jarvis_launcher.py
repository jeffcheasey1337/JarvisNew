#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 JARVIS Launcher Menu
Меню для запуска различных компонентов
"""

import sys
from pathlib import Path

def show_menu():
    """Показать меню"""
    print("="*60)
    print("🤖 JARVIS - Launcher Menu")
    print("="*60)
    print()
    print("Выберите действие:")
    print()
    print("1. 🚀 Запустить JARVIS")
    print("2. 📊 Открыть Dashboard (графики обучения)")
    print("3. 🧪 Тест системы")
    print("4. ⚙️  Настройки")
    print("5. 📚 Посмотреть темы обучения")
    print("6. ❌ Выход")
    print()
    
    choice = input("Ваш выбор (1-6): ").strip()
    
    return choice

def launch_jarvis():
    """Запуск JARVIS"""
    print("\n🚀 Запуск JARVIS...\n")
    from jarvis.assistant import JarvisAssistant
    import asyncio
    
    assistant = JarvisAssistant()
    asyncio.run(assistant.run())

def launch_dashboard():
    """Запуск Dashboard"""
    print("\n📊 Запуск Learning Dashboard...\n")
    try:
        from jarvis.gui.learning_dashboard import launch_visualization
        launch_visualization()
    except ImportError:
        print("❌ Ошибка: learning_dashboard не найден")
        print("Запустите: python auto_integrate_complete.py")

def run_tests():
    """Запуск тестов"""
    print("\n🧪 Запуск тестов...\n")
    try:
        from test_turbo_integration import main as test_main
        test_main()
    except ImportError:
        print("❌ Тесты не найдены")

def show_topics():
    """Показать темы"""
    print("\n📚 База тем для обучения:\n")
    try:
        from jarvis.core.learning.topics_database import get_topics_count, get_random_topics
        
        total = get_topics_count()
        print(f"Всего тем: {total}")
        print(f"\nПримеры тем:")
        
        for topic in get_random_topics(15):
            print(f"  • {topic}")
        
        print(f"\n... и ещё {total - 15} тем!")
    except ImportError:
        print("❌ База тем не найдена")

def main():
    """Главная функция"""
    while True:
        choice = show_menu()
        
        if choice == '1':
            launch_jarvis()
        elif choice == '2':
            launch_dashboard()
        elif choice == '3':
            run_tests()
        elif choice == '4':
            print("\n⚙️ Настройки в разработке...")
            input("Нажмите Enter...")
        elif choice == '5':
            show_topics()
            input("\nНажмите Enter...")
        elif choice == '6':
            print("\n👋 До свидания!")
            sys.exit(0)
        else:
            print("\n❌ Неверный выбор!")
            input("Нажмите Enter...")

if __name__ == "__main__":
    main()
