# -*- coding: utf-8 -*-
"""
Упрощенный тест голосовых систем JARVIS
Без зависаний и проблем с asyncio
"""

import sys
import os

# Исправление кодировки для PyCharm
if 'PYCHARM_HOSTED' in os.environ:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_microphone():
    """Тест микрофона"""
    print("\n" + "="*70)
    print("ТЕСТ 1: ПРОВЕРКА МИКРОФОНА")
    print("="*70)

    try:
        import sounddevice as sd

        print("\n[1] Список ВСЕХ устройств:")
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            device_type = []
            if device['max_input_channels'] > 0:
                device_type.append("INPUT")
            if device['max_output_channels'] > 0:
                device_type.append("OUTPUT")

            print(f"\n  [{i}] {device['name']}")
            print(f"      Тип: {', '.join(device_type)}")
            print(f"      Входных каналов: {device['max_input_channels']}")
            print(f"      Частота: {device['default_samplerate']} Hz")

        print("\n[2] Текущее ВХОДНОЕ устройство (микрофон):")
        try:
            default_input = sd.query_devices(kind='input')
            print(f"  Название: {default_input['name']}")
            print(f"  Каналов: {default_input['max_input_channels']}")

            if default_input['max_input_channels'] > 0:
                print("\n  [OK] Микрофон найден и доступен!")

                # Попробовать записать звук
                print("\n[3] Проверка записи с микрофона...")
                print("  Говорите ЧТО-НИБУДЬ в микрофон (3 секунды)...")

                import numpy as np

                duration = 3
                recording = sd.rec(int(duration * 16000),
                                  samplerate=16000,
                                  channels=1,
                                  dtype='int16')
                sd.wait()

                # Проверить, есть ли звук
                max_amplitude = np.abs(recording).max()
                print(f"\n  Максимальная амплитуда: {max_amplitude}")

                if max_amplitude > 100:
                    print("  [OK] Микрофон ЗАПИСЫВАЕТ звук!")
                    return True
                else:
                    print("  [ПРОБЛЕМА] Микрофон не слышит!")
                    print("  Возможные причины:")
                    print("    - Микрофон выключен")
                    print("    - Неправильное устройство по умолчанию")
                    print("    - Уровень записи на минимуме")
                    print("\n  РЕШЕНИЕ:")
                    print("    1. Windows → Настройки → Звук")
                    print("    2. Ввод → Выберите правильный микрофон")
                    print("    3. Проверьте уровень громкости микрофона")
                    return False
            else:
                print("\n  [ОШИБКА] Нет доступных входных каналов!")
                return False

        except Exception as e:
            print(f"\n  [ОШИБКА] Не найдено входное устройство: {e}")
            return False

    except Exception as e:
        print(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_speakers():
    """Тест динамиков/наушников"""
    print("\n" + "="*70)
    print("ТЕСТ 2: ПРОВЕРКА ДИНАМИКОВ")
    print("="*70)

    try:
        import sounddevice as sd
        import numpy as np

        print("\nВоспроизведение тестового сигнала (1 секунда)...")
        print("Вы должны услышать ЗВУКОВОЙ СИГНАЛ!")

        # Генерация простого сигнала (440 Hz - нота Ля)
        duration = 1
        frequency = 440
        samplerate = 44100

        t = np.linspace(0, duration, int(samplerate * duration))
        signal = 0.3 * np.sin(2 * np.pi * frequency * t)

        sd.play(signal, samplerate)
        sd.wait()

        print("\n[OK] Сигнал воспроизведен")

        heard = input("\nВы СЛЫШАЛИ звуковой сигнал? (да/нет): ").lower().strip()

        if heard in ['да', 'yes', 'y', 'д']:
            print("[OK] Динамики РАБОТАЮТ!")
            return True
        else:
            print("[ПРОБЛЕМА] Звук не слышен!")
            print("  Проверьте:")
            print("    - Динамики/наушники подключены")
            print("    - Громкость Windows")
            print("    - Звук не отключен")
            return False

    except Exception as e:
        print(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pyttsx3():
    """Тест синтеза речи pyttsx3"""
    print("\n" + "="*70)
    print("ТЕСТ 3: СИНТЕЗ РЕЧИ (PYTTSX3)")
    print("="*70)

    try:
        import pyttsx3

        print("\nИнициализация pyttsx3...")
        engine = pyttsx3.init()

        print("[OK] pyttsx3 инициализирован")

        # Список голосов
        print("\nДоступные голоса:")
        voices = engine.getProperty('voices')

        russian_voice = None
        for i, voice in enumerate(voices[:10], 1):
            print(f"\n  [{i}] {voice.name}")

            # Попытка найти русский голос
            if 'ru' in str(voice.languages).lower() or 'russian' in voice.name.lower():
                russian_voice = voice
                print("      ^^ РУССКИЙ ГОЛОС ^^")

        # Установить русский голос если нашли
        if russian_voice:
            engine.setProperty('voice', russian_voice.id)
            print(f"\n[OK] Установлен русский голос: {russian_voice.name}")

        # Настройки
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 20)
        engine.setProperty('volume', 1.0)

        print("\n" + "-"*70)
        print("ТЕСТ ОЗВУЧИВАНИЯ")
        print("-"*70)
        print("\nСейчас будет произнесено 3 фразы:")

        test_phrases = [
            "Доброе утро, сэр.",
            "Да, сэр.",
            "Системы готовы."
        ]

        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n  [{i}] Озвучиваю: '{phrase}'")
            try:
                engine.say(phrase)
                engine.runAndWait()
                print("      [OK] Произнесено")
            except Exception as e:
                print(f"      [ОШИБКА] {e}")
                return False

        print("\n" + "-"*70)
        heard = input("\nВы СЛЫШАЛИ голос? (да/нет): ").lower().strip()

        if heard in ['да', 'yes', 'y', 'д']:
            print("[OK] Синтез речи РАБОТАЕТ!")
            return True
        else:
            print("[ПРОБЛЕМА] Голос не слышен!")
            print("  Но тест динамиков прошел...")
            print("  Возможно проблема с pyttsx3 или голосами Windows")
            return False

    except Exception as e:
        print(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_jarvis_synthesis():
    """Тест модуля синтеза JARVIS БЕЗ asyncio"""
    print("\n" + "="*70)
    print("ТЕСТ 4: МОДУЛЬ СИНТЕЗА JARVIS")
    print("="*70)

    try:
        print("\nПроверка файла speech_synthesis.py...")

        # Проверить что файл существует
        import os
        if not os.path.exists('core/speech_synthesis.py'):
            print("[ОШИБКА] Файл core/speech_synthesis.py не найден!")
            return False

        print("[OK] Файл найден")

        # Попробовать импортировать
        print("\nИмпорт модуля...")
        from core.speech_synthesis import SpeechSynthesizer
        print("[OK] Модуль импортирован")

        # Инициализация
        print("\nИнициализация SpeechSynthesizer...")
        config = {}
        synth = SpeechSynthesizer(config)

        if synth.engine is None:
            print("[ОШИБКА] synth.engine = None")
            print("Проблема с инициализацией pyttsx3 в модуле")
            return False

        print("[OK] SpeechSynthesizer инициализирован")

        # ВАЖНО: Использовать синхронный метод вместо asyncio
        print("\n" + "-"*70)
        print("ТЕСТ ОЗВУЧИВАНИЯ ЧЕРЕЗ JARVIS")
        print("-"*70)

        test_phrases = [
            "Доброе утро, сэр.",
            "Да, сэр."
        ]

        print("\nИспользуется СИНХРОННЫЙ метод (_speak_sync)...")

        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n  [{i}] Озвучиваю: '{phrase}'")
            try:
                # Прямой вызов синхронного метода
                synth._speak_sync(phrase)
                print("      [OK] Произнесено")
            except Exception as e:
                print(f"      [ОШИБКА] {e}")
                import traceback
                traceback.print_exc()
                return False

        print("\n" + "-"*70)
        heard = input("\nВы СЛЫШАЛИ голос JARVIS? (да/нет): ").lower().strip()

        if heard in ['да', 'yes', 'y', 'д']:
            print("[OK] Модуль синтеза JARVIS РАБОТАЕТ!")
            return True
        else:
            print("[ПРОБЛЕМА] Голос JARVIS не слышен")
            return False

    except Exception as e:
        print(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vosk_simple():
    """Простой тест Vosk"""
    print("\n" + "="*70)
    print("ТЕСТ 5: РАСПОЗНАВАНИЕ РЕЧИ (VOSK)")
    print("="*70)

    try:
        from vosk import Model, KaldiRecognizer
        import sounddevice as sd
        import queue
        import json

        print("\nЗагрузка модели...")
        model_path = "models/vosk-model-ru"

        if not os.path.exists(model_path):
            print(f"[ОШИБКА] Модель не найдена: {model_path}")
            return False

        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)

        print("[OK] Модель загружена")

        print("\n" + "-"*70)
        print("ТЕСТ РАСПОЗНАВАНИЯ")
        print("-"*70)
        print("\nГОВОРИТЕ В МИКРОФОН!")
        print("Скажите что-нибудь громко и четко")
        print("(тест 5 секунд)")
        print("")

        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                print(f"  [Предупреждение] {status}")
            q.put(bytes(indata))

        recognized_text = ""

        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000,
                                  dtype='int16', channels=1, callback=callback):

                import time
                start_time = time.time()

                while time.time() - start_time < 5:
                    data = q.get()

                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get('text', '')
                        if text:
                            recognized_text += text + " "
                            print(f"  [Распознано] {text}")
                    else:
                        partial = json.loads(recognizer.PartialResult())
                        text = partial.get('partial', '')
                        if text:
                            print(f"  [Частично] {text}          ", end='\r')

        except Exception as e:
            print(f"\n[ОШИБКА записи] {e}")
            return False

        print("\n")

        if recognized_text.strip():
            print(f"[OK] Распознано: '{recognized_text.strip()}'")
            return True
        else:
            print("[ПРОБЛЕМА] Ничего не распознано!")
            print("\nВозможные причины:")
            print("  1. Микрофон не работает (проверьте Тест 1)")
            print("  2. Говорили слишком тихо")
            print("  3. Неправильное устройство выбрано в Windows")
            print("\nПопробуйте:")
            print("  - Говорить ГРОМЧЕ")
            print("  - Проверить уровень записи в Windows")
            print("  - Выбрать другой микрофон в настройках Windows")
            return False

    except Exception as e:
        print(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*70)
    print("  ДИАГНОСТИКА ГОЛОСОВЫХ СИСТЕМ JARVIS")
    print("  (Исправленная версия без зависаний)")
    print("="*70)
    print()
    input("Нажмите Enter для начала...")

    results = {}

    # Тест 1: Микрофон
    results['microphone'] = test_microphone()

    if not results['microphone']:
        print("\n" + "="*70)
        print("ВНИМАНИЕ!")
        print("="*70)
        print("\nМикрофон не работает!")
        print("Без микрофона JARVIS не сможет вас слышать.")
        print("\nИсправьте проблему с микрофоном и запустите тест снова.")
        print()
        input("Нажмите Enter для выхода...")
        return

    # Тест 2: Динамики
    results['speakers'] = test_speakers()

    if not results['speakers']:
        print("\n" + "="*70)
        print("ВНИМАНИЕ!")
        print("="*70)
        print("\nДинамики не работают!")
        print("Без динамиков вы не услышите голос JARVIS.")
        print("\nИсправьте проблему со звуком и запустите тест снова.")
        print()
        input("Нажмите Enter для выхода...")
        return

    # Тест 3: pyttsx3
    results['pyttsx3'] = test_pyttsx3()

    # Тест 4: JARVIS синтез
    results['jarvis_synthesis'] = test_jarvis_synthesis()

    # Тест 5: Vosk распознавание
    results['vosk'] = test_vosk_simple()

    # Итоги
    print("\n" + "="*70)
    print("ИТОГИ ДИАГНОСТИКИ")
    print("="*70)
    print()

    tests = [
        ('Микрофон', 'microphone'),
        ('Динамики', 'speakers'),
        ('pyttsx3', 'pyttsx3'),
        ('JARVIS синтез', 'jarvis_synthesis'),
        ('Vosk распознавание', 'vosk')
    ]

    for name, key in tests:
        if key in results:
            status = "[OK] РАБОТАЕТ" if results[key] else "[ПРОБЛЕМА] НЕ РАБОТАЕТ"
            print(f"  {name:20} : {status}")

    print()
    print("="*70)

    all_ok = all(results.values())

    if all_ok:
        print("\n[ОТЛИЧНО] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\nГолосовые системы JARVIS полностью функциональны.")
        print("Можете запускать main.py - JARVIS будет работать!")
    else:
        print("\n[ВНИМАНИЕ] Есть проблемы!")
        print("\nНеобходимо исправить проблемы выше.")
        print("Без этого JARVIS не сможет полноценно работать.")

    print()
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nТест прерван пользователем.")
    except Exception as e:
        print(f"\n\nНепредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter...")
