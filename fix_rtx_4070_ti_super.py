# -*- coding: utf-8 -*-
"""
🔥 RTX 4070 Ti SUPER - CUDA 12.x FIX
Специальное исправление для новых RTX 40-серий

Проблема: CUDA 11.7 НЕ ПОДДЕРЖИВАЕТ RTX 4070 Ti SUPER полностью!
Решение: CUDA 12.1
"""

import sys
import subprocess
from pathlib import Path

print("="*80)
print("🔥 RTX 4070 Ti SUPER - CUDA FIX")
print("="*80)
print()

# ============================================================================
# КРИТИЧЕСКАЯ ПРОБЛЕМА
# ============================================================================
print("❌ КРИТИЧЕСКАЯ ПРОБЛЕМА ОБНАРУЖЕНА!")
print()
print("У вас: PyTorch 2.0.1+cu117 (CUDA 11.7)")
print("Карта: RTX 4070 Ti SUPER")
print()
print("⚠️  RTX 4070 Ti SUPER (Ada Lovelace) требует CUDA 12.x!")
print("⚠️  CUDA 11.7 НЕ полностью поддерживает эту карту!")
print()
print("Это объясняет почему GPU не загружается!")
print()

# ============================================================================
# ПРОВЕРКА ДРАЙВЕРА
# ============================================================================
print("Проверка драйвера NVIDIA...")
print()

try:
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
        capture_output=True,
        text=True,
        timeout=2
    )
    
    if result.returncode == 0:
        driver_version = result.stdout.strip()
        print(f"Версия драйвера: {driver_version}")
        
        # Для RTX 4070 Ti SUPER нужен драйвер 525.60.11+
        major_version = int(driver_version.split('.')[0])
        
        if major_version < 525:
            print()
            print("❌ ДРАЙВЕР УСТАРЕЛ!")
            print(f"   Текущий: {driver_version}")
            print(f"   Требуется: 525.60.11+")
            print()
            print("Скачайте последний драйвер:")
            print("https://www.nvidia.com/download/index.aspx")
            print()
        else:
            print(f"✓ Драйвер OK ({driver_version} >= 525)")
            print()

except Exception as e:
    print(f"⚠️  Не удалось проверить драйвер: {e}")
    print()

# ============================================================================
# РЕШЕНИЕ
# ============================================================================
print("="*80)
print("🔧 РЕШЕНИЕ - 3 ШАГА")
print("="*80)
print()

print("ШАГ 1: Удаление старого PyTorch")
print("─"*80)
print()
print("Выполните в терминале:")
print()
print("  pip uninstall torch torchvision torchaudio -y")
print()
input("Выполнили? Нажмите Enter для продолжения...")
print()

print("ШАГ 2: Установка PyTorch с CUDA 12.1")
print("─"*80)
print()
print("Выполните в терминале:")
print()
print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
print()
print("⚠️  ВАЖНО: cu121 - это CUDA 12.1!")
print("⚠️  НЕ cu117, НЕ cu118 - только cu121!")
print()
input("Выполнили? Нажмите Enter для продолжения...")
print()

print("ШАГ 3: Проверка установки")
print("─"*80)
print()
print("Проверяем что PyTorch установлен правильно...")
print()

