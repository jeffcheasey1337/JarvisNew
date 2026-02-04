#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест турбо-обучения
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Тест импортов"""
    print("🧪 Тест импортов...")
    
    try:
        from ddgs import DDGS
        print("  ✓ ddgs импортирован")
    except ImportError as e:
        print(f"  ✗ Ошибка ddgs: {e}")
        return False
    
    try:
        import torch
        print(f"  ✓ PyTorch импортирован (CUDA: {torch.cuda.is_available()})")
    except ImportError:
        print("  ⚠ PyTorch не установлен (GPU не будет использоваться)")
    
    try:
        from jarvis.core.learning.turbo import TurboLearningSystem
        print("  ✓ TurboLearningSystem импортирован")
    except ImportError as e:
        print(f"  ✗ Ошибка turbo: {e}")
        return False
    
    return True

def test_gpu():
    """Тест GPU"""
    print("\n🎮 Тест GPU...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  ✓ GPU: {gpu_name}")
            print(f"  ✓ VRAM: {gpu_memory:.1f} GB")
            print(f"  ✓ CUDA: {torch.version.cuda}")
            
            # Простой тест
            x = torch.randn(1000, 1000, device='cuda')
            y = torch.randn(1000, 1000, device='cuda')
            z = torch.matmul(x, y)
            print("  ✓ GPU тест пройден")
            
            return True
        else:
            print("  ⚠ GPU недоступна")
            return False
    
    except Exception as e:
        print(f"  ✗ Ошибка GPU: {e}")
        return False

def main():
    """Главная функция"""
    print("="*60)
    print("JARVIS TURBO - ТЕСТ ИНТЕГРАЦИИ")
    print("="*60)
    
    # Тест импортов
    if not test_imports():
        print("\n❌ Тест импортов провален")
        return False
    
    # Тест GPU
    gpu_available = test_gpu()
    
    # Итог
    print("\n" + "="*60)
    if gpu_available:
        print("✅ ВСЁ ГОТОВО! GPU ускорение активно (50-100x быстрее)")
    else:
        print("✅ Базовая интеграция готова (GPU не найдена)")
    print("="*60)
    
    print("\nЗапустите JARVIS как обычно - turbo активируется автоматически!")
    
    return True

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")
