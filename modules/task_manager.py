"""
Модуль управления задачами и напоминаниями
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import uuid
from dataclasses import dataclass, asdict
from typing import List, Optional
import schedule
import time
import threading

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Структура задачи"""
    id: str
    title: str
    description: str
    created_at: str
    due_date: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    status: str = "pending"  # pending, in_progress, completed
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Reminder:
    """Структура напоминания"""
    id: str
    message: str
    remind_at: str
    created_at: str
    repeat: Optional[str] = None  # daily, weekly, monthly
    is_active: bool = True


class TaskManager:
    """Менеджер задач и напоминаний"""
    
    def __init__(self, memory_system):
        self.memory = memory_system
        self.tasks_file = Path("data/tasks.json")
        self.reminders_file = Path("data/reminders.json")
        
        self.tasks = []
        self.reminders = []
        
        self._load_tasks()
        self._load_reminders()
        
        # Запуск планировщика напоминаний
        self._start_reminder_scheduler()
    
    def _load_tasks(self):
        """Загрузка задач из файла"""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = [Task(**task) for task in data]
            logger.info(f"Загружено задач: {len(self.tasks)}")
    
    def _load_reminders(self):
        """Загрузка напоминаний из файла"""
        if self.reminders_file.exists():
            with open(self.reminders_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.reminders = [Reminder(**reminder) for reminder in data]
            logger.info(f"Загружено напоминаний: {len(self.reminders)}")
    
    def _save_tasks(self):
        """Сохранение задач в файл"""
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(task) for task in self.tasks], f, ensure_ascii=False, indent=2)
    
    def _save_reminders(self):
        """Сохранение напоминаний в файл"""
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(reminder) for reminder in self.reminders], f, ensure_ascii=False, indent=2)
    
    async def handle_command(self, user_input, entities):
        """
        Обработка команд по управлению задачами
        
        Args:
            user_input: Текст команды
            entities: Извлеченные сущности
            
        Returns:
            str: Ответ пользователю
        """
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['создай', 'добавь', 'новая']):
            return await self.create_task(user_input, entities)
        
        elif any(word in user_lower for word in ['покажи', 'список', 'какие']):
            return await self.list_tasks(entities)
        
        elif any(word in user_lower for word in ['выполнена', 'завершена', 'сделано']):
            return await self.complete_task(entities)
        
        elif 'удали' in user_lower:
            return await self.delete_task(entities)
        
        else:
            return "Я могу создать задачу, показать список задач или отметить задачу как выполненную. Что вам нужно?"
    
    async def create_task(self, user_input, entities):
        """Создание новой задачи"""
        try:
            # Извлечение описания задачи
            description = entities.get('description', user_input)
            
            # Определение приоритета
            priority = "medium"
            if any(word in user_input.lower() for word in ['срочно', 'важно', 'критично']):
                priority = "high"
            elif any(word in user_input.lower() for word in ['можно позже', 'не срочно']):
                priority = "low"
            
            # Создание задачи
            task = Task(
                id=str(uuid.uuid4()),
                title=description[:100],  # Первые 100 символов как заголовок
                description=description,
                created_at=datetime.now().isoformat(),
                due_date=entities.get('date'),
                priority=priority
            )
            
            self.tasks.append(task)
            self._save_tasks()
            
            # Сохранение в память
            await self.memory.store_memory(
                f"Задача: {task.title}",
                memory_type="task",
                metadata={
                    'task_id': task.id,
                    'priority': task.priority,
                    'due_date': task.due_date
                }
            )
            
            response = f"Задача создана: '{task.title}'"
            if task.due_date:
                response += f" (срок: {task.due_date})"
            if task.priority == "high":
                response += ". Отмечена как приоритетная"
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {e}")
            return "Не удалось создать задачу"
    
    async def list_tasks(self, entities):
        """Получение списка задач"""
        try:
            # Фильтрация задач
            filtered_tasks = [t for t in self.tasks if t.status == "pending"]
            
            if not filtered_tasks:
                return "У вас нет активных задач"
            
            # Сортировка по приоритету и дате
            priority_order = {"high": 0, "medium": 1, "low": 2}
            filtered_tasks.sort(key=lambda t: (
                priority_order.get(t.priority, 1),
                t.due_date or "9999-12-31"
            ))
            
            # Формирование ответа
            response = f"У вас {len(filtered_tasks)} активных задач:\n"
            
            for i, task in enumerate(filtered_tasks[:10], 1):  # Показываем только первые 10
                priority_marker = "❗" if task.priority == "high" else ""
                due = f" (до {task.due_date})" if task.due_date else ""
                response += f"{i}. {priority_marker}{task.title}{due}\n"
            
            if len(filtered_tasks) > 10:
                response += f"\n... и еще {len(filtered_tasks) - 10} задач"
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Ошибка получения списка задач: {e}")
            return "Не удалось получить список задач"
    
    async def complete_task(self, entities):
        """Отметка задачи как выполненной"""
        try:
            # Поиск задачи по описанию или индексу
            task_description = entities.get('description', '')
            
            for task in self.tasks:
                if task.status == "pending" and task_description.lower() in task.title.lower():
                    task.status = "completed"
                    self._save_tasks()
                    return f"Отлично! Задача '{task.title}' отмечена как выполненная"
            
            return "Не удалось найти указанную задачу"
            
        except Exception as e:
            logger.error(f"Ошибка завершения задачи: {e}")
            return "Не удалось завершить задачу"
    
    async def delete_task(self, entities):
        """Удаление задачи"""
        try:
            task_description = entities.get('description', '')
            
            for i, task in enumerate(self.tasks):
                if task_description.lower() in task.title.lower():
                    deleted_task = self.tasks.pop(i)
                    self._save_tasks()
                    return f"Задача '{deleted_task.title}' удалена"
            
            return "Не удалось найти указанную задачу"
            
        except Exception as e:
            logger.error(f"Ошибка удаления задачи: {e}")
            return "Не удалось удалить задачу"
    
    async def handle_reminder(self, user_input, entities):
        """Создание напоминания"""
        try:
            message = entities.get('description', user_input)
            remind_time = entities.get('time', entities.get('date'))
            
            if not remind_time:
                return "Укажите, когда вам напомнить"
            
            # Парсинг времени
            remind_at = self._parse_reminder_time(remind_time)
            
            reminder = Reminder(
                id=str(uuid.uuid4()),
                message=message,
                remind_at=remind_at.isoformat(),
                created_at=datetime.now().isoformat()
            )
            
            self.reminders.append(reminder)
            self._save_reminders()
            
            return f"Напоминание установлено: '{message}' в {remind_at.strftime('%H:%M %d.%m.%Y')}"
            
        except Exception as e:
            logger.error(f"Ошибка создания напоминания: {e}")
            return "Не удалось создать напоминание"
    
    def _parse_reminder_time(self, time_str):
        """Парсинг времени напоминания"""
        time_str = time_str.lower()
        
        # Относительные времена
        if 'через' in time_str:
            if 'час' in time_str:
                hours = 1
                return datetime.now() + timedelta(hours=hours)
            elif 'минут' in time_str:
                minutes = 30
                return datetime.now() + timedelta(minutes=minutes)
        
        # Сегодня/завтра
        if 'сегодня' in time_str:
            # Извлечение времени
            return datetime.now().replace(hour=18, minute=0, second=0)
        elif 'завтра' in time_str:
            return (datetime.now() + timedelta(days=1)).replace(hour=9, minute=0, second=0)
        
        # По умолчанию - через час
        return datetime.now() + timedelta(hours=1)
    
    def _start_reminder_scheduler(self):
        """Запуск планировщика напоминаний"""
        def check_reminders():
            """Проверка активных напоминаний"""
            now = datetime.now()
            
            for reminder in self.reminders:
                if not reminder.is_active:
                    continue
                
                remind_time = datetime.fromisoformat(reminder.remind_at)
                
                if remind_time <= now:
                    logger.info(f"🔔 Напоминание: {reminder.message}")
                    # Здесь должна быть озвучка напоминания
                    reminder.is_active = False
                    self._save_reminders()
        
        # Запуск проверки каждую минуту
        schedule.every(1).minutes.do(check_reminders)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        # Запуск в отдельном потоке
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("Планировщик напоминаний запущен")
    
    async def get_today_tasks(self):
        """Получение задач на сегодня"""
        today = datetime.now().date().isoformat()
        
        today_tasks = [
            task for task in self.tasks 
            if task.status == "pending" and task.due_date and task.due_date.startswith(today)
        ]
        
        return today_tasks
    
    async def get_overdue_tasks(self):
        """Получение просроченных задач"""
        today = datetime.now().date()
        
        overdue = [
            task for task in self.tasks
            if task.status == "pending" and task.due_date
            and datetime.fromisoformat(task.due_date).date() < today
        ]
        
        return overdue
