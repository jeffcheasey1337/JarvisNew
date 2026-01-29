"""
Система памяти для хранения контекста, предпочтений и истории
Использует векторную базу данных для эффективного поиска
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import numpy as np
from collections import defaultdict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class MemorySystem:
    """Система долговременной и кратковременной памяти"""
    
    def __init__(self, config):
        self.config = config
        self.db_path = Path("data/memory_db")
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Векторная база данных для семантического поиска
        self.chroma_client = None
        self.collection = None
        
        # Модель для создания эмбеддингов
        self.embedder = None
        
        # Кратковременная память (текущая сессия)
        self.short_term_memory = []
        
        # Метаданные пользователя
        self.user_profile = {}
        
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Инициализация систем памяти"""
        try:
            logger.info("Инициализация системы памяти...")
            
            # Инициализация ChromaDB
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Создание или получение коллекции
            self.collection = self.chroma_client.get_or_create_collection(
                name="jarvis_memory",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Загрузка модели для эмбеддингов
            logger.info("Загрузка модели эмбеддингов...")
            self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            
            # Загрузка профиля пользователя
            self._load_user_profile()
            
            logger.info(f"Система памяти инициализирована. Записей: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации памяти: {e}")
            raise
    
    def _load_user_profile(self):
        """Загрузка профиля пользователя"""
        profile_path = Path("data/user_profile.json")
        
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                self.user_profile = json.load(f)
            logger.info("Профиль пользователя загружен")
        else:
            self.user_profile = {
                'name': 'сэр',
                'preferences': {},
                'important_dates': {},
                'routines': {},
                'created_at': datetime.now().isoformat()
            }
            self._save_user_profile()
    
    def _save_user_profile(self):
        """Сохранение профиля пользователя"""
        profile_path = Path("data/user_profile.json")
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.user_profile, f, ensure_ascii=False, indent=2)
    
    async def store_memory(self, content, memory_type="general", metadata=None):
        """
        Сохранение информации в долговременную память
        
        Args:
            content: Текстовое содержание для сохранения
            memory_type: Тип памяти (general, task, preference, fact)
            metadata: Дополнительные метаданные
        """
        try:
            if not content:
                return
            
            # Создание эмбеддинга
            embedding = self.embedder.encode(content).tolist()
            
            # Подготовка метаданных
            meta = {
                'type': memory_type,
                'timestamp': datetime.now().isoformat(),
                'importance': metadata.get('importance', 0.5) if metadata else 0.5
            }
            
            if metadata:
                meta.update(metadata)
            
            # Генерация уникального ID
            memory_id = f"{memory_type}_{datetime.now().timestamp()}"
            
            # Сохранение в векторную БД
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[meta],
                ids=[memory_id]
            )
            
            logger.info(f"Память сохранена: {memory_type} - {content[:50]}...")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения памяти: {e}")
    
    async def recall_memory(self, query, n_results=5, memory_type=None):
        """
        Поиск релевантной информации в памяти
        
        Args:
            query: Поисковый запрос
            n_results: Количество результатов
            memory_type: Фильтр по типу памяти
            
        Returns:
            list: Список релевантных воспоминаний
        """
        try:
            # Создание эмбеддинга запроса
            query_embedding = self.embedder.encode(query).tolist()
            
            # Подготовка фильтра
            where_filter = {"type": memory_type} if memory_type else None
            
            # Поиск
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )
            
            memories = []
            if results['documents'] and results['documents'][0]:
                for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                    memories.append({
                        'content': doc,
                        'metadata': meta
                    })
            
            logger.info(f"Найдено воспоминаний: {len(memories)}")
            return memories
            
        except Exception as e:
            logger.error(f"Ошибка поиска в памяти: {e}")
            return []
    
    async def get_context(self, user_input, max_memories=5):
        """
        Получение контекста для текущего запроса
        
        Args:
            user_input: Текущий запрос пользователя
            max_memories: Максимум воспоминаний для контекста
            
        Returns:
            dict: Словарь с контекстной информацией
        """
        try:
            context = {
                'relevant_memories': [],
                'user_info': self.user_profile,
                'recent_conversation': self.short_term_memory[-5:],
                'current_time': datetime.now().isoformat()
            }
            
            # Поиск релевантных воспоминаний
            memories = await self.recall_memory(user_input, n_results=max_memories)
            context['relevant_memories'] = [m['content'] for m in memories]
            
            return context
            
        except Exception as e:
            logger.error(f"Ошибка получения контекста: {e}")
            return {'relevant_memories': [], 'user_info': {}}
    
    async def get_daily_context(self):
        """
        Получение контекста на день (задачи, события, напоминания)
        
        Returns:
            dict: Словарь с информацией на день
        """
        try:
            today = datetime.now().date().isoformat()
            
            # Поиск задач и событий на сегодня
            tasks_query = f"задачи на {today}"
            tasks = await self.recall_memory(tasks_query, memory_type="task")
            
            events_query = f"события на {today}"
            events = await self.recall_memory(events_query, memory_type="event")
            
            return {
                'pending_tasks': [t['content'] for t in tasks],
                'scheduled_events': [e['content'] for e in events],
                'date': today
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения дневного контекста: {e}")
            return {'pending_tasks': [], 'scheduled_events': []}
    
    def add_to_short_term(self, role, content):
        """
        Добавление в кратковременную память (текущий диалог)
        
        Args:
            role: user или assistant
            content: Содержание сообщения
        """
        self.short_term_memory.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Ограничение размера кратковременной памяти
        if len(self.short_term_memory) > 50:
            self.short_term_memory = self.short_term_memory[-50:]
    
    async def update_user_preference(self, key, value):
        """
        Обновление предпочтений пользователя
        
        Args:
            key: Ключ предпочтения
            value: Значение
        """
        self.user_profile['preferences'][key] = value
        self._save_user_profile()
        
        # Сохранение в долговременную память
        await self.store_memory(
            f"Предпочтение пользователя: {key} = {value}",
            memory_type="preference",
            metadata={'key': key, 'value': value}
        )
    
    async def clean_old_memories(self, days=90):
        """
        Очистка старых воспоминаний
        
        Args:
            days: Сколько дней хранить
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Получение всех записей
            all_memories = self.collection.get()
            
            ids_to_delete = []
            for memory_id, metadata in zip(all_memories['ids'], all_memories['metadatas']):
                memory_time = datetime.fromisoformat(metadata['timestamp'])
                
                # Удаление старых неважных воспоминаний
                if memory_time < cutoff_date and metadata.get('importance', 0) < 0.7:
                    ids_to_delete.append(memory_id)
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Удалено старых воспоминаний: {len(ids_to_delete)}")
            
        except Exception as e:
            logger.error(f"Ошибка очистки памяти: {e}")
    
    async def export_memories(self, output_file="data/memory_export.json"):
        """Экспорт всех воспоминаний в файл"""
        try:
            all_memories = self.collection.get()
            
            export_data = {
                'user_profile': self.user_profile,
                'memories': []
            }
            
            for doc, meta, memory_id in zip(
                all_memories['documents'],
                all_memories['metadatas'],
                all_memories['ids']
            ):
                export_data['memories'].append({
                    'id': memory_id,
                    'content': doc,
                    'metadata': meta
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Память экспортирована в {output_file}")
            
        except Exception as e:
            logger.error(f"Ошибка экспорта памяти: {e}")
    
    async def close(self):
        """Закрытие соединений и сохранение данных"""
        try:
            # Сохранение профиля
            self._save_user_profile()
            
            # Сохранение кратковременной памяти в долговременную
            for entry in self.short_term_memory[-10:]:
                if entry['role'] == 'user':
                    await self.store_memory(
                        entry['content'],
                        memory_type="conversation"
                    )
            
            logger.info("Система памяти закрыта")
            
        except Exception as e:
            logger.error(f"Ошибка закрытия памяти: {e}")
