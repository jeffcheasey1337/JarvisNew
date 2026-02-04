# -*- coding: utf-8 -*-
"""
✅ WORKING WEB LEARNING v3.0
С исправленным User-Agent для Wikipedia
"""

import logging
import requests
import time
import re
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class WorkingWikipediaCollector:
    """Сборщик из Wikipedia с правильным User-Agent"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # ПРАВИЛЬНЫЙ User-Agent для Wikipedia
        self.session.headers.update({
            'User-Agent': 'JARVIS-Learning/1.0 (Educational Project; Python/3.11) requests/2.31.0'
        })
        
        self.stats = {
            'topics_processed': 0,
            'sources_collected': 0,
            'chars_collected': 0,
        }
    
    def search_wikipedia(self, query, lang='ru'):
        """Поиск в Wikipedia"""
        try:
            api_url = f"https://{lang}.wikipedia.org/w/api.php"
            
            # Поиск
            search_params = {
                'action': 'opensearch',
                'search': query,
                'limit': 3,
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=search_params, timeout=15)
            response.raise_for_status()
            
            results = response.json()
            
            if len(results) < 2 or not results[1]:
                return None
            
            title = results[1][0]
            
            # Получение контента
            content_params = {
                'action': 'query',
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'titles': title,
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=content_params, timeout=15)
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
            logger.debug(f"Ошибка Wikipedia {lang}: {e}")
            return None
    
    def collect_knowledge(self, topic):
        """Сбор знаний по теме"""
        logger.info(f"📚 Сбор: {topic}")
        
        knowledge = {
            'topic': topic,
            'sources': [],
            'content': [],
            'total_chars': 0,
        }
        
        # Русская Wikipedia
        wiki_ru = self.search_wikipedia(topic, lang='ru')
        if wiki_ru:
            knowledge['sources'].append(wiki_ru)
            knowledge['content'].append(wiki_ru['content'])
            logger.info(f"✓ Wikipedia RU: {len(wiki_ru['content'])} символов")
            time.sleep(1)
        
        # Английская Wikipedia
        wiki_en = self.search_wikipedia(topic, lang='en')
        if wiki_en:
            knowledge['sources'].append(wiki_en)
            knowledge['content'].append(wiki_en['content'])
            logger.info(f"✓ Wikipedia EN: {len(wiki_en['content'])} символов")
            time.sleep(1)
        
        knowledge['total_chars'] = sum(len(c) for c in knowledge['content'])
        
        self.stats['topics_processed'] += 1
        self.stats['sources_collected'] += len(knowledge['sources'])
        self.stats['chars_collected'] += knowledge['total_chars']
        
        if knowledge['sources']:
            logger.info(f"📊 Итого: {len(knowledge['sources'])} источников, {knowledge['total_chars']} символов")
        
        return knowledge


class WorkingLearningSystem:
    """Рабочая система обучения"""
    
    def __init__(self, turbo_system=None):
        self.turbo_system = turbo_system
        self.collector = WorkingWikipediaCollector()
        
        self.stats = {
            'topics_learned': 0,
            'total_content': 0,
            'embeddings_created': 0,
        }
        
        self.data_dir = Path('data/knowledge')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Система готова")
    
    def learn_topic(self, topic):
        """Обучение на теме"""
        try:
            logger.info(f"🎓 Обучение: {topic}")
            
            knowledge = self.collector.collect_knowledge(topic)
            
            if not knowledge['content']:
                logger.warning(f"⚠ Нет данных для '{topic}'")
                return False
            
            full_content = "\n\n".join(knowledge['content'])
            
            # Сохранение
            self._save(topic, knowledge)
            
            # Embeddings
            if self.turbo_system:
                try:
                    chunks = self._split(full_content)
                    chunks_ctx = [f"{topic}: {c}" for c in chunks]
                    
                    self.turbo_system.learn_batch(chunks_ctx, category="web")
                    
                    self.stats['embeddings_created'] += len(chunks)
                    logger.info(f"✅ Создано {len(chunks)} embeddings")
                except Exception as e:
                    logger.error(f"Ошибка embeddings: {e}")
            
            self.stats['topics_learned'] += 1
            self.stats['total_content'] += knowledge['total_chars']
            
            logger.info(f"✅ '{topic}' изучена!")
            return True
        
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            return False
    
    def _split(self, content, max_size=2000):
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
    
    def _save(self, topic, knowledge):
        """Сохранение"""
        try:
            filename = re.sub(r'[<>:"/\\|?*]', '_', topic)[:100] + '.json'
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
    
    def batch_learn(self, topics, delay=2):
        """Пакетное обучение"""
        logger.info(f"📚 Обучение: {len(topics)} тем")
        
        for i, topic in enumerate(topics):
            logger.info(f"[{i+1}/{len(topics)}] {topic}")
            self.learn_topic(topic)
            
            if i < len(topics) - 1:
                time.sleep(delay)
        
        logger.info("="*80)
        logger.info(f"Изучено: {self.stats['topics_learned']}/{len(topics)}")
        logger.info(f"Контент: {self.stats['total_content']} символов")
        logger.info(f"Embeddings: {self.stats['embeddings_created']}")
        logger.info("="*80)
    
    def get_stats(self):
        return {**self.stats, 'collector': self.collector.stats}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    print("="*80)
    print("✅ WORKING WEB LEARNING v3.0 - TEST")
    print("="*80)
    print()
    
    system = WorkingLearningSystem()
    
    test_topics = ["Python", "Квентин Тарантино"]
    
    system.batch_learn(test_topics, delay=2)
    
    stats = system.get_stats()
    print()
    print(f"Успешно: {stats['topics_learned']}/{len(test_topics)}")
    print(f"Контент: {stats['total_content']/1024:.1f} KB")
    print(f"Источников: {stats['collector']['sources_collected']}")
    print()
