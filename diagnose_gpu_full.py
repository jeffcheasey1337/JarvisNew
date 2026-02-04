# -*- coding: utf-8 -*-
"""
🔍 ПОЛНАЯ ДИАГНОСТИКА GPU
Детальная проверка всех аспектов GPU
"""

import subprocess
import sys

print("="*80)
print("🔍 ПОЛНАЯ ДИАГНОСТИКА RTX 4070 Ti SUPER")
print("="*80)
print()

# ============================================================================
# 1. NVIDIA-SMI ДЕТАЛИ
# ============================================================================
print("[1/7] Детальная информация nvidia-smi...")
print()

try:
    result = subprocess.run(['nvidia-smi', '-q'], capture_output=True, text=True, timeout=5)
    
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        
        # Извлекаем важную информацию
        for line in lines:
            if any(keyword in line for keyword in [
                'Product Name',
                'Driver Version',
                'CUDA Version',
                'GPU Current Temp',
                'Performance State',
                'Power Draw',
                'Power Limit',
                'FB Memory Usage',
                'Compute Mode',
                'GPU Clocks',
            ]):
                print(f"  {line.strip()}")
        
        print()
        
        # Проверяем Compute Mode
        compute_mode = None
        for line in lines:
            if 'Compute Mode' in line:
                compute_mode = line.split(':')[1].strip()
                break
        
        if compute_mode and compute_mode != 'Default':
            print(f"⚠️  ВНИМАНИЕ: Compute Mode = {compute_mode}")
            print("   Должно быть: Default")
            print()

except Exception as e:
    print(f"❌ Ошибка: {e}")
    print()

# ============================================================================
# 2. PYTORCH CUDA ДЕТАЛИ
# ============================================================================
print("[2/7] PyTorch и CUDA...")
print()

try:
    import torch
    
    print(f"PyTorch версия: {torch.__version__}")
    print(f"CUDA доступна: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA версия (PyTorch): {torch.version.cuda}")
        print(f"cuDNN версия: {torch.backends.cudnn.version()}")
        print(f"cuDNN enabled: {torch.backends.cudnn.enabled}")
        print(f"Количество GPU: {torch.cuda.device_count()}")
        print()
        
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}:")
            print(f"  Имя: {torch.cuda.get_device_name(i)}")
            print(f"  Capability: {torch.cuda.get_device_capability(i)}")
            print(f"  Total memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.1f} GB")
            print()
        
        # ============================================================
        # КРИТИЧЕСКАЯ ПРОВЕРКА - ВЕРСИЯ CUDA
        # ============================================================
        cuda_version = torch.version.cuda
        
        if cuda_version:
            major = int(cuda_version.split('.')[0])
            
            print("─"*80)
            if major < 12:
                print("❌ КРИТИЧЕСКАЯ ПРОБЛЕМА НАЙДЕНА!")
                print()
                print(f"   CUDA версия: {cuda_version}")
                print("   RTX 4070 Ti SUPER требует: CUDA 12.x")
                print()
                print("   Это объясняет низкую загрузку GPU!")
                print()
                print("РЕШЕНИЕ:")
                print()
                print("1. pip uninstall torch torchvision torchaudio -y")
                print("2. pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
                print()
                print("─"*80)
            else:
                print("✅ CUDA версия OK (12.x)")
                print("─"*80)
        
        print()
    
    else:
        print("❌ CUDA недоступна в PyTorch!")
        print()

except ImportError:
    print("❌ PyTorch не установлен!")
    print()

# ============================================================================
# 3. БЫСТРЫЙ GPU ТЕСТ
# ============================================================================
print("[3/7] Быстрый тест GPU...")
print()

try:
    import torch
    import time
    
    if torch.cuda.is_available():
        device = torch.device('cuda:0')
        
        print("Создание тензоров на GPU...")
        x = torch.randn(5000, 5000, device=device)
        y = torch.randn(5000, 5000, device=device)
        
        print(f"VRAM до операции: {torch.cuda.memory_allocated(0) / 1024**2:.0f} MB")
        
        print("Умножение матриц...")
        start = time.time()
        
        for i in range(10):
            z = torch.matmul(x, y)
        
        elapsed = time.time() - start
        
        print(f"VRAM после операции: {torch.cuda.memory_allocated(0) / 1024**2:.0f} MB")
        print(f"Время: {elapsed:.3f} сек")
        print(f"Скорость: {10/elapsed:.1f} ops/sec")
        print()
        
        # Проверяем что операция была на GPU
        print("✓ Операции выполнены на GPU")
        print()

except Exception as e:
    print(f"❌ Ошибка: {e}")
    print()

# ============================================================================
# 4. ПРОВЕРКА TCC/WDDM РЕЖИМА
# ============================================================================
print("[4/7] Проверка режима GPU (TCC/WDDM)...")
print()

try:
    result = subprocess.run(
        ['nvidia-smi', '-q', '-d', 'COMPUTE'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        if 'WDDM' in result.stdout:
            print("✓ Режим: WDDM (правильно для Windows)")
        elif 'TCC' in result.stdout:
            print("⚠️  Режим: TCC (режим Data Center)")
            print("   Для игровых карт должен быть WDDM")
            print()
            print("Переключите в WDDM:")
            print("  nvidia-smi -dm 0")
            print()
        else:
            print("? Не удалось определить режим")
        
        print()

except Exception as e:
    print(f"⚠️  Не удалось проверить: {e}")
    print()

# ============================================================================
# 5. ПРОВЕРКА PCI-E
# ============================================================================
print("[5/7] Проверка PCI-E подключения...")
print()

try:
    result = subprocess.run(
        ['nvidia-smi', '-q', '-d', 'PCIE'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in [
                'Link Width',
                'Current Link Width',
                'Max Link Width',
                'Link Speed',
                'Current Link Speed',
            ]):
                print(f"  {line.strip()}")
        
        print()
        
        # Проверяем что x16
        if 'x16' not in result.stdout:
            print("⚠️  ВНИМАНИЕ: GPU не в слоте x16!")
            print("   Производительность может быть снижена")
            print()

except Exception as e:
    print(f"⚠️  Не удалось проверить: {e}")
    print()

# ============================================================================
# 6. ПРОВЕРКА ТЕМПЕРАТУРНЫХ ЛИМИТОВ
# ============================================================================
print("[6/7] Проверка температурных лимитов...")
print()

try:
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=temperature.gpu,temperature.gpu.tlimit',
         '--format=csv,noheader'],
        capture_output=True,
        text=True,
        timeout=2
    )
    
    if result.returncode == 0:
        data = result.stdout.strip().split(',')
        current_temp = int(data[0])
        temp_limit = int(data[1]) if len(data) > 1 else 0
        
        print(f"Текущая температура: {current_temp}°C")
        print(f"Температурный лимит: {temp_limit}°C")
        
        if current_temp > temp_limit - 5:
            print()
            print("⚠️  GPU близка к температурному лимиту!")
            print("   Может включаться троттлинг")
            print()
        else:
            print("✓ Температура в норме")
        
        print()

except Exception as e:
    print(f"⚠️  Не удалось проверить: {e}")
    print()

# ============================================================================
# 7. ПРОВЕРКА POWER LIMIT
# ============================================================================
print("[7/7] Проверка лимита мощности...")
print()

try:
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=power.draw,power.limit',
         '--format=csv,noheader,nounits'],
        capture_output=True,
        text=True,
        timeout=2
    )
    
    if result.returncode == 0:
        data = result.stdout.strip().split(',')
        power_draw = float(data[0])
        power_limit = float(data[1])
        
        print(f"Текущая мощность: {power_draw:.1f} W")
        print(f"Лимит мощности: {power_limit:.1f} W")
        print(f"Использование: {power_draw/power_limit*100:.1f}%")
        print()
        
        # RTX 4070 Ti SUPER имеет TDP 285W
        if power_limit < 250:
            print("⚠️  ВНИМАНИЕ: Лимит мощности слишком низкий!")
            print(f"   Текущий: {power_limit:.0f}W")
            print("   Ожидается: 285W для RTX 4070 Ti SUPER")
            print()
            print("Это может ограничивать производительность!")
            print()
        else:
            print("✓ Лимит мощности OK")
            print()

