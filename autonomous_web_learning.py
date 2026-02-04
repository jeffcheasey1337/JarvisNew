# -*- coding: utf-8 -*-
"""
AUTONOMOUS WEB LEARNING SYSTEM
Автономная система обучения из интернета

Процесс:
1. Берет тему из базы данных
2. Ищет информацию в Google/DuckDuckGo
3. Парсит контент с сайтов, форумов, Reddit
4. Извлекает знания
5. Создает embeddings
6. Сохраняет в векторную БД
"""

import logging
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote_plus, urlparse
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class WebKnowledgeCollector:
    """Сборщик знаний из интернета"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Статистика
        self.stats = {
            'topics_processed': 0,
            'searches_performed': 0,
            'pages_scraped': 0,
            'knowledge_extracted': 0,
            'errors': 0,
        }
    
    def search_google(self, query, num_results=10):
        """
        Поиск в Google
        
        Args:
            query: Поисковый запрос
            num_results: Количество результатов
            
        Returns:
            List of URLs
        """
        try:
            # Google Search API (бесплатная альтернатива)
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлекаем URL из результатов
            urls = []
            for result in soup.find_all('div', class_='g'):
                link = result.find('a')
                if link and link.get('href'):
                    url = link.get('href')
                    if url.startswith('http'):
                        urls.append(url)
            
            self.stats['searches_performed'] += 1
            return urls[:num_results]
        
        except Exception as e:
            logger.error(f"Ошибка поиска в Google: {e}")
            self.stats['errors'] += 1
            return []
    
    def search_duckduckgo(self, query, num_results=10):
        """
        Поиск в DuckDuckGo (не требует API ключа)
        
        Args:
            query: Поисковый запрос
            num_results: Количество результатов
            
        Returns:
            List of URLs
        """
        try:
            # DuckDuckGo HTML search
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлекаем URL
            urls = []
            for result in soup.find_all('a', class_='result__url'):
                url = result.get('href')
                if url and url.startswith('http'):
                    # Очищаем URL от DuckDuckGo редиректа
                    if 'uddg=' in url:
                        url = url.split('uddg=')[1]
                    urls.append(url)
            
            self.stats['searches_performed'] += 1
            return urls[:num_results]
        
        except Exception as e:
            logger.error(f"Ошибка поиска в DuckDuckGo: {e}")
            self.stats['errors'] += 1
            return []
    
    def scrape_webpage(self, url, max_length=5000):
        """
        Парсинг веб-страницы
        
        Args:
            url: URL страницы
            max_length: Максимальная длина текста
            
        Returns:
            Extracted text content
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Удаляем ненужные элементы
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Извлекаем текст
            text = soup.get_text(separator=' ', strip=True)
            
            # Очищаем текст
            text = re.sub(r'\s+', ' ', text)  # Множественные пробелы
            text = re.sub(r'\n+', '\n', text)  # Множественные переводы строк
            
            # Ограничиваем длину
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            self.stats['pages_scraped'] += 1
            return text
        
        except Exception as e:
            logger.error(f"Ошибка парсинга {url}: {e}")
            self.stats['errors'] += 1
            return ""
    
    def scrape_reddit(self, query, limit=5):
        """
        Парсинг Reddit discussions
        
        Args:
            query: Тема для поиска
            limit: Количество постов
            
        Returns:
            List of discussion texts
        """
        try:
            # Reddit поиск (не требует API)
            search_url = f"https://www.reddit.com/search.json?q={quote_plus(query)}&limit={limit}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            discussions = []
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                
                if title or selftext:
                    discussions.append(f"{title}\n{selftext}")
            
            self.stats['pages_scraped'] += len(discussions)
            return discussions
        
        except Exception as e:
            logger.error(f"Ошибка парсинга Reddit: {e}")
            self.stats['errors'] += 1
            return []
    
    def collect_knowledge_for_topic(self, topic, sources=['google', 'duckduckgo', 'reddit']):
        """
        Сбор знаний по теме из разных источников
        
        Args:
            topic: Тема для изучения
            sources: Список источников
            
        Returns:
            Dict with collected knowledge
        """
        logger.info(f"Сбор знаний по теме: {topic}")
        
        knowledge = {
            'topic': topic,
            'sources': [],
            'content': [],
            'total_text_length': 0,
        }
        
        try:
            # 1. Поиск в Google
            if 'google' in sources:
                logger.debug(f"Поиск в Google: {topic}")
                urls = self.search_google(topic, num_results=5)
                
                for url in urls[:3]:  # Берем топ-3
                    content = self.scrape_webpage(url, max_length=3000)
                    if content:
                        knowledge['sources'].append({
                            'type': 'google',
                            'url': url,
                            'content': content
                        })
                        knowledge['content'].append(content)
                
                # Пауза между запросами
                time.sleep(random.uniform(1, 3))
            
            # 2. Поиск в DuckDuckGo
            if 'duckduckgo' in sources:
                logger.debug(f"Поиск в DuckDuckGo: {topic}")
                urls = self.search_duckduckgo(topic, num_results=5)
                
                for url in urls[:3]:  # Берем топ-3
                    content = self.scrape_webpage(url, max_length=3000)
                    if content:
                        knowledge['sources'].append({
                            'type': 'duckduckgo',
                            'url': url,
                            'content': content
                        })
                        knowledge['content'].append(content)
                
                time.sleep(random.uniform(1, 3))
            
            # 3. Reddit обсуждения
            if 'reddit' in sources:
                logger.debug(f"Поиск на Reddit: {topic}")
                discussions = self.scrape_reddit(topic, limit=3)
                
                for discussion in discussions:
                    knowledge['sources'].append({
                        'type': 'reddit',
                        'content': discussion
                    })
                    knowledge['content'].append(discussion)
                
                time.sleep(random.uniform(1, 2))
            
            # Подсчет общего объема
            knowledge['total_text_length'] = sum(len(c) for c in knowledge['content'])
            
            self.stats['topics_processed'] += 1
            if knowledge['content']:
                self.stats['knowledge_extracted'] += 1
            
            logger.info(f"Собрано {len(knowledge['content'])} источников, {knowledge['total_text_length']} символов")
            
            return knowledge
        
        except Exception as e:
            logger.error(f"Ошибка сбора знаний по теме '{topic}': {e}")
            self.stats['errors'] += 1
            return knowledge
    
    def get_stats(self):
        """Получение статистики"""
        return self.stats.copy()


