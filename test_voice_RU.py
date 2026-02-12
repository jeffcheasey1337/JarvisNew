# -*- coding: utf-8 -*-
"""
Диагностика голосовых систем JARVIS
Русская версия БЕЗ крокозябр
"""

import sys
import os
import subprocess

# ПРИНУДИТЕЛЬНАЯ установка UTF-8 для Windows консоли
if sys.platform == 'win32':
    # Изменить кодовую страницу консоли на UTF-8
    subprocess.run('chcp 65001', shell=True, capture_output=True)
    
    # Переназначить stdout/stderr с UTF-8
    import codecs
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def print_safe(text):
    """Безопасный вывод текста"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Если не получается - пишем в ASCII
        print(text.encode('ascii', 'replace').decode('ascii'))

def test_microphone():
    """Тест микрофона"""
    print_safe("\n" + "="*70)
    print_safe("ТЕСТ 1: МИКРОФОН")
    print_safe("="*70)
    
    try:
        import sounddevice as sd
        
        print_safe("\nДоступные устройства:")
        print(sd.query_devices())
        
        print_safe("\nТекущее устройство ввода:")
        default_input = sd.query_devices(kind='input')
        print_safe(f"  Название: {default_input['name']}")
        print_safe(f"  Каналов: {default_input['max_input_channels']}")
        print_safe(f"  Частота: {default_input['default_samplerate']} Hz")
        
        print_safe("\n[OK] Микрофон доступен")
        return True
        
    except Exception as e:
        print_safe(f"\n[ОШИБКА] {e}")
        return False

def test_vosk_recognition():
    """Тест распознавания речи Vosk"""
    print_safe("\n" + "="*70)
    print_safe("ТЕСТ 2: РАСПОЗНАВАНИЕ РЕЧИ (VOSK)")
    print_safe("="*70)
    
    try:
        from vosk import Model, KaldiRecognizer
        import sounddevice as sd
        import queue
        import json
        
        print_safe("\nЗагрузка модели Vosk...")
        model_path = "models/vosk-model-ru"
        
        try:
            model = Model(model_path)
            print_safe(f"[OK] Модель загружена: {model_path}")
        except:
            print_safe(f"[ОШИБКА] Модель не найдена: {model_path}")
            return False
        
        recognizer = KaldiRecognizer(model, 16000)
        
        print_safe("\n" + "-"*70)
        print_safe("ТЕСТ РАСПОЗНАВАНИЯ")
        print_safe("-"*70)
        print_safe("\nГОВОРИТЕ В МИКРОФОН!")
        print_safe("(тест 5 секунд)")
        print_safe("")
        
        q = queue.Queue()
        
        def audio_callback(indata, frames, time, status):
            q.put(bytes(indata))
        
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                              channels=1, callback=audio_callback):
            
            import time
            start_time = time.time()
            recognized_text = ""
            
            while time.time() - start_time < 5:
                data = q.get()
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '')
                    if text:
                        recognized_text += text + " "
                        print_safe(f"  Распознано: {text}")
                else:
                    partial = json.loads(recognizer.PartialResult())
                    text = partial.get('partial', '')
                    if text:
                        # Используем \r для перезаписи строки
                        print(f"  [Частично]: {text}                    ", end='\r', flush=True)
        
        print_safe("\n")
        
        if recognized_text.strip():
            print_safe(f"[OK] ИТОГО распознано: '{recognized_text.strip()}'")
            return True
        else:
            print_safe("[ВНИМАНИЕ] Ничего не распознано")
            print_safe("   Возможные причины:")
            print_safe("   - Микрофон не подключен")
            print_safe("   - Уровень громкости слишком низкий")
            print_safe("   - Говорили слишком тихо")
            return False
        
    except Exception as e:
        print_safe(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pyttsx3_synthesis():
    """Тест синтеза речи pyttsx3"""
    print_safe("\n" + "="*70)
    print_safe("ТЕСТ 3: СИНТЕЗ РЕЧИ (PYTTSX3)")
    print_safe("="*70)
    
    try:
        import pyttsx3
        
        print_safe("\nИнициализация pyttsx3...")
        engine = pyttsx3.init()
        
        print_safe("[OK] pyttsx3 инициализирован")
        
        print_safe("\nДоступные голоса:")
        voices = engine.getProperty('voices')
        
        for i, voice in enumerate(voices[:5], 1):
            print_safe(f"\n  [{i}] {voice.name}")
            print_safe(f"      ID: {voice.id[:50]}...")
            print_safe(f"      Языки: {voice.languages}")
        
        current_rate = engine.getProperty('rate')
        current_volume = engine.getProperty('volume')
        
        print_safe(f"\nТекущие настройки:")
        print_safe(f"  Скорость: {current_rate}")
        print_safe(f"  Громкость: {current_volume}")
        
        print_safe("\n" + "-"*70)
        print_safe("ТЕСТ ОЗВУЧИВАНИЯ")
        print_safe("-"*70)
        
        test_phrases = [
            "Доброе утро, сэр.",
            "Да, сэр.",
            "Системы готовы к работе."
        ]
        
        for phrase in test_phrases:
            print_safe(f"\nОзвучиваю: '{phrase}'")
            print_safe("(Вы должны услышать голос!)")
            
            try:
                engine.say(phrase)
                engine.runAndWait()
                print_safe("  [OK] Озвучено")
            except Exception as e:
                print_safe(f"  [ОШИБКА] {e}")
                return False
        
        print_safe("\n[OK] Синтез речи работает!")
        
        print_safe("\n" + "-"*70)
        heard = input("\nВы СЛЫШАЛИ голос? (да/нет): ").lower().strip()
        
        if heard in ['да', 'yes', 'y', 'д']:
            print_safe("[OK] Голосовой синтез РАБОТАЕТ!")
            return True
        else:
            print_safe("[ОШИБКА] Голос не слышен")
            print_safe("\nВозможные причины:")
            print_safe("  - Динамики выключены")
            print_safe("  - Звук Windows отключен")
            print_safe("  - Громкость на минимуме")
            return False
        
    except Exception as e:
        print_safe(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_jarvis_speech_synthesis():
    """Тест модуля синтеза JARVIS"""
    print_safe("\n" + "="*70)
    print_safe("ТЕСТ 4: МОДУЛЬ СИНТЕЗА JARVIS")
    print_safe("="*70)
    
    try:
        import asyncio
        from core.speech_synthesis import SpeechSynthesizer
        
        print_safe("\nИнициализация SpeechSynthesizer...")
        config = {}
        synthesizer = SpeechSynthesizer(config)
        
        if synthesizer.engine:
            print_safe("[OK] SpeechSynthesizer инициализирован")
        else:
            print_safe("[ОШИБКА] SpeechSynthesizer.engine = None")
            return False
        
        print_safe("\n" + "-"*70)
        print_safe("ТЕСТ ОЗВУЧИВАНИЯ ЧЕРЕЗ JARVIS")
        print_safe("-"*70)
        
        test_phrases = [
            "Доброе утро, сэр.",
            "Да, сэр.",
            "Я готов к работе."
        ]
        
        async def test():
            for phrase in test_phrases:
                print_safe(f"\nОзвучиваю: '{phrase}'")
                await synthesizer.speak(phrase)
        
        asyncio.run(test())
        
        print_safe("\n[OK] Модуль синтеза JARVIS работает!")
        
        heard = input("\nВы СЛЫШАЛИ голос JARVIS? (да/нет): ").lower().strip()
        
        if heard in ['да', 'yes', 'y', 'д']:
            print_safe("[OK] Голосовой модуль JARVIS РАБОТАЕТ!")
            return True
        else:
            print_safe("[ОШИБКА] Голос JARVIS не слышен")
            return False
        
    except Exception as e:
        print_safe(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_jarvis_speech_recognition():
    """Тест модуля распознавания JARVIS"""
    print_safe("\n" + "="*70)
    print_safe("ТЕСТ 5: МОДУЛЬ РАСПОЗНАВАНИЯ JARVIS")
    print_safe("="*70)
    
    try:
        from core.speech_recognition import SpeechRecognizer
        import asyncio
        
        print_safe("\nИнициализация SpeechRecognizer...")
        config = {'vosk_model_path': 'models/vosk-model-ru'}
        recognizer = SpeechRecognizer(config)
        
        print_safe("[OK] SpeechRecognizer инициализирован")
        
        print_safe("\n" + "-"*70)
        print_safe("ТЕСТ РАСПОЗНАВАНИЯ ЧЕРЕЗ JARVIS")
        print_safe("-"*70)
        print_safe("\nСКАЖИТЕ: 'Привет Джарвис'")
        print_safe("(тест 10 секунд)")
        print_safe("")
        
        async def test():
            import time
            start = time.time()
            
            while time.time() - start < 10:
                text = await recognizer.listen_once()
                
                if text:
                    print_safe(f"[OK] Распознано: '{text}'")
                    return True
            
            print_safe("[ВНИМАНИЕ] Время вышло, ничего не распознано")
            return False
        
        result = asyncio.run(test())
        
        if result:
            print_safe("\n[OK] Модуль распознавания JARVIS РАБОТАЕТ!")
        else:
            print_safe("\n[ОШИБКА] Распознавание не работает или микрофон не слышит")
        
        return result
        
    except Exception as e:
        print_safe(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print_safe("="*70)
    print_safe("  ДИАГНОСТИКА ГОЛОСОВЫХ СИСТЕМ JARVIS")
    print_safe("="*70)
    print_safe("")
    print_safe("Этот скрипт проверит:")
    print_safe("  1. Микрофон")
    print_safe("  2. Распознавание речи (Vosk)")
    print_safe("  3. Синтез речи (pyttsx3)")
    print_safe("  4. Модуль синтеза JARVIS")
    print_safe("  5. Модуль распознавания JARVIS")
    print_safe("")
    input("Нажмите Enter для начала...")
    
    results = {}
    
    results['microphone'] = test_microphone()
    
    if results['microphone']:
        results['vosk'] = test_vosk_recognition()
    else:
        results['vosk'] = False
        print_safe("\n[ПРОПУЩЕНО] Тест Vosk пропущен (микрофон недоступен)")
    
    results['pyttsx3'] = test_pyttsx3_synthesis()
    results['jarvis_synthesis'] = test_jarvis_speech_synthesis()
    
    if results['microphone']:
        results['jarvis_recognition'] = test_jarvis_speech_recognition()
    else:
        results['jarvis_recognition'] = False
    
    # Итоги
    print_safe("\n" + "="*70)
    print_safe("ИТОГИ ДИАГНОСТИКИ")
    print_safe("="*70)
    print_safe("")
    
    for test_name, passed in results.items():
        status = "[OK] РАБОТАЕТ" if passed else "[ОШИБКА] НЕ РАБОТАЕТ"
        print_safe(f"  {test_name:25} : {status}")
    
    print_safe("")
    print_safe("="*70)
    
    all_passed = all(results.values())
    
    if all_passed:
        print_safe("[OK] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print_safe("")
        print_safe("Голосовые системы JARVIS полностью функциональны.")
    else:
        print_safe("[ОШИБКА] НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print_safe("")
        print_safe("Рекомендации:")
        
        if not results['microphone']:
            print_safe("  * Подключите микрофон")
            print_safe("  * Проверьте настройки Windows")
        
        if not results['pyttsx3']:
            print_safe("  * Установите: pip install pyttsx3 pywin32")
            print_safe("  * Проверьте динамики")
        
        if not results['jarvis_synthesis']:
            print_safe("  * Проверьте core/speech_synthesis.py")
        
        if not results['jarvis_recognition']:
            print_safe("  * Проверьте models/vosk-model-ru")
            print_safe("  * Проверьте core/speech_recognition.py")
    
    print_safe("")
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
