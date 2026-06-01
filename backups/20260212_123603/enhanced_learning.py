# -*- coding: utf-8 -*-
"""
🧠 ENHANCED LEARNING SYSTEM - Умная система обучения
Включает:
- Очистку и валидацию данных
- Извлечение структурированных знаний
- Мониторинг качества обучения
- Адаптивную стратегию обучения
"""

import logging
import re
import numpy as np
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
import hashlib

logger = logging.getLogger(__name__)


class ContentCleaner:
    """Очистка и валидация обучающих данных"""
    
    SPAM_PHRASES = [
        'cookie policy', 'accept cookies', 'privacy policy',
        'subscribe to newsletter', 'sign up', 'advertisement',
        'terms of service', 'read more', 'click here',
        'buy now', 'shop now', 'limited offer'
    ]
    
    HTML_PATTERNS = [
        r'<[^>]+>',  # HTML теги
        r'&[a-z]+;',  # HTML entities
        r'<!--.*?-->',  # HTML комментарии
    ]
    
    @classmethod
    def clean(cls, content: str, topic: str) -> Optional[str]:
        """
        Полная очистка контента
        
        Args:
            content: Исходный текст
            topic: Тема для проверки релевантности
            
        Returns:
            Очищенный текст или None если контент некачественный
        """
        if not content or len(content) < 100:
            return None
        
        # 1. Удаляем HTML
        for pattern in cls.HTML_PATTERNS:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # 2. Нормализуем пробелы
        content = re.sub(r'\s+', ' ', content).strip()
        
        # 3. Удаляем повторяющиеся фразы (копипаста)
        content = cls._remove_duplicates(content)
        
        # 4. Проверяем релевантность
        if not cls._is_relevant(content, topic):
            logger.debug(f"Контент не релевантен теме '{topic}'")
            return None
        
        # 5. Удаляем спам
        content = cls._remove_spam(content)
        
        # 6. Финальная проверка длины
        if len(content) < 150:
            return None
        
        return content[:5000]  # Ограничиваем размер
    
    @staticmethod
    def _remove_duplicates(text: str) -> str:
        """Удаление повторяющихся предложений"""
        sentences = re.split(r'[.!?]+', text)
        seen = set()
        unique_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip().lower()
            if sentence and sentence not in seen and len(sentence) > 10:
                seen.add(sentence)
                unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences) + '.'
    
    @staticmethod
    def _is_relevant(content: str, topic: str) -> bool:
        """Проверка релевантности контента теме"""
        topic_words = set(topic.lower().split())
        content_words = set(content.lower().split())
        
        # Минимум 1 слово из темы должно быть в контенте
        overlap = len(topic_words & content_words)
        
        # Или тема должна быть подстрокой контента
        topic_in_content = topic.lower() in content.lower()
        
        return overlap > 0 or topic_in_content
    
    @classmethod
    def _remove_spam(cls, content: str) -> str:
        """Удаление спам-фраз"""
        content_lower = content.lower()
        
        # Находим первое вхождение спама
        first_spam_pos = len(content)
        for phrase in cls.SPAM_PHRASES:
            pos = content_lower.find(phrase)
            if pos != -1 and pos < first_spam_pos:
                first_spam_pos = pos
        
        # Обрезаем до спама
        if first_spam_pos < len(content):
            content = content[:first_spam_pos]
        
        return content.strip()


