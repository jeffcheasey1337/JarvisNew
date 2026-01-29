"""
НЕПРЕРЫВНАЯ система автономного обучения JARVIS 24/7
Постоянное обучение из ВСЕХ источников интернета без остановки
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import random
from typing import List, Dict, Set
import feedparser
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import hashlib
import re
import time

logger = logging.getLogger(__name__)


class ContinuousLearning:
    """Непрерывное обучение 24/7"""
    
    def __init__(self, config, memory_system, nlp_processor):
        self.config = config
        self.memory = memory_system
        self.nlp = nlp_processor
        
        # Непрерывный режим обучения
        self.continuous_mode = config.get('autonomous_learning', {}).get('continuous', True)
        self.learning_speed = config.get('autonomous_learning', {}).get('speed', 'normal')  # slow, normal, fast, turbo
        
        # Темы для изучения
        self.topics_of_interest = self._load_topics()
        
        # Уже изученные URL
        self.learned_urls = set()
        
        # Очередь источников для обучения
        self.learning_queue = asyncio.Queue()
        
        # Статистика в реальном времени
        self.stats = {
            'start_time': datetime.now(),
            'articles_processed': 0,
            'knowledge_items': 0,
            'sources_processed': 0,
            'current_topic': None,
            'learning_speed_items_per_hour': 0,
            'uptime_hours': 0
        }
        
        # Источники для непрерывного обучения
        self.all_sources = self._initialize_all_sources()
        
        logger.info(" НЕПРЕРЫВНАЯ система обучения 24/7 инициализирована")
        logger.info(f" Скорость обучения: {self.learning_speed.upper()}")
            
        # Ссылка на GUI (будет установлена позже)
        self.gui = None

    def _load_topics(self) -> List[str]:
        """Загрузка расширенного списка тем"""
        topics_file = Path("data/learning_topics.json")
        
        if topics_file.exists():
            with open(topics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('topics', [])
        
        # Максимально расширенный список тем
        mega_topics = [
            # AI и ML
            "искусственный интеллект", "машинное обучение", "нейронные сети", "deep learning",
            "computer vision", "NLP", "трансформеры", "GPT", "LLM", "AGI", "reinforcement learning",
            
            # Программирование (все языки)
            "Python", "JavaScript", "TypeScript", "Rust", "Go", "C++", "Java", "Kotlin",
            "Swift", "Ruby", "PHP", "Scala", "Haskell", "Elixir", "Clojure",
            
            # Фреймворки
            "React", "Vue", "Angular", "Django", "FastAPI", "Flask", "Express",
            "Next.js", "PyTorch", "TensorFlow", "Keras", "scikit-learn",
            
            # DevOps и инфраструктура
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "GitHub Actions",
            "Terraform", "Ansible", "микросервисы", "serverless",
            
            # Базы данных
            "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "векторные базы данных",
            "ChromaDB", "Pinecone", "Qdrant",
            
            # Наука
            "квантовая физика", "астрофизика", "биология", "химия", "математика",
            "квантовые компьютеры", "термоядерный синтез", "CRISPR", "генная инженерия",
            
            # Космос
            "SpaceX", "NASA", "Mars", "космические технологии", "ракеты", "спутники",
            "астрономия", "экзопланеты",
            
            # Робототехника
            "роботы", "Boston Dynamics", "автономные системы", "дроны", "беспилотники",
            "промышленная автоматизация",
            
            # Блокчейн и Web3
            "blockchain", "Ethereum", "Bitcoin", "криптовалюты", "DeFi", "NFT",
            "Web3", "смарт-контракты", "децентрализация",
            
            # Медицина и биотех
            "биотехнологии", "медицинские технологии", "нейротехнологии",
            "brain-computer interface", "персонализированная медицина", "ИИ в медицине",
            
            # Энергетика
            "солнечная энергия", "ветряная энергия", "ядерная энергия",
            "батареи", "накопители энергии", "водород",
            
            # Бизнес и стартапы
            "стартапы", "венчурный капитал", "Y Combinator", "технологический бизнес",
            "SaaS", "монетизация", "рост продукта",
            
            # Дизайн и UX
            "UI/UX", "дизайн интерфейсов", "Figma", "прототипирование",
            
            # Кибербезопасность
            "кибербезопасность", "этичный хакинг", "пентестинг", "encryption",
            
            # AR/VR
            "виртуальная реальность", "дополненная реальность", "метавселенная",
            
            # Игры
            "gamedev", "Unity", "Unreal Engine", "инди-игры",
            
            # Общее
            "инновации", "технологические тренды", "будущее", "прорывы",
            "исследования", "открытия", "патенты"
        ]
        
        self._save_topics(mega_topics)
        return mega_topics
    
    def _save_topics(self, topics: List[str]):
        """Сохранение тем"""
        Path("data").mkdir(exist_ok=True)
        with open("data/learning_topics.json", 'w', encoding='utf-8') as f:
            json.dump({'topics': topics}, f, ensure_ascii=False, indent=2)
    
    def _initialize_all_sources(self) -> Dict:
        """Инициализация ВСЕХ возможных источников"""
        return {
            # RSS-ленты (новости и блоги)
            'rss': [
                {'name': 'Habr AI', 'url': 'https://habr.com/ru/rss/hub/artificial_intelligence/all/'},
                {'name': 'Habr ML', 'url': 'https://habr.com/ru/rss/hub/machine_learning/all/'},
                {'name': 'Habr Python', 'url': 'https://habr.com/ru/rss/hub/python/all/'},
                {'name': 'ArXiv AI', 'url': 'http://export.arxiv.org/rss/cs.AI'},
                {'name': 'ArXiv ML', 'url': 'http://export.arxiv.org/rss/cs.LG'},
                {'name': 'MIT News AI', 'url': 'https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml'},
                {'name': 'TechCrunch', 'url': 'https://techcrunch.com/feed/'},
                {'name': 'Hacker News', 'url': 'https://news.ycombinator.com/rss'},
                {'name': 'Medium AI', 'url': 'https://medium.com/feed/tag/artificial-intelligence'},
                {'name': 'OpenAI Blog', 'url': 'https://openai.com/blog/rss.xml'},
            ],
            
            # Поисковые запросы (постоянно обновляемые)
            'search_patterns': [
                "{topic} latest news",
                "{topic} breakthrough 2025",
                "{topic} tutorial",
                "{topic} best practices",
                "{topic} research papers",
                "new {topic} technology",
                "{topic} innovations",
                "{topic} trends 2025"
            ],
            
            # Reddit (сообщества)
            'reddit': [
                'MachineLearning', 'artificial', 'deeplearning', 'learnmachinelearning',
                'programming', 'Python', 'javascript', 'webdev', 'datascience',
                'science', 'Futurology', 'technology', 'coding', 'compsci'
            ],
            
            # GitHub (трендовые репозитории)
            'github_trending': ['python', 'javascript', 'typescript', 'rust', 'go'],
            
            # Stack Overflow (новые вопросы/ответы)
            'stackoverflow_tags': ['python', 'javascript', 'machine-learning', 'deep-learning', 'ai'],
            
            # Документация популярных проектов
            'documentation': [
                'https://pytorch.org/docs/',
                'https://www.tensorflow.org/api_docs',
                'https://fastapi.tiangolo.com/',
                'https://react.dev/learn'
            ],
            
            # Академические источники
            'academic': [
                'https://arxiv.org/',
                'https://scholar.google.com/',
                'https://www.semanticscholar.org/'
            ]
        }
    
    def _get_learning_delay(self) -> float:
        """Определение задержки между запросами в зависимости от скорости"""
        delays = {
            'slow': 300,      # 5 минут между запросами
            'normal': 60,     # 1 минута
            'fast': 10,       # 10 секунд
            'turbo': 1        # 1 секунда (АГРЕССИВНО!)
        }
        return delays.get(self.learning_speed, 60)
    
    async def start_continuous_learning(self):
        """
        Запуск НЕПРЕРЫВНОГО обучения 24/7
        Работает постоянно в фоне, без остановок
        """
        if not self.continuous_mode:
            logger.info("⏸  Непрерывное обучение отключено")
            return
        
        logger.info("="*70)
        logger.info(" ЗАПУСК НЕПРЕРЫВНОГО ОБУЧЕНИЯ 24/7")
        logger.info("="*70)
        logger.info(f" Режим: {self.learning_speed.upper()}")
        logger.info(f"⏱  Задержка между запросами: {self._get_learning_delay()}сек")
        logger.info(f" Тем для изучения: {len(self.topics_of_interest)}")
        logger.info(" Начинаю впитывать знания из интернета...")
        logger.info("="*70)
        
        # Запуск параллельных процессов обучения
        tasks = [
            asyncio.create_task(self._continuous_rss_learning()),
            asyncio.create_task(self._continuous_search_learning()),
            asyncio.create_task(self._continuous_trending_learning()),
            asyncio.create_task(self._stats_updater()),
            asyncio.create_task(self._knowledge_consolidator())
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _continuous_rss_learning(self):
        """Непрерывное изучение RSS-лент"""
        logger.info(" Поток RSS-лент: ЗАПУЩЕН")
        
        while True:
            try:
                for source in self.all_sources['rss']:
                    try:
                        feed = feedparser.parse(source['url'])
                        
                        for entry in feed.entries[:3]:  # Последние 3 статьи
                            await self._process_article(
                                title=entry.get('title', ''),
                                content=entry.get('summary', ''),
                                url=entry.get('link', ''),
                                source=source['name'],
                                category='RSS'
                            )
                        
                        await asyncio.sleep(2)  # Пауза между источниками
                        
                    except Exception as e:
                        logger.debug(f"Ошибка RSS {source['name']}: {e}")
                
                # Задержка перед следующим циклом
                await asyncio.sleep(self._get_learning_delay())
                
            except Exception as e:
                logger.error(f"Критическая ошибка RSS потока: {e}")
                await asyncio.sleep(60)
    
    async def _continuous_search_learning(self):
        """Непрерывный поиск и изучение"""
        logger.info(" Поток WEB-ПОИСКА: ЗАПУЩЕН")
        
        while True:
            try:
                # Выбираем случайную тему
                topic = random.choice(self.topics_of_interest)
                self.stats['current_topic'] = topic
                
                # Выбираем случайный паттерн поиска
                pattern = random.choice(self.all_sources['search_patterns'])
                query = pattern.format(topic=topic)
                
                logger.info(f" Изучаю: {query}")
                
                # Поиск
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=5))
                
                for result in results:
                    await self._process_article(
                        title=result.get('title', ''),
                        content=result.get('body', ''),
                        url=result.get('href', ''),
                        source='Web Search',
                        category=topic
                    )
                
                await asyncio.sleep(self._get_learning_delay())
                
            except Exception as e:
                logger.debug(f"Ошибка поиска: {e}")
                await asyncio.sleep(30)
    
    async def _continuous_trending_learning(self):
        """Непрерывное изучение трендов"""
        logger.info(" Поток ТРЕНДОВ: ЗАПУЩЕН")
        
        trending_queries = [
            "AI breakthroughs today",
            "latest technology news",
            "programming trends 2025",
            "научные открытия",
            "технологические новости",
            "AI research papers",
            "github trending",
            "hacker news top"
        ]
        
        while True:
            try:
                query = random.choice(trending_queries)
                
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=3))
                
                for result in results:
                    await self._process_article(
                        title=result.get('title', ''),
                        content=result.get('body', ''),
                        url=result.get('href', ''),
                        source='Trending',
                        category='Trend'
                    )
                
                await asyncio.sleep(self._get_learning_delay() * 2)
                
            except Exception as e:
                logger.debug(f"Ошибка трендов: {e}")
                await asyncio.sleep(60)

    async def _process_article(self, title: str, content: str, url: str, source: str, category: str):
        """Обработка и сохранение статьи"""
        try:
            # Проверка, не изучали ли уже
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if url_hash in self.learned_urls:
                return

            if not title or not content:
                return

            # Создание знания
            knowledge = f"[{category}] {title}. {content[:500]}"

            # Сохранение в память
            metadata = {
                'source': source,
                'category': category,
                'url': url,
                'learned_at': datetime.now().isoformat(),
                'importance': 0.7
            }

            await self.memory.store_memory(
                knowledge,
                memory_type="continuous_learning",
                metadata=metadata
            )

            # Обновление GUI после сохранения
            self.stats['knowledge_items'] += 1
            if hasattr(self, 'gui') and self.gui:
                self.gui.add_log(f"[ОБУЧЕНИЕ] Сохранена статья: {title[:50]}...")
                self.gui.update_stat('memory_items', self.stats['knowledge_items'])

            # Обновление статистики
            self.learned_urls.add(url_hash)
            self.stats['articles_processed'] += 1
            self.stats['sources_processed'] += 1

            logger.info(f" [{self.stats['articles_processed']}] {title[:60]}...")

        except Exception as e:
            logger.debug(f"Ошибка обработки статьи: {e}")
    
    async def _stats_updater(self):
        """Обновление статистики в реальном времени"""
        logger.info(" Поток СТАТИСТИКИ: ЗАПУЩЕН")
        
        while True:
            try:
                # Расчет времени работы
                uptime = datetime.now() - self.stats['start_time']
                self.stats['uptime_hours'] = uptime.total_seconds() / 3600
                
                # Скорость обучения (элементов в час)
                if self.stats['uptime_hours'] > 0:
                    self.stats['learning_speed_items_per_hour'] = int(
                        self.stats['knowledge_items'] / self.stats['uptime_hours']
                    )
                
                # Логирование статистики каждые 5 минут
                await asyncio.sleep(300)
                
                logger.info("="*70)
                logger.info(" СТАТИСТИКА НЕПРЕРЫВНОГО ОБУЧЕНИЯ")
                logger.info(f"⏰ Время работы: {self.stats['uptime_hours']:.2f} часов")
                logger.info(f" Изучено статей: {self.stats['articles_processed']}")
                logger.info(f"🧠 Знаний получено: {self.stats['knowledge_items']}")
                logger.info(f" Скорость: {self.stats['learning_speed_items_per_hour']} элементов/час")
                logger.info(f" Текущая тема: {self.stats['current_topic']}")
                logger.info("="*70)
                
                # Сохранение статистики
                self._save_stats()
                
            except Exception as e:
                logger.error(f"Ошибка обновления статистики: {e}")
                await asyncio.sleep(60)
    
    async def _knowledge_consolidator(self):
        """Консолидация и оптимизация знаний"""
        logger.info(" Поток КОНСОЛИДАЦИИ: ЗАПУЩЕН")
        
        while True:
            try:
                # Каждый час проверяем и оптимизируем базу знаний
                await asyncio.sleep(3600)
                
                logger.info(" Консолидация знаний...")
                
                # Здесь можно добавить логику:
                # - Удаление дубликатов
                # - Объединение похожих знаний
                # - Повышение важности часто встречающихся тем
                
                logger.info(" Консолидация завершена")
                
            except Exception as e:
                logger.error(f"Ошибка консолидации: {e}")
                await asyncio.sleep(3600)
    
    def _save_stats(self):
        """Сохранение статистики"""
        try:
            stats_file = Path("data/continuous_learning_stats.json")
            stats_file.parent.mkdir(exist_ok=True)
            
            # Конвертация для JSON
            stats_to_save = self.stats.copy()
            stats_to_save['start_time'] = stats_to_save['start_time'].isoformat()
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")
    
    async def get_realtime_stats(self) -> Dict:
        """Получение статистики в реальном времени"""
        return {
            'uptime_hours': self.stats['uptime_hours'],
            'articles_total': self.stats['articles_processed'],
            'knowledge_items': self.stats['knowledge_items'],
            'speed_per_hour': self.stats['learning_speed_items_per_hour'],
            'current_topic': self.stats['current_topic'],
            'learning_mode': self.learning_speed,
            'sources_count': len(self.all_sources['rss'])
        }
    
    async def change_speed(self, new_speed: str):
        """Изменение скорости обучения на лету"""
        if new_speed in ['slow', 'normal', 'fast', 'turbo']:
            self.learning_speed = new_speed
            logger.info(f" Скорость обучения изменена на: {new_speed.upper()}")
            return f"Скорость обучения установлена: {new_speed}"
        return "Допустимые скорости: slow, normal, fast, turbo"
