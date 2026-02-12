"""
JARVIS GUI v2 - Расширенный интерфейс с полной диагностикой
Показывает ВСЮ информацию о памяти, обучении и системах
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
import queue
import random
import os
import json


class JarvisGUIExtended:
    """Расширенный графический интерфейс JARVIS"""
    
    def __init__(self, jarvis_instance=None):
        self.jarvis = jarvis_instance
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S - РАСШИРЕННЫЙ СИСТЕМНЫЙ ИНТЕРФЕЙС")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#0a0e27')
        
        # Очереди для обновлений
        self.log_queue = queue.Queue()
        self.stats_queue = queue.Queue()
        
        # Данные для мониторинга
        self.system_status = {
            'speech_recognition': 'STANDBY',
            'speech_synthesis': 'READY',
            'nlp_processor': 'ACTIVE',
            'memory_system': 'ONLINE',
            'learning_system': 'TRAINING',
            'continuous_learning': 'RUNNING',
            'task_manager': 'IDLE',
            'network': 'CONNECTED'
        }
        
        self.stats = {
            'uptime': 0,
            'commands_processed': 0,
            'words_spoken': 0,
            'tasks_completed': 0,
            'articles_learned': 0,
            'memory_items': 0,
            'cpu_usage': 0,
            'gpu_usage': 0
        }
        
        # Детальная информация о памяти
        self.memory_details = {
            'total_records': 0,
            'by_type': {},
            'by_source': {},
            'recent_records': [],
            'db_size_mb': 0,
            'db_path': 'data/memory_db'
        }
        
        self.activities = []
        
        self._create_ui()
        self._start_animation()
        self._start_update_loop()
        self._start_memory_analyzer()
    
    def _create_ui(self):
        """Создание пользовательского интерфейса"""
        
        # Заголовок
        header = tk.Frame(self.root, bg='#0a0e27', height=70)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        title = tk.Label(
            header,
            text="J.A.R.V.I.S",
            font=('Orbitron', 32, 'bold'),
            fg='#00d4ff',
            bg='#0a0e27'
        )
        title.pack(side=tk.LEFT, padx=20)
        
        subtitle = tk.Label(
            header,
            text="Extended Diagnostic Interface",
            font=('Consolas', 11),
            fg='#0088ff',
            bg='#0a0e27'
        )
        subtitle.pack(side=tk.LEFT, padx=10)
        
        # Время
        self.time_label = tk.Label(
            header,
            text="",
            font=('Consolas', 12),
            fg='#00ff88',
            bg='#0a0e27'
        )
        self.time_label.pack(side=tk.RIGHT, padx=20)
        
        # Главный контейнер с вкладками
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Настройка стиля для вкладок
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#0a0e27', borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#0f1535',
                       foreground='#00d4ff',
                       padding=[20, 10],
                       font=('Orbitron', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', '#1a2550')],
                 foreground=[('selected', '#00ff88')])
        
        # Вкладка 1: Обзор
        overview_tab = self._create_overview_tab()
        notebook.add(overview_tab, text='  ОБЗОР  ')
        
        # Вкладка 2: Память (детально!)
        memory_tab = self._create_memory_tab()
        notebook.add(memory_tab, text='  ПАМЯТЬ  ')
        
        # Вкладка 3: Обучение
        learning_tab = self._create_learning_tab()
        notebook.add(learning_tab, text='  ОБУЧЕНИЕ  ')
        
        # Вкладка 4: Логи
        logs_tab = self._create_logs_tab()
        notebook.add(logs_tab, text='  АКТИВНОСТЬ  ')
    
    def _create_overview_tab(self):
        """Вкладка обзора - главная информация"""
        frame = tk.Frame(self.root, bg='#0a0e27')
        
        # Верхняя часть - статусы
        top_frame = tk.Frame(frame, bg='#0a0e27')
        top_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - статусы систем
        left = self._create_status_panel(top_frame)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Правая панель - статистика
        right = self._create_stats_panel(top_frame)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Нижняя часть - текущая операция
        bottom_frame = tk.Frame(frame, bg='#0f1535', highlightbackground='#00d4ff', highlightthickness=2)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(
            bottom_frame,
            text="ТЕКУЩАЯ ОПЕРАЦИЯ:",
            font=('Consolas', 11, 'bold'),
            fg='#ffaa00',
            bg='#0f1535'
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        self.current_operation = tk.Label(
            bottom_frame,
            text="Инициализация систем...",
            font=('Consolas', 12),
            fg='#ffffff',
            bg='#0f1535',
            wraplength=800,
            justify=tk.LEFT
        )
        self.current_operation.pack(anchor=tk.W, padx=10, pady=10)
        
        return frame
    
    def _create_memory_tab(self):
        """Вкладка ДЕТАЛЬНОЙ информации о памяти"""
        frame = tk.Frame(self.root, bg='#0a0e27')
        
        # Заголовок
        header = tk.Label(
            frame,
            text="ПОЛНАЯ ДИАГНОСТИКА ПАМЯТИ",
            font=('Orbitron', 18, 'bold'),
            fg='#00d4ff',
            bg='#0a0e27'
        )
        header.pack(pady=10)
        
        # Контейнер для информации
        info_container = tk.Frame(frame, bg='#0a0e27')
        info_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Левая часть - статистика
        left_panel = tk.Frame(info_container, bg='#0f1535', 
                             highlightbackground='#00d4ff', highlightthickness=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(
            left_panel,
            text="ОБЩАЯ СТАТИСТИКА",
            font=('Orbitron', 14, 'bold'),
            fg='#00d4ff',
            bg='#0f1535'
        ).pack(pady=10)
        
        # Информация о памяти
        self.memory_info_text = scrolledtext.ScrolledText(
            left_panel,
            font=('Consolas', 10),
            bg='#000000',
            fg='#00ff88',
            insertbackground='#00ff88',
            state='disabled',
            wrap=tk.WORD,
            height=25
        )
        self.memory_info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Правая часть - последние записи
        right_panel = tk.Frame(info_container, bg='#0f1535',
                              highlightbackground='#00d4ff', highlightthickness=2)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(
            right_panel,
            text="ПОСЛЕДНИЕ ЗАПИСИ В ПАМЯТИ",
            font=('Orbitron', 14, 'bold'),
            fg='#00d4ff',
            bg='#0f1535'
        ).pack(pady=10)
        
        self.recent_records_text = scrolledtext.ScrolledText(
            right_panel,
            font=('Consolas', 9),
            bg='#000000',
            fg='#ffffff',
            insertbackground='#ffffff',
            state='disabled',
            wrap=tk.WORD,
            height=25
        )
        self.recent_records_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопка обновления
        btn_frame = tk.Frame(frame, bg='#0a0e27')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        refresh_btn = tk.Button(
            btn_frame,
            text="ОБНОВИТЬ АНАЛИЗ ПАМЯТИ",
            font=('Orbitron', 11, 'bold'),
            fg='#000000',
            bg='#00ff88',
            activebackground='#00ff88',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self._manual_memory_refresh,
            cursor='hand2'
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            btn_frame,
            text="ОЧИСТИТЬ ПАМЯТЬ",
            font=('Orbitron', 11, 'bold'),
            fg='#000000',
            bg='#ff4444',
            activebackground='#ff4444',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self._clear_memory_warning,
            cursor='hand2'
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def _create_learning_tab(self):
        """Вкладка обучения"""
        frame = tk.Frame(self.root, bg='#0a0e27')
        
        # Заголовок
        header = tk.Label(
            frame,
            text="НЕПРЕРЫВНОЕ ОБУЧЕНИЕ 24/7",
            font=('Orbitron', 18, 'bold'),
            fg='#00d4ff',
            bg='#0a0e27'
        )
        header.pack(pady=10)
        
        # Статистика обучения
        stats_frame = tk.Frame(frame, bg='#0f1535',
                              highlightbackground='#00d4ff', highlightthickness=2)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.learning_stats_text = scrolledtext.ScrolledText(
            stats_frame,
            font=('Consolas', 11),
            bg='#000000',
            fg='#00ff88',
            insertbackground='#00ff88',
            state='disabled',
            wrap=tk.WORD
        )
        self.learning_stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Управление скоростью
        control_frame = tk.Frame(frame, bg='#0a0e27')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            control_frame,
            text="СКОРОСТЬ ОБУЧЕНИЯ:",
            font=('Orbitron', 12, 'bold'),
            fg='#00d4ff',
            bg='#0a0e27'
        ).pack(side=tk.LEFT, padx=10)
        
        speeds = ['SLOW', 'NORMAL', 'FAST', 'TURBO']
        for speed in speeds:
            btn = tk.Button(
                control_frame,
                text=speed,
                font=('Orbitron', 10, 'bold'),
                fg='#000000',
                bg='#00ff88' if speed == 'NORMAL' else '#0088ff',
                relief=tk.FLAT,
                padx=15,
                pady=8,
                command=lambda s=speed: self._change_learning_speed(s),
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def _create_logs_tab(self):
        """Вкладка логов активности"""
        frame = tk.Frame(self.root, bg='#0a0e27')
        
        # Заголовок
        header = tk.Label(
            frame,
            text="АКТИВНОСТЬ В РЕАЛЬНОМ ВРЕМЕНИ",
            font=('Orbitron', 18, 'bold'),
            fg='#00d4ff',
            bg='#0a0e27'
        )
        header.pack(pady=10)
        
        # Лог
        log_frame = tk.Frame(frame, bg='#0f1535',
                            highlightbackground='#00d4ff', highlightthickness=2)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.activity_log = scrolledtext.ScrolledText(
            log_frame,
            font=('Consolas', 10),
            bg='#000000',
            fg='#00ff00',
            insertbackground='#00ff00',
            state='disabled',
            wrap=tk.WORD
        )
        self.activity_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки управления
        btn_frame = tk.Frame(frame, bg='#0a0e27')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        clear_log_btn = tk.Button(
            btn_frame,
            text="ОЧИСТИТЬ ЛОГ",
            font=('Orbitron', 10, 'bold'),
            fg='#000000',
            bg='#ffaa00',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._clear_log,
            cursor='hand2'
        )
        clear_log_btn.pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def _create_status_panel(self, parent):
        """Панель статусов систем"""
        frame = tk.Frame(parent, bg='#0f1535', 
                        highlightbackground='#00d4ff', highlightthickness=2)
        
        tk.Label(
            frame,
            text="СТАТУС СИСТЕМ",
            font=('Orbitron', 14, 'bold'),
            fg='#00d4ff',
            bg='#0f1535'
        ).pack(pady=10)
        
        status_container = tk.Frame(frame, bg='#0f1535')
        status_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_labels = {}
        for system, status in self.system_status.items():
            self._create_status_row(status_container, system, status)
        
        return frame
    
    def _create_stats_panel(self, parent):
        """Панель статистики"""
        frame = tk.Frame(parent, bg='#0f1535',
                        highlightbackground='#00d4ff', highlightthickness=2)
        
        tk.Label(
            frame,
            text="СТАТИСТИКА",
            font=('Orbitron', 14, 'bold'),
            fg='#00d4ff',
            bg='#0f1535'
        ).pack(pady=10)
        
        stats_container = tk.Frame(frame, bg='#0f1535')
        stats_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.stats_labels = {}
        
        stats_display = [
            ('Время работы', 'uptime', 'ч'),
            ('Команд обработано', 'commands_processed', ''),
            ('Слов произнесено', 'words_spoken', ''),
            ('Задач выполнено', 'tasks_completed', ''),
            ('Статей изучено', 'articles_learned', ''),
            ('Записей в памяти', 'memory_items', ''),
            ('CPU нагрузка', 'cpu_usage', '%'),
            ('GPU нагрузка', 'gpu_usage', '%')
        ]
        
        for label, key, unit in stats_display:
            self._create_stat_row(stats_container, label, key, unit)
        
        return frame
    
    def _create_status_row(self, parent, system, status):
        """Создание строки статуса"""
        row = tk.Frame(parent, bg='#0f1535')
        row.pack(fill=tk.X, pady=3)
        
        name = system.replace('_', ' ').upper()
        tk.Label(
            row,
            text=name,
            font=('Consolas', 9),
            fg='#ffffff',
            bg='#0f1535',
            width=22,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        indicator = tk.Canvas(row, width=12, height=12, bg='#0f1535', highlightthickness=0)
        indicator.pack(side=tk.LEFT, padx=5)
        
        color = self._get_status_color(status)
        indicator.create_oval(2, 2, 11, 11, fill=color, outline=color)
        
        status_label = tk.Label(
            row,
            text=status,
            font=('Consolas', 9, 'bold'),
            fg=color,
            bg='#0f1535',
            width=10,
            anchor=tk.W
        )
        status_label.pack(side=tk.LEFT)
        
        self.status_labels[system] = (indicator, status_label)
    
    def _create_stat_row(self, parent, label, key, unit):
        """Создание строки статистики"""
        row = tk.Frame(parent, bg='#0f1535')
        row.pack(fill=tk.X, pady=4)
        
        tk.Label(
            row,
            text=label + ":",
            font=('Consolas', 9),
            fg='#aaaaaa',
            bg='#0f1535',
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        value_label = tk.Label(
            row,
            text=f"0 {unit}",
            font=('Consolas', 11, 'bold'),
            fg='#00ff88',
            bg='#0f1535',
            anchor=tk.E
        )
        value_label.pack(side=tk.RIGHT)
        
        self.stats_labels[key] = (value_label, unit)
    
    def _get_status_color(self, status):
        """Получение цвета для статуса"""
        colors = {
            'ONLINE': '#00ff00',
            'ACTIVE': '#00ff00',
            'READY': '#00ff88',
            'RUNNING': '#00ff88',
            'TRAINING': '#ffaa00',
            'IDLE': '#ffaa00',
            'STANDBY': '#ffaa00',
            'CONNECTED': '#00ff00',
            'OFFLINE': '#ff0000',
            'ERROR': '#ff0000'
        }
        return colors.get(status, '#888888')
    
    def _start_animation(self):
        """Запуск анимаций"""
        def animate_time():
            while True:
                current_time = datetime.now().strftime("%H:%M:%S | %d.%m.%Y")
                self.time_label.config(text=current_time)
                time.sleep(1)
        
        threading.Thread(target=animate_time, daemon=True).start()
    
    def _start_update_loop(self):
        """Запуск цикла обновления"""
        def update():
            try:
                while True:
                    msg = self.log_queue.get_nowait()
                    self._add_log_message(msg)
            except queue.Empty:
                pass
            
            try:
                while True:
                    stats = self.stats_queue.get_nowait()
                    self._update_stats(stats)
            except queue.Empty:
                pass
            
            if not self.jarvis:
                self._simulate_activity()
            else:
                self._update_real_data()
            
            self.root.after(500, update)
        
        update()
    
    def _start_memory_analyzer(self):
        """Запуск анализа памяти в фоне"""
        def analyze():
            while True:
                try:
                    self._analyze_memory()
                    time.sleep(10)  # Обновление каждые 10 секунд
                except Exception as e:
                    print(f"Error in memory analyzer: {e}")
                    time.sleep(30)
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _analyze_memory(self):
        """Детальный анализ памяти"""
        try:
            if not self.jarvis or not hasattr(self.jarvis, 'memory_system'):
                return
            
            memory = self.jarvis.memory_system
            all_data = memory.collection.get()
            
            total = len(all_data['ids'])
            self.memory_details['total_records'] = total
            
            # Подсчет по типам и источникам
            by_type = {}
            by_source = {}
            recent = []
            
            for i, metadata in enumerate(all_data['metadatas']):
                mem_type = metadata.get('type', 'unknown')
                by_type[mem_type] = by_type.get(mem_type, 0) + 1
                
                source = metadata.get('source', 'unknown')
                by_source[source] = by_source.get(source, 0) + 1
                
                if i >= total - 10:  # Последние 10
                    recent.append({
                        'id': all_data['ids'][i],
                        'content': all_data['documents'][i],
                        'metadata': metadata
                    })
            
            self.memory_details['by_type'] = by_type
            self.memory_details['by_source'] = by_source
            self.memory_details['recent_records'] = recent
            
            # Размер БД
            db_path = self.memory_details['db_path']
            if os.path.exists(db_path):
                total_size = sum(
                    os.path.getsize(os.path.join(root, file))
                    for root, dirs, files in os.walk(db_path)
                    for file in files
                )
                self.memory_details['db_size_mb'] = total_size / (1024 * 1024)
            
            # Обновление GUI
            self._update_memory_display()
            
        except Exception as e:
            print(f"Error analyzing memory: {e}")
    
    def _update_memory_display(self):
        """Обновление отображения памяти"""
        try:
            # Обновление общей информации
            self.memory_info_text.config(state='normal')
            self.memory_info_text.delete('1.0', tk.END)
            
            info = f"""
