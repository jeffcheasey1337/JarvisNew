# -*- coding: utf-8 -*-
"""
Real-time log viewer
"""

import time
import json
from pathlib import Path

def tail_log(filepath, interval=0.1):
    """Просмотр логов в реальном времени"""
    with open(filepath, 'r', encoding='utf-8') as f:
        # Переходим в конец
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                print(line, end='')
            else:
                time.sleep(interval)

def show_live_stats():
    """Показ статистики в реальном времени"""
    stats_file = Path('logs/realtime/live_stats.json')
    
    while True:
        try:
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                
                # Очищаем экран
                print('\033[2J\033[H')
                
                # Показываем статистику
                print("="*80)
                print("📊 LIVE STATS")
                print("="*80)
                print(f"Topics: {stats.get('topics_learned', 0)} / {stats.get('total_topics', 0)}")
                print(f"Speed: {stats.get('topics_per_second', 0):.1f} topics/sec")
                print(f"GPU: {stats.get('gpu_usage', 0):.1f}%")
                print(f"VRAM: {stats.get('gpu_memory', 0):.0f} MB")
                print(f"Temp: {stats.get('gpu_temp', 0):.0f}°C")
                print(f"CPU: {stats.get('cpu_usage', 0):.1f}%")
                print(f"RAM: {stats.get('ram_usage', 0):.1f}%")
                print("="*80)
            
            time.sleep(1)
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'stats':
        show_live_stats()
    else:
        # Tail логов
        log_file = Path('logs/turbo_detailed.log')
        if log_file.exists():
            tail_log(log_file)
        else:
            print("Лог файл не найден. Запустите обучение сначала.")
