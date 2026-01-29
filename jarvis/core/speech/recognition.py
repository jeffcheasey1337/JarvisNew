"""
Модуль распознавания речи (Speech-to-Text)
Использует Vosk для офлайн распознавания
"""

import asyncio
import json
import queue
import logging
from pathlib import Path
import sounddevice as sd
import vosk
import numpy as np

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """Класс для распознавания речи"""
    
    def __init__(self, config):
        self.config = config
        self.sample_rate = 16000
        self.audio_queue = queue.Queue()
        self.model = None
        self.recognizer = None
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Инициализация модели Vosk"""
        model_path = Path("models/vosk-model-ru")
        
        if not model_path.exists():
            logger.error(f"Модель не найдена: {model_path}")
            logger.info("Скачайте модель с https://alphacephei.com/vosk/models")
            logger.info("Распакуйте в папку models/vosk-model-ru")
            raise FileNotFoundError("Модель Vosk не найдена")
        
        logger.info(f"Загрузка модели из {model_path}")
        self.model = vosk.Model(str(model_path))
        self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
        self.recognizer.SetWords(True)
        logger.info("Модель загружена успешно")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback для записи аудио"""
        if status:
            logger.warning(f"Статус аудио: {status}")
        self.audio_queue.put(bytes(indata))
    
    async def listen(self, timeout=None):
        """
        Прослушивание микрофона
        
        Args:
            timeout: Максимальное время ожидания в секундах
            
        Returns:
            bytes: Аудиоданные или None при таймауте
        """
        try:
            # Очистка очереди
            while not self.audio_queue.empty():
                self.audio_queue.get()
            
            audio_chunks = []
            silence_threshold = 0.01
            silence_duration = 0
            max_silence = 2.0  # секунды тишины для остановки
            
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=self._audio_callback
            ):
                logger.debug("Начало записи...")
                start_time = asyncio.get_event_loop().time()
                recording_started = False
                
                while True:
                    # Проверка таймаута
                    if timeout and (asyncio.get_event_loop().time() - start_time) > timeout:
                        logger.debug("Таймаут ожидания")
                        return None
                    
                    try:
                        data = self.audio_queue.get(timeout=0.1)
                        
                        # Определение уровня звука
                        audio_level = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                        audio_level = np.abs(audio_level).mean() / 32768.0
                        
                        # Начало записи при обнаружении звука
                        if audio_level > silence_threshold:
                            recording_started = True
                            silence_duration = 0
                            audio_chunks.append(data)
                        elif recording_started:
                            silence_duration += 0.1
                            audio_chunks.append(data)
                            
                            # Остановка при длительной тишине
                            if silence_duration >= max_silence:
                                logger.debug("Конец записи")
                                break
                        
                    except queue.Empty:
                        await asyncio.sleep(0.01)
                        continue
                
                if audio_chunks:
                    return b''.join(audio_chunks)
                return None
                
        except Exception as e:
            logger.error(f"Ошибка записи аудио: {e}")
            return None
    
    async def recognize(self, audio_data):
        """
        Распознавание речи из аудиоданных
        
        Args:
            audio_data: Аудиоданные в формате bytes
            
        Returns:
            str: Распознанный текст
        """
        if not audio_data:
            return ""
        
        try:
            # Сброс распознавателя
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)
            
            # Обработка аудио
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
            else:
                result = json.loads(self.recognizer.FinalResult())
            
            text = result.get('text', '')
            
            if text:
                logger.info(f"Распознано: {text}")
                return text
            
            return ""
            
        except Exception as e:
            logger.error(f"Ошибка распознавания: {e}")
            return ""
    
    async def recognize_file(self, audio_file_path):
        """
        Распознавание речи из аудиофайла
        
        Args:
            audio_file_path: Путь к аудиофайлу
            
        Returns:
            str: Распознанный текст
        """
        try:
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            return await self.recognize(audio_data)
            
        except Exception as e:
            logger.error(f"Ошибка чтения файла {audio_file_path}: {e}")
            return ""
    
    def get_available_devices(self):
        """Получение списка доступных аудиоустройств"""
        devices = sd.query_devices()
        logger.info("Доступные аудиоустройства:")
        for i, device in enumerate(devices):
            logger.info(f"  {i}: {device['name']}")
        return devices
    
    def set_input_device(self, device_id):
        """Установка устройства ввода"""
        try:
            sd.default.device = device_id
            logger.info(f"Устройство ввода установлено: {device_id}")
        except Exception as e:
            logger.error(f"Ошибка установки устройства: {e}")
