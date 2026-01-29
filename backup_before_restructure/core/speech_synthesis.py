# -*- coding: utf-8 -*-
"""
Модуль синтеза речи для JARVIS
РАБОЧАЯ версия для Windows с pyttsx3
"""

import asyncio
import logging
import pyttsx3
import threading

logger = logging.getLogger(__name__)


class SpeechSynthesizer:
    """Синтез речи через pyttsx3"""

    def __init__(self, config):
        self.config = config
        self.engine = None
        self._lock = threading.Lock()
        self._initialize_tts()

    def _initialize_tts(self):
        """Инициализация TTS"""
        try:
            logger.info("Инициализация голосового синтеза...")

            # Инициализация pyttsx3
            self.engine = pyttsx3.init()

            # Получение голосов
            voices = self.engine.getProperty('voices')

            # Поиск русского мужского голоса
            russian_voice = None
            male_voice = None

            for voice in voices:
                voice_name = voice.name.lower()

                # Русский голос
                if 'russian' in voice_name or 'ru' in str(voice.languages).lower():
                    russian_voice = voice
                    # Мужской русский
                    if 'male' in voice_name or 'pavel' in voice_name:
                        male_voice = voice
                        break

                # Английский мужской
                if not male_voice and ('male' in voice_name or 'david' in voice_name):
                    male_voice = voice

            # Установить голос
            if male_voice:
                self.engine.setProperty('voice', male_voice.id)
                logger.info(f"Установлен голос: {male_voice.name}")
            elif russian_voice:
                self.engine.setProperty('voice', russian_voice.id)
                logger.info(f"Установлен голос: {russian_voice.name}")

            # Настройка параметров
            current_rate = self.engine.getProperty('rate')
            self.engine.setProperty('rate', current_rate - 20)
            self.engine.setProperty('volume', 1.0)

            logger.info("Голосовой синтез готов")
            print("\n ГОЛОСОВОЙ РЕЖИМ АКТИВЕН!\n")

        except Exception as e:
            logger.error(f"Ошибка инициализации TTS: {e}")
            self.engine = None

    async def speak(self, text, save_path=None):
        """
        Озвучивание текста

        Args:
            text: Текст для озвучивания
            save_path: Путь для сохранения (не используется)
        """
        if not text:
            return

        try:
            # Вывод в консоль
            print(f"\nJARVIS: {text}\n")

            # Озвучивание
            if self.engine:
                # ВАЖНО: Запускать в executor для неблокирующей работы
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._speak_sync,
                    text
                )
            else:
                # Если TTS недоступен
                logger.warning("TTS engine не инициализирован")
                await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Ошибка синтеза речи: {e}")

    def _speak_sync(self, text):
        """
        Синхронное озвучивание (вызывается в отдельном потоке)

        Args:
            text: Текст для озвучивания
        """
        try:
            with self._lock:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Ошибка при озвучивании: {e}")

    def set_voice_parameters(self, rate=None, volume=None):
        """
        Настройка параметров голоса

        Args:
            rate: Скорость речи
            volume: Громкость (0.0 - 1.0)
        """
        if not self.engine:
            return

        try:
            if rate is not None:
                self.engine.setProperty('rate', rate)
                logger.info(f"Скорость речи: {rate}")

            if volume is not None:
                self.engine.setProperty('volume', min(1.0, max(0.0, volume)))
                logger.info(f"Громкость: {volume}")

        except Exception as e:
            logger.error(f"Ошибка установки параметров: {e}")


# Тест
if __name__ == "__main__":
    import asyncio

    async def test():
        synth = SpeechSynthesizer({})

        phrases = [
            "Доброе утро, сэр.",
            "Да, сэр.",
            "Системы готовы к работе."
        ]

        for phrase in phrases:
            print(f"Озвучиваю: {phrase}")
            await synth.speak(phrase)
            await asyncio.sleep(0.5)

    asyncio.run(test())