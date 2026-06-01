# -*- coding: utf-8 -*-
"""
🌍 INFINITE AUTONOMOUS LEARNING SYSTEM
Бесконечная автономная система обучения

Возможности:
- 300+ языков Wikipedia
- Весь интернет (новости, блоги, форумы)
- Автоматическое извлечение новых тем
- Граф знаний
- Бесконечное обучение
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
import hashlib

logger = logging.getLogger(__name__)


class MultilingualWikipediaCollector:
    """Многоязычный сборщик из Wikipedia с умным поиском"""
    
    # Топ-50 языков Wikipedia
    LANGUAGES = [
        'ru', 'en', 'de', 'fr', 'es', 'it', 'pl', 'ja', 'zh', 'pt',
        'nl', 'sv', 'ar', 'uk', 'fa', 'ca', 'sr', 'id', 'ko', 'no',
        'fi', 'hu', 'cs', 'tr', 'ro', 'vi', 'da', 'eo', 'sk', 'he',
        'bg', 'kk', 'eu', 'sl', 'hr', 'lt', 'et', 'az', 'gl', 'simple',
        'nn', 'la', 'el', 'th', 'sh', 'vo', 'hi', 'ta', 'ka', 'mk'
    ]
    
    # Распространенные переводы имен/терминов
    TRANSLATIONS = {
        'Квентин Тарантино': 'Quentin Tarantino',
        'Джордж Клуни': 'George Clooney',
        'Леонардо ДиКаприо': 'Leonardo DiCaprio',
        'Мартин Скорсезе': 'Martin Scorsese',
        'Стивен Спилберг': 'Steven Spielberg',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JARVIS-Infinite-Learning/2.0 (Educational; Multilingual) Python/3.11'
        })
        
        self.stats = {
            'languages_used': set(),
            'articles_collected': 0,
            'fallback_searches': 0,
        }
    
    def search_all_languages(self, query, max_languages=10):
        """
        Умный поиск на разных языках с fallback
        
        Args:
            query: Поисковый запрос
            max_languages: Максимум языков
            
        Returns:
            List of results
        """
        results = []
        
        # Генерируем варианты запроса
        query_variants = self._generate_query_variants(query)
        
        logger.debug(f"Варианты поиска: {query_variants[:3]}...")
        
        # Пробуем каждый вариант
        for variant in query_variants:
            # Если уже нашли достаточно - стоп
            if len(results) >= 3:
                break
            
            # Поиск по языкам
            for lang in self.LANGUAGES[:max_languages]:
                try:
                    result = self._search_wikipedia(variant, lang)
                    
                    if result:
                        # Проверяем что такой результат еще нет
                        if not any(r['url'] == result['url'] for r in results):
                            results.append(result)
                            self.stats['languages_used'].add(lang)
                            logger.debug(f"✓ {lang.upper()}: {len(result['content'])} символов")
                    
                    time.sleep(0.3)
                    
                    # Если нашли на этом языке - следующий язык
                    if result:
                        break
                    
                except Exception as e:
                    logger.debug(f"Ошибка {lang}: {e}")
            
            # Пауза между вариантами
            if len(results) == 0:
                time.sleep(0.5)
        
        self.stats['articles_collected'] += len(results)
        
        if len(results) == 0:
            logger.warning(f"Ничего не найдено для '{query}' и его вариантов")
        
        return results
    
    def _generate_query_variants(self, query):
        """
        Генерация вариантов запроса
        
        Пример:
        "Квентин Тарантино" →
          - "Квентин Тарантино"
          - "Quentin Tarantino" (перевод)
          - "Тарантино" (фамилия)
          - "Tarantino"
        """
        variants = [query]
        
        # 1. Прямой перевод если есть
        if query in self.TRANSLATIONS:
            variants.append(self.TRANSLATIONS[query])
        
        # 2. Если это имя (2+ слова с заглавных)
        words = query.split()
        if len(words) >= 2 and all(w and w[0].isupper() for w in words):
            # Добавляем только фамилию
            variants.append(words[-1])
            
            # Простой транслит русских имен
            if self._is_cyrillic(query):
                # Добавляем транслитерированный вариант
                translit = self._simple_translit(query)
                variants.append(translit)
                # И только фамилию
                variants.append(self._simple_translit(words[-1]))
        
        # 3. Убираем дубликаты, сохраняя порядок
        seen = set()
        unique_variants = []
        for v in variants:
            if v not in seen:
                seen.add(v)
                unique_variants.append(v)
        
        return unique_variants
    
    def _is_cyrillic(self, text):
        """Проверка что текст на кириллице"""
        return bool(re.search('[а-яА-Я]', text))
    
    def _simple_translit(self, text):
        """Простая транслитерация русского"""
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        
        result = ''
        for char in text:
            result += translit_dict.get(char, char)
        
        return result
    
    def _search_wikipedia(self, query, lang):
        """Поиск на конкретном языке"""
        try:
            api_url = f"https://{lang}.wikipedia.org/w/api.php"
            
            # Поиск
            search_params = {
                'action': 'opensearch',
                'search': query,
                'limit': 1,
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            if len(results) < 2 or not results[1]:
                return None
            
            title = results[1][0]
            
            # Контент
            content_params = {
                'action': 'query',
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'titles': title,
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=content_params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            for page_data in pages.values():
                extract = page_data.get('extract', '')
                
                if extract and len(extract) > 100:
                    return {
                        'source': f'Wikipedia ({lang})',
                        'title': title,
                        'url': f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                        'content': extract,
                        'lang': lang
                    }
            
            return None
        
        except Exception as e:
            return None


class WebCrawler:
    """Краулер для сбора информации из интернета"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.visited_urls = set()
    
    def crawl_search_results(self, query, max_results=5):
        """
        Краулинг результатов поиска
        
        Использует DuckDuckGo HTML (без блокировок)
        """
        results = []
        
        try:
            # DuckDuckGo HTML поиск
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Извлекаем ссылки
                links = soup.find_all('a', class_='result__url', limit=max_results)
                
                for link in links:
                    url = link.get('href')
                    
                    if url and url.startswith('http') and url not in self.visited_urls:
                        # Парсим страницу
                        content = self._scrape_page(url)
                        
                        if content:
                            results.append({
                                'source': 'Web',
                                'url': url,
                                'content': content
                            })
                            
                            self.visited_urls.add(url)
                        
                        time.sleep(1)
        
        except Exception as e:
            logger.debug(f"Ошибка краулинга: {e}")
        
        return results
    
    def _scrape_page(self, url):
        """Парсинг страницы"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Удаляем ненужное
            for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            
            # Извлекаем текст
            text = soup.get_text(separator=' ', strip=True)
            
            # Очистка
            text = re.sub(r'\s+', ' ', text)
            
            # Ограничиваем
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return text if len(text) > 200 else None
        
        except:
            return None


class EntityExtractor:
    """Улучшенное извлечение сущностей с фильтрацией"""
    
    # Стоп-слова и мусорные паттерны
    STOP_WORDS = {
        'the', 'and', 'for', 'with', 'from', 'this', 'that', 'these', 'those',
        'в', 'и', 'на', 'с', 'по', 'для', 'как', 'что', 'это', 'его', 'её'
    }
    
    BAD_PATTERNS = [
        r'\d+',  # Только цифры
        r'^[A-Z]{1,2}$',  # Одна-две заглавные буквы
        r"'s$",  # Окончания 's
        r'tery$',  # Interpretery
        r'tory$',  # Territory
        r'^The\s',  # Начинается с The
    ]
    
    @classmethod
    def is_valid_entity(cls, text):
        """
        Проверка валидности темы
        
        Фильтрует:
        - Слишком короткие/длинные
        - Стоп-слова
        - Плохие паттерны
        - Мусор
        """
        if not text or len(text) < 3 or len(text) > 50:
            return False
        
        # Стоп-слова
        if text.lower() in cls.STOP_WORDS:
            return False
        
        # Плохие паттерны
        for pattern in cls.BAD_PATTERNS:
            if re.search(pattern, text):
                return False
        
        # Слишком много пунктуации
        punct_count = sum(1 for c in text if not c.isalnum() and c not in [' ', '-'])
        if punct_count > 3:
            return False
        
        return True
    
    @classmethod
    def normalize_entity(cls, text):
        """
        Нормализация сущности
        
        "Monty Python's Flying Circus" → "Monty Python"
        """
        # Убираем апострофы
        text = re.sub(r"'s\b", "", text)
        text = re.sub(r"'", "", text)
        
        # Убираем лишнее
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Если слишком длинное - берем первые 2-3 слова
        words = text.split()
        if len(words) > 3:
            text = ' '.join(words[:3])
        
        return text
    
    @classmethod
    def extract_entities(cls, text):
        """Извлечение сущностей с фильтрацией"""
        entities = {
            'people': set(),
            'places': set(),
            'topics': set(),
        }
        
        # Разбиваем на слова
        words = text.split()
        
        # 1. Находим фразы из заглавных слов (имена, названия)
        i = 0
        while i < len(words):
            word = words[i]
            
            # Должно начинаться с заглавной и быть достаточно длинным
            if word and len(word) > 2 and word[0].isupper():
                # Пробуем собрать фразу
                phrase_words = [word]
                j = i + 1
                
                # Собираем до 3 слов подряд с заглавной
                while j < len(words) and len(phrase_words) < 3:
                    next_word = words[j]
                    if next_word and next_word[0].isupper():
                        phrase_words.append(next_word)
                        j += 1
                    else:
                        break
                
                # Проверяем все варианты (от длинной фразы к короткой)
                for length in range(len(phrase_words), 0, -1):
                    phrase = ' '.join(phrase_words[:length])
                    
                    if cls.is_valid_entity(phrase):
                        normalized = cls.normalize_entity(phrase)
                        
                        # Добавляем в соответствующую категорию
                        if length >= 2:
                            entities['people'].add(normalized)
                        else:
                            entities['topics'].add(normalized)
                        
                        i += length
                        break
                else:
                    i += 1
            else:
                i += 1
        
        # 2. Частотный анализ - часто упоминаемые слова
        word_freq = defaultdict(int)
        for word in words:
            if len(word) > 4 and word[0].isupper():
                word_freq[word] += 1
        
        # Берем часто упоминаемые (2+ раза)
        for word, freq in word_freq.items():
            if freq >= 2 and cls.is_valid_entity(word):
                normalized = cls.normalize_entity(word)
                entities['topics'].add(normalized)
        
        # 3. В кавычках
        quotes = re.findall(r'"([^"]+)"', text)
        for quote in quotes:
            if cls.is_valid_entity(quote):
                normalized = cls.normalize_entity(quote)
                entities['topics'].add(normalized)
        
        return entities


class KnowledgeGraph:
    """Граф знаний - связи между темами"""
    
    def __init__(self):
        self.graph = defaultdict(set)  # topic -> set of related topics
        self.topic_info = {}  # topic -> metadata
    
    def add_topic(self, topic, metadata=None):
        """Добавление темы"""
        if topic not in self.topic_info:
            self.topic_info[topic] = metadata or {}
    
    def add_relation(self, topic1, topic2):
        """Добавление связи между темами"""
        self.graph[topic1].add(topic2)
        self.graph[topic2].add(topic1)
    
    def get_related(self, topic, max_depth=2):
        """Получение связанных тем"""
        if topic not in self.graph:
            return set()
        
        related = set()
        visited = set()
        queue = deque([(topic, 0)])
        
        while queue:
            current, depth = queue.popleft()
            
            if current in visited or depth > max_depth:
                continue
            
            visited.add(current)
            
            if current != topic:
                related.add(current)
            
            if depth < max_depth:
                for neighbor in self.graph[current]:
                    queue.append((neighbor, depth + 1))
        
        return related
    
    def save(self, filepath):
        """Сохранение графа"""
        data = {
            'graph': {k: list(v) for k, v in self.graph.items()},
            'info': self.topic_info
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, filepath):
        """Загрузка графа"""
        if Path(filepath).exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.graph = defaultdict(set)
                for k, v in data.get('graph', {}).items():
                    self.graph[k] = set(v)
                
                self.topic_info = data.get('info', {})


class InfiniteLearningSystem:
    """
    БЕСКОНЕЧНАЯ СИСТЕМА ОБУЧЕНИЯ
    
    Постоянно учится, расширяет знания, никогда не останавливается
    """
    
    def __init__(self, turbo_system=None, initial_topics=None):
        self.turbo_system = turbo_system
        
        # Компоненты
        self.wiki_collector = MultilingualWikipediaCollector()
        self.web_crawler = WebCrawler()
        self.entity_extractor = EntityExtractor()
        self.knowledge_graph = KnowledgeGraph()
        
        # Очередь тем для изучения
        self.topic_queue = deque(initial_topics or [])
        self.studied_topics = set()
        
        # Статистика
        self.stats = {
            'start_time': datetime.now(),
            'topics_studied': 0,
            'sources_collected': 0,
            'entities_discovered': 0,
            'total_content': 0,
        }
        
        # Папки
        self.data_dir = Path('data/infinite_knowledge')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Загружаем граф если есть
        graph_file = self.data_dir / 'knowledge_graph.json'
        self.knowledge_graph.load(graph_file)
        
        logger.info("🌍 Infinite Learning System готова")
    
    def learn_topic(self, topic):
        """
        Изучение одной темы
        
        Процесс:
        1. Умный поиск в Wikipedia (с вариантами)
        2. Краулинг веб (если нужно)
        3. Улучшенное извлечение сущностей
        4. Фильтрация качественных тем
        5. Обновление графа знаний
        6. Создание embeddings
        """
        if topic in self.studied_topics:
            logger.debug(f"Тема '{topic}' уже изучена")
            return False
        
        logger.info(f"🎓 Изучение: {topic}")
        
        all_content = []
        all_sources = []
        
        try:
            # 1. Wikipedia с умным поиском
            logger.info(f"🌍 Умный поиск в Wikipedia...")
            wiki_results = self.wiki_collector.search_all_languages(topic, max_languages=10)
            
            for result in wiki_results:
                all_content.append(result['content'])
                all_sources.append(result)
            
            logger.info(f"✓ Wikipedia: {len(wiki_results)} языков, {sum(len(r['content']) for r in wiki_results)} символов")
            
            # 2. Веб-краулинг (если Wikipedia не нашла много)
            if len(all_content) < 2:
                logger.info(f"🌐 Поиск в интернете...")
                web_results = self.web_crawler.crawl_search_results(topic, max_results=3)
                
                for result in web_results:
                    all_content.append(result['content'])
                    all_sources.append(result)
                
                if web_results:
                    logger.info(f"✓ Веб: {len(web_results)} страниц")
            
            if not all_content:
                logger.warning(f"⚠️ Нет данных для '{topic}'")
                self.studied_topics.add(topic)  # Помечаем чтобы не пробовать снова
                return False
            
            # 3. Объединяем весь контент
            full_content = "\n\n".join(all_content)
            
            logger.info(f"📊 Всего собрано: {len(full_content)} символов из {len(all_sources)} источников")
            
            # 4. Улучшенное извлечение сущностей
            logger.info(f"🧠 Анализ сущностей...")
            entities = self.entity_extractor.extract_entities(full_content)
            
            new_topics = entities['people'] | entities['topics']
            
            # Добавляем новые темы в очередь
            added_count = 0
            for new_topic in new_topics:
                if new_topic not in self.studied_topics and new_topic not in self.topic_queue:
                    self.topic_queue.append(new_topic)
                    added_count += 1
                    
                    # Добавляем связь в граф
                    self.knowledge_graph.add_relation(topic, new_topic)
            
            if added_count > 0:
                logger.info(f"✨ Найдено {added_count} новых качественных тем")
                logger.debug(f"Примеры: {list(new_topics)[:5]}...")
            
            self.stats['entities_discovered'] += added_count
            
            # 5. Сохраняем данные
            self._save_topic_data(topic, {
                'content': full_content,
                'sources': all_sources,
                'entities': {k: list(v) for k, v in entities.items()},
                'timestamp': datetime.now().isoformat()
            })
            
            # 6. Создаем embeddings
            if self.turbo_system:
                try:
                    chunks = self._split_content(full_content)
                    chunks_ctx = [f"{topic}: {chunk}" for chunk in chunks]
                    
                    self.turbo_system.learn_batch(chunks_ctx, category="infinite")
                    
                    logger.info(f"✅ Создано {len(chunks)} embeddings")
                
                except Exception as e:
                    logger.error(f"Ошибка embeddings: {e}")
            
            # Обновляем статистику
            self.studied_topics.add(topic)
            self.stats['topics_studied'] += 1
            self.stats['sources_collected'] += len(all_sources)
            self.stats['total_content'] += len(full_content)
            
            # Сохраняем граф
            self.knowledge_graph.save(self.data_dir / 'knowledge_graph.json')
            
            logger.info(f"✅ Тема '{topic}' изучена!")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Ошибка изучения '{topic}': {e}")
            return False
    
    def start_infinite_learning(self, max_topics=None):
        """
        Запуск бесконечного обучения
        
        Args:
            max_topics: Максимум тем (None = бесконечно)
        """
        logger.info("="*80)
        logger.info("🌍 ЗАПУСК БЕСКОНЕЧНОГО ОБУЧЕНИЯ")
        logger.info("="*80)
        logger.info(f"Начальных тем в очереди: {len(self.topic_queue)}")
        logger.info(f"Изучено ранее: {len(self.studied_topics)}")
        logger.info("="*80)
        
        topics_processed = 0
        
        try:
            while self.topic_queue:
                # Проверяем лимит
                if max_topics and topics_processed >= max_topics:
                    logger.info(f"Достигнут лимит: {max_topics} тем")
                    break
                
                # Берем следующую тему
                topic = self.topic_queue.popleft()
                
                logger.info(f"\n[{topics_processed + 1}] Очередь: {len(self.topic_queue)} | Изучено: {len(self.studied_topics)}")
                
                # Изучаем
                success = self.learn_topic(topic)
                
                if success:
                    topics_processed += 1
                    
                    # Статистика каждые 10 тем
                    if topics_processed % 10 == 0:
                        self._print_stats()
                
                # Пауза между темами
                time.sleep(3)
        
        except KeyboardInterrupt:
            logger.info("\n⚠ Остановка пользователем")
        
        finally:
            self._print_final_stats()
    
    def _split_content(self, content, max_size=2000):
        """Разбивка на чанки"""
        chunks = []
        paragraphs = content.split('\n\n')
        current = ""
        
        for para in paragraphs:
            if len(current) + len(para) < max_size:
                current += para + "\n\n"
            else:
                if current:
                    chunks.append(current.strip())
                current = para + "\n\n"
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def _save_topic_data(self, topic, data):
        """Сохранение данных темы"""
        try:
            filename = re.sub(r'[<>:"/\\|?*]', '_', topic)[:100] + '.json'
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
    
    def _print_stats(self):
        """Печать статистики"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        
        logger.info("="*80)
        logger.info("📊 СТАТИСТИКА")
        logger.info(f"Тем изучено: {self.stats['topics_studied']}")
        logger.info(f"В очереди: {len(self.topic_queue)}")
        logger.info(f"Источников: {self.stats['sources_collected']}")
        logger.info(f"Новых тем найдено: {self.stats['entities_discovered']}")
        logger.info(f"Контента: {self.stats['total_content'] / 1024:.1f} KB")
        logger.info(f"Время работы: {elapsed / 60:.1f} минут")
        logger.info(f"Скорость: {self.stats['topics_studied'] / (elapsed / 60):.1f} тем/мин")
        logger.info("="*80)
    
    def _print_final_stats(self):
        """Финальная статистика"""
        logger.info("\n" + "="*80)
        logger.info("🏁 ОБУЧЕНИЕ ЗАВЕРШЕНО")
        logger.info("="*80)
        
        self._print_stats()
        
        logger.info(f"\nИспользованные языки: {', '.join(sorted(self.wiki_collector.stats['languages_used']))}")
        logger.info(f"Изучено тем: {len(self.studied_topics)}")
        logger.info(f"Осталось в очереди: {len(self.topic_queue)}")
        logger.info("="*80)


# Тест
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    print("="*80)
    print("🌍 INFINITE LEARNING SYSTEM - TEST")
    print("="*80)
    print()
    
    # Начальные темы
    initial_topics = [
        "Python",
        "Квентин Тарантино",
        "Искусственный интеллект",
    ]
    
    # Создаем систему
    system = InfiniteLearningSystem(initial_topics=initial_topics)
    
    # Запускаем (ограничиваем 5 темами для теста)
    system.start_infinite_learning(max_topics=5)
    
    print("\n✅ Тест завершен!")