except Exception as e:
    print(f"⚠️  Не удалось проверить: {e}")
    print()

# ============================================================================
# ИТОГИ И РЕКОМЕНДАЦИИ
# ============================================================================
print("="*80)
print("📋 ИТОГИ ДИАГНОСТИКИ")
print("="*80)
print()

print("Проверьте следующее:")
print()

print("1. CUDA версия PyTorch:")
try:
    import torch
    cuda_ver = torch.version.cuda
    if cuda_ver:
        major = int(cuda_ver.split('.')[0])
        if major < 12:
            print(f"   ❌ CUDA {cuda_ver} - СЛИШКОМ СТАРАЯ!")
            print("   ✓ Переустановите PyTorch с CUDA 12.1")
        else:
            print(f"   ✓ CUDA {cuda_ver} - OK")
    else:
        print("   ❌ CUDA версия не определена")
except:
    print("   ❌ PyTorch не установлен")

print()
print("2. Драйвер NVIDIA:")
try:
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
        capture_output=True, text=True, timeout=2
    )
    if result.returncode == 0:
        driver = result.stdout.strip()
        major = int(driver.split('.')[0])
        if major < 525:
            print(f"   ❌ Драйвер {driver} - УСТАРЕЛ!")
            print("   ✓ Обновите до 525.60.11+")
        else:
            print(f"   ✓ Драйвер {driver} - OK")
except:
    print("   ❌ Не удалось проверить")

print()
print("3. Режим GPU:")
print("   Проверьте выше - должен быть WDDM")

print()
print("4. PCI-E:")
print("   Проверьте выше - должно быть x16")

print()
print("5. Лимит мощности:")
print("   Должно быть ~285W для максимальной производительности")

print()
print("="*80)
print()

print("🔥 ГЛАВНАЯ РЕКОМЕНДАЦИЯ:")
print()
print("Если CUDA версия < 12.0:")
print()
print("  pip uninstall torch torchvision torchaudio -y")
print("  pip cache purge")
print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
print()
print("Затем запустите:")
print("  python fix_rtx_4070_ti_super.py")
print()
print("="*80)

input("\nНажмите Enter для выхода...")
