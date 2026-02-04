# -*- coding: utf-8 -*-
"""
🌐 IMPROVED AUTONOMOUS WEB LEARNING SYSTEM v2.0
Улучшенная система с обходом блокировок

Источники:
✅ Wikipedia API (русская + английская)
✅ Specialized search libraries
✅ Multiple fallback options
✅ Anti-blocking measures
"""

import logging
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote_plus
import re
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ImprovedWebCollector:
    """Улучшенный сборщик знаний"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Ротация User-Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        self.stats = {
            'topics_processed': 0,
            'sources_collected': 0,
            'chars_collected': 0,
            'errors': 0,
        }
    
    def _get_random_ua(self):
        """Случайный User-Agent"""
        return random.choice(self.user_agents)
    
    def search_wikipedia(self, query, lang='ru'):
        """
        Поиск в Wikipedia через API
        
        Args:
            query: Поисковый запрос
            lang: Язык ('ru' или 'en')
            
        Returns:
            Dict с контентом
        """
        try:
            # Wikipedia API
            api_url = f"https://{lang}.wikipedia.org/w/api.php"
            
            # 1. Поиск статей
            search_params = {
                'action': 'opensearch',
                'search': query,
                'limit': 3,
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            search_results = response.json()
            
            if len(search_results) < 2 or not search_results[1]:
                return None
            
            # Берем первый результат
            title = search_results[1][0]
            
            # 2. Получаем контент статьи
            content_params = {
                'action': 'query',
                'prop': 'extracts',
                'exintro': True,  # Только введение
                'explaintext': True,  # Только текст
                'titles': title,
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=content_params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page_data in pages.items():
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
            logger.debug(f"Ошибка Wikipedia {lang}: {e}")
            return None
    
    def search_simple_wikipedia(self, query):
        """
        Simple Wikipedia (упрощенная версия)
        Отлично подходит для базовых концепций
        """
        try:
            api_url = "https://simple.wikipedia.org/w/api.php"
            
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
            
            # Получаем контент
            content_params = {
                'action': 'query',
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'titles': title,
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=content_params, timeout=10)
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            
            for page_data in pages.values():
                extract = page_data.get('extract', '')
                
                if extract and len(extract) > 50:
                    return {
                        'source': 'Simple Wikipedia',
                        'title': title,
                        'url': f"https://simple.wikipedia.org/wiki/{title.replace(' ', '_')}",
                        'content': extract,
                        'lang': 'simple'
                    }
        
        except Exception as e:
            logger.debug(f"Ошибка Simple Wikipedia: {e}")
        
        return None
    
    def search_wikidata(self, query):
        """
        Wikidata - структурированные данные
        """
        try:
            api_url = "https://www.wikidata.org/w/api.php"
            
            # Поиск сущности
            params = {
                'action': 'wbsearchentities',
                'search': query,
                'language': 'ru',
                'limit': 1,
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'search' in data and data['search']:
                entity = data['search'][0]
                
                description = entity.get('description', '')
                label = entity.get('label', '')
                
                if description:
                    return {
                        'source': 'Wikidata',
                        'title': label,
                        'content': f"{label}: {description}",
                        'url': f"https://www.wikidata.org/wiki/{entity['id']}"
                    }
        
        except Exception as e:
            logger.debug(f"Ошибка Wikidata: {e}")
        
        return None
    
    def collect_knowledge(self, topic):
        """
        Сбор знаний по теме из всех доступных источников
        
        Args:
            topic: Тема для изучения
            
        Returns:
            Dict с собранными знаниями
        """
        logger.info(f"📚 Сбор знаний: {topic}")
        
        knowledge = {
            'topic': topic,
            'sources': [],
            'content': [],
            'total_chars': 0,
        }
        
        try:
            # 1. Русская Wikipedia
            logger.debug("Поиск в Русской Wikipedia...")
            wiki_ru = self.search_wikipedia(topic, lang='ru')
            
            if wiki_ru:
                knowledge['sources'].append(wiki_ru)
                knowledge['content'].append(wiki_ru['content'])
                logger.info(f"✓ Wikipedia RU: {len(wiki_ru['content'])} символов")
                time.sleep(0.5)
            
            # 2. Английская Wikipedia
            logger.debug("Поиск в Английской Wikipedia...")
            wiki_en = self.search_wikipedia(topic, lang='en')
            
            if wiki_en:
                knowledge['sources'].append(wiki_en)
                knowledge['content'].append(wiki_en['content'])
                logger.info(f"✓ Wikipedia EN: {len(wiki_en['content'])} символов")
                time.sleep(0.5)
            
            # 3. Simple Wikipedia
            logger.debug("Поиск в Simple Wikipedia...")
            wiki_simple = self.search_simple_wikipedia(topic)
            
            if wiki_simple:
                knowledge['sources'].append(wiki_simple)
                knowledge['content'].append(wiki_simple['content'])
                logger.info(f"✓ Simple Wikipedia: {len(wiki_simple['content'])} символов")
                time.sleep(0.5)
            
            # 4. Wikidata
            logger.debug("Поиск в Wikidata...")
            wikidata = self.search_wikidata(topic)
            
            if wikidata:
                knowledge['sources'].append(wikidata)
                knowledge['content'].append(wikidata['content'])
                logger.info(f"✓ Wikidata: {len(wikidata['content'])} символов")
            
            # Подсчет
            knowledge['total_chars'] = sum(len(c) for c in knowledge['content'])
            
            self.stats['topics_processed'] += 1
            self.stats['sources_collected'] += len(knowledge['sources'])
            self.stats['chars_collected'] += knowledge['total_chars']
            
            logger.info(f"📊 Итого: {len(knowledge['sources'])} источников, {knowledge['total_chars']} символов")
            
            return knowledge
        
        except Exception as e:
            logger.error(f"Ошибка сбора знаний '{topic}': {e}")
            self.stats['errors'] += 1
            return knowledge


class ImprovedAutonomousLearning:
    """Улучшенная автономная система обучения"""
    
    def __init__(self, memory_system=None, turbo_system=None):
        self.memory_system = memory_system
        self.turbo_system = turbo_system
        
        # Коллектор
        self.collector = ImprovedWebCollector()
        
        # Статистика
        self.stats = {
            'topics_learned': 0,
            'total_content': 0,
            'embeddings_created': 0,
        }
        
        # Папка для сохранения
        self.data_dir = Path('data/knowledge')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Улучшенная система обучения готова")
    
    def learn_topic(self, topic):
        """
        Обучение на теме
        
        Args:
            topic: Тема для изучения
            
        Returns:
            Success status
        """
        try:
            logger.info(f"🎓 Обучение: {topic}")
            
            # 1. Собираем знания
            knowledge = self.collector.collect_knowledge(topic)
            
            if not knowledge['content']:
                logger.warning(f"⚠️ Нет данных для '{topic}'")
                return False
            
            # 2. Объединяем контент
            full_content = "\n\n".join(knowledge['content'])
            
            logger.info(f"📝 Собрано {len(knowledge['content'])} источников")
            
            # 3. Сохраняем
            self._save_knowledge(topic, knowledge)
            
            # 4. Создаем embeddings
            if self.turbo_system:
                try:
                    # Разбиваем на чанки
                    chunks = self._split_content(full_content, max_size=2000)
                    
                    # Добавляем контекст темы
                    chunks_with_context = [f"{topic}: {chunk}" for chunk in chunks]
                    
                    # Обрабатываем через GPU
                    result = self.turbo_system.learn_batch(
                        chunks_with_context,
                        category="web_learning"
                    )
                    
                    self.stats['embeddings_created'] += len(chunks)
                    
                    logger.info(f"✅ Создано {len(chunks)} embeddings")
                
                except Exception as e:
                    logger.error(f"Ошибка создания embeddings: {e}")
            
            # Статистика
            self.stats['topics_learned'] += 1
            self.stats['total_content'] += knowledge['total_chars']
            
            logger.info(f"✅ Тема '{topic}' изучена!")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Ошибка обучения '{topic}': {e}")
            return False
    
    def _split_content(self, content, max_size=2000):
        """Разбивка контента на чанки"""
        chunks = []
        
        # Разбиваем по параграфам
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _save_knowledge(self, topic, knowledge):
        """Сохранение знаний в файл"""
        try:
            filename = self._sanitize_filename(topic) + '.json'
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"💾 Сохранено: {filepath}")
        
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
    
    def _sanitize_filename(self, text):
        """Очистка имени файла"""
        text = re.sub(r'[<>:"/\\|?*]', '_', text)
        return text[:100]
    
    def batch_learn(self, topics_list, delay=2):
        """
        Пакетное обучение
        
        Args:
            topics_list: Список тем
            delay: Задержка между темами (сек)
        """
        logger.info(f"📚 Пакетное обучение: {len(topics_list)} тем")
        
        for i, topic in enumerate(topics_list):
            logger.info(f"[{i+1}/{len(topics_list)}] {topic}")
            
            success = self.learn_topic(topic)
            
            if not success:
                logger.warning(f"⚠️ Не удалось обучиться: {topic}")
            
            # Пауза
            if i < len(topics_list) - 1:
                time.sleep(delay)
        
        logger.info("="*80)
        logger.info("📊 СТАТИСТИКА")
        logger.info("="*80)
        logger.info(f"Тем изучено: {self.stats['topics_learned']}/{len(topics_list)}")
        logger.info(f"Контента собрано: {self.stats['total_content']} символов")
        logger.info(f"Embeddings создано: {self.stats['embeddings_created']}")
        logger.info("="*80)
    
    def get_stats(self):
        """Получение статистики"""
        return {
            **self.stats,
            'collector': self.collector.stats
        }


# Тестовый запуск
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*80)
    print("🌐 IMPROVED WEB LEARNING SYSTEM v2.0 - TEST")
    print("="*80)
    print()
    
    # Создаем систему
    system = ImprovedAutonomousLearning()
    
    # Тестовые темы
    test_topics = [
        "Python",
        "Квентин Тарантино",
        "Машинное обучение",
        "Sex Pistols",
    ]
    
    print(f"Тестируем на {len(test_topics)} темах")
    print()
    
    # Запускаем
    system.batch_learn(test_topics, delay=1)
    
    # Итоговая статистика
    stats = system.get_stats()
    
    print()
    print("Финальная статистика:")
    print(f"  Успешно изучено: {stats['topics_learned']}/{len(test_topics)}")
    print(f"  Контент: {stats['total_content']} символов ({stats['total_content']/1024:.1f} KB)")
    print(f"  Embeddings: {stats['embeddings_created']}")
    print(f"  Источников: {stats['collector']['sources_collected']}")
    print()
