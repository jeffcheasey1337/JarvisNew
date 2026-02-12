"""
Интерактивный Dashboard для мониторинга Full Web Learning
Показывает статус каждого потока в реальном времени
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict


class LearningDashboard:
    """Real-time dashboard для мониторинга обучения"""
    
    def __init__(self, full_web_learning):
        self.fwl = full_web_learning
        self.running = False
        self.dashboard_thread = None
        
        # Статистика по потокам
        self.thread_stats = defaultdict(lambda: {
            'current_topic': 'Ожидание...',
            'status': 'idle',
            'topics_done': 0,
            'last_update': datetime.now(),
            'speed': 0.0,
            'errors': 0
        })
        
        self.start_time = datetime.now()
    
    def update_thread_status(self, thread_id, topic, status):
        """Обновление статуса потока"""
        stats = self.thread_stats[thread_id]
        stats['current_topic'] = topic
        stats['status'] = status
        stats['last_update'] = datetime.now()
        
        if status == 'completed':
            stats['topics_done'] += 1
        elif status == 'error':
            stats['errors'] += 1
    
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_progress_bar(self, current, total, width=40):
        """Генерация прогресс-бара"""
        if total == 0:
            return '░' * width
        
        filled = int(width * current / total)
        bar = '█' * filled + '░' * (width - filled)
        percent = (current / total * 100)
        return f"{bar} {percent:.1f}%"
    
    def get_status_emoji(self, status):
        """Эмодзи для статуса"""
        emojis = {
            'idle': '⏸️',
            'searching': '🔍',
            'parsing': '📄',
            'saving': '💾',
            'completed': '✅',
            'error': '❌',
            'timeout': '⏱️'
        }
        return emojis.get(status, '❓')
    
    def format_time(self, seconds):
        """Форматирование времени"""
        if seconds < 60:
            return f"{int(seconds)}с"
        elif seconds < 3600:
            return f"{int(seconds // 60)}м {int(seconds % 60)}с"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}ч {minutes}м"
    
    def render(self):
        """Отрисовка dashboard"""
        self.clear_screen()
        
        # Заголовок
        print("╔" + "═" * 98 + "╗")
        print("║" + " " * 30 + "🚀 JARVIS FULL WEB LEARNING 🚀" + " " * 37 + "║")
        print("╚" + "═" * 98 + "╝")
        print()
        
        # Общая статистика
        elapsed = (datetime.now() - self.start_time).total_seconds()
        total_topics = len(self.fwl.topic_queue) + len(self.fwl.studied_topics)
        studied = len(self.fwl.studied_topics)
        
        speed = (studied / (elapsed / 60)) if elapsed > 0 else 0
        eta_seconds = ((total_topics - studied) / speed * 60) if speed > 0 else 0
        
        print("┌─────────────────────────────────── ОБЩАЯ СТАТИСТИКА ───────────────────────────────────┐")
        print(f"│ Время работы: {self.format_time(elapsed):>15} │ Скорость: {speed:>6.1f} тем/мин │ ETA: {self.format_time(eta_seconds):>12} │")
        print(f"│ Изучено тем:  {studied:>15,} │ Осталось: {len(self.fwl.topic_queue):>12,} │ Всего: {total_topics:>10,} │")
        
        # Прогресс бар
        progress_bar = self.get_progress_bar(studied, total_topics, width=85)
        print(f"│ Прогресс:     {progress_bar} │")
        print(f"│ В памяти:     {self.fwl.stats['memory_records_added']:>15,} записей │ Страниц: {self.fwl.stats['pages_crawled']:>9,} │ Доменов: {self.fwl.stats['sources_collected']:>6} │")
        print("└─────────────────────────────────────────────────────────────────────────────────────────┘")
        print()
        
        # Статус потоков
        print("┌──────────────────────────────────── ПОТОКИ ({} активных) ────────────────────────────────┐".format(self.fwl.num_workers))
        print("│ ID │ Статус │ Текущая тема                                    │ Выполнено │ Ошибки │ Время  │")
        print("├────┼────────┼─────────────────────────────────────────────────┼───────────┼────────┼────────┤")
        
        for thread_id in range(self.fwl.num_workers):
            stats = self.thread_stats[thread_id]
            
            # Форматирование
            status_emoji = self.get_status_emoji(stats['status'])
            topic_display = stats['current_topic'][:48]
            if len(stats['current_topic']) > 48:
                topic_display = topic_display[:45] + "..."
            
            elapsed_thread = (datetime.now() - stats['last_update']).total_seconds()
            time_display = self.format_time(elapsed_thread)
            
            # Цвет статуса (через ANSI если терминал поддерживает)
            status_color = ""
            reset_color = ""
            
            if stats['status'] == 'searching':
                status_color = "\033[93m"  # Yellow
                reset_color = "\033[0m"
            elif stats['status'] == 'completed':
                status_color = "\033[92m"  # Green
                reset_color = "\033[0m"
            elif stats['status'] == 'error':
                status_color = "\033[91m"  # Red
                reset_color = "\033[0m"
            
            print(f"│ {thread_id:>2} │ {status_color}{status_emoji} {stats['status']:<6}{reset_color} │ {topic_display:<48} │ {stats['topics_done']:>9} │ {stats['errors']:>6} │ {time_display:>6} │")
        
        print("└─────────────────────────────────────────────────────────────────────────────────────────┘")
        print()
        
        # Последние события
        print("┌───────────────────────────────── ПОСЛЕДНИЕ СОБЫТИЯ ────────────────────────────────────┐")
        
        # Топ-5 последних изученных тем
        recent_topics = list(self.fwl.studied_topics)[-5:]
        if recent_topics:
            print("│ Недавно изучено:                                                                      │")
            for i, topic in enumerate(reversed(recent_topics), 1):
                print(f"│   {i}. {topic[:80]:<80} │")
        else:
            print("│ Пока нет изученных тем...                                                             │")
        
        print("└─────────────────────────────────────────────────────────────────────────────────────────┘")
        print()
        
        # Подсказки
        print("💡 Нажмите Ctrl+C для выхода из dashboard (обучение продолжится в фоне)")
        print("🔄 Обновление каждые 2 секунды...")
    
    def start(self):
        """Запуск dashboard"""
        self.running = True
        self.start_time = datetime.now()
        
        def dashboard_loop():
            while self.running:
                try:
                    self.render()
                    time.sleep(2)  # Обновление каждые 2 секунды
                except KeyboardInterrupt:
                    print("\n\n✅ Dashboard закрыт. Обучение продолжается в фоне...\n")
                    self.running = False
                    break
                except Exception as e:
                    print(f"\n❌ Ошибка dashboard: {e}\n")
                    time.sleep(5)
        
        self.dashboard_thread = threading.Thread(target=dashboard_loop, daemon=True)
        self.dashboard_thread.start()
        
        print("✅ Dashboard запущен! Открываю интерфейс...")
        time.sleep(1)
    
    def stop(self):
        """Остановка dashboard"""
        self.running = False
        if self.dashboard_thread:
            self.dashboard_thread.join(timeout=3)


class ThreadAwareLearning:
    """Wrapper для отслеживания статуса потоков"""
    
    def __init__(self, original_learning, dashboard):
        self.original = original_learning
        self.dashboard = dashboard
        self.thread_mapping = {}
    
    def learn_topic_with_tracking(self, topic, thread_id):
        """Обёртка над learn_topic с отслеживанием"""
        try:
            # Начало поиска
            self.dashboard.update_thread_status(thread_id, topic, 'searching')
            
            # Вызов оригинального метода
            result = self.original.learn_topic(topic)
            
            # Успех
            if result:
                self.dashboard.update_thread_status(thread_id, topic, 'completed')
            else:
                self.dashboard.update_thread_status(thread_id, topic, 'idle')
            
            return result
            
        except Exception as e:
            self.dashboard.update_thread_status(thread_id, topic, 'error')
            raise


def integrate_dashboard(full_web_learning):
    """
    Интеграция dashboard в Full Web Learning
    
    Использование:
        from learning_dashboard import integrate_dashboard
        
        # После создания full_web_learning
        dashboard = integrate_dashboard(full_web_learning)
        dashboard.start()
    """
    
    dashboard = LearningDashboard(full_web_learning)
    
    # Патчим метод обучения для отслеживания
    original_start = full_web_learning.start_learning
    
    def start_with_dashboard():
        """Запуск с dashboard"""
        dashboard.start()
        original_start()
    
    full_web_learning.start_learning_with_dashboard = start_with_dashboard
    
    return dashboard


if __name__ == "__main__":
    print("🎯 Learning Dashboard Module")
    print("Импортируйте и используйте integrate_dashboard() в вашем коде")
