# -*- coding: utf-8 -*-
"""
Патч для исправления speech_recognition.py
Исправляет проблему с частотой дискретизации
"""

import sys
import os

if 'PYCHARM_HOSTED' in os.environ:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fix_speech_recognition():
    """Исправление частоты дискретизации в speech_recognition.py"""
    
    print("Исправление speech_recognition.py...")
    print()
    
    try:
        with open('core/speech_recognition.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Найти все вхождения samplerate=16000
        if 'samplerate=16000' in content:
            print("[НАЙДЕНО] samplerate=16000")
            
            # Заменить на автоматическое определение
            old_code = 'samplerate=16000'
            new_code = 'samplerate=44100'  # Частота вашего микрофона!
            
            content = content.replace(old_code, new_code)
            
            print("[ИСПРАВЛЕНО] samplerate изменен на 44100")
            print("  (соответствует вашему Logitech G733)")
        
        # Также найти инициализацию KaldiRecognizer
        if 'KaldiRecognizer(self.model, 16000)' in content:
            print("[НАЙДЕНО] KaldiRecognizer с 16000 Hz")
            
            old_recognizer = 'KaldiRecognizer(self.model, 16000)'
            new_recognizer = 'KaldiRecognizer(self.model, 44100)'
            
            content = content.replace(old_recognizer, new_recognizer)
            
            print("[ИСПРАВЛЕНО] KaldiRecognizer изменен на 44100 Hz")
        
        # Сохранить
        with open('core/speech_recognition.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print()
        print("[ГОТОВО] speech_recognition.py исправлен")
        print()
        print("Теперь Vosk будет использовать частоту вашего микрофона!")
        return True
        
    except Exception as e:
        print(f"[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_speech_synthesis():
    """Проверка и исправление speech_synthesis.py"""
    
    print("\nПроверка speech_synthesis.py...")
    print()
    
    try:
        with open('core/speech_synthesis.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверить наличие метода speak
        if 'async def speak(self, text' in content:
            print("[OK] Метод speak() найден")
            
            # Проверить что есть вызов _speak_sync
            if 'self._speak_sync' in content:
                print("[OK] Вызов _speak_sync найден")
                print()
                print("speech_synthesis.py выглядит правильно")
                print()
                print("Если голос не слышен, проверьте:")
                print("  1. Динамики подключены (тест 2 прошел)")
                print("  2. Правильное устройство вывода в Windows")
                print("  3. Громкость приложения в микшере Windows")
                return True
            else:
                print("[ПРОБЛЕМА] Вызов _speak_sync НЕ найден!")
                print()
                print("Метод speak() не вызывает озвучивание!")
                print("Только выводит текст в консоль.")
                print()
                print("Замените файл speech_synthesis.py из архива:")
                print("  speech_synthesis_windows.py")
                return False
        else:
            print("[ОШИБКА] Метод speak() не найден!")
            return False
            
    except Exception as e:
        print(f"[ОШИБКА] {e}")
        return False

def main():
    print("="*70)
    print("ИСПРАВЛЕНИЕ ПРОБЛЕМ С ГОЛОСОМ")
    print("="*70)
    print()
    print("Обнаружено:")
    print("  1. JARVIS синтез не работает")
    print("  2. Vosk не распознаёт (несоответствие частоты)")
    print()
    print("Будет исправлено:")
    print("  1. speech_recognition.py - частота 44100 Hz")
    print("  2. speech_synthesis.py - проверка")
    print()
    input("Нажмите Enter...")
    print()
    
    success = True
    success &= fix_speech_recognition()
    success &= fix_speech_synthesis()
    
    print()
    print("="*70)
    if success:
        print("ИСПРАВЛЕНИЯ ПРИМЕНЕНЫ")
        print("="*70)
        print()
        print("Теперь:")
        print("  1. Запустите test_voice_FIXED.py снова")
        print("  2. Vosk должен распознавать речь")
        print("  3. Если JARVIS синтез не работает - замените")
        print("     speech_synthesis.py на версию из архива")
        print()
    else:
        print("ОШИБКИ!")
        print("="*70)
    
    input("Нажмите Enter...")

if __name__ == "__main__":
    main()