class KnowledgeExtractor:
    """Извлечение структурированных знаний из текста"""
    
    # Паттерны для извлечения фактов
    DEFINITION_PATTERNS = [
        r'(.+?)\s+is\s+a\s+(.+?)[\.,]',
        r'(.+?)\s+является\s+(.+?)[\.,]',
        r'(.+?)\s+это\s+(.+?)[\.,]',
        r'(.+?)\s+—\s+(.+?)[\.,]',
    ]
    
    RELATIONSHIP_PATTERNS = [
        (r'(.+?)\s+created\s+(.+?)[\.,]', 'created'),
        (r'(.+?)\s+invented\s+(.+?)[\.,]', 'invented'),
        (r'(.+?)\s+founded\s+(.+?)[\.,]', 'founded'),
        (r'(.+?)\s+wrote\s+(.+?)[\.,]', 'wrote'),
        (r'(.+?)\s+directed\s+(.+?)[\.,]', 'directed'),
        (r'(.+?)\s+создал\s+(.+?)[\.,]', 'created'),
        (r'(.+?)\s+изобрёл\s+(.+?)[\.,]', 'invented'),
        (r'(.+?)\s+основал\s+(.+?)[\.,]', 'founded'),
    ]
    
    @classmethod
    def extract_facts(cls, text: str, topic: str) -> List[str]:
        """
        Извлечение фактов из текста
        
        Returns:
            Список фактов (до 10 самых важных)
        """
        facts = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Определения
            for pattern in cls.DEFINITION_PATTERNS:
                if re.search(pattern, sentence, re.IGNORECASE):
                    facts.append(sentence)
                    break
            
            # Даты и временные события
            if re.search(r'\b(19|20)\d{2}\b', sentence):
                facts.append(sentence)
            
            # Числовые данные
            if re.search(r'\d+\s*(процентов|%|км|метров|млн|млрд|тысяч)', sentence, re.IGNORECASE):
                facts.append(sentence)
            
            # Важные слова
            if any(word in sentence.lower() for word in ['first', 'largest', 'highest', 'important', 'главный', 'первый', 'самый']):
                facts.append(sentence)
        
        # Убираем дубликаты и сортируем по важности
        facts = list(dict.fromkeys(facts))
        
        # Оцениваем важность
        scored_facts = []
        for fact in facts:
            score = cls._score_fact_importance(fact, topic)
            scored_facts.append((fact, score))
        
        scored_facts.sort(key=lambda x: x[1], reverse=True)
        
        return [fact for fact, score in scored_facts[:10]]
    
    @classmethod
    def _score_fact_importance(cls, fact: str, topic: str) -> float:
        """Оценка важности факта"""
        score = 0.0
        
        # Содержит тему
        if topic.lower() in fact.lower():
            score += 1.0
        
        # Содержит числа
        if re.search(r'\d+', fact):
            score += 0.5
        
        # Содержит даты
        if re.search(r'\b(19|20)\d{2}\b', fact):
            score += 0.3
        
        # Содержит важные слова
        important_words = ['first', 'largest', 'most', 'главный', 'первый', 'самый', 'важнейший']
        if any(word in fact.lower() for word in important_words):
            score += 0.4
        
        # Длина (средние факты обычно полезнее)
        if 50 < len(fact) < 200:
            score += 0.2
        
        return score
    
    @classmethod
    def extract_relationships(cls, text: str, topic: str) -> List[Dict]:
        """
        Извлечение связей между сущностями
        
        Returns:
            Список словарей с отношениями
        """
        relationships = []
        
        for pattern, rel_type in cls.RELATIONSHIP_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                subject = match.group(1).strip()
                obj = match.group(2).strip()
                
                # Фильтруем слишком длинные или короткие
                if 3 < len(subject) < 100 and 3 < len(obj) < 100:
                    relationships.append({
                        'subject': subject,
                        'relation': rel_type,
                        'object': obj,
                        'confidence': 0.7
                    })
        
        return relationships[:20]  # Максимум 20 связей
    
    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, List[str]]:
        """
        Извлечение именованных сущностей
        
        Returns:
            Словарь {тип: [сущности]}
        """
        entities = {
            'people': set(),
            'organizations': set(),
            'locations': set(),
            'dates': set(),
            'numbers': set()
        }
        
        # Даты
        date_matches = re.finditer(r'\b(19|20)\d{2}\b', text)
        for match in date_matches:
            entities['dates'].add(match.group(0))
        
        # Числа с единицами
        number_matches = re.finditer(r'\d+\s*(?:млн|млрд|тысяч|%|км|м)', text, re.IGNORECASE)
        for match in number_matches:
            entities['numbers'].add(match.group(0))
        
        # Заглавные слова (потенциальные имена/названия)
        # Фразы из 2-3 заглавных слов
        cap_phrases = re.finditer(r'\b([A-ZА-Я][a-zа-я]+(?:\s+[A-ZА-Я][a-zа-я]+){1,2})\b', text)
        for match in cap_phrases:
            phrase = match.group(1)
            # Эвристика: если 2+ слова, вероятно человек или организация
            words = phrase.split()
            if len(words) == 2:
                entities['people'].add(phrase)
            elif len(words) >= 3:
                entities['organizations'].add(phrase)
        
        # Конвертируем sets в lists
        return {k: list(v)[:10] for k, v in entities.items()}


