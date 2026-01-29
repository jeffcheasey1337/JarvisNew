"""
Модуль управления файлами
"""

import asyncio
import logging
import os
import subprocess
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class FileManager:
    """Менеджер файловой системы"""
    
    def __init__(self):
        self.allowed_extensions = {
            '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.py', '.js', '.html', '.css', '.json', '.md'
        }
    
    async def open_file(self, user_input, entities):
        """Открытие файла"""
        try:
            # Извлечение имени файла из запроса
            filename = self._extract_filename(user_input)
            
            if not filename:
                return "Укажите имя файла для открытия"
            
            # Поиск файла
            file_path = self._find_file(filename)
            
            if not file_path:
                return f"Файл '{filename}' не найден"
            
            # Открытие файла
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.call(['xdg-open', file_path])
            
            return f"Открываю файл: {file_path.name}"
            
        except Exception as e:
            logger.error(f"Ошибка открытия файла: {e}")
            return "Не удалось открыть файл"
    
    async def create_file(self, user_input, entities):
        """Создание файла"""
        try:
            filename = self._extract_filename(user_input)
            
            if not filename:
                return "Укажите имя для нового файла"
            
            # Определение директории
            save_dir = Path.home() / "Documents" / "JARVIS"
            save_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = save_dir / filename
            
            # Создание файла
            file_path.touch()
            
            return f"Файл '{filename}' создан в {save_dir}"
            
        except Exception as e:
            logger.error(f"Ошибка создания файла: {e}")
            return "Не удалось создать файл"
    
    def _extract_filename(self, text):
        """Извлечение имени файла из текста"""
        # Упрощенная версия - ищем слова с расширениями
        words = text.split()
        for word in words:
            if any(word.endswith(ext) for ext in self.allowed_extensions):
                return word
        return None
    
    def _find_file(self, filename):
        """Поиск файла в стандартных директориях"""
        search_dirs = [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.home() / "Documents" / "JARVIS"
        ]
        
        for directory in search_dirs:
            if directory.exists():
                for file_path in directory.rglob(filename):
                    return file_path
        
        return None
