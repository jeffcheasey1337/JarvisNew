"""
Модуль системного контроля (громкость, яркость и т.д.)
"""

import asyncio
import logging
import subprocess
import platform

logger = logging.getLogger(__name__)


class SystemControl:
    """Управление системными функциями"""
    
    def __init__(self):
        self.system = platform.system()
    
    async def execute_command(self, user_input, entities):
        """Выполнение системной команды"""
        user_lower = user_input.lower()
        
        if 'громкость' in user_lower:
            return await self.control_volume(user_input)
        elif 'яркость' in user_lower:
            return await self.control_brightness(user_input)
        elif 'выключи компьютер' in user_lower:
            return await self.shutdown_system()
        elif 'перезагрузи компьютер' in user_lower:
            return await self.restart_system()
        else:
            return "Доступные команды: громкость, яркость, выключение, перезагрузка"
    
    async def control_volume(self, command):
        """Управление громкостью"""
        try:
            if 'увеличь' in command or 'громче' in command:
                change = 10
            elif 'уменьши' in command or 'тише' in command:
                change = -10
            elif 'максимум' in command:
                change = 100
            elif 'выключи звук' in command:
                change = 0
            else:
                return "Укажите, как изменить громкость"
            
            if self.system == "Linux":
                if change == 0:
                    subprocess.run(['amixer', 'set', 'Master', 'mute'])
                else:
                    subprocess.run(['amixer', 'set', 'Master', f'{abs(change)}%{"+" if change > 0 else "-"}'])
            
            return f"Громкость {'увеличена' if change > 0 else 'уменьшена' if change < 0 else 'выключена'}"
            
        except Exception as e:
            logger.error(f"Ошибка управления громкостью: {e}")
            return "Не удалось изменить громкость"
    
    async def control_brightness(self, command):
        """Управление яркостью"""
        try:
            # Это требует специальных прав
            return "Управление яркостью требует системных прав"
            
        except Exception as e:
            logger.error(f"Ошибка управления яркостью: {e}")
            return "Не удалось изменить яркость"
    
    async def shutdown_system(self):
        """Выключение системы"""
        return "Для безопасности автоматическое выключение отключено. Выключите систему вручную"
    
    async def restart_system(self):
        """Перезагрузка системы"""
        return "Для безопасности автоматическая перезагрузка отключена"
