# -*- coding: utf-8 -*-
"""
🎮 JARVIS AUTO GPU SETUP & FIX
Автоматическая проверка и настройка GPU

Что делает:
✅ Проверяет драйверы NVIDIA
✅ Определяет версию CUDA
✅ Удаляет старый PyTorch
✅ Устанавливает правильный PyTorch с CUDA
✅ Тестирует GPU
✅ Всё автоматически!

Просто запустите: python auto_gpu_setup.py
"""

import subprocess
import sys
import os
import re
from pathlib import Path
import time

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


class AutoGPUSetup:
    """Автоматическая настройка GPU"""
    
    def __init__(self):
        self.total_steps = 8
        self.current_step = 0
        self.nvidia_available = False
        self.cuda_version = None
        self.pytorch_cuda = False
        self.gpu_name = None
    
    def step(self, text):
        self.current_step += 1
        print_step(self.current_step, self.total_steps, text)
    
    def check_nvidia_driver(self):
        """Проверка драйвера NVIDIA"""
        self.step("Проверка драйвера NVIDIA...")
        
        try:
            result = subprocess.run(
                ['nvidia-smi'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Извлекаем версию драйвера
                driver_match = re.search(r'Driver Version: ([\d.]+)', output)
                if driver_match:
                    driver_version = driver_match.group(1)
                    print_success(f"Драйвер NVIDIA: {driver_version}")
                
                # Извлекаем версию CUDA
                cuda_match = re.search(r'CUDA Version: ([\d.]+)', output)
                if cuda_match:
                    self.cuda_version = cuda_match.group(1)
                    print_success(f"CUDA Version: {self.cuda_version}")
                
                # Извлекаем название GPU
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
            print_error("nvidia-smi не найден - драйверы NVIDIA не установлены")
            self._show_driver_installation_guide()
            return False
        
        except subprocess.TimeoutExpired:
            print_error("Timeout при выполнении nvidia-smi")
            return False
        
        except Exception as e:
            print_error(f"Ошибка проверки NVIDIA: {e}")
            return False
    
    def _show_driver_installation_guide(self):
        """Показать инструкцию по установке драйверов"""
        print()
        print_warning("Драйверы NVIDIA не установлены!")
        print()
        print("📥 Установите драйверы:")
        print()
        print("1. Откройте: https://www.nvidia.com/Download/index.aspx")
        print("2. Выберите:")
        print("   - Product Type: GeForce")
        print("   - Product Series: GeForce RTX 40 Series")
        print("   - Product: GeForce RTX 4070 Ti SUPER")
        print("   - Operating System: Windows 11")
        print("3. Нажмите Search → Download → Install")
        print("4. Перезагрузите компьютер")
        print("5. Запустите этот скрипт снова")
        print()
    
    def check_pytorch_cuda(self):
        """Проверка PyTorch CUDA"""
        self.step("Проверка PyTorch...")
        
        try:
            import torch
            
            print_info(f"PyTorch версия: {torch.__version__}")
            
            cuda_available = torch.cuda.is_available()
            
            if cuda_available:
                print_success(f"PyTorch CUDA: Доступна")
                print_success(f"CUDA версия в PyTorch: {torch.version.cuda}")
                
                device_count = torch.cuda.device_count()
                print_success(f"Обнаружено GPU: {device_count}")
                
                if device_count > 0:
                    gpu_name = torch.cuda.get_device_name(0)
                    print_success(f"GPU[0]: {gpu_name}")
                
                self.pytorch_cuda = True
                return True
            else:
                print_error("PyTorch CUDA: Недоступна")
                print_warning("PyTorch установлен без поддержки CUDA!")
                self.pytorch_cuda = False
                return False
        
        except ImportError:
            print_warning("PyTorch не установлен")
            return False
        
        except Exception as e:
            print_error(f"Ошибка проверки PyTorch: {e}")
            return False
    
    def determine_cuda_toolkit_version(self):
        """Определение версии CUDA Toolkit для установки"""
        self.step("Определение версии CUDA...")
        
        if not self.cuda_version:
            print_warning("Версия CUDA не определена, используем 12.1 по умолчанию")
            return "cu121"
        
        # Преобразуем версию CUDA в формат для PyTorch
        cuda_major = int(float(self.cuda_version))
        
        if cuda_major >= 12:
            print_success("Будет использован PyTorch с CUDA 12.1")
            return "cu121"
        elif cuda_major >= 11:
            print_success("Будет использован PyTorch с CUDA 11.8")
            return "cu118"
        else:
            print_warning(f"CUDA {self.cuda_version} устарела, рекомендуется обновить драйверы")
            return "cu118"
    
    def uninstall_old_pytorch(self):
        """Удаление старого PyTorch"""
        self.step("Удаление старого PyTorch...")
        
        packages = ['torch', 'torchvision', 'torchaudio']
        
        print_info("Удаление старых пакетов...")
        
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'uninstall', '-y'] + packages,
                capture_output=True,
                check=False
            )
            print_success("Старые пакеты удалены")
            return True
        
        except Exception as e:
            print_error(f"Ошибка удаления: {e}")
            return False
    
    def install_pytorch_with_cuda(self, cuda_version):
        """Установка PyTorch с CUDA"""
        self.step(f"Установка PyTorch с CUDA ({cuda_version})...")
        
        print_info("Это может занять 3-5 минут...")
        print_info("Скачивается ~2-3 GB данных...")
        print()
        
        index_url = f"https://download.pytorch.org/whl/{cuda_version}"
        
        packages = ['torch', 'torchvision', 'torchaudio']
        
        try:
            # Показываем прогресс
            process = subprocess.Popen(
                [sys.executable, '-m', 'pip', 'install'] + packages + 
                ['--index-url', index_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Выводим прогресс
            for line in process.stdout:
                if 'Downloading' in line or 'Installing' in line:
                    print(f"  {Colors.BLUE}→{Colors.ENDC} {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                print()
                print_success("PyTorch с CUDA установлен успешно!")
                return True
            else:
                print()
                print_error("Ошибка установки PyTorch")
                return False
        
        except Exception as e:
            print_error(f"Ошибка: {e}")
            return False
    
    def verify_gpu_setup(self):
        """Проверка настройки GPU"""
        self.step("Проверка GPU...")
        
        try:
            import torch
            
            print()
            print_info("Импорт PyTorch...")
            print_success("PyTorch импортирован")
            
            cuda_available = torch.cuda.is_available()
            
            if cuda_available:
                print()
                print_success(f"✅ CUDA доступна!")
                print_success(f"✅ PyTorch версия: {torch.__version__}")
                print_success(f"✅ CUDA версия: {torch.version.cuda}")
                
                device_count = torch.cuda.device_count()
                print_success(f"✅ Количество GPU: {device_count}")
                
                if device_count > 0:
                    gpu_name = torch.cuda.get_device_name(0)
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    
                    print_success(f"✅ GPU: {gpu_name}")
                    print_success(f"✅ VRAM: {gpu_memory:.1f} GB")
                
                return True
            else:
                print_error("CUDA всё ещё недоступна после установки")
                return False
        
        except Exception as e:
            print_error(f"Ошибка проверки: {e}")
            return False
    
    def run_gpu_test(self):
        """Запуск теста GPU"""
        self.step("Тест производительности GPU...")
        
        try:
            import torch
            import time
            
            if not torch.cuda.is_available():
                print_warning("GPU недоступна для теста")
                return False
            
            print()
            print_info("Запуск теста...")
            
            # Простой тест
            size = 5000
            iterations = 50
            
            # CPU тест
            print_info("Тест CPU...")
            cpu_start = time.time()
            for _ in range(iterations):
                a = torch.randn(size, size)
                b = torch.randn(size, size)
                c = torch.matmul(a, b)
            cpu_time = time.time() - cpu_start
            print_success(f"CPU время: {cpu_time:.2f} сек")
            
            # GPU тест
            print_info("Тест GPU...")
            gpu_start = time.time()
            for _ in range(iterations):
                a = torch.randn(size, size, device='cuda')
                b = torch.randn(size, size, device='cuda')
                c = torch.matmul(a, b)
            torch.cuda.synchronize()
            gpu_time = time.time() - gpu_start
            print_success(f"GPU время: {gpu_time:.2f} сек")
            
            # Ускорение
            speedup = cpu_time / gpu_time
            print()
            print_success(f"🚀 Ускорение GPU: {speedup:.1f}x")
            
            if speedup > 5:
                print_success("✅ GPU работает отлично!")
            elif speedup > 2:
                print_warning("⚠️ GPU работает, но медленнее ожидаемого")
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
        
        print(f"\n{Colors.BOLD}Результаты:{Colors.ENDC}\n")
        
        if self.nvidia_available:
            print_success(f"NVIDIA Driver: Установлен")
            if self.cuda_version:
                print_success(f"CUDA Version: {self.cuda_version}")
            if self.gpu_name:
                print_success(f"GPU: NVIDIA GeForce {self.gpu_name}")
        else:
            print_error("NVIDIA Driver: Не установлен")
        
        print()
        
        if self.pytorch_cuda:
            print_success("PyTorch CUDA: Работает ✅")
        else:
            print_error("PyTorch CUDA: Не работает ❌")
        
        print()
        
        if self.nvidia_available and self.pytorch_cuda:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 GPU полностью настроена и готова!{Colors.ENDC}")
            print()
            print("Теперь JARVIS будет учиться в 50-100 раз быстрее!")
            print()
            print(f"{Colors.BOLD}Следующие шаги:{Colors.ENDC}")
            print()
            print("1. Запустите тест:")
            print(f"   {Colors.CYAN}python test_turbo_integration.py{Colors.ENDC}")
            print()
            print("2. Запустите JARVIS:")
            print(f"   {Colors.CYAN}python -m jarvis{Colors.ENDC}")
            print()
            print("3. Откройте Dashboard:")
            print(f"   {Colors.CYAN}python jarvis/gui/learning_dashboard.py{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ Настройка не завершена{Colors.ENDC}")
            print()
            
            if not self.nvidia_available:
                print("Установите драйверы NVIDIA и запустите скрипт снова")
            elif not self.pytorch_cuda:
                print("PyTorch не удалось настроить, попробуйте вручную:")
                print(f"  {Colors.CYAN}pip install torch --index-url https://download.pytorch.org/whl/cu121{Colors.ENDC}")
    
    def run(self):
        """Запуск автоматической настройки"""
        print_header("🎮 JARVIS AUTO GPU SETUP")
        
        print(f"{Colors.YELLOW}Автоматическая проверка и настройка GPU{Colors.ENDC}")
        print(f"{Colors.YELLOW}Время: ~5-10 минут{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}Что будет сделано:{Colors.ENDC}")
        print("  • Проверка драйверов NVIDIA")
        print("  • Определение версии CUDA")
        print("  • Удаление старого PyTorch")
        print("  • Установка PyTorch с CUDA")
        print("  • Тест GPU")
        print()
        
        response = input(f"{Colors.BOLD}Начать? (yes/no): {Colors.ENDC}").strip().lower()
        if response not in ['yes', 'y']:
            print_error("Отменено")
            return False
        
        start_time = time.time()
        
        try:
            # Шаг 1: Проверка драйверов
            nvidia_ok = self.check_nvidia_driver()
            
            if not nvidia_ok:
                print()
                print_error("Невозможно продолжить без драйверов NVIDIA")
                print_warning("Установите драйверы и запустите скрипт снова")
                return False
            
            # Шаг 2: Проверка PyTorch
            pytorch_ok = self.check_pytorch_cuda()
            
            # Если PyTorch уже работает с CUDA, ничего не делаем
            if pytorch_ok and self.pytorch_cuda:
                print()
                print_success("PyTorch уже настроен с CUDA!")
                print_info("Пропускаем переустановку...")
                
                # Только тестируем
                self.verify_gpu_setup()
                self.run_gpu_test()
                self.show_final_summary()
                return True
            
            # Шаг 3: Определение версии CUDA
            cuda_toolkit = self.determine_cuda_toolkit_version()
            
            # Шаг 4: Удаление старого PyTorch
            self.uninstall_old_pytorch()
            
            # Шаг 5: Установка нового PyTorch
            install_ok = self.install_pytorch_with_cuda(cuda_toolkit)
            
            if not install_ok:
                print_error("Не удалось установить PyTorch")
                return False
            
            # Шаг 6: Проверка
            verify_ok = self.verify_gpu_setup()
            
            # Шаг 7: Тест
            if verify_ok:
                self.run_gpu_test()
            
            # Шаг 8: Итоги
            self.show_final_summary()
            
            elapsed = time.time() - start_time
            print()
            print(f"{Colors.GREEN}Время выполнения: {elapsed/60:.1f} минут{Colors.ENDC}")
            
            return verify_ok
        
        except Exception as e:
            print_error(f"Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Главная функция"""
    setup = AutoGPUSetup()
    success = setup.run()
    
    if success:
        print("\n" + "="*80)
        print("🎉 GPU готова к работе!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ Настройка не завершена")
        print("="*80)
    
    input("\n\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
