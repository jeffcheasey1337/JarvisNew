"""
Модуль веб-поиска
"""

import asyncio
import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)


class WebSearch:
    """Класс для веб-поиска"""
    
    def __init__(self, config):
        self.config = config
    
    async def search(self, user_input, entities):
        """
        Поиск в интернете
        
        Args:
            user_input: Запрос пользователя
            entities: Извлеченные сущности
            
        Returns:
            str: Результаты поиска
        """
        try:
            # Извлечение поискового запроса
            query = entities.get('query', user_input.replace('найди', '').replace('поищи', '').strip())
            
            logger.info(f"Поиск: {query}")
            
            # Выполнение поиска
            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=3):
                    results.append(result)
            
            if not results:
                return f"Не удалось найти информацию по запросу: {query}"
            
            # Формирование ответа
            response = f"Результаты поиска по запросу '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                response += f"{i}. {result['title']}\n"
                response += f"   {result['body'][:150]}...\n"
                response += f"   Источник: {result['href']}\n\n"
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return "Произошла ошибка при поиске. Проверьте подключение к интернету"
