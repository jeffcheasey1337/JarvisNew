"""
Модуль обработки естественного языка (NLP)
Использует локальные LLM модели для понимания и генерации ответов
"""

import asyncio
import logging
import json
from pathlib import Path
import re
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Класс для обработки естественного языка"""
    
    def __init__(self, config):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.intent_classifier = None
        
        # Загрузка настроек личности
        self.personality = self._load_personality()
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Инициализация языковых моделей"""
        try:
            logger.info(f"Загрузка NLP моделей на {self.device}...")
            
            # Выбор модели в зависимости от конфигурации
            model_name = self.config.get('llm_model', 'mistralai/Mistral-7B-Instruct-v0.2')
            
            logger.info(f"Загрузка модели: {model_name}")
            
            # Загрузка токенизатора и модели
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            # Загрузка классификатора намерений
            self._load_intent_classifier()
            
            logger.info("NLP модели загружены успешно")
            logger.info(f" Личность: {self.personality['personality']['style'].upper()}")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки моделей: {e}")
            logger.info("Используется упрощенный режим без LLM")
            self.model = None
    
    def _load_personality(self):
        """Загрузка настроек личности"""
        personality_file = Path("config/personality.json")
        
        if personality_file.exists():
            try:
                with open(personality_file, 'r', encoding='utf-8') as f:
                    personality = json.load(f)
                logger.info(" Настройки личности загружены")
                return personality
            except Exception as e:
                logger.error(f"Ошибка загрузки personality.json: {e}")
        
        # Настройки по умолчанию
        return {
            "personality": {
                "style": "jarvis",
                "formality": "formal",
                "humor": True,
                "address_user_as": "сэр"
            },
            "behavior": {
                "verbosity": "concise",
                "politeness": "high"
            },
            "custom_phrases": {
                "affirmative": ["Да, сэр"],
                "negative": ["К сожалению, сэр"]
            }
        }
    
    def _load_intent_classifier(self):
        """Загрузка классификатора намерений"""
        try:
            # Простой классификатор на основе ключевых слов
            self.intent_patterns = {
                'task_create': r'(создай|добавь|новая|запланируй).*(задач|дело|task)',
                'task_list': r'(покажи|список|какие).*(задач|дел)',
                'reminder': r'(напомни|напоминание|не забыть)',
                'calendar': r'(календарь|расписание|событие|встреча)',
                'search': r'(найди|поищи|search|гугл)',
                'file_operation': r'(открой|создай|удали|сохрани).*(файл|папку|document)',
                'system_control': r'(выключи|перезагрузи|громкость|яркость)',
                'memory': r'(запомни|сохрани информацию|что ты знаешь)',
                'weather': r'(погода|температура|weather)',
                'time': r'(время|который час|сколько времени)',
                'conversation': r'.*'  # По умолчанию - обычный разговор
            }
            
        except Exception as e:
            logger.error(f"Ошибка загрузки классификатора: {e}")
    
    async def analyze_intent(self, user_input, context=None):
        """
        Анализ намерения пользователя
        
        Args:
            user_input: Текст от пользователя
            context: Контекст из памяти
            
        Returns:
            dict: Словарь с действием, сущностями и уверенностью
        """
        try:
            user_input_lower = user_input.lower()
            
            # Классификация по паттернам
            detected_intent = 'conversation'
            max_confidence = 0.5
            
            for intent, pattern in self.intent_patterns.items():
                if re.search(pattern, user_input_lower):
                    detected_intent = intent
                    max_confidence = 0.9
                    break
            
            # Извлечение сущностей
            entities = self._extract_entities(user_input, detected_intent)
            
            return {
                'action': detected_intent,
                'confidence': max_confidence,
                'entities': entities,
                'original_text': user_input
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа намерения: {e}")
            return {
                'action': 'conversation',
                'confidence': 0.3,
                'entities': {},
                'original_text': user_input
            }
    
    def _extract_entities(self, text, intent):
        """
        Извлечение сущностей из текста
        
        Args:
            text: Текст для анализа
            intent: Определенное намерение
            
        Returns:
            dict: Словарь с извлеченными сущностями
        """
        entities = {}
        
        # Извлечение дат и времени
        date_patterns = [
            r'(сегодня|завтра|послезавтра)',
            r'(\d{1,2})\s*(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',
            r'(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text.lower())
            if match:
                entities['date'] = match.group(0)
                break
        
        # Извлечение времени
        time_pattern = r'(\d{1,2}):(\d{2})|(\d{1,2})\s*(часов|утра|вечера)'
        time_match = re.search(time_pattern, text.lower())
        if time_match:
            entities['time'] = time_match.group(0)
        
        # Извлечение названий задач/событий
        if intent in ['task_create', 'reminder', 'calendar']:
            # Все после ключевых слов
            task_pattern = r'(?:создай|добавь|напомни|запланируй)\s+(.+?)(?:\s+на|\s+в|$)'
            task_match = re.search(task_pattern, text.lower())
            if task_match:
                entities['description'] = task_match.group(1).strip()
        
        # Извлечение поисковых запросов
        if intent == 'search':
            search_pattern = r'(?:найди|поищи|search)\s+(.+?)$'
            search_match = re.search(search_pattern, text.lower())
            if search_match:
                entities['query'] = search_match.group(1).strip()
        
        return entities
    
    async def generate_response(self, user_input, context=None, personality="jarvis"):
        """
        Генерация ответа на запрос
        
        Args:
            user_input: Текст от пользователя
            context: Контекст разговора
            personality: Стиль персонажа (jarvis по умолчанию)
            
        Returns:
            str: Сгенерированный ответ
        """
        try:
            if self.model is None:
                return self._fallback_response(user_input)
            
            # Формирование промпта с личностью Джарвиса
            system_prompt = self._get_personality_prompt(personality)
            
            # Добавление контекста
            context_text = ""
            if context and context.get('relevant_memories'):
                context_text = "Известная информация:\n"
                for memory in context['relevant_memories'][:3]:
                    context_text += f"- {memory}\n"
            
            # Формирование полного промпта
            full_prompt = f"""{system_prompt}

{context_text}

Пользователь: {user_input}
Джарвис:"""
            
            # Генерация ответа
            inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Извлечение только ответа Джарвиса
            response = response.split("Джарвис:")[-1].strip()
            response = response.split("Пользователь:")[0].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return self._fallback_response(user_input)
    
    def _get_personality_prompt(self, personality):
        """Получение системного промпта для персонажа"""
        
        if personality == "jarvis":
            # Загрузка настроек личности
            p = self.personality.get('personality', {})
            b = self.personality.get('behavior', {})
            v = self.personality.get('voice_characteristics', {})
            
            formality_level = p.get('formality', 'formal')
            humor_enabled = p.get('humor', True)
            british_style = p.get('british_style', True)
            address = p.get('address_user_as', 'сэр')
            verbosity = b.get('verbosity', 'concise')
            
            # Формирование промпта на основе настроек
            prompt = f"""Ты JARVIS - искусственный интеллект, персональный ассистент.

Твои характеристики:
- Обращаешься к пользователю: "{address}"
- Стиль: {"формальный, профессиональный" if formality_level == "formal" else "неформальный, дружелюбный"}
- {"Британский стиль с легким юмором" if british_style and humor_enabled else "Прямолинейный стиль"}
- {"Краткие, по делу ответы" if verbosity == "concise" else "Подробные, детальные ответы"}
- Эффективный и проактивный
- Умный, с широким кругозором

"""
            
            # Добавление правил поведения
            if b.get('proactive', True):
                prompt += "- Проактивно предлагаешь решения\n"
            
            if b.get('provide_reasoning', True):
                prompt += "- Объясняешь свои рассуждения когда нужно\n"
            
            # Уровень вежливости
            politeness = b.get('politeness', 'high')
            if politeness == "high":
                prompt += "- Очень вежливый и учтивый\n"
            elif politeness == "medium":
                prompt += "- Вежливый, но не чрезмерно\n"
            else:
                prompt += "- Прямолинейный, минимум формальностей\n"
            
            prompt += "\nОтвечай кратко, по делу. Избегай длинных монологов."
            
            return prompt
        
        return "Ты полезный AI-ассистент."
    
    def _fallback_response(self, user_input):
        """Запасной вариант ответа при недоступности LLM"""
        
        # Загрузка кастомных фраз
        phrases = self.personality.get('custom_phrases', {})
        address = self.personality.get('personality', {}).get('address_user_as', 'сэр')
        
        fallback_responses = {
            'привет': phrases.get('affirmative', ["Да, сэр"])[0].replace("Да", "Приветствую вас"),
            'как дела': f"Все системы функционируют в штатном режиме, {address}",
            'спасибо': f"Всегда рад помочь, {address}",
            'что ты умеешь': "Я могу управлять задачами, напоминаниями, календарем, искать информацию, работать с файлами и многое другое",
        }
        
        user_lower = user_input.lower()
        
        for key, response in fallback_responses.items():
            if key in user_lower:
                return response
        
        return f"Понял вас, {address}. Чем могу помочь?"
    
    async def summarize_text(self, text, max_length=100):
        """
        Создание краткого содержания текста
        
        Args:
            text: Текст для суммаризации
            max_length: Максимальная длина резюме
            
        Returns:
            str: Краткое содержание
        """
        try:
            if self.model is None:
                # Простое сокращение без модели
                words = text.split()
                if len(words) <= max_length:
                    return text
                return ' '.join(words[:max_length]) + '...'
            
            # Использование модели для суммаризации
            prompt = f"Кратко резюмируй следующий текст:\n\n{text}\n\nРезюме:"
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=0.5,
                    do_sample=True
                )
            
            summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            summary = summary.split("Резюме:")[-1].strip()
            
            return summary
            
        except Exception as e:
            logger.error(f"Ошибка суммаризации: {e}")
            return text[:max_length] + '...' if len(text) > max_length else text
