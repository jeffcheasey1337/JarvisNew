"""
JARVIS - Персональный голосовой ассистент с обучением
Основной модуль управления
"""

import asyncio
from jarvis.gui.main_window import launch_gui
import threading
import json
from datetime import datetime
from pathlib import Path
import logging

from jarvis.core.speech.recognition import SpeechRecognizer
from jarvis.core.speech.synthesis import SpeechSynthesizer
from jarvis.core.nlp.processor import NLPProcessor
from jarvis.core.memory.system import MemorySystem
from jarvis.core.learning.base import LearningSystem
from jarvis.core.learning.continuous import ContinuousLearning
from jarvis.modules.tasks import TaskManager
from jarvis.modules.calendar import CalendarManager
from jarvis.modules.search import WebSearch
from jarvis.modules.files import FileManager
from jarvis.modules.system import SystemControl

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class JarvisAssistant:
    """Главный класс голосового ассистента JARVIS"""
    
    def __init__(self, config_path="config/config.json"):
        """Инициализация ассистента"""
        self.config = self._load_config(config_path)
        self.running = False
        
        # Инициализация основных компонентов
        logger.info("Инициализация JARVIS...")
        
        self.speech_recognizer = SpeechRecognizer(self.config)
        self.speech_synthesizer = SpeechSynthesizer(self.config)
        self.nlp_processor = NLPProcessor(self.config)
        self.memory_system = MemorySystem(self.config)
        self.learning_system = LearningSystem(self.config, self.memory_system)
        self.continuous_learning = ContinuousLearning(self.config, self.memory_system, self.nlp_processor)
        
        # Связывание continuous_learning с GUI
        if hasattr(self, 'gui') and self.gui:
            self.continuous_learning.gui = self.gui
            self.gui.continuous_learning = self.continuous_learning
        
        # Инициализация модулей функционала
        self.task_manager = TaskManager(self.memory_system)
        self.calendar_manager = CalendarManager(self.memory_system)
        self.web_search = WebSearch(self.config)
        self.file_manager = FileManager()
        self.system_control = SystemControl()
        
        # Словарь команд для быстрого доступа
        self.command_handlers = self._register_commands()
        
        logger.info("JARVIS готов к работе!")
    
    def _load_config(self, config_path):
        """Загрузка конфигурации"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Конфиг не найден, используются настройки по умолчанию")
            return self._default_config()
    
    def _default_config(self):
        """Конфигурация по умолчанию"""
        return {
            "wake_word": "джарвис",
            "language": "ru-RU",
            "voice_model": "jarvis_tts",
            "llm_model": "mistral-7b",
            "memory_retention_days": 90,
            "learning_enabled": True,
            "privacy_mode": True
        }
    
    def _register_commands(self):
        """Регистрация обработчиков команд"""
        return {
            "задача": self.task_manager.handle_command,
            "напоминание": self.task_manager.handle_reminder,
            "календарь": self.calendar_manager.handle_command,
            "найди": self.web_search.search,
            "открой": self.file_manager.open_file,
            "создай": self.file_manager.create_file,
            "системная": self.system_control.execute_command,
            "запомни": self.memory_system.store_memory,
            "что ты знаешь": self.memory_system.recall_memory,
            "учись": self._handle_learning_command,
            "отчет об обучении": self._get_learning_report,
        }
    
    async def listen_for_wake_word(self):
        """Ожидание ключевого слова активации"""
        logger.info(f"Ожидание активационного слова: '{self.config['wake_word']}'")
        
        while self.running:
            try:
                audio_data = await self.speech_recognizer.listen()
                text = await self.speech_recognizer.recognize(audio_data)
                
                if text and self.config['wake_word'].lower() in text.lower():
                    await self.speech_synthesizer.speak("Слушаю вас, сэр")
                    logger.info("Ассистент активирован")
                    return True
                    
            except Exception as e:
                logger.error(f"Ошибка при ожидании активации: {e}")
                await asyncio.sleep(0.5)
        
        return False
    
    async def process_command(self, user_input):
        """Обработка команды пользователя"""
        try:
            # Логирование взаимодействия для обучения
            interaction_id = await self.learning_system.log_interaction(user_input)
            
            # Получение контекста из памяти
            context = await self.memory_system.get_context(user_input)
            
            # Анализ намерения через NLP
            intent = await self.nlp_processor.analyze_intent(user_input, context)
            
            logger.info(f"Намерение: {intent['action']}, Уверенность: {intent['confidence']}")
            
            # Выполнение команды
            response = await self._execute_command(intent, user_input, context)
            
            # Обучение на основе результата
            await self.learning_system.learn_from_interaction(
                interaction_id, 
                user_input, 
                response, 
                intent
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка обработки команды: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса"
    
    async def _execute_command(self, intent, user_input, context):
        """Выполнение конкретной команды"""
        action = intent['action']
        entities = intent.get('entities', {})
        
        # Проверка специфических команд
        for keyword, handler in self.command_handlers.items():
            if keyword in action.lower():
                return await handler(user_input, entities)
        
        # Если нет специфической команды - общение через LLM
        return await self.nlp_processor.generate_response(
            user_input, 
            context,
            personality="jarvis"
        )
    
    async def conversation_loop(self):
        """Основной цикл общения"""
        logger.info("Начало диалога")
        conversation_active = True
        silence_count = 0
        max_silence = 3
        
        while conversation_active and self.running:
            try:
                # Прослушивание команды
                audio_data = await self.speech_recognizer.listen(timeout=10)
                
                if audio_data is None:
                    silence_count += 1
                    if silence_count >= max_silence:
                        await self.speech_synthesizer.speak("Перехожу в режим ожидания")
                        conversation_active = False
                    continue
                
                silence_count = 0
                
                # Распознавание речи
                user_input = await self.speech_recognizer.recognize(audio_data)
                
                if not user_input:
                    continue
                
                logger.info(f"Пользователь: {user_input}")
                
                # Проверка команды выхода
                if any(word in user_input.lower() for word in ["хватит", "стоп", "отключись", "спасибо всё"]):
                    await self.speech_synthesizer.speak("Хорошо, сэр. Буду ждать вашей команды")
                    conversation_active = False
                    continue
                
                # Обработка команды
                response = await self.process_command(user_input)
                
                logger.info(f"JARVIS: {response}")
                
                # Озвучивание ответа
                await self.speech_synthesizer.speak(response)
                
            except Exception as e:
                logger.error(f"Ошибка в цикле общения: {e}")
                await asyncio.sleep(1)
    
    async def run(self):
        """Запуск ассистента"""
        self.running = True
        
        # Приветствие
        greeting = await self._get_greeting()
        await self.speech_synthesizer.speak(greeting)
        
        # Подтверждение готовности
        await asyncio.sleep(0.5)
        await self.speech_synthesizer.speak("Да, сэр")
        
        # Запуск НЕПРЕРЫВНОГО обучения 24/7
        if self.config.get('autonomous_learning', {}).get('continuous', True):
            asyncio.create_task(self.continuous_learning.start_continuous_learning())
            logger.info(" НЕПРЕРЫВНОЕ обучение 24/7 запущено!")
        
        try:
            while self.running:
                # Ожидание активации
                activated = await self.listen_for_wake_word()
                
                if activated:
                    # Запуск диалога
                    await self.conversation_loop()
                    
        except KeyboardInterrupt:
            logger.info("Получен сигнал завершения")
        finally:
            await self.shutdown()
    
    async def _handle_learning_command(self, user_input, entities):
        """Обработка команд обучения"""
        if "статистика" in user_input.lower() or "отчет" in user_input.lower():
            stats = await self.continuous_learning.get_realtime_stats()
            response = f"Статистика непрерывного обучения:\n"
            response += f"⏰ Работаю: {stats['uptime_hours']:.1f} часов\n"
            response += f" Изучено статей: {stats['articles_total']}\n"
            response += f"🧠 Знаний получено: {stats['knowledge_items']}\n"
            response += f" Скорость: {stats['speed_per_hour']} элементов/час\n"
            response += f" Сейчас изучаю: {stats['current_topic']}"
            return response
        elif "скорость" in user_input.lower():
            if "медленно" in user_input.lower() or "slow" in user_input.lower():
                return await self.continuous_learning.change_speed('slow')
            elif "быстро" in user_input.lower() or "fast" in user_input.lower():
                return await self.continuous_learning.change_speed('fast')
            elif "турбо" in user_input.lower() or "turbo" in user_input.lower():
                return await self.continuous_learning.change_speed('turbo')
            elif "нормально" in user_input.lower() or "normal" in user_input.lower():
                return await self.continuous_learning.change_speed('normal')
            else:
                return "Доступные скорости: медленно, нормально, быстро, турбо"
        else:
            return "Могу показать статистику обучения или изменить скорость"
    
    async def _get_learning_report(self, user_input, entities):
        """Получение подробного отчета об обучении"""
        stats = await self.continuous_learning.get_realtime_stats()
        
        response = " ПОДРОБНЫЙ ОТЧЕТ О НЕПРЕРЫВНОМ ОБУЧЕНИИ\n\n"
        response += f" Время непрерывной работы: {stats['uptime_hours']:.2f} часов\n"
        response += f" Всего изучено статей: {stats['articles_total']}\n"
        response += f"🧠 Единиц знаний получено: {stats['knowledge_items']}\n"
        response += f" Текущая скорость: {stats['speed_per_hour']} элементов/час\n"
        response += f" Текущая тема изучения: {stats['current_topic']}\n"
        response += f" Активных источников: {stats['sources_count']}\n"
        response += f" Режим обучения: {stats['learning_mode'].upper()}\n\n"
        response += " Я постоянно учусь из интернета 24/7 без остановок!"
        
        return response
    
    async def _get_greeting(self):
        """Получение приветствия в зависимости от времени"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "Доброе утро, сэр"
        elif 12 <= hour < 17:
            greeting = "Добрый день, сэр"
        elif 17 <= hour < 23:
            greeting = "Добрый вечер, сэр"
        else:
            greeting = "Доброй ночи, сэр"
        
        # Добавление персонализированной информации
        context = await self.memory_system.get_daily_context()
        if context.get('pending_tasks'):
            greeting += f". У вас {len(context['pending_tasks'])} задач на сегодня"
        
        return greeting
    
    async def shutdown(self):
        """Корректное завершение работы"""
        logger.info("Завершение работы JARVIS...")
        self.running = False
        
        # Сохранение данных обучения
        await self.learning_system.save_training_data()
        
        # Закрытие соединений
        await self.memory_system.close()
        
        await self.speech_synthesizer.speak("Система отключена. До свидания, сэр")
        logger.info("JARVIS отключен")


async def main():
    # Запуск расширенного GUI
    print("Запуск графического интерфейса...")
    # Создание GUI (без запуска mainloop)
    gui = launch_gui()
    # GUI создан (не запускается пока)
    
    """Точка входа в программу"""
    # Создание необходимых директорий
    Path("config").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Запуск ассистента
    jarvis = JarvisAssistant()
    
    # Привязка GUI к JARVIS
    jarvis.gui = gui
    gui.jarvis = jarvis
    gui.add_log("=== JARVIS ИНИЦИАЛИЗИРОВАН ===")
    gui.add_log("Графический интерфейс подключен")
    
    # Запуск JARVIS и GUI
    # GUI.run() блокирует поток, поэтому запускаем JARVIS в фоне
    import threading
    
    def run_jarvis():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(jarvis.run())
    
    jarvis_thread = threading.Thread(target=run_jarvis, daemon=False)
    jarvis_thread.start()
    
    # Запуск GUI в главном потоке (блокирует)
    print("Запуск графического интерфейса...")
    gui.run()


if __name__ == "__main__":
    asyncio.run(main())
