# -*- coding: utf-8 -*-
"""
🌐 FULL WEB CRAWLER - ВЕСЬ ИНТЕРНЕТ!
Краулер который собирает информацию из ЛЮБЫХ источников

Источники:
✅ DuckDuckGo (результаты Google)
✅ Любые веб-страницы
✅ Новостные сайты
✅ Блоги
✅ Форумы
✅ Wikipedia (как один из многих)
✅ Парсинг контента с любых сайтов
"""

import logging
import requests
from bs4 import BeautifulSoup
import time
import re
from pathlib import Path
import json
from collections import defaultdict, deque
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from urllib.parse import urlparse
import hashlib

logger = logging.getLogger(__name__)


class UniversalWebCrawler:
    """Универсальный краулер - ищет ВЕЗДЕ"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        adapter = HTTPAdapter(
            pool_connections=50,
            pool_maxsize=50,
            max_retries=Retry(total=2, backoff_factor=0.3)
        )
        
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.visited_urls = set()
        self.lock = threading.Lock()
        
        self.stats = {
            'pages_crawled': 0,
            'sources_used': set(),
        }
    
    def search_everywhere(self, query, max_results=5):
        """Поиск ВЕЗДЕ"""
        all_results = []
        
        # DuckDuckGo
        ddg_results = self._search_duckduckgo(query, limit=max_results)
        all_results.extend(ddg_results)
        
        # Wikipedia быстро
        if len(all_results) < 2:
            wiki_results = self._search_wikipedia(query)
            all_results.extend(wiki_results)
        
        # Парсим страницы
        parsed_results = []
        for result in all_results[:max_results]:
            content = self._scrape_page(result['url'])
            if content:
                result['content'] = content
                parsed_results.append(result)
        
        with self.lock:
            self.stats['pages_crawled'] += len(parsed_results)
            for r in parsed_results:
                domain = urlparse(r['url']).netloc
                self.stats['sources_used'].add(domain)
        
        return parsed_results
    
    def _search_duckduckgo(self, query, limit=5):
        """DuckDuckGo HTML поиск"""
        results = []
        
        try:
            url = "https://html.duckduckgo.com/html/"
            response = self.session.post(url, data={'q': query}, timeout=5)  # СОКРАТИЛИ ТАЙМАУТ!
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                result_divs = soup.find_all('div', class_='result', limit=limit)
                
                for div in result_divs:
                    try:
                        link_tag = div.find('a', class_='result__a')
                        if not link_tag:
                            continue
                        
                        url = link_tag.get('href', '')
                        if not url.startswith('http'):
                            continue
                        
                        title = link_tag.get_text(strip=True)
                        snippet_tag = div.find('a', class_='result__snippet')
                        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ''
                        
                        results.append({
                            'url': url,
                            'title': title,
                            'content': snippet,
                            'source': 'DuckDuckGo'
                        })
                    except:
                        continue
        except Exception as e:
            logger.debug(f"DuckDuckGo ошибка: {e}")
        
        return results
    
    def _search_wikipedia(self, query):
        """Wikipedia быстрый поиск"""
        results = []
        
        for lang in ['ru', 'en']:
            try:
                api_url = f"https://{lang}.wikipedia.org/w/api.php"
                
                response = self.session.get(api_url, params={
                    'action': 'opensearch',
                    'search': query,
                    'limit': 1,
                    'format': 'json'
                }, timeout=4)  # СОКРАТИЛИ ТАЙМАУТ!
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                if len(data) < 2 or not data[1]:
                    continue
                
                title = data[1][0]
                url = data[3][0] if len(data) > 3 else f"https://{lang}.wikipedia.org/wiki/{title}"
                
                # Контент
                response = self.session.get(api_url, params={
                    'action': 'query',
                    'prop': 'extracts',
                    'exintro': True,
                    'explaintext': True,
                    'titles': title,
                    'format': 'json'
                }, timeout=8)
                
                if response.status_code == 200:
                    content_data = response.json()
                    pages = content_data.get('query', {}).get('pages', {})
                    
                    for page_data in pages.values():
                        extract = page_data.get('extract', '')
                        if extract and len(extract) > 100:
                            results.append({
                                'url': url,
                                'title': title,
                                'content': extract[:3000],
                                'source': f'Wikipedia ({lang})'
                            })
                            break
            except:
                continue
        
        return results
    
    def _scrape_page(self, url):
        """Универсальный парсер страницы"""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            
            with self.lock:
                if url_hash in self.visited_urls:
                    return None
                self.visited_urls.add(url_hash)
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Удаляем мусор
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 
                            'iframe', 'noscript', 'form', 'button']):
                tag.decompose()
            
            # Извлекаем текст
            content_tag = (
                soup.find('article') or 
                soup.find('main') or 
                soup.find('div', class_=re.compile(r'content|article|post', re.I)) or
                soup.find('body')
            )
            
            if not content_tag:
                return None
            
            text = content_tag.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            if len(text) < 100:
                return None
            
            return text[:5000]  # Ограничиваем
        
        except Exception as e:
            logger.debug(f"Парсинг {url}: {e}")
            return None


class FastEntityExtractor:
    """Быстрое извлечение сущностей"""
    
    @classmethod
    def extract_fast(cls, text):
        """Быстрое извлечение"""
        entities = set()
        words = text.split()
        i = 0
        
        while i < len(words):
            word = words[i]
            
            if word and len(word) > 2 and word[0].isupper():
                phrase = [word]
                j = i + 1
                
                while j < len(words) and len(phrase) < 3:
                    next_word = words[j]
                    if next_word and next_word[0].isupper():
                        phrase.append(next_word)
                        j += 1
                    else:
                        break
                
                if len(phrase) >= 2:
                    entity = ' '.join(phrase).replace("'s", "").strip()
                    if 3 <= len(entity) <= 50:
                        entities.add(entity)
                    i = j
                else:
                    i += 1
            else:
                i += 1
        
        return entities


class FullWebLearningSystem:
    """ПОЛНАЯ ВЕБ-СИСТЕМА ОБУЧЕНИЯ"""
    
    def __init__(self, turbo_system=None, memory_system=None, topics_list=None, num_workers=10):
        self.turbo_system = turbo_system
        self.memory_system = memory_system
        self.num_workers = num_workers
        
        self.crawler = UniversalWebCrawler()
        self.entity_extractor = FastEntityExtractor()
        
        self.topic_queue = deque(topics_list or [])
        self.studied_topics = set()
        self.knowledge_graph = defaultdict(set)
        
        self.stats = {
            'start_time': datetime.now(),
            'topics_studied': 0,
            'pages_crawled': 0,
            'sources_collected': 0,
            'entities_discovered': 0,
            'total_content': 0,
            'memory_records_added': 0,
        }
        
        self.data_dir = Path('data/web_knowledge')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.embeddings_batch = []
        self.batch_size = 300
        self.lock = threading.Lock()
        
        # Dashboard support
        self.dashboard = None
        self.current_thread_topics = {}  # thread_id -> current_topic
        
        logger.info(f"Full Web Learning готова ({num_workers} потоков)")
    
    def enable_dashboard(self):
        """Включение интерактивного dashboard"""
        try:
            from .learning_dashboard import LearningDashboard
            self.dashboard = LearningDashboard(self)
            self.dashboard.start()
            logger.info("✅ Dashboard активирован!")
        except ImportError:
            logger.warning("❌ Не найден модуль learning_dashboard")
        except Exception as e:
            logger.error(f"❌ Ошибка запуска dashboard: {e}")
    
    def learn_topic(self, topic, thread_id=None):
        """Изучение темы из всего интернета"""
        if topic in self.studied_topics:
            return False
        
        # Dashboard update
        if self.dashboard and thread_id is not None:
            self.dashboard.update_thread_status(thread_id, topic, 'searching')
        
        logger.info(f"🔍 Начинаю изучение: {topic}")
        
        try:
            # БЫСТРЫЙ ПОИСК: пропускаем темы которые долго ищутся
            results = []
            search_success = [False]
            
            def do_search():
                try:
                    search_success[0] = True
                    return self.crawler.search_everywhere(topic, max_results=5)
                except Exception as e:
                    logger.error(f"❌ Ошибка поиска {topic}: {e}")
                    return []
            
            # Пытаемся найти с коротким timeout
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(do_search)
                try:
                    results = future.result(timeout=20)  # 20 секунд максимум
                except concurrent.futures.TimeoutError:
                    logger.warning(f"⏱️ Таймаут поиска: {topic}")
                    with self.lock:
                        self.studied_topics.add(topic)
                    return False
            
            if not results:
                with self.lock:
                    self.studied_topics.add(topic)
                logger.debug(f"❌ {topic}: нет результатов")
                return False
            
            logger.info(f"✓ {topic}: найдено {len(results)} результатов")
            
            # Dashboard update - parsing
            if self.dashboard and thread_id is not None:
                self.dashboard.update_thread_status(thread_id, topic, 'parsing')
            
            all_content = []
            for result in results:
                if result.get('content'):
                    all_content.append(result['content'])
            
            if not all_content:
                with self.lock:
                    self.studied_topics.add(topic)
                return False
            
            full_content = "\n\n".join(all_content)
            
            # Сущности
            entities = self.entity_extractor.extract_fast(full_content)
            
            added = 0
            with self.lock:
                for entity in entities:
                    if entity not in self.studied_topics and entity not in self.topic_queue:
                        self.topic_queue.append(entity)
                        self.knowledge_graph[topic].add(entity)
                        added += 1
            
            # Dashboard update - saving to memory
            if self.dashboard and thread_id is not None:
                self.dashboard.update_thread_status(thread_id, topic, 'saving')
            
            # Сохраняем в память - BATCH метод с массовым добавлением!
            memory_added = 0
            if self.memory_system:
                logger.info(f"Попытка сохранить {topic} в память...")
                try:
                    chunks = self._split_content(full_content, max_size=400)
                    logger.info(f"Создано {len(chunks)} чанков для {topic}")
                    
                    # ТУРБО ОПТИМИЗАЦИЯ: Batch добавление ВСЕХ чанков сразу!
                    if chunks[:5]:
                        import datetime
                        
                        # МЕТОД 1: Прямой доступ к ChromaDB (быстро)
                        try:
                            # Подготовка batch данных
                            batch_embeddings = []
                            batch_documents = []
                            batch_metadatas = []
                            batch_ids = []
                            
                            # Генерация эмбеддингов для ВСЕХ чанков СРАЗУ (векторизация!)
                            texts = [f"{topic}: {chunk}" for chunk in chunks[:5]]
                            batch_embeddings = self.memory_system.embedder.encode(texts).tolist()
                            
                            # Подготовка метаданных
                            base_timestamp = datetime.datetime.now().timestamp()
                            for idx, (chunk, embedding) in enumerate(zip(chunks[:5], batch_embeddings)):
                                batch_documents.append(f"{topic}: {chunk}")
                                batch_metadatas.append({
                                    'type': 'knowledge',
                                    'timestamp': datetime.datetime.now().isoformat(),
                                    'importance': 0.7,
                                    'topic': topic,
                                    'source': 'web_crawler',
                                    'auto_learned': True
                                })
                                batch_ids.append(f"knowledge_{base_timestamp}_{idx}")
                            
                            # МАССОВОЕ добавление одним вызовом!
                            self.memory_system.collection.add(
                                embeddings=batch_embeddings,
                                documents=batch_documents,
                                metadatas=batch_metadatas,
                                ids=batch_ids
                            )
                            
                            memory_added = len(batch_documents)
                            logger.info(f"✅ Batch сохранение: {memory_added} записей")
                            
                        except Exception as batch_error:
                            logger.warning(f"Batch метод не сработал: {batch_error}")
                            logger.info("Переключаюсь на асинхронный метод...")
                            
                            # МЕТОД 2: FALLBACK - асинхронный метод через asyncio (медленнее, но надёжнее)
                            import asyncio
                            for chunk in chunks[:5]:
                                try:
                                    asyncio.run(self.memory_system.store_memory(
                                        content=f"{topic}: {chunk}",
                                        memory_type="knowledge",
                                        metadata={
                                            'topic': topic,
                                            'source': 'web_crawler',
                                            'auto_learned': True
                                        }
                                    ))
                                    memory_added += 1
                                except Exception as e:
                                    logger.error(f"Ошибка сохранения чанка: {e}")
                            
                            logger.info(f"✅ Async сохранение: {memory_added} записей")
                        
                        with self.lock:
                            self.stats['memory_records_added'] += memory_added
                        
                        logger.info(f"В память добавлено {memory_added} записей для {topic}")
                
                except Exception as e:
                    logger.error(f"Ошибка памяти для {topic}: {e}", exc_info=True)
            else:
                logger.warning("memory_system = None! Не могу сохранить в память!")
            
            # Сохраняем
            self._save_fast(topic, {
                'content': full_content[:2000],
                'sources': [{'url': r['url'], 'source': r['source']} for r in results],
                'entities': list(entities)[:20],
            })
            
            # Embeddings
            chunks = self._split_content(full_content)
            with self.lock:
                for chunk in chunks:
                    self.embeddings_batch.append(f"{topic}: {chunk}")
            
            with self.lock:
                self.studied_topics.add(topic)
                self.stats['topics_studied'] += 1
                self.stats['sources_collected'] += len(results)
                self.stats['pages_crawled'] = self.crawler.stats['pages_crawled']
                self.stats['total_content'] += len(full_content)
                self.stats['entities_discovered'] += added
            
            # Dashboard update - completed
            if self.dashboard and thread_id is not None:
                self.dashboard.update_thread_status(thread_id, topic, 'completed')
            
            return True
        
        except Exception as e:
            logger.debug(f"Ошибка {topic}: {e}")
            
            # Dashboard update - error
            if self.dashboard and thread_id is not None:
                self.dashboard.update_thread_status(thread_id, topic, 'error')
            
            return False
    
    def process_embeddings_batch(self):
        """Обработка embeddings"""
        with self.lock:
            if not self.embeddings_batch or not self.turbo_system:
                return
            
            batch = self.embeddings_batch.copy()
            self.embeddings_batch = []
        
        try:
            self.turbo_system.learn_batch(batch, category="web")
            logger.info(f"GPU: {len(batch)} embeddings")
        except Exception as e:
            logger.debug(f"GPU ошибка: {e}")
    
    def start_web_learning(self):
        """Запуск веб-обучения"""
        logger.info("="*80)
        logger.info(f"FULL WEB LEARNING - {self.num_workers} ПОТОКОВ")
        logger.info("="*80)
        logger.info(f"Всего тем: {len(self.topic_queue)}")
        logger.info("="*80)
        
        total_topics = len(self.topic_queue)
        processed = 0
        
        try:
            thread_id_counter = [0]  # Mutable counter for thread IDs
            thread_id_map = {}  # Map threads to IDs
            
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                while self.topic_queue:
                    batch = []
                    for _ in range(min(self.num_workers * 2, len(self.topic_queue))):
                        if self.topic_queue:
                            batch.append(self.topic_queue.popleft())
                    
                    if not batch:
                        break
                    
                    # Create futures with thread ID tracking
                    futures = {}
                    for topic in batch:
                        # Assign thread ID
                        thread_id = thread_id_counter[0] % self.num_workers
                        thread_id_counter[0] += 1
                        
                        future = executor.submit(self.learn_topic, topic, thread_id)
                        futures[future] = (topic, thread_id)
                    
                    for future in as_completed(futures):
                        processed += 1
                        
                        if len(self.embeddings_batch) >= self.batch_size:
                            self.process_embeddings_batch()
                        
                        if processed % 50 == 0:
                            self._print_stats(processed, total_topics)
        
        except KeyboardInterrupt:
            logger.info("\nОстановка")
        
        finally:
            if self.embeddings_batch:
                self.process_embeddings_batch()
            
            self._print_final_stats(total_topics)
    
    # Алиас для совместимости
    def start_learning(self):
        """Алиас для start_web_learning()"""
        return self.start_web_learning()
    
    def _split_content(self, content, max_size=1500):
        chunks = []
        for i in range(0, len(content), max_size):
            chunks.append(content[i:i+max_size])
        return chunks
    
    def _save_fast(self, topic, data):
        try:
            filename = re.sub(r'[<>:"/\\|?*]', '_', topic)[:100] + '.json'
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except:
            pass
    
    def _print_stats(self, processed, total):
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        speed = self.stats['topics_studied'] / elapsed if elapsed > 0 else 0
        eta = (total - processed) / speed if speed > 0 else 0
        
        logger.info("="*80)
        logger.info(f"[{processed}/{total}] {(processed/total*100):.1f}%")
        logger.info(f"Изучено: {self.stats['topics_studied']}")
        logger.info(f"В ПАМЯТЬ: +{self.stats['memory_records_added']} записей")
        logger.info(f"Страниц: {self.stats['pages_crawled']}")
        logger.info(f"Доменов: {len(self.crawler.stats['sources_used'])}")
        logger.info(f"Новых тем: {self.stats['entities_discovered']}")
        logger.info(f"Скорость: {speed*60:.0f} тем/мин")
        logger.info(f"ETA: {eta/60:.1f} мин")
        logger.info("="*80)
    
    def _print_final_stats(self, total):
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        
        logger.info("\n" + "="*80)
        logger.info("ОБУЧЕНИЕ ЗАВЕРШЕНО")
        logger.info("="*80)
        logger.info(f"Изучено: {self.stats['topics_studied']}")
        logger.info(f"В ПАМЯТЬ ДОБАВЛЕНО: {self.stats['memory_records_added']} записей!")
        logger.info(f"Страниц: {self.stats['pages_crawled']}")
        logger.info(f"Доменов: {len(self.crawler.stats['sources_used'])}")
        logger.info(f"Контента: {self.stats['total_content']/1024/1024:.1f} MB")
        logger.info(f"Время: {elapsed/60:.1f} мин")
        logger.info(f"Скорость: {self.stats['topics_studied']/(elapsed/60):.0f} тем/мин")
        logger.info("\nИспользованные домены:")
        for domain in sorted(self.crawler.stats['sources_used'])[:20]:
            logger.info(f"  - {domain}")
        logger.info("="*80)