class LearningQualityMonitor:
    """Мониторинг качества обучения"""
    
    def __init__(self):
        self.metrics = {
            'content_quality_scores': [],
            'topics_processed': Counter(),
            'facts_extracted': 0,
            'low_quality_rejected': 0,
            'total_processed': 0
        }
    
    def evaluate_content_quality(self, topic: str, content: str, metadata: Dict) -> float:
        """
        Оценка качества контента (0.0 - 1.0)
        
        Критерии:
        - Релевантность теме (0-0.3)
        - Информативность (0-0.3)
        - Структурированность (0-0.2)
        - Уникальность (0-0.2)
        """
        score = 0.0
        
        # 1. Релевантность (0-0.3)
        topic_words = set(topic.lower().split())
        content_words = set(content.lower().split())
        if topic_words:
            relevance = len(topic_words & content_words) / len(topic_words)
            score += min(relevance, 0.3)
        
        # 2. Информативность (0-0.3)
        # Содержит числа
        if re.search(r'\d+', content):
            score += 0.1
        
        # Содержит даты
        if re.search(r'\b(19|20)\d{2}\b', content):
            score += 0.1
        
        # Содержит сущности (заглавные слова)
        if re.search(r'[A-ZА-Я][a-zа-я]+\s+[A-ZА-Я][a-zа-я]+', content):
            score += 0.1
        
        # 3. Структурированность (0-0.2)
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) >= 3:
            score += 0.1
        
        # Есть абзацы
        if '\n' in content:
            score += 0.1
        
        # 4. Уникальность (0-0.2)
        is_unique = metadata.get('is_unique', True)
        if is_unique:
            score += 0.2
        
        # Записываем метрику
        self.metrics['content_quality_scores'].append(score)
        self.metrics['topics_processed'][topic] += 1
        self.metrics['total_processed'] += 1
        
        if score < 0.4:
            self.metrics['low_quality_rejected'] += 1
        
        return score
    
    def record_facts_extracted(self, count: int):
        """Записать количество извлечённых фактов"""
        self.metrics['facts_extracted'] += count
    
    def get_statistics(self) -> Dict:
        """Получить статистику обучения"""
        scores = self.metrics['content_quality_scores']
        
        if not scores:
            return {
                'avg_quality': 0.0,
                'total_processed': 0,
                'status': 'NO_DATA'
            }
        
        avg_quality = np.mean(scores)
        
        return {
            'avg_quality': avg_quality,
            'min_quality': np.min(scores),
            'max_quality': np.max(scores),
            'total_processed': self.metrics['total_processed'],
            'facts_extracted': self.metrics['facts_extracted'],
            'low_quality_rejected': self.metrics['low_quality_rejected'],
            'rejection_rate': self.metrics['low_quality_rejected'] / self.metrics['total_processed'] if self.metrics['total_processed'] > 0 else 0,
            'top_topics': self.metrics['topics_processed'].most_common(10),
            'status': 'EXCELLENT' if avg_quality > 0.7 else 'GOOD' if avg_quality > 0.5 else 'NEEDS_IMPROVEMENT'
        }
    
    def get_report(self) -> str:
        """Получить текстовый отчёт"""
        stats = self.get_statistics()
        
        if stats['status'] == 'NO_DATA':
            return "📊 Недостаточно данных для анализа"
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║          📊 ОТЧЁТ О КАЧЕСТВЕ ОБУЧЕНИЯ                     ║
╚══════════════════════════════════════════════════════════╝

