"""
Система обучения и адаптации ассистента
Анализирует взаимодействия и улучшает ответы со временем
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from collections import defaultdict, Counter
import pickle

logger = logging.getLogger(__name__)


class LearningSystem:
    """Система обучения и адаптации поведения ассистента"""
    
    def __init__(self, config, memory_system):
        self.config = config
        self.memory = memory_system
        
        # Путь для хранения данных обучения
        self.learning_data_path = Path("data/learning")
        self.learning_data_path.mkdir(parents=True, exist_ok=True)
        
        # Статистика взаимодействий
        self.interaction_stats = defaultdict(lambda: {
            'count': 0,
            'success_rate': 0.0,
            'avg_response_time': 0.0,
            'user_satisfaction': []
        })
        
        # Паттерны поведения пользователя
        self.user_patterns = {
            'frequent_queries': Counter(),
            'time_patterns': defaultdict(list),  # Время дня -> типы запросов
            'preferred_responses': {},  # Тип запроса -> предпочитаемый стиль ответа
            'correction_history': []  # История исправлений
        }
        
        # Обратная связь от пользователя
        self.feedback_log = []
        
        # Загрузка существующих данных
        self._load_learning_data()
    
    def _load_learning_data(self):
        """Загрузка сохраненных данных обучения"""
        try:
            stats_file = self.learning_data_path / "interaction_stats.pkl"
            patterns_file = self.learning_data_path / "user_patterns.pkl"
            
            if stats_file.exists():
                with open(stats_file, 'rb') as f:
                    self.interaction_stats = pickle.load(f)
                logger.info("Статистика взаимодействий загружена")
            
            if patterns_file.exists():
                with open(patterns_file, 'rb') as f:
                    self.user_patterns = pickle.load(f)
                logger.info("Паттерны пользователя загружены")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных обучения: {e}")
    
    async def save_training_data(self):
        """Сохранение данных обучения"""
        try:
            stats_file = self.learning_data_path / "interaction_stats.pkl"
            patterns_file = self.learning_data_path / "user_patterns.pkl"
            
            with open(stats_file, 'wb') as f:
                pickle.dump(dict(self.interaction_stats), f)
            
            with open(patterns_file, 'wb') as f:
                pickle.dump(self.user_patterns, f)
            
            logger.info("Данные обучения сохранены")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных обучения: {e}")
    
    async def log_interaction(self, user_input, intent=None):
        """
        Логирование взаимодействия для последующего анализа
        
        Args:
            user_input: Запрос пользователя
            intent: Определенное намерение (опционально)
            
        Returns:
            str: ID взаимодействия
        """
        interaction_id = f"int_{datetime.now().timestamp()}"
        
        # Обновление частоты запросов
        self.user_patterns['frequent_queries'][user_input.lower()] += 1
        
        # Анализ временных паттернов
        hour = datetime.now().hour
        if intent:
            self.user_patterns['time_patterns'][hour].append(intent)
        
        # Создание записи взаимодействия
        interaction_record = {
            'id': interaction_id,
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'intent': intent,
            'hour': hour
        }
        
        # Сохранение в лог
        log_file = self.learning_data_path / "interactions.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(interaction_record, ensure_ascii=False) + '\n')
        
        return interaction_id
    
    async def learn_from_interaction(self, interaction_id, user_input, response, intent):
        """
        Обучение на основе завершенного взаимодействия
        
        Args:
            interaction_id: ID взаимодействия
            user_input: Запрос пользователя
            response: Ответ ассистента
            intent: Определенное намерение
        """
        try:
            action = intent.get('action', 'unknown')
            
            # Обновление статистики
            self.interaction_stats[action]['count'] += 1
            
            # Анализ качества ответа (упрощенная версия)
            quality_score = await self._estimate_response_quality(
                user_input, 
                response, 
                intent
            )
            
            # Обновление среднего качества
            current_stats = self.interaction_stats[action]
            current_success = current_stats['success_rate']
            count = current_stats['count']
            
            new_success_rate = (current_success * (count - 1) + quality_score) / count
            self.interaction_stats[action]['success_rate'] = new_success_rate
            
            # Сохранение удачных паттернов
            if quality_score > 0.7:
                await self._save_successful_pattern(user_input, response, intent)
            
        except Exception as e:
            logger.error(f"Ошибка обучения на взаимодействии: {e}")
    
    async def _estimate_response_quality(self, user_input, response, intent):
        """
        Оценка качества ответа (эвристический подход)
        
        Returns:
            float: Оценка от 0 до 1
        """
        score = 0.5  # Базовая оценка
        
        # Проверка длины ответа
        if len(response) > 10:
            score += 0.1
        
        # Проверка релевантности (простая)
        user_words = set(user_input.lower().split())
        response_words = set(response.lower().split())
        
        overlap = len(user_words & response_words)
        if overlap > 0:
            score += min(0.2, overlap * 0.05)
        
        # Проверка соответствия намерению
        if intent.get('confidence', 0) > 0.7:
            score += 0.1
        
        # Проверка наличия извинений или неуверенности
        uncertainty_markers = ['не знаю', 'не уверен', 'извините', 'к сожалению']
        if any(marker in response.lower() for marker in uncertainty_markers):
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    async def _save_successful_pattern(self, user_input, response, intent):
        """Сохранение успешного паттерна взаимодействия"""
        action = intent.get('action', 'unknown')
        
        pattern = {
            'user_input': user_input,
            'response': response,
            'intent': intent,
            'timestamp': datetime.now().isoformat()
        }
        
        # Сохранение в файл успешных паттернов
        patterns_file = self.learning_data_path / f"successful_patterns_{action}.jsonl"
        with open(patterns_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(pattern, ensure_ascii=False) + '\n')
    
    async def record_feedback(self, interaction_id, feedback_type, comment=None):
        """
        Запись обратной связи от пользователя
        
        Args:
            interaction_id: ID взаимодействия
            feedback_type: 'positive', 'negative', 'correction'
            comment: Дополнительный комментарий
        """
        feedback = {
            'interaction_id': interaction_id,
            'type': feedback_type,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_log.append(feedback)
        
        # Сохранение в файл
        feedback_file = self.learning_data_path / "feedback.jsonl"
        with open(feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback, ensure_ascii=False) + '\n')
        
        # Если это исправление, сохраняем в историю
        if feedback_type == 'correction':
            self.user_patterns['correction_history'].append(feedback)
    
    async def get_personalized_suggestions(self):
        """
        Получение персонализированных предложений на основе паттернов
        
        Returns:
            dict: Словарь с предложениями
        """
        suggestions = {
            'frequent_tasks': [],
            'time_based_reminders': [],
            'routine_suggestions': []
        }
        
        # Анализ частых запросов
        most_common = self.user_patterns['frequent_queries'].most_common(5)
        suggestions['frequent_tasks'] = [query for query, count in most_common if count > 3]
        
        # Анализ временных паттернов
        current_hour = datetime.now().hour
        if current_hour in self.user_patterns['time_patterns']:
            common_intents = Counter(self.user_patterns['time_patterns'][current_hour])
            if common_intents:
                most_common_intent = common_intents.most_common(1)[0][0]
                suggestions['time_based_reminders'].append(
                    f"В это время вы обычно интересуетесь: {most_common_intent}"
                )
        
        return suggestions
    
    async def analyze_learning_progress(self):
        """
        Анализ прогресса обучения
        
        Returns:
            dict: Статистика обучения
        """
        total_interactions = sum(
            stats['count'] for stats in self.interaction_stats.values()
        )
        
        avg_success_rate = np.mean([
            stats['success_rate'] 
            for stats in self.interaction_stats.values()
            if stats['count'] > 0
        ]) if self.interaction_stats else 0.0
        
        return {
            'total_interactions': total_interactions,
            'average_success_rate': avg_success_rate,
            'learned_patterns': len(self.user_patterns['frequent_queries']),
            'feedback_received': len(self.feedback_log),
            'action_stats': dict(self.interaction_stats)
        }
    
    async def get_learning_insights(self):
        """
        Получение инсайтов из обучения
        
        Returns:
            list: Список инсайтов
        """
        insights = []
        
        # Анализ частых запросов
        top_queries = self.user_patterns['frequent_queries'].most_common(3)
        if top_queries:
            insights.append(
                f"Наиболее частые запросы: {', '.join([q for q, _ in top_queries])}"
            )
        
        # Анализ временных паттернов
        time_pattern_counts = {
            hour: len(intents) 
            for hour, intents in self.user_patterns['time_patterns'].items()
        }
        
        if time_pattern_counts:
            peak_hour = max(time_pattern_counts, key=time_pattern_counts.get)
            insights.append(
                f"Пик активности в {peak_hour}:00"
            )
        
        # Анализ эффективности
        progress = await self.analyze_learning_progress()
        if progress['average_success_rate'] > 0.7:
            insights.append("Высокая точность распознавания намерений")
        elif progress['average_success_rate'] < 0.5:
            insights.append("Требуется дополнительное обучение")
        
        return insights
    
    async def adaptive_response_selection(self, intent, possible_responses):
        """
        Выбор наилучшего ответа на основе обучения
        
        Args:
            intent: Намерение запроса
            possible_responses: Список возможных ответов
            
        Returns:
            str: Выбранный ответ
        """
        action = intent.get('action', 'unknown')
        
        # Если есть статистика по этому действию
        if action in self.interaction_stats:
            stats = self.interaction_stats[action]
            
            # Если высокая успешность, используем проверенный подход
            if stats['success_rate'] > 0.8 and stats['count'] > 5:
                # Загрузка успешных паттернов
                patterns_file = self.learning_data_path / f"successful_patterns_{action}.jsonl"
                
                if patterns_file.exists():
                    # Поиск наиболее похожего успешного паттерна
                    # (упрощенная версия)
                    return possible_responses[0] if possible_responses else ""
        
        # По умолчанию - первый ответ
        return possible_responses[0] if possible_responses else ""
    
    async def fine_tune_on_corrections(self):
        """
        Дообучение на основе исправлений пользователя
        Эта функция должна периодически вызываться для улучшения модели
        """
        if not self.user_patterns['correction_history']:
            logger.info("Нет исправлений для обучения")
            return
        
        logger.info(f"Обработка {len(self.user_patterns['correction_history'])} исправлений...")
        
        # Здесь должна быть логика fine-tuning модели
        # Для полноценного обучения требуется:
        # 1. Сбор пар (неправильный ответ, правильный ответ)
        # 2. Fine-tuning языковой модели на этих данных
        # 3. Обновление весов модели
        
        # Пока сохраняем для будущего использования
        corrections_file = self.learning_data_path / "corrections_dataset.jsonl"
        with open(corrections_file, 'w', encoding='utf-8') as f:
            for correction in self.user_patterns['correction_history']:
                f.write(json.dumps(correction, ensure_ascii=False) + '\n')
        
        logger.info(f"Датасет исправлений сохранен в {corrections_file}")