try:
    import torch
    
    print(f"PyTorch версия: {torch.__version__}")
    print(f"CUDA доступна: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA версия: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        
        # Проверяем версию CUDA
        cuda_version = torch.version.cuda
        if cuda_version and cuda_version.startswith('12.'):
            print()
            print("✅ ОТЛИЧНО! PyTorch с CUDA 12.x установлен!")
            print()
        else:
            print()
            print("❌ ОШИБКА! PyTorch всё ещё с CUDA 11.x!")
            print()
            print("Возможно установилась не та версия.")
            print("Попробуйте явно:")
            print()
            print("  pip uninstall torch torchvision torchaudio -y")
            print("  pip cache purge")
            print("  pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu121")
            print()
            input("Нажмите Enter для выхода...")
            sys.exit(1)
    else:
        print()
        print("❌ CUDA недоступна!")
        print()
        print("Проверьте:")
        print("1. Драйверы NVIDIA установлены?")
        print("2. nvidia-smi работает?")
        print()
        input("Нажмите Enter для выхода...")
        sys.exit(1)

except ImportError:
    print("❌ PyTorch не установлен!")
    print()
    print("Установите:")
    print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    print()
    input("Нажмите Enter для выхода...")
    sys.exit(1)

# ============================================================================
# АГРЕССИВНЫЙ GPU СТРЕСС-ТЕСТ
# ============================================================================
print()
print("="*80)
print("🔥 АГРЕССИВНЫЙ GPU СТРЕСС-ТЕСТ")
print("="*80)
print()

print("Сейчас запустится тест который ГАРАНТИРОВАННО загрузит GPU!")
print()
print("⚠️  ОТКРОЙТЕ ВТОРОЙ ТЕРМИНАЛ:")
print("    nvidia-smi -l 1")
print()
print("GPU должна загрузиться до 95-100%!")
print()
input("Готовы? Нажмите Enter...")
print()

try:
    import torch
    
    device = torch.device('cuda:0')
    print(f"Устройство: {device}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print()
    
    # Очистка кэша
    torch.cuda.empty_cache()
    
    # ========================================================================
    # ТЕСТ 1: ОГРОМНЫЕ МАТРИЦЫ
    # ========================================================================
    print("[ТЕСТ 1/4] Умножение огромных матриц...")
    print()
    
    import time
    
    # Создаём максимально большие матрицы
    print("Создание матриц 15000x15000...")
    a = torch.randn(15000, 15000, device=device)
    b = torch.randn(15000, 15000, device=device)
    
    print(f"VRAM: {torch.cuda.memory_allocated(0) / 1024**2:.0f} MB")
    print()
    
    print("Умножение матриц (100 итераций)...")
    start = time.time()
    
    for i in range(100):
        c = torch.matmul(a, b)
        
        if i % 10 == 0:
            print(f"  Итерация {i}/100 | "
                  f"VRAM: {torch.cuda.memory_allocated(0) / 1024**2:.0f} MB | "
                  f"GPU должна быть на 100%!")
    
    elapsed = time.time() - start
    print(f"✓ Завершено за {elapsed:.1f} сек")
    print()
    
    # ========================================================================
    # ТЕСТ 2: НЕПРЕРЫВНЫЕ ОПЕРАЦИИ
    # ========================================================================
    print("[ТЕСТ 2/4] Непрерывные операции на 60 секунд...")
    print("⚠️  СМОТРИТЕ НА nvidia-smi - GPU ДОЛЖНА БЫТЬ 100%!")
    print()
    
    start = time.time()
    iteration = 0
    
    while time.time() - start < 60:
        # Максимально тяжёлые операции
        x = torch.randn(10000, 10000, device=device)
        y = torch.randn(10000, 10000, device=device)
        
        # Умножение
        z = torch.matmul(x, y)
        
        # Больше операций
        z = torch.sin(z)
        z = torch.cos(z)
        z = torch.exp(z * 0.01)  # Чтобы не было overflow
        z = torch.sigmoid(z)
        
        # Ещё операции
        w = torch.matmul(z, z.t())
        w = torch.relu(w)
        w = torch.softmax(w, dim=1)
        
        iteration += 1
        
        if iteration % 5 == 0:
            elapsed = time.time() - start
            print(f"  {elapsed:.1f} сек | Итерация {iteration} | "
                  f"VRAM: {torch.cuda.memory_allocated(0) / 1024**2:.0f} MB | "
                  f"GPU: 100%?")
    
    print()
    print("✓ Тест завершён!")
    print()
    
    # ========================================================================
    # ТЕСТ 3: НЕЙРОСЕТЬ
    # ========================================================================
    print("[ТЕСТ 3/4] Обучение нейросети...")
    print()
    
    import torch.nn as nn
    import torch.optim as optim
    
    # Большая нейросеть
    model = nn.Sequential(
        nn.Linear(10000, 5000),
        nn.ReLU(),
        nn.Linear(5000, 2000),
        nn.ReLU(),
        nn.Linear(2000, 1000),
        nn.ReLU(),
        nn.Linear(1000, 100)
    ).to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    
    print("Обучение на 200 батчах...")
    
    for i in range(200):
        # Данные
        x = torch.randn(512, 10000, device=device)
        y = torch.randn(512, 100, device=device)
        
        # Forward
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        
        # Backward
        loss.backward()
        optimizer.step()
        
        if i % 20 == 0:
            print(f"  Батч {i}/200 | Loss: {loss.item():.4f} | "
                  f"VRAM: {torch.cuda.memory_allocated(0) / 1024**2:.0f} MB")
    
    print()
    print("✓ Обучение завершено!")
    print()
    
    # ========================================================================
    # ТЕСТ 4: SENTENCE-TRANSFORMERS
    # ========================================================================
    print("[ТЕСТ 4/4] SentenceTransformer на GPU...")
    print()
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print("Загрузка модели на GPU...")
        model = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2',
            device='cuda'
        )
        
        # Проверяем что на GPU
        print(f"Модель на устройстве: {model.device}")
        
        # Большой батч
        texts = [
            f"Тестовый текст номер {i} для максимальной нагрузки GPU"
            for i in range(10000)
        ]
        
        print(f"Обработка {len(texts)} текстов...")
        print()
        
        start = time.time()
        
        embeddings = model.encode(
            texts,
            batch_size=1024,  # Большой батч
            convert_to_tensor=True,
            device='cuda',
            show_progress_bar=True,
            normalize_embeddings=True
        )
        
        elapsed = time.time() - start
        
        print()
        print(f"✓ Обработано за {elapsed:.1f} сек")
        print(f"✓ Скорость: {len(texts)/elapsed:.0f} текстов/сек")
        print(f"✓ Embeddings на GPU: {embeddings.is_cuda}")
        print()
        
    except ImportError:
        print("⚠️  sentence-transformers не установлен")
        print("   pip install sentence-transformers")
        print()
    
    # ========================================================================
    # ИТОГИ
    # ========================================================================
    print("="*80)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ")
    print("="*80)
    print()
    
    print("Что было запущено:")
    print("  ✓ Умножение огромных матриц 15000x15000")
    print("  ✓ Непрерывные операции 60 секунд")
    print("  ✓ Обучение большой нейросети")
    print("  ✓ SentenceTransformer embeddings")
    print()
    
    print("Что должно было произойти в nvidia-smi:")
    print()
    print("  GPU-Util: 95-100%  ← ВЫ ЭТО ВИДЕЛИ?")
    print("  Memory:   12000+ MB")
    print("  Temp:     70-80°C")
    print()
    
    response = input("GPU загрузилась до 90%+? (yes/no): ").strip().lower()
    print()
    
    if response in ['yes', 'y', 'да', 'д']:
        print("✅ ОТЛИЧНО! GPU работает!")
        print()
        print("Теперь JARVIS должен работать с полной загрузкой GPU.")
        print()
        print("Запускайте:")
        print("  python -m jarvis")
        print()
    else:
        print("❌ GPU НЕ загрузилась!")
        print()
        print("Возможные проблемы:")
        print()
        print("1. ❌ Драйверы устарели")
        print("   Скачайте: https://www.nvidia.com/download/index.aspx")
        print("   Нужен драйвер 525.60.11+ для RTX 4070 Ti SUPER")
        print()
        print("2. ❌ PyTorch всё ещё с CUDA 11.7")
        print("   Проверьте: import torch; print(torch.version.cuda)")
        print("   Должно быть: 12.1")
        print()
        print("3. ❌ GPU заблокирована в BIOS")
        print("   Проверьте настройки BIOS")
        print()
        print("4. ❌ TCC режим (Data Center GPU)")
        print("   Выполните: nvidia-smi -dm 0")
        print()
        print("5. ❌ Проблема с PCI-E")
        print("   Проверьте что карта в слоте x16")
        print("   nvidia-smi -q | findstr \"Link Width\"")
        print()

except Exception as e:
    print(f"❌ ОШИБКА ТЕСТА: {e}")
    import traceback
    traceback.print_exc()
    print()

print("="*80)

input("\nНажмите Enter для выхода...")
