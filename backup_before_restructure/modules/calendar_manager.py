"""
Менеджер календаря и событий
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import uuid
from dataclasses import dataclass, asdict
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """Структура события календаря"""
    id: str
    title: str
    description: str
    start_time: str
    end_time: str
    location: Optional[str] = None
    attendees: list = None
    reminder_minutes: int = 15
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []


class CalendarManager:
    """Менеджер календаря"""
    
    def __init__(self, memory_system):
        self.memory = memory_system
        self.events_file = Path("data/calendar_events.json")
        self.events = []
        
        self._load_events()
    
    def _load_events(self):
        """Загрузка событий"""
        if self.events_file.exists():
            with open(self.events_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.events = [CalendarEvent(**event) for event in data]
    
    def _save_events(self):
        """Сохранение событий"""
        with open(self.events_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(event) for event in self.events], f, ensure_ascii=False, indent=2)
    
    async def handle_command(self, user_input, entities):
        """Обработка команд календаря"""
        if 'создай' in user_input.lower() or 'добавь' in user_input.lower():
            return await self.create_event(user_input, entities)
        elif 'покажи' in user_input.lower() or 'расписание' in user_input.lower():
            return await self.show_schedule(entities)
        else:
            return "Я могу создать событие или показать расписание"
    
    async def create_event(self, user_input, entities):
        """Создание события"""
        try:
            description = entities.get('description', 'Новое событие')
            start_time = entities.get('time', entities.get('date'))
            
            if not start_time:
                return "Укажите время события"
            
            event = CalendarEvent(
                id=str(uuid.uuid4()),
                title=description[:100],
                description=description,
                start_time=start_time,
                end_time=start_time  # Упрощенно - конец = начало
            )
            
            self.events.append(event)
            self._save_events()
            
            return f"Событие '{event.title}' добавлено в календарь на {start_time}"
            
        except Exception as e:
            logger.error(f"Ошибка создания события: {e}")
            return "Не удалось создать событие"
    
    async def show_schedule(self, entities):
        """Показать расписание"""
        try:
            today = datetime.now().date()
            upcoming = [e for e in self.events if datetime.fromisoformat(e.start_time).date() >= today]
            
            if not upcoming:
                return "В календаре нет предстоящих событий"
            
            upcoming.sort(key=lambda e: e.start_time)
            
            response = f"Предстоящие события ({len(upcoming)}):\n"
            for event in upcoming[:5]:
                time = datetime.fromisoformat(event.start_time).strftime('%d.%m %H:%M')
                response += f"• {event.title} - {time}\n"
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Ошибка показа расписания: {e}")
            return "Не удалось получить расписание"
