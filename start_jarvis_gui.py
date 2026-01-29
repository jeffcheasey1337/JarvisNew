# -*- coding: utf-8 -*-
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
        print("\n\nЗавершение работы JARVIS...")
        print("До свидания, сэр.")
