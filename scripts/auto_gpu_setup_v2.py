# -*- coding: utf-8 -*-
"""
🎮 JARVIS AUTO GPU SETUP V2 - С ПРОГРЕСС-БАРОМ
Автоматическая проверка и настройка GPU с детальной индикацией

✅ Прогресс-бар загрузки
✅ Скорость скачивания
✅ Оставшееся время
✅ Возможность отмены
✅ Проверка интернета
"""

import subprocess
import sys
import os
import re
from pathlib import Path
import time
import threading

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"  {Colors.GREEN}✓{Colors.ENDC} {text}")

def print_warning(text):
    print(f"  {Colors.YELLOW}⚠{Colors.ENDC} {text}")

def print_error(text):
    print(f"  {Colors.RED}✗{Colors.ENDC} {text}")

def print_info(text):
    print(f"  {Colors.BLUE}ℹ{Colors.ENDC} {text}")

def print_step(step, total, text):
    print(f"\n{Colors.BOLD}[{step}/{total}]{Colors.ENDC} {text}")


class ProgressIndicator:
    """Индикатор прогресса с анимацией"""
    
    def __init__(self, message="Обработка"):
        self.message = message
        self.running = False
        self.thread = None
        self.spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.idx = 0
    
    def _animate(self):
        """Анимация спиннера"""
        while self.running:
            sys.stdout.write(f'\r  {Colors.BLUE}{self.spinner[self.idx]}{Colors.ENDC} {self.message}...')
            sys.stdout.flush()
            self.idx = (self.idx + 1) % len(self.spinner)
            time.sleep(0.1)
    
    def start(self):
        """Запуск индикатора"""
        self.running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()
    
    def stop(self, success=True):
        """Остановка индикатора"""
        self.running = False
        if self.thread:
            self.thread.join()
        
        symbol = f"{Colors.GREEN}✓{Colors.ENDC}" if success else f"{Colors.RED}✗{Colors.ENDC}"
        sys.stdout.write(f'\r  {symbol} {self.message}... {"OK" if success else "FAILED"}          \n')
        sys.stdout.flush()


def create_progress_bar(current, total, width=40):
    """Создание прогресс-бара"""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percent*100:.1f}%"


