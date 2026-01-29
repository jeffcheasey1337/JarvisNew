"""
Модуль автономного обучения JARVIS из интернета
Система самостоятельно ищет, анализирует и изучает информацию в интернете
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import random
from typing import List, Dict
import feedparser
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import hashlib

logger = logging.getLogger(__name__)


class AutonomousLearning:
    """Автономная система обучения из интернета"""
    
    def __init__(self, config, memory_system, nlp_processor):
        self.config = config
        self.memory = memory_system
        self.nlp = nlp_processor
        
        # Параметры обучения
        self.learning_enabled = config.get('autonomous_learning', {}).get('enabled', True)
        self.learning_interval = config.get('autonomous_learning', {}).get('interval_hours', 6)
        self.topics_of_interest = self._load_topics()
        
        # Источники для обучения
        self.news_sources = self._get_news_sources()
        self.learning_queries = []
        
        # Статистика
        self.stats = {
            'articles_processed': 0,
            'knowledge_items_learned': 0,
            'last_learning_session': None
        }
        
        logger.info("🌐 Система автономного обучения инициализирована")
    
    def _load_topics(self) -> List[str]:
        """Загрузка тем для изучения"""
        topics_file = Path("data/learning_topics.json")
        
        if topics_file.exists():
            with open(topics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('topics', [])
        
        # Темы по умолчанию
        default_topics = [
            "искусственный интеллект",
            "машинное обучение",
            "нейронные сети",
            "технологии",
            "наука",
            "программирование",
            "космос",
            "робототехника",
            "квантовые компьютеры",
            "биотехнологии"
        ]
        
        self._save_topics(default_topics)
        return default_topics
    
    def _save_topics(self, topics: List[str]):
        """Сохранение тем"""
        topics_file = Path("data/learning_topics.json")
        with open(topics_file, 'w', encoding='utf-8') as f:
            json.dump({'topics': topics}, f, ensure_ascii=False, indent=2)
    
    def _get_news_sources(self) -> List[Dict]:
        """RSS-ленты для обучения"""
        return [
            {
                'name': 'Habr',
                'url': 'https://habr.com/ru/rss/hub/artificial_intelligence/all/',
                'category': 'AI'
            },
            {
                'name': 'Arxiv AI',
                'url': 'http://export.arxiv.org/rss/cs.AI',
                'category': 'Research'
            },
            {
                'name': 'MIT News AI',
                'url': 'https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml',
                'category': 'Research'
            },
            {
                'name': 'TechCrunch',
                'url': 'https://techcrunch.com/feed/',
                'category': 'Tech'
            }
        ]
    
    async def start_continuous_learning(self):
        """
        Запуск непрерывного обучения
        Работает в фоне и периодически изучает новую информацию
        """
        if not self.learning_enabled:
            logger.info("⏸️  Автономное обучение отключено в конфигурации")
            return
        
        logger.info("🚀 Запуск непрерывного обучения из интернета")
        logger.info(f"📊 Интервал обучения: каждые {self.learning_interval} часов")
        
        while True:
            try:
                # Сессия обучения
                await self.learning_session()
                
                # Пауза до следующей сессии
                wait_seconds = self.learning_interval * 3600
                logger.info(f"💤 Следующая сессия через {self.learning_interval} часов")
                await asyncio.sleep(wait_seconds)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в сессии обучения: {e}")
                await asyncio.sleep(3600)  # Пауза час при ошибке
    
    async def learning_session(self):
        """Одна сессия обучения"""
        logger.info("=" * 60)
        logger.info("🧠 НАЧАЛО СЕССИИ ОБУЧЕНИЯ")
        logger.info("=" * 60)
        
        session_start = datetime.now()
        learned_items = 0
        
        # 1. Обучение из новостных лент
        logger.info("📰 Изучение новостных RSS-лент...")
        learned_items += await self._learn_from_rss_feeds()
        
        # 2. Поиск по интересующим темам
        logger.info("🔍 Поиск информации по темам...")
        learned_items += await self._learn_from_search()
        
        # 3. Изучение трендовых тем
        logger.info("📈 Анализ трендов...")
        learned_items += await self._learn_trending_topics()
        
        # 4. Углубленное изучение конкретных статей
        logger.info("📖 Детальный анализ статей...")
        learned_items += await self._deep_article_analysis()
        
        # 5. Обновление интересов на основе выученного
        await self._update_interests()
        
        # Статистика сессии
        session_duration = (datetime.now() - session_start).total_seconds()
        self.stats['articles_processed'] += learned_items
        self.stats['knowledge_items_learned'] += learned_items
        self.stats['last_learning_session'] = datetime.now().isoformat()
        
        logger.info("=" * 60)
        logger.info(f"✅ СЕССИЯ ЗАВЕРШЕНА")
        logger.info(f"📊 Изучено элементов: {learned_items}")
        logger.info(f"⏱️  Время: {session_duration:.1f} сек")
        logger.info(f"📚 Всего знаний: {self.stats['knowledge_items_learned']}")
        logger.info("=" * 60)
        
        self._save_stats()
    
    async def _learn_from_rss_feeds(self) -> int:
        """Обучение из RSS-лент"""
        learned = 0
        
        for source in self.news_sources:
            try:
                logger.info(f"  📡 Подключение к {source['name']}...")
                
                # Парсинг RSS
                feed = feedparser.parse(source['url'])
                
                # Обработка последних 5 статей
                for entry in feed.entries[:5]:
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    link = entry.get('link', '')
                    
                    if not title:
                        continue
                    
                    # Проверка, не изучали ли уже
                    if await self._already_learned(link):
                        continue
                    
                    # Создание знания
                    knowledge = f"Статья: {title}. {summary}"
                    
                    # Сохранение в память
                    await self.memory.store_memory(
                        knowledge,
                        memory_type="learned_knowledge",
                        metadata={
                            'source': source['name'],
                            'category': source['category'],
                            'url': link,
                            'learned_at': datetime.now().isoformat()
                        }
                    )
                    
                    learned += 1
                    logger.info(f"    ✅ Изучено: {title[:60]}...")
                
            except Exception as e:
                logger.error(f"  ❌ Ошибка с {source['name']}: {e}")
        
        return learned
    
    async def _learn_from_search(self) -> int:
        """Активный поиск информации по темам"""
        learned = 0
        
        # Выбираем случайные темы для изучения
        topics_to_learn = random.sample(
            self.topics_of_interest, 
            min(3, len(self.topics_of_interest))
        )
        
        for topic in topics_to_learn:
            try:
                logger.info(f"  🔍 Поиск по теме: {topic}")
                
                # Поиск через DuckDuckGo
                with DDGS() as ddgs:
                    results = list(ddgs.text(
                        f"{topic} новости исследования 2024 2025",
                        max_results=3
                    ))
                
                for result in results:
                    title = result.get('title', '')
                    body = result.get('body', '')
                    url = result.get('href', '')
                    
                    if await self._already_learned(url):
                        continue
                    
                    # Извлечение ключевой информации через NLP
                    knowledge = f"Тема '{topic}': {title}. {body}"
                    
                    # Сохранение
                    await self.memory.store_memory(
                        knowledge,
                        memory_type="learned_knowledge",
                        metadata={
                            'source': 'web_search',
                            'topic': topic,
                            'url': url,
                            'learned_at': datetime.now().isoformat(),
                            'importance': 0.7
                        }
                    )
                    
                    learned += 1
                    logger.info(f"    ✅ {title[:50]}...")
                
                # Пауза между запросами
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"  ❌ Ошибка поиска по '{topic}': {e}")
        
        return learned
    
    async def _learn_trending_topics(self) -> int:
        """Изучение трендовых тем"""
        learned = 0
        
        try:
            # Поиск трендов
            trending_queries = [
                "AI новости сегодня",
                "технологические прорывы 2025",
                "последние открытия в науке"
            ]
            
            query = random.choice(trending_queries)
            logger.info(f"  📈 Анализ трендов: {query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
            
            for result in results:
                if await self._already_learned(result.get('href', '')):
                    continue
                
                knowledge = f"Тренд: {result.get('title', '')}. {result.get('body', '')}"
                
                await self.memory.store_memory(
                    knowledge,
                    memory_type="learned_knowledge",
                    metadata={
                        'source': 'trending',
                        'url': result.get('href', ''),
                        'learned_at': datetime.now().isoformat(),
                        'importance': 0.8
                    }
                )
                
                learned += 1
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка анализа трендов: {e}")
        
        return learned
    
    async def _deep_article_analysis(self) -> int:
        """Углубленный анализ полного текста статей"""
        learned = 0
        
        # Выбираем несколько URL для детального изучения
        try:
            # Получаем недавно найденные статьи
            recent_articles = await self._get_recent_urls(limit=2)
            
            for url in recent_articles:
                try:
                    logger.info(f"  📖 Детальное изучение: {url[:50]}...")
                    
                    # Скачивание и парсинг страницы
                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Извлечение основного текста
                    paragraphs = soup.find_all('p')
                    text = ' '.join([p.get_text() for p in paragraphs[:10]])
                    
                    if len(text) < 100:
                        continue
                    
                    # Суммаризация через NLP
                    summary = await self.nlp.summarize_text(text, max_length=200)
                    
                    # Сохранение детального знания
                    await self.memory.store_memory(
                        f"Детальное изучение: {summary}",
                        memory_type="deep_knowledge",
                        metadata={
                            'source': 'deep_analysis',
                            'url': url,
                            'learned_at': datetime.now().isoformat(),
                            'importance': 0.9
                        }
                    )
                    
                    learned += 1
                    await asyncio.sleep(3)  # Пауза между запросами
                    
                except Exception as e:
                    logger.error(f"    ❌ Ошибка анализа {url}: {e}")
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка детального анализа: {e}")
        
        return learned
    
    async def _already_learned(self, url: str) -> bool:
        """Проверка, не изучали ли уже этот URL"""
        if not url:
            return True
        
        # Создаем хэш URL для быстрой проверки
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Ищем в памяти
        try:
            results = await self.memory.recall_memory(url_hash, n_results=1)
            return len(results) > 0
        except:
            return False
    
    async def _get_recent_urls(self, limit: int = 5) -> List[str]:
        """Получение недавно найденных URL для детального изучения"""
        # Здесь можно реализовать выборку из базы памяти
        # Пока возвращаем пустой список
        return []
    
    async def _update_interests(self):
        """Обновление тем интереса на основе выученного"""
        try:
            # Анализ часто встречающихся тем
            # Можно расширить темы, которые часто появляются
            
            logger.info("  🎯 Обновление интересов...")
            
            # Пример: добавление новых трендовых тем
            new_topics = []
            
            # Поиск новых интересных тем через анализ выученного
            # (упрощенная версия)
            
            if new_topics:
                self.topics_of_interest.extend(new_topics)
                self.topics_of_interest = list(set(self.topics_of_interest))  # Убираем дубли
                self._save_topics(self.topics_of_interest)
                logger.info(f"    ✅ Добавлено новых тем: {len(new_topics)}")
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка обновления интересов: {e}")
    
    def _save_stats(self):
        """Сохранение статистики"""
        stats_file = Path("data/learning_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    async def add_topic(self, topic: str):
        """Добавление новой темы для изучения"""
        if topic not in self.topics_of_interest:
            self.topics_of_interest.append(topic)
            self._save_topics(self.topics_of_interest)
            logger.info(f"➕ Добавлена новая тема для изучения: {topic}")
    
    async def remove_topic(self, topic: str):
        """Удаление темы из изучения"""
        if topic in self.topics_of_interest:
            self.topics_of_interest.remove(topic)
            self._save_topics(self.topics_of_interest)
            logger.info(f"➖ Тема удалена из изучения: {topic}")
    
    async def get_learning_report(self) -> Dict:
        """Получение отчета об обучении"""
        return {
            'total_articles': self.stats['articles_processed'],
            'total_knowledge': self.stats['knowledge_items_learned'],
            'last_session': self.stats['last_learning_session'],
            'topics': self.topics_of_interest,
            'sources': len(self.news_sources)
        }
    
    async def manual_learning_session(self, topic: str = None):
        """Ручной запуск сессии обучения по конкретной теме"""
        if topic:
            logger.info(f"🎯 Ручная сессия обучения по теме: {topic}")
            # Временно заменяем темы
            original_topics = self.topics_of_interest.copy()
            self.topics_of_interest = [topic]
            
            await self.learning_session()
            
            # Восстанавливаем темы
            self.topics_of_interest = original_topics
        else:
            await self.learning_session()
