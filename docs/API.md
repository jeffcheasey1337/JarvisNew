# JARVIS API Documentation

## Быстрый старт

```python
from jarvis.assistant import JarvisAssistant

# Создание экземпляра
jarvis = JarvisAssistant()

# Запуск
await jarvis.run()
```

## Core Components

### Speech Recognition
```python
from jarvis.core.speech.recognition import SpeechRecognizer

recognizer = SpeechRecognizer(config)
audio_data = await recognizer.listen()
text = await recognizer.recognize(audio_data)
```

### Speech Synthesis
```python
from jarvis.core.speech.synthesis import SpeechSynthesizer

synthesizer = SpeechSynthesizer(config)
await synthesizer.speak("Доброе утро, сэр")
```

### Memory System
```python
from jarvis.core.memory.system import MemorySystem

memory = MemorySystem(config)
await memory.store_memory("Важная информация", memory_type="fact")
results = await memory.recall_memory("запрос")
```

### Learning System
```python
from jarvis.core.learning.continuous import ContinuousLearning

learning = ContinuousLearning(config, memory, nlp)
await learning.start_continuous_learning()
```

## Modules

### Task Manager
```python
from jarvis.modules.tasks import TaskManager

tasks = TaskManager(memory)
response = await tasks.handle_command("Создай задачу купить молоко", entities)
```

### Web Search
```python
from jarvis.modules.search import WebSearch

search = WebSearch(config)
results = await search.search("новости ИИ", entities)
```

## GUI

```python
from jarvis.gui.main_window import launch_gui

gui = launch_gui(jarvis_instance)
```
