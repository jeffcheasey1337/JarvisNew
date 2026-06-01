# -*- coding: utf-8 -*-
"""
⚡ JARVIS TURBO LEARNING - GPU FORCED
Турбо-обучение с ПРИНУДИТЕЛЬНЫМ использованием GPU
"""

import torch
import torch.nn as nn
import numpy as np
from sentence_transformers import SentenceTransformer
import time

class GPUEmbeddings:
    """GPU Embeddings - ПРИНУДИТЕЛЬНО на CUDA"""
    
    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        print("🔥 Инициализация GPU Embeddings...")
        
        # Проверяем CUDA
        if not torch.cuda.is_available():
            raise RuntimeError("❌ CUDA недоступна! Установите PyTorch с CUDA.")
        
        self.device = torch.device('cuda')
        print(f"  ✓ Устройство: {self.device}")
        print(f"  ✓ GPU: {torch.cuda.get_device_name(0)}")
        
        # Загружаем модель НА GPU
        print(f"  ⏳ Загрузка модели {model_name}...")
        self.model = SentenceTransformer(model_name, device='cuda')
        self.model.to(self.device)
        
        # Устанавливаем eval режим
        self.model.eval()
        
        print(f"  ✓ Модель загружена на GPU")
        
        # Проверяем что модель на GPU
        for param in self.model.parameters():
            if not param.is_cuda:
                raise RuntimeError("❌ Модель не на GPU!")
        
        print("  ✓ Проверка: модель на CUDA")
        
    def encode(self, texts, batch_size=512, show_progress=False):
        """Создание embeddings НА GPU"""
        
        if isinstance(texts, str):
            texts = [texts]
        
        # КРИТИЧНО: convert_to_tensor=True и device='cuda'
        with torch.no_grad():
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_tensor=True,  # ← ВАЖНО!
                device='cuda',            # ← ВАЖНО!
                show_progress_bar=show_progress,
                normalize_embeddings=True
            )
        
        # Проверяем что embeddings на GPU
        if not embeddings.is_cuda:
            raise RuntimeError("❌ Embeddings не на GPU!")
        
        return embeddings
    
    def get_device_info(self):
        """Информация о GPU"""
        return {
            'device': str(self.device),
            'gpu_name': torch.cuda.get_device_name(0),
            'memory_allocated': torch.cuda.memory_allocated(0) / 1024**2,  # MB
            'memory_reserved': torch.cuda.memory_reserved(0) / 1024**2,    # MB
        }


class TurboLearningSystem:
    """Система турбо-обучения с GPU"""
    
    def __init__(self, batch_size=512, num_workers=32):
        print("\n🚀 Инициализация Turbo Learning System...")
        
        self.batch_size = batch_size
        self.num_workers = num_workers
        
        # GPU Embeddings
        self.embeddings = GPUEmbeddings()
        
        print(f"  ✓ Batch size: {batch_size}")
        print(f"  ✓ Workers: {num_workers}")
        
        # Статистика
        self.total_processed = 0
        self.start_time = None
        
        # Включаем все GPU оптимизации
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.enabled = True
        
        print("  ✓ cuDNN оптимизации включены")
        print("\n✅ Turbo система готова!\n")
    
    def learn_batch(self, topics, category="mixed"):
        """Обучение батча НА GPU"""
        
        if not topics:
            return
        
        batch_start = time.time()
        
        # Генерируем embeddings НА GPU
        with torch.cuda.amp.autocast():  # Mixed precision для скорости
            embeddings = self.embeddings.encode(
                topics,
                batch_size=self.batch_size,
                show_progress=False
            )
        
        # Проверяем что на GPU
        if not embeddings.is_cuda:
            raise RuntimeError("❌ Embeddings не на CUDA!")
        
        # Симулируем обработку (в реальности здесь сохранение в векторную БД)
        # Держим данные на GPU для демонстрации нагрузки
        _ = torch.nn.functional.cosine_similarity(
            embeddings.unsqueeze(1),
            embeddings.unsqueeze(0),
            dim=2
        )
        
        batch_time = time.time() - batch_start
        
        self.total_processed += len(topics)
        
        return {
            'processed': len(topics),
            'time': batch_time,
            'speed': len(topics) / batch_time if batch_time > 0 else 0,
            'gpu_memory_mb': torch.cuda.memory_allocated(0) / 1024**2,
        }
    
    def get_stats(self):
        """Статистика обучения"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            speed = self.total_processed / elapsed if elapsed > 0 else 0
        else:
            speed = 0
        
        return {
            'total_processed': self.total_processed,
            'speed': speed,
            'gpu_info': self.embeddings.get_device_info(),
        }


def test_gpu_load():
    """Тест GPU нагрузки"""
    print("="*80)
    print("🔥 ТЕСТ GPU НАГРУЗКИ")
    print("="*80)
    print()
    
    print("Создание большого батча для нагрузки GPU...")
    
    # Создаём турбо-систему
    turbo = TurboLearningSystem(batch_size=512)
    
    # Генерируем тестовые данные
    test_topics = [
        f"тестовая тема номер {i} для проверки GPU нагрузки"
        for i in range(1024)
    ]
    
    print(f"Обработка {len(test_topics)} тем...")
    print()
    
    turbo.start_time = time.time()
    
    # Обрабатываем в батчах
    for i in range(0, len(test_topics), 512):
        batch = test_topics[i:i+512]
        result = turbo.learn_batch(batch)
        
        print(f"Батч {i//512 + 1}:")
        print(f"  Обработано: {result['processed']}")
        print(f"  Время: {result['time']:.3f} сек")
        print(f"  Скорость: {result['speed']:.1f} тем/сек")
        print(f"  GPU Memory: {result['gpu_memory_mb']:.0f} MB")
        print()
    
    stats = turbo.get_stats()
    print("="*80)
    print("ИТОГИ:")
    print(f"  Всего обработано: {stats['total_processed']}")
    print(f"  Средняя скорость: {stats['speed']:.1f} тем/сек")
    print(f"  GPU: {stats['gpu_info']['gpu_name']}")
    print(f"  VRAM: {stats['gpu_info']['memory_allocated']:.0f} MB")
    print("="*80)
    print()
    print("⚠️  ПРОВЕРЬТЕ nvidia-smi - GPU должна быть загружена на 90%+!")


if __name__ == "__main__":
    test_gpu_load()
