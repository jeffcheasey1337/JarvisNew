# -*- coding: utf-8 -*-
"""
🔥 GPU LOAD TEST
Тест нагрузки GPU - должна быть 90%+
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jarvis.core.learning.turbo import test_gpu_load

if __name__ == "__main__":
    print("="*80)
    print("🔥 ЗАПУСК GPU НАГРУЗОЧНОГО ТЕСТА")
    print("="*80)
    print()
    print("Откройте второй терминал и запустите:")
    print("  nvidia-smi -l 1")
    print()
    print("GPU загрузка должна подняться до 90-95%!")
    print()
    input("Нажмите Enter когда готовы...")
    print()
    
    test_gpu_load()
    
    print()
    print("✅ Тест завершён!")
    print()
    print("Если GPU была загружена на 90%+ - всё работает!")
    print("Если GPU была загружена на 2% - есть проблема с PyTorch/CUDA")
    print()
    input("Нажмите Enter для выхода...")