class AutonomousWebLearningSystem:
    """
    Автономная система обучения из интернета
    
    Полный цикл:
    1. Берет тему
    2. Собирает информацию
    3. Обрабатывает
    4. Сохраняет в память
    """
    
    def __init__(self, memory_system=None, topics_database=None, turbo_system=None):
        self.memory_system = memory_system
        self.topics_database = topics_database
        self.turbo_system = turbo_system
        
        # Сборщик знаний
        self.collector = WebKnowledgeCollector()
        
        # Статистика
        self.stats = {
            'start_time': None,
            'topics_learned': 0,
            'total_content_collected': 0,
            'embeddings_created': 0,
        }
        
        logger.info("Автономная система обучения инициализирована")
    
    def learn_topic_from_web(self, topic):
        """
        Полный цикл обучения по одной теме
        
        Args:
            topic: Тема для изучения
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Начало обучения: {topic}")
            
            # 1. Сбор знаний из интернета
            knowledge = self.collector.collect_knowledge_for_topic(
                topic,
                sources=['duckduckgo', 'reddit']  # Google может блокировать
            )
            
            if not knowledge['content']:
                logger.warning(f"Не удалось собрать контент по теме: {topic}")
                return False
            
            # 2. Объединяем весь контент
            full_content = "\n\n".join(knowledge['content'])
            
            logger.info(f"Собрано {len(knowledge['content'])} источников, {len(full_content)} символов")
            
            # 3. Создаем embeddings через Turbo систему
            if self.turbo_system:
                # Разбиваем на чанки если текст большой
                max_chunk_size = 2000
                chunks = []
                
                for i in range(0, len(full_content), max_chunk_size):
                    chunk = full_content[i:i+max_chunk_size]
                    chunks.append(f"{topic}: {chunk}")
                
                # Обрабатываем через GPU
                self.turbo_system.learn_batch(chunks, category="web_learning")
                
                self.stats['embeddings_created'] += len(chunks)
                logger.info(f"Создано {len(chunks)} embeddings для темы '{topic}'")
            
            # 4. Сохраняем в память (опционально)
            if self.memory_system:
                try:
                    # Сохраняем краткое резюме
                    summary = full_content[:500] + "..." if len(full_content) > 500 else full_content
                    
                    # Можно добавить в episodic memory
                    # self.memory_system.add_memory(...)
                    
                    logger.debug(f"Информация сохранена в память: {topic}")
                except Exception as e:
                    logger.error(f"Ошибка сохранения в память: {e}")
            
            # Обновляем статистику
            self.stats['topics_learned'] += 1
            self.stats['total_content_collected'] += len(full_content)
            
            logger.info(f"Обучение завершено: {topic}")
            return True
        
        except Exception as e:
            logger.error(f"Критическая ошибка обучения по теме '{topic}': {e}")
            return False
    
    def start_autonomous_learning(self, topics_list, delay_between_topics=5):
        """
        Запуск автономного обучения
        
        Args:
            topics_list: Список тем для изучения
            delay_between_topics: Задержка между темами (сек)
        """
        import time
        
        self.stats['start_time'] = time.time()
        
        logger.info(f"Начало автономного обучения на {len(topics_list)} темах")
        
        for i, topic in enumerate(topics_list):
            logger.info(f"[{i+1}/{len(topics_list)}] Обработка темы: {topic}")
            
            success = self.learn_topic_from_web(topic)
            
            if success:
                logger.info(f"Успешно: {topic}")
            else:
                logger.warning(f"Не удалось обучиться: {topic}")
            
            # Задержка между темами
            if i < len(topics_list) - 1:
                logger.debug(f"Пауза {delay_between_topics} сек...")
                time.sleep(delay_between_topics)
        
        # Финальная статистика
        elapsed = time.time() - self.stats['start_time']
        
        logger.info("="*80)
        logger.info("АВТОНОМНОЕ ОБУЧЕНИЕ ЗАВЕРШЕНО")
        logger.info("="*80)
        logger.info(f"Тем изучено: {self.stats['topics_learned']}/{len(topics_list)}")
        logger.info(f"Контента собрано: {self.stats['total_content_collected']} символов")
        logger.info(f"Embeddings создано: {self.stats['embeddings_created']}")
        logger.info(f"Время работы: {elapsed/60:.1f} минут")
        logger.info("="*80)
    
    def get_stats(self):
        """Получение статистики"""
        stats = self.stats.copy()
        stats['collector'] = self.collector.get_stats()
        return stats


# Тестовый запуск
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*80)
    print("AUTONOMOUS WEB LEARNING SYSTEM - TEST")
    print("="*80)
    print()
    
    # Создаем систему
    system = AutonomousWebLearningSystem()
    
    # Тестовые темы
    test_topics = [
        "Квентин Тарантино фильмография",
        "Sex Pistols панк-рок",
        "SQL injection хакинг",
    ]
    
    print(f"Тестирование на {len(test_topics)} темах")
    print()
    
    # Запускаем
    system.start_autonomous_learning(test_topics, delay_between_topics=3)
    
    # Статистика
    stats = system.get_stats()
    print("\nСтатистика:")
    print(f"  Тем изучено: {stats['topics_learned']}")
    print(f"  Контента: {stats['total_content_collected']} символов")
    print(f"  Поисков: {stats['collector']['searches_performed']}")
    print(f"  Страниц: {stats['collector']['pages_scraped']}")
    print()