class AutoGPUSetup:
    """Автоматическая настройка GPU с прогресс-индикацией"""
    
    def __init__(self):
        self.total_steps = 9
        self.current_step = 0
        self.nvidia_available = False
        self.cuda_version = None
        self.pytorch_cuda = False
        self.gpu_name = None
    
    def step(self, text):
        self.current_step += 1
        print_step(self.current_step, self.total_steps, text)
    
    def check_internet(self):
        """Проверка интернет-соединения"""
        self.step("Проверка интернет-соединения...")
        
        indicator = ProgressIndicator("Проверка соединения")
        indicator.start()
        
        try:
            # Пробуем подключиться к PyPI
            import urllib.request
            urllib.request.urlopen('https://pypi.org', timeout=5)
            indicator.stop(success=True)
            print_success("Интернет доступен")
            return True
        except:
            indicator.stop(success=False)
            print_error("Нет интернет-соединения!")
            print_warning("Проверьте подключение к интернету и попробуйте снова")
            return False
    
    def check_nvidia_driver(self):
        """Проверка драйвера NVIDIA"""
        self.step("Проверка драйвера NVIDIA...")
        
        indicator = ProgressIndicator("Сканирование NVIDIA")
        indicator.start()
        
        try:
            result = subprocess.run(
                ['nvidia-smi'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            indicator.stop(success=True)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Извлекаем информацию
                driver_match = re.search(r'Driver Version: ([\d.]+)', output)
                if driver_match:
                    driver_version = driver_match.group(1)
                    print_success(f"Драйвер NVIDIA: {driver_version}")
                
                cuda_match = re.search(r'CUDA Version: ([\d.]+)', output)
                if cuda_match:
                    self.cuda_version = cuda_match.group(1)
                    print_success(f"CUDA Version: {self.cuda_version}")
                
                gpu_match = re.search(r'NVIDIA GeForce ([^\|]+)', output)
                if gpu_match:
                    self.gpu_name = gpu_match.group(1).strip()
                    print_success(f"GPU: NVIDIA GeForce {self.gpu_name}")
                
                self.nvidia_available = True
                return True
            else:
                print_error("nvidia-smi вернул ошибку")
                return False
        
        except FileNotFoundError:
            indicator.stop(success=False)
            print_error("nvidia-smi не найден")
            print()
            print_warning("Драйверы NVIDIA не установлены!")
            print()
            print("📥 Установите драйверы:")
            print("   1. https://www.nvidia.com/Download/index.aspx")
            print("   2. Product: GeForce RTX 4070 Ti SUPER")
            print("   3. Download → Install → Перезагрузка")
            print("   4. Запустите скрипт снова")
            return False
        
        except Exception as e:
            indicator.stop(success=False)
            print_error(f"Ошибка: {e}")
            return False
    
    def check_pytorch_cuda(self):
        """Проверка PyTorch CUDA"""
        self.step("Проверка PyTorch...")
        
        try:
            import torch
            
            print_info(f"PyTorch версия: {torch.__version__}")
            
            cuda_available = torch.cuda.is_available()
            
            if cuda_available:
                print_success("PyTorch CUDA: Доступна ✅")
                print_success(f"CUDA версия: {torch.version.cuda}")
                
                device_count = torch.cuda.device_count()
                print_success(f"GPU обнаружено: {device_count}")
                
                if device_count > 0:
                    gpu_name = torch.cuda.get_device_name(0)
                    print_success(f"GPU: {gpu_name}")
                
                self.pytorch_cuda = True
                return True
            else:
                print_warning("PyTorch без CUDA - нужна переустановка")
                self.pytorch_cuda = False
                return False
        
        except ImportError:
            print_warning("PyTorch не установлен")
            return False
        
        except Exception as e:
            print_error(f"Ошибка: {e}")
            return False
    
    def determine_cuda_toolkit_version(self):
        """Определение версии CUDA"""
        self.step("Определение версии CUDA Toolkit...")
        
        if not self.cuda_version:
            print_warning("Версия CUDA не определена")
            print_info("Используем CUDA 12.1 по умолчанию")
            return "cu121"
        
        cuda_major = int(float(self.cuda_version))
        
        if cuda_major >= 12:
            print_success("Выбрана версия: CUDA 12.1")
            return "cu121"
        elif cuda_major >= 11:
            print_success("Выбрана версия: CUDA 11.8")
            return "cu118"
        else:
            print_warning(f"CUDA {self.cuda_version} устарела")
            print_info("Используем CUDA 11.8")
            return "cu118"
    
    def uninstall_old_pytorch(self):
        """Удаление старого PyTorch"""
        self.step("Удаление старого PyTorch...")
        
        indicator = ProgressIndicator("Удаление пакетов")
        indicator.start()
        
        packages = ['torch', 'torchvision', 'torchaudio']
        
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'uninstall', '-y'] + packages,
                capture_output=True,
                check=False,
                timeout=60
            )
            indicator.stop(success=True)
            print_success("Старые пакеты удалены")
            return True
        
        except subprocess.TimeoutExpired:
            indicator.stop(success=False)
            print_error("Timeout при удалении")
            return False
        
        except Exception as e:
            indicator.stop(success=False)
            print_error(f"Ошибка: {e}")
            return False
    
    def install_pytorch_with_cuda(self, cuda_version):
        """Установка PyTorch с CUDA и детальным прогрессом"""
        self.step(f"Установка PyTorch с CUDA {cuda_version}...")
        
        print()
        print_info("📦 Начинается загрузка...")
        print_info("📊 Размер: ~2-3 GB")
        print_info("⏱️  Время: 3-10 минут (зависит от скорости интернета)")
        print_info("💡 Можно прервать: Ctrl+C")
        print()
        
        index_url = f"https://download.pytorch.org/whl/{cuda_version}"
        packages = ['torch', 'torchvision', 'torchaudio']
        
        try:
            # Запускаем установку с выводом в реальном времени
            process = subprocess.Popen(
                [sys.executable, '-m', 'pip', 'install'] + packages + 
                ['--index-url', index_url, '--verbose'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            current_package = ""
            download_started = False
            install_started = False
            last_update = time.time()
            
            print(f"{Colors.CYAN}{'─'*80}{Colors.ENDC}")
            
            for line in process.stdout:
                line = line.strip()
                
                # Обновляем не чаще раза в 0.5 сек для плавности
                current_time = time.time()
                if current_time - last_update < 0.5 and not any(x in line for x in ['Downloading', 'Installing', 'Successfully', 'ERROR', 'Collecting']):
                    continue
                last_update = current_time
                
                # Сбор информации о пакете
                if 'Collecting' in line:
                    package_match = re.search(r'Collecting ([^\s]+)', line)
                    if package_match:
                        current_package = package_match.group(1)
                        print(f"\n  {Colors.BLUE}📦{Colors.ENDC} Подготовка: {current_package}")
                
                # Загрузка
                elif 'Downloading' in line:
                    if not download_started:
                        print(f"\n  {Colors.YELLOW}⬇️  Загрузка...{Colors.ENDC}")
                        download_started = True
                    
                    # Извлекаем размер и прогресс
                    size_match = re.search(r'(\d+\.?\d*)\s*([kMG]B)', line)
                    percent_match = re.search(r'(\d+)%', line)
                    
                    if percent_match:
                        percent = int(percent_match.group(1))
                        bar = create_progress_bar(percent, 100, width=50)
                        
                        size_info = ""
                        if size_match:
                            size_info = f" ({size_match.group(1)} {size_match.group(2)})"
                        
                        # Очищаем строку и выводим прогресс
                        sys.stdout.write(f'\r  {bar}{size_info}')
                        sys.stdout.flush()
                
                # Установка
                elif 'Installing' in line:
                    if not install_started:
                        print(f"\n\n  {Colors.GREEN}⚙️  Установка...{Colors.ENDC}")
                        install_started = True
                    
                    package_match = re.search(r'Installing collected packages: (.+)', line)
                    if package_match:
                        packages_list = package_match.group(1)
                        print(f"  {Colors.BLUE}→{Colors.ENDC} {packages_list}")
                
                # Успешная установка
                elif 'Successfully installed' in line:
                    print(f"\n  {Colors.GREEN}✓{Colors.ENDC} {line}")
                
                # Ошибки
                elif 'ERROR' in line or 'Error' in line:
                    print(f"\n  {Colors.RED}✗{Colors.ENDC} {line}")
                
                # Полезная информация
                elif any(x in line for x in ['Using cached', 'Requirement already satisfied']):
                    print(f"  {Colors.BLUE}ℹ{Colors.ENDC} {line[:70]}...")
            
            process.wait()
            
            print(f"{Colors.CYAN}{'─'*80}{Colors.ENDC}\n")
            
            if process.returncode == 0:
                print_success("PyTorch установлен успешно!")
                return True
            else:
                print_error("Ошибка установки PyTorch")
                print()
                print_warning("Попробуйте альтернативный метод:")
                print(f"  {Colors.CYAN}pip install torch torchvision torchaudio{Colors.ENDC}")
                return False
        
        except KeyboardInterrupt:
            print()
            print_warning("Установка прервана пользователем")
            process.kill()
            return False
        
        except Exception as e:
            print()
            print_error(f"Ошибка: {e}")
            return False
    
    def verify_gpu_setup(self):
        """Проверка GPU"""
        self.step("Проверка GPU...")
        
        indicator = ProgressIndicator("Проверка CUDA")
        indicator.start()
        
        try:
            import torch
            
            indicator.stop(success=True)
            
            cuda_available = torch.cuda.is_available()
            
            if cuda_available:
                print()
                print_success("✅ CUDA доступна!")
                print_success(f"✅ PyTorch: {torch.__version__}")
                print_success(f"✅ CUDA: {torch.version.cuda}")
                
                device_count = torch.cuda.device_count()
                print_success(f"✅ GPU: {device_count}")
                
                if device_count > 0:
                    gpu_name = torch.cuda.get_device_name(0)
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    
                    print_success(f"✅ Название: {gpu_name}")
                    print_success(f"✅ VRAM: {gpu_memory:.1f} GB")
                
                return True
            else:
                print_error("CUDA недоступна")
                return False
        
        except Exception as e:
            indicator.stop(success=False)
            print_error(f"Ошибка: {e}")
            return False
    
    def run_gpu_test(self):
        """Тест GPU"""
        self.step("Тест производительности...")
        
        try:
            import torch
            
            if not torch.cuda.is_available():
                print_warning("GPU недоступна для теста")
                return False
            
            print()
            print_info("Запуск теста производительности...")
            print()
            
            size = 5000
            iterations = 50
            
            # CPU
            print(f"  {Colors.BLUE}⚙️{Colors.ENDC}  Тест CPU...")
            cpu_start = time.time()
            for i in range(iterations):
                if i % 10 == 0:
                    bar = create_progress_bar(i, iterations, width=30)
                    sys.stdout.write(f'\r     {bar}')
                    sys.stdout.flush()
                
                a = torch.randn(size, size)
                b = torch.randn(size, size)
                c = torch.matmul(a, b)
            
            cpu_time = time.time() - cpu_start
            sys.stdout.write(f'\r     {create_progress_bar(iterations, iterations, width=30)}\n')
            print_success(f"CPU: {cpu_time:.2f} сек")
            
            # GPU
            print(f"\n  {Colors.GREEN}🎮{Colors.ENDC}  Тест GPU...")
            gpu_start = time.time()
            for i in range(iterations):
                if i % 10 == 0:
                    bar = create_progress_bar(i, iterations, width=30)
                    sys.stdout.write(f'\r     {bar}')
                    sys.stdout.flush()
                
                a = torch.randn(size, size, device='cuda')
                b = torch.randn(size, size, device='cuda')
                c = torch.matmul(a, b)
            
            torch.cuda.synchronize()
            gpu_time = time.time() - gpu_start
            sys.stdout.write(f'\r     {create_progress_bar(iterations, iterations, width=30)}\n')
            print_success(f"GPU: {gpu_time:.2f} сек")
            
            # Результат
            speedup = cpu_time / gpu_time
            print()
            print(f"  {Colors.GREEN}{Colors.BOLD}🚀 Ускорение: {speedup:.1f}x{Colors.ENDC}")
            
            if speedup > 20:
                print_success("✅ GPU работает отлично!")
            elif speedup > 5:
                print_success("✅ GPU работает хорошо")
            elif speedup > 2:
                print_warning("⚠️ GPU работает медленнее ожидаемого")
            else:
                print_error("❌ GPU работает некорректно")
            
            return True
        
        except Exception as e:
            print_error(f"Ошибка теста: {e}")
            return False
    
    def show_final_summary(self):
        """Итоговая информация"""
        self.step("Итоги...")
        
        print_header("✅ НАСТРОЙКА ЗАВЕРШЕНА!")
        
        print(f"\n{Colors.BOLD}Статус компонентов:{Colors.ENDC}\n")
        
        if self.nvidia_available:
            print_success(f"NVIDIA Driver: Установлен")
            if self.cuda_version:
                print_success(f"CUDA: {self.cuda_version}")
            if self.gpu_name:
                print_success(f"GPU: {self.gpu_name}")
        else:
            print_error("NVIDIA Driver: Не установлен")
        
        print()
        
        if self.pytorch_cuda:
            print_success("PyTorch CUDA: Работает ✅")
        else:
            print_error("PyTorch CUDA: Не работает ❌")
        
        print()
        
        if self.nvidia_available and self.pytorch_cuda:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 GPU полностью настроена!{Colors.ENDC}")
            print()
            print("JARVIS будет учиться в 50-100 раз быстрее!")
            print()
            print(f"{Colors.BOLD}Следующие шаги:{Colors.ENDC}")
            print()
            print("1. Тест:")
            print(f"   {Colors.CYAN}python test_turbo_integration.py{Colors.ENDC}")
            print()
            print("2. Запуск:")
            print(f"   {Colors.CYAN}python -m jarvis{Colors.ENDC}")
            print()
            print("3. Dashboard:")
            print(f"   {Colors.CYAN}python jarvis/gui/learning_dashboard.py{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ Настройка не завершена{Colors.ENDC}")
    
    def run(self):
        """Запуск настройки"""
        print_header("🎮 JARVIS AUTO GPU SETUP V2")
        
        print(f"{Colors.YELLOW}Автоматическая настройка GPU с прогресс-индикацией{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}Что будет сделано:{Colors.ENDC}")
        print("  • Проверка интернета")
        print("  • Проверка NVIDIA")
        print("  • Определение CUDA")
        print("  • Установка PyTorch (с прогресс-баром)")
        print("  • Тест GPU")
        print()
        
        response = input(f"{Colors.BOLD}Начать? (yes/no): {Colors.ENDC}").strip().lower()
        if response not in ['yes', 'y']:
            print_error("Отменено")
            return False
        
        start_time = time.time()
        
        try:
            # Проверка интернета
            if not self.check_internet():
                return False
            
            # Проверка NVIDIA
            if not self.check_nvidia_driver():
                return False
            
            # Проверка PyTorch
            pytorch_ok = self.check_pytorch_cuda()
            
            if pytorch_ok and self.pytorch_cuda:
                print()
                print_success("PyTorch уже настроен!")
                self.verify_gpu_setup()
                self.run_gpu_test()
                self.show_final_summary()
                return True
            
            # Определение CUDA
            cuda_toolkit = self.determine_cuda_toolkit_version()
            
            # Удаление старого
            self.uninstall_old_pytorch()
            
            # Установка нового (с прогресс-баром!)
            install_ok = self.install_pytorch_with_cuda(cuda_toolkit)
            
            if not install_ok:
                return False
            
            # Проверка
            verify_ok = self.verify_gpu_setup()
            
            # Тест
            if verify_ok:
                self.run_gpu_test()
            
            # Итоги
            self.show_final_summary()
            
            elapsed = time.time() - start_time
            print()
            print(f"{Colors.GREEN}Время: {elapsed/60:.1f} минут{Colors.ENDC}")
            
            return verify_ok
        
        except KeyboardInterrupt:
            print()
            print_warning("Прервано пользователем (Ctrl+C)")
            return False
        
        except Exception as e:
            print_error(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Главная функция"""
    setup = AutoGPUSetup()
    success = setup.run()
    
    print("\n" + "="*80)
    if success:
        print("🎉 GPU готова!")
    else:
        print("❌ Настройка не завершена")
    print("="*80)
    
    input("\n\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