╔══════════════════════════════════════════╗
║     БАЗА ДАННЫХ ПАМЯТИ JARVIS            ║
╚══════════════════════════════════════════╝

📊 ОБЩАЯ ИНФОРМАЦИЯ:
   • Всего записей: {self.memory_details['total_records']}
   • Размер на диске: {self.memory_details['db_size_mb']:.2f} MB
   • Путь: {self.memory_details['db_path']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 ПО ТИПАМ ПАМЯТИ:
"""
            
            for mem_type, count in sorted(self.memory_details['by_type'].items(), 
                                         key=lambda x: x[1], reverse=True):
                info += f"   • {mem_type:25} : {count:5} записей\n"
            
            info += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            info += "🌐 ПО ИСТОЧНИКАМ:\n"
            
            for source, count in sorted(self.memory_details['by_source'].items(),
                                       key=lambda x: x[1], reverse=True)[:15]:
                info += f"   • {source:25} : {count:5} записей\n"
            
            self.memory_info_text.insert('1.0', info)
            self.memory_info_text.config(state='disabled')
            
            # Обновление последних записей
            self.recent_records_text.config(state='normal')
            self.recent_records_text.delete('1.0', tk.END)
            
            records_text = "╔════════════════════════════════════════════════╗\n"
            records_text += "║   ПОСЛЕДНИЕ 10 ЗАПИСЕЙ В ПАМЯТИ                ║\n"
            records_text += "╚════════════════════════════════════════════════╝\n\n"
            
            for i, record in enumerate(reversed(self.memory_details['recent_records']), 1):
                metadata = record['metadata']
                content = record['content'][:150]
                
                records_text += f"[{i}] ───────────────────────────────────────\n"
                records_text += f"📝 Тип: {metadata.get('type', 'N/A')}\n"
                records_text += f"🌐 Источник: {metadata.get('source', 'N/A')}\n"
                records_text += f"🕐 Дата: {metadata.get('timestamp', 'N/A')}\n"
                records_text += f"📄 Контент:\n   {content}...\n\n"
            
            self.recent_records_text.insert('1.0', records_text)
            self.recent_records_text.config(state='disabled')
            
        except Exception as e:
            print(f"Error updating memory display: {e}")
    
    def _update_learning_display(self):
        """Обновление отображения обучения"""
        try:
            stats_file = "data/continuous_learning_stats.json"
            
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                
                self.learning_stats_text.config(state='normal')
                self.learning_stats_text.delete('1.0', tk.END)
                
                text = f"""
╔══════════════════════════════════════════════════════════╗
║     СТАТИСТИКА НЕПРЕРЫВНОГО ОБУЧЕНИЯ 24/7                ║
╚══════════════════════════════════════════════════════════╝

📊 ОБРАБОТКА ДАННЫХ:
   • Статей обработано:     {stats.get('articles_processed', 0)}
   • Знаний получено:        {stats.get('knowledge_items', 0)}
   • Источников обработано:  {stats.get('sources_processed', 0)}

⏱️  ПРОИЗВОДИТЕЛЬНОСТЬ:
   • Время работы:           {stats.get('uptime_hours', 0):.2f} часов
   • Скорость обучения:      {stats.get('learning_speed_items_per_hour', 0)} эл/час
   • Текущая тема:           {stats.get('current_topic', 'N/A')}

🎯 РЕЖИМ РАБОТЫ:
   • Непрерывное обучение:   АКТИВНО ✓
   • Скорость:               {stats.get('learning_speed', 'NORMAL').upper()}
   • Задержка между запросами: ~{self._get_speed_delay()} сек

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 JARVIS постоянно учится из интернета, впитывая новые знания!
"""
                
                self.learning_stats_text.insert('1.0', text)
                self.learning_stats_text.config(state='disabled')
                
        except Exception as e:
            pass
    
    def _get_speed_delay(self):
        """Получение задержки для текущей скорости"""
        speeds = {'slow': 300, 'normal': 60, 'fast': 10, 'turbo': 1}
        if self.jarvis and hasattr(self.jarvis, 'continuous_learning'):
            speed = self.jarvis.continuous_learning.learning_speed
            return speeds.get(speed, 60)
        return 60
    
    def _update_real_data(self):
        """Обновление реальных данных из JARVIS"""
        try:
            if hasattr(self.jarvis, 'memory_system'):
                real_memory = len(self.jarvis.memory_system.collection.get()['ids'])
                if real_memory != self.stats['memory_items']:
                    self.stats['memory_items'] = real_memory
                    self.stats_queue.put({'memory_items': real_memory})
            
            if hasattr(self.jarvis, 'continuous_learning'):
                cl_stats = self.jarvis.continuous_learning.stats
                self.stats['articles_learned'] = cl_stats.get('articles_processed', 0)
                self.stats['uptime'] = cl_stats.get('uptime_hours', 0)
                self.stats_queue.put({
                    'articles_learned': self.stats['articles_learned'],
                    'uptime': self.stats['uptime']
                })
                
                # Обновление статистики обучения
                self._update_learning_display()
            
            # CPU/GPU
            try:
                import psutil
                self.stats['cpu_usage'] = int(psutil.cpu_percent(interval=0.1))
                self.stats_queue.put({'cpu_usage': self.stats['cpu_usage']})
            except:
                pass
            
        except Exception as e:
            pass
    
    def _simulate_activity(self):
        """Симуляция для демо-режима"""
        if random.random() < 0.1:
            activities = [
                "Мониторинг систем...",
                "Обработка данных...",
                "Обучение на новых статьях...",
                "Синхронизация памяти..."
            ]
            activity = random.choice(activities)
            self.log_queue.put(activity)
            self.current_operation.config(text=activity)
            
            self.stats['memory_items'] += random.randint(0, 2)
            self.stats['articles_learned'] += random.randint(0, 3)
            self.stats_queue.put(self.stats)
    
    def _add_log_message(self, message):
        """Добавление сообщения в лог"""
        self.activity_log.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_log.see(tk.END)
        self.activity_log.config(state='disabled')
    
    def _update_stats(self, stats_dict):
        """Обновление статистики"""
        for key, value in stats_dict.items():
            if key in self.stats_labels:
                label, unit = self.stats_labels[key]
                label.config(text=f"{value} {unit}")
    
    def _manual_memory_refresh(self):
        """Ручное обновление анализа памяти"""
        self.log_queue.put(">> Обновление анализа памяти...")
        threading.Thread(target=self._analyze_memory, daemon=True).start()
    
    def _clear_memory_warning(self):
        """Предупреждение перед очисткой памяти"""
        # Здесь можно добавить диалог подтверждения
        self.log_queue.put(">> ВНИМАНИЕ: Очистка памяти требует подтверждения!")
    
    def _clear_log(self):
        """Очистка лога"""
        self.activity_log.config(state='normal')
        self.activity_log.delete('1.0', tk.END)
        self.activity_log.config(state='disabled')
        self.log_queue.put(">> Лог очищен")
    
    def _change_learning_speed(self, speed):
        """Изменение скорости обучения"""
        if self.jarvis and hasattr(self.jarvis, 'continuous_learning'):
            self.jarvis.continuous_learning.change_speed(speed.lower())
            self.log_queue.put(f">> Скорость обучения изменена на: {speed}")
        else:
            self.log_queue.put(f">> Демо-режим: скорость установлена {speed}")
    
    def add_log(self, message):
        """Публичный метод для добавления лога"""
        self.log_queue.put(message)
    
    def update_status(self, system, status):
        """Публичный метод для обновления статуса"""
        if system in self.system_status:
            self.system_status[system] = status
            if system in self.status_labels:
                indicator, label = self.status_labels[system]
                color = self._get_status_color(status)
                indicator.delete("all")
                indicator.create_oval(2, 2, 11, 11, fill=color, outline=color)
                label.config(text=status, fg=color)
    
    def run(self):
        """Запуск GUI"""
        self.root.mainloop()


def launch_gui(jarvis=None):
    """Запуск расширенного GUI"""
    gui = JarvisGUIExtended(jarvis)
    
    if jarvis:
        jarvis.gui = gui
    
    gui_thread = threading.Thread(target=gui.run, daemon=True)
    gui_thread.start()
    
    return gui


if __name__ == "__main__":
    # Тестовый запуск
    gui = JarvisGUIExtended()
    
    def simulate():
        time.sleep(2)
        gui.add_log(">> JARVIS системы инициализированы")
        time.sleep(1)
        gui.add_log(">> Анализ памяти запущен")
    
    threading.Thread(target=simulate, daemon=True).start()
    
    gui.run()