📈 МЕТРИКИ КАЧЕСТВА:
   • Средняя оценка:        {stats['avg_quality']:.2%}
   • Диапазон:              {stats['min_quality']:.2%} - {stats['max_quality']:.2%}
   • Статус:                {stats['status']}

📚 ОБРАБОТКА ДАННЫХ:
   • Всего обработано:      {stats['total_processed']}
   • Фактов извлечено:      {stats['facts_extracted']}
   • Отклонено (низкое кач.): {stats['low_quality_rejected']} ({stats['rejection_rate']:.1%})

🎯 ТОП-5 ТЕМ:
"""
        
        for topic, count in stats['top_topics'][:5]:
            report += f"   • {topic[:40]:<40} : {count:>4} записей\n"
        
        report += "\n"
        
        if stats['status'] == 'EXCELLENT':
            report += "✅ ОТЛИЧНОЕ КАЧЕСТВО - Система обучается эффективно!\n"
        elif stats['status'] == 'GOOD':
            report += "✓ ХОРОШЕЕ КАЧЕСТВО - Система работает стабильно\n"
        else:
            report += "⚠️ ТРЕБУЕТСЯ УЛУЧШЕНИЕ - Рекомендуется пересмотреть источники\n"
        
        return report


class AdaptiveLearningStrategy:
    """Адаптивная стратегия обучения"""
    
    def __init__(self, memory_system):
        self.memory = memory_system
        self.knowledge_gaps = {}
        self.topic_priorities = {}
        self.last_gap_analysis = None
    
    def analyze_knowledge_gaps(self) -> Dict[str, float]:
        """
        Анализ пробелов в знаниях
        
        Returns:
            Словарь {тема: важность_пробела}
        """
        try:
            all_data = self.memory.collection.get()
            
            if not all_data['metadatas']:
                return {}
            
            # Подсчитываем покрытие тем
            topic_coverage = Counter()
            for metadata in all_data['metadatas']:
                topic = metadata.get('topic', 'unknown')
                topic_coverage[topic] += 1
            
            # Вычисляем среднее покрытие
            avg_coverage = np.mean(list(topic_coverage.values())) if topic_coverage else 1
            
            # Находим пробелы
            gaps = {}
            for topic, count in topic_coverage.items():
                if count < avg_coverage * 0.6:  # Менее 60% от среднего
                    gap_size = (avg_coverage - count) / avg_coverage
                    gaps[topic] = gap_size
            
            self.knowledge_gaps = gaps
            self.last_gap_analysis = datetime.now()
            
            logger.info(f"Обнаружено пробелов в знаниях: {len(gaps)}")
            
            return gaps
            
        except Exception as e:
            logger.error(f"Ошибка анализа пробелов: {e}")
            return {}
    
    def prioritize_topics(self, available_topics: List[str]) -> List[str]:
        """
        Приоритизация тем для обучения
        
        Args:
            available_topics: Доступные темы
            
        Returns:
            Отсортированный список тем по приоритету
        """
        scored_topics = []
        
        for topic in available_topics:
            score = self._calculate_topic_priority(topic)
            scored_topics.append((topic, score))
        
        # Сортируем по убыванию приоритета
        scored_topics.sort(key=lambda x: x[1], reverse=True)
        
        # Сохраняем приоритеты
        self.topic_priorities = {topic: score for topic, score in scored_topics}
        
        return [topic for topic, score in scored_topics]
    
    def _calculate_topic_priority(self, topic: str) -> float:
        """Вычисление приоритета темы"""
        priority = 1.0  # Базовый приоритет
        
        # 1. Пробелы в знаниях (вес: 2.0)
        if topic in self.knowledge_gaps:
            priority += self.knowledge_gaps[topic] * 2.0
        
        # 2. Трендовость (вес: 1.5)
        if self._is_trending(topic):
            priority += 1.5
        
        # 3. Актуальность (вес: 1.0)
        if self._is_current_topic(topic):
            priority += 1.0
        
        # 4. Сложность/Глубина (вес: 0.5)
        # Более специфичные темы получают бонус
        if len(topic.split()) > 2:
            priority += 0.5
        
        return priority
    
    @staticmethod
    def _is_trending(topic: str) -> bool:
        """Проверка трендовости темы"""
        trending_keywords = [
            'AI', 'ChatGPT', 'GPT', '2025', '2026',
            'нейросеть', 'искусственный интеллект',
            'блокчейн', 'квантов', 'новый', 'последний'
        ]
        
        return any(kw.lower() in topic.lower() for kw in trending_keywords)
    
    @staticmethod
    def _is_current_topic(topic: str) -> bool:
        """Проверка актуальности темы"""
        current_year = datetime.now().year
        
        # Содержит текущий или следующий год
        if str(current_year) in topic or str(current_year + 1) in topic:
            return True
        
        # Содержит слова актуальности
        current_keywords = ['сегодня', 'сейчас', 'текущий', 'modern', 'current', 'latest']
        return any(kw in topic.lower() for kw in current_keywords)
    
    def get_learning_recommendations(self, n: int = 10) -> List[Tuple[str, str]]:
        """
        Получить рекомендации для обучения
        
        Args:
            n: Количество рекомендаций
            
        Returns:
            Список (тема, причина)
        """
        recommendations = []
        
        # Обновляем анализ пробелов если давно не обновляли
        if not self.last_gap_analysis or \
           (datetime.now() - self.last_gap_analysis).seconds > 3600:
            self.analyze_knowledge_gaps()
        
        # Рекомендуем заполнить пробелы
        for topic, gap_size in sorted(self.knowledge_gaps.items(), 
                                      key=lambda x: x[1], 
                                      reverse=True)[:n]:
            reason = f"Пробел в знаниях (недостаток: {gap_size:.0%})"
            recommendations.append((topic, reason))
        
        return recommendations


# ============================================================================
# ГЛАВНЫЙ КЛАСС - ИНТЕГРАЦИЯ ВСЕХ КОМПОНЕНТОВ
# ============================================================================

class EnhancedLearningSystem:
    """
    Улучшенная система обучения - интеграция всех компонентов
    
    Использование:
        enhanced_learning = EnhancedLearningSystem(memory_system)
        success = await enhanced_learning.learn_from_content(topic, content, metadata)
        report = enhanced_learning.get_quality_report()
    """
    
    def __init__(self, memory_system):
        self.memory = memory_system
        
        # Компоненты
        self.cleaner = ContentCleaner()
        self.extractor = KnowledgeExtractor()
        self.quality_monitor = LearningQualityMonitor()
        self.learning_strategy = AdaptiveLearningStrategy(memory_system)
        
        logger.info("✅ Enhanced Learning System инициализирована")
    
    async def learn_from_content(self, topic: str, content: str, metadata: Dict = None) -> bool:
        """
        Умное обучение из контента
        
        Args:
            topic: Тема
            content: Контент для обучения
            metadata: Дополнительные метаданные
            
        Returns:
            True если обучение успешно
        """
        if metadata is None:
            metadata = {}
        
        # 1. ОЧИСТКА
        clean_content = self.cleaner.clean(content, topic)
        if not clean_content:
            logger.debug(f"❌ Контент отклонён при очистке: {topic}")
            return False
        
        # 2. ОЦЕНКА КАЧЕСТВА
        quality_score = self.quality_monitor.evaluate_content_quality(
            topic, clean_content, metadata
        )
        
        if quality_score < 0.4:
            logger.info(f"⚠️ Низкое качество ({quality_score:.2f}): {topic}")
            return False
        
        logger.info(f"✓ Качество {quality_score:.2f}: {topic}")
        
        # 3. ИЗВЛЕЧЕНИЕ ЗНАНИЙ
        facts = self.extractor.extract_facts(clean_content, topic)
        relationships = self.extractor.extract_relationships(clean_content, topic)
        entities = self.extractor.extract_entities(clean_content)
        
        self.quality_monitor.record_facts_extracted(len(facts))
        
        # 4. СОХРАНЕНИЕ В ПАМЯТЬ
        saved_count = 0
        
        # 4a. Основной контент (чанки)
        chunks = self._split_content(clean_content, max_size=500)
        for idx, chunk in enumerate(chunks[:5]):
            await self.memory.store_memory(
                f"{topic}: {chunk}",
                memory_type="knowledge",
                metadata={
                    'topic': topic,
                    'source': metadata.get('source', 'web_crawler'),
                    'quality_score': quality_score,
                    'auto_learned': True,
                    'chunk_index': idx,
                    'total_chunks': len(chunks),
                    'importance': quality_score
                }
            )
            saved_count += 1
        
        # 4b. Факты (отдельно, с высоким приоритетом)
        for fact in facts[:10]:
            await self.memory.store_memory(
                fact,
                memory_type="fact",
                metadata={
                    'topic': topic,
                    'source': 'extracted',
                    'importance': 0.9,
                    'auto_learned': True
                }
            )
            saved_count += 1
        
        # 4c. Отношения
        for rel in relationships[:5]:
            rel_text = f"{rel['subject']} {rel['relation']} {rel['object']}"
            await self.memory.store_memory(
                rel_text,
                memory_type="relationship",
                metadata={
                    'topic': topic,
                    'source': 'extracted',
                    'importance': 0.8,
                    'auto_learned': True,
                    'relation_type': rel['relation']
                }
            )
            saved_count += 1
        
        logger.info(f"💾 Сохранено {saved_count} записей для '{topic}'")
        
        return True
    
    @staticmethod
    def _split_content(content: str, max_size: int = 500) -> List[str]:
        """Разбивка контента на чанки"""
        # Разбиваем по предложениям
        sentences = re.split(r'[.!?]+', content)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) < max_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_quality_report(self) -> str:
        """Получить отчёт о качестве обучения"""
        return self.quality_monitor.get_report()
    
    def get_statistics(self) -> Dict:
        """Получить статистику обучения"""
        return self.quality_monitor.get_statistics()
    
    def get_learning_recommendations(self, n: int = 10) -> List[Tuple[str, str]]:
        """Получить рекомендации по темам для обучения"""
        return self.learning_strategy.get_learning_recommendations(n)
    
    def analyze_knowledge_gaps(self) -> Dict[str, float]:
        """Анализ пробелов в знаниях"""
        return self.learning_strategy.analyze_knowledge_gaps()
    
    def prioritize_topics(self, topics: List[str]) -> List[str]:
        """Приоритизация тем для обучения"""
        return self.learning_strategy.prioritize_topics(topics)


# Пример использования
if __name__ == "__main__":
    print("="*70)
    print("🧠 ENHANCED LEARNING SYSTEM - Тестирование компонентов")
    print("="*70)
    print()
    
    # Тест очистки
    print("1. Тест очистки контента:")
    test_content = """
    <div>Python is a programming language</div>
    Python was created by Guido van Rossum in 1991.
    Subscribe to our newsletter!
    Python is widely used in AI and ML.
    Click here to buy now!
    """
    cleaned = ContentCleaner.clean(test_content, "Python")
    print(f"   Исходный: {len(test_content)} символов")
    print(f"   Очищенный: {len(cleaned) if cleaned else 0} символов")
    print(f"   Результат: {cleaned}")
    print()
    
    # Тест извлечения знаний
    print("2. Тест извлечения знаний:")
    facts = KnowledgeExtractor.extract_facts(cleaned or test_content, "Python")
    print(f"   Извлечено фактов: {len(facts)}")
    for i, fact in enumerate(facts, 1):
        print(f"   {i}. {fact}")
    print()
    
    print("✅ Все компоненты работают!")
