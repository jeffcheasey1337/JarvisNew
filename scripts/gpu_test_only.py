# -*- coding: utf-8 -*-
"""
🧪 JARVIS GPU TESTER - Только проверка и тесты
Без установки! Только проверяет что всё работает.
"""

import subprocess
import sys
import re
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


class GPUTester:
    """Только тестирование GPU без установки"""
    
    def __init__(self):
        self.nvidia_available = False
        self.cuda_version = None
        self.pytorch_cuda = False
        self.gpu_name = None
    
    def test_nvidia_driver(self):
        """Тест 1: Драйвер NVIDIA"""
        print_header("ТЕСТ 1: NVIDIA DRIVER")
        
        try:
            result = subprocess.run(
                ['nvidia-smi'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Версия драйвера
                driver_match = re.search(r'Driver Version: ([\d.]+)', output)
                if driver_match:
                    driver_version = driver_match.group(1)
                    print_success(f"Драйвер NVIDIA: {driver_version}")
                else:
                    print_warning("Версия драйвера не определена")
                
                # CUDA версия
                cuda_match = re.search(r'CUDA Version: ([\d.]+)', output)
                if cuda_match:
                    self.cuda_version = cuda_match.group(1)
                    print_success(f"CUDA Version: {self.cuda_version}")
                else:
                    print_warning("CUDA версия не определена")
                
                # GPU название
                gpu_match = re.search(r'NVIDIA GeForce ([^\|]+)', output)
                if gpu_match:
                    self.gpu_name = gpu_match.group(1).strip()
                    print_success(f"GPU: NVIDIA GeForce {self.gpu_name}")
                else:
                    gpu_match2 = re.search(r'(NVIDIA [^\|]+)', output)
                    if gpu_match2:
                        self.gpu_name = gpu_match2.group(1).strip()
                        print_success(f"GPU: {self.gpu_name}")
                
                # Температура и использование
                temp_match = re.search(r'(\d+)C', output)
                if temp_match:
                    temp = temp_match.group(1)
                    print_info(f"Температура: {temp}°C")
                
                util_match = re.search(r'(\d+)%', output)
                if util_match:
                    util = util_match.group(1)
                    print_info(f"Использование GPU: {util}%")
                
                self.nvidia_available = True
                print()
                print_success("✅ NVIDIA Driver работает!")
                return True
            else:
                print_error("nvidia-smi вернул ошибку")
                return False
        
        except FileNotFoundError:
            print_error("nvidia-smi не найден")
            print()
            print_warning("Драйверы NVIDIA не установлены!")
            print()
            print("Скачайте и установите:")
            print("  https://www.nvidia.com/Download/index.aspx")
            return False
        
        except Exception as e:
            print_error(f"Ошибка: {e}")
            return False
    
    def test_pytorch(self):
        """Тест 2: PyTorch"""
        print_header("ТЕСТ 2: PYTORCH")
        
        try:
            import torch
            
            version = torch.__version__
            print_success(f"PyTorch установлен: {version}")
            
            # Проверка CUDA в PyTorch
            cuda_available = torch.cuda.is_available()
            
            if cuda_available:
                print_success("CUDA доступна в PyTorch ✅")
                
                cuda_version = torch.version.cuda
                print_success(f"CUDA версия: {cuda_version}")
                
                device_count = torch.cuda.device_count()
                print_success(f"Количество GPU: {device_count}")
                
                if device_count > 0:
                    for i in range(device_count):
                        gpu_name = torch.cuda.get_device_name(i)
                        props = torch.cuda.get_device_properties(i)
                        vram = props.total_memory / (1024**3)
                        
                        print_success(f"GPU[{i}]: {gpu_name}")
                        print_info(f"  VRAM: {vram:.1f} GB")
                        print_info(f"  Compute Capability: {props.major}.{props.minor}")
                
                self.pytorch_cuda = True
                print()
                print_success("✅ PyTorch CUDA работает!")
                return True
            else:
                print_error("CUDA недоступна в PyTorch ❌")
                print()
                print_warning("PyTorch установлен без поддержки CUDA")
                print()
                print("Нужно установить версию с CUDA!")
                self.pytorch_cuda = False
                return False
        
        except ImportError:
            print_error("PyTorch не установлен ❌")
            print()
            print_warning("Установите PyTorch")
            return False
        
        except Exception as e:
            print_error(f"Ошибка: {e}")
            return False
    
    def test_gpu_performance(self):
        """Тест 3: Производительность GPU"""
        print_header("ТЕСТ 3: ПРОИЗВОДИТЕЛЬНОСТЬ GPU")
        
        try:
            import torch
            
            if not torch.cuda.is_available():
                print_warning("GPU недоступна, тест пропущен")
                return False
            
            print_info("Запуск бенчмарка...")
            print()
            
            size = 5000
            iterations = 50
            
            # CPU тест
            print(f"  {Colors.BLUE}⚙️  CPU Test...{Colors.ENDC}")
            cpu_times = []
            for _ in range(3):  # 3 прогона
                start = time.time()
                for _ in range(iterations):
                    a = torch.randn(size, size)
                    b = torch.randn(size, size)
                    c = torch.matmul(a, b)
                cpu_times.append(time.time() - start)
            
            cpu_time = min(cpu_times)  # Берём лучший результат
            print_success(f"CPU время: {cpu_time:.2f} сек")
            
            # GPU тест
            print(f"\n  {Colors.GREEN}🎮  GPU Test...{Colors.ENDC}")
            
            # Warm-up
            for _ in range(5):
                a = torch.randn(size, size, device='cuda')
                b = torch.randn(size, size, device='cuda')
                c = torch.matmul(a, b)
            torch.cuda.synchronize()
            
            gpu_times = []
            for _ in range(3):  # 3 прогона
                start = time.time()
                for _ in range(iterations):
                    a = torch.randn(size, size, device='cuda')
                    b = torch.randn(size, size, device='cuda')
                    c = torch.matmul(a, b)
                torch.cuda.synchronize()
                gpu_times.append(time.time() - start)
            
            gpu_time = min(gpu_times)  # Берём лучший результат
            print_success(f"GPU время: {gpu_time:.2f} сек")
            
            # Результат
            speedup = cpu_time / gpu_time
            print()
            print(f"  {Colors.GREEN}{Colors.BOLD}🚀 Ускорение GPU: {speedup:.1f}x{Colors.ENDC}")
            print()
            
            if speedup > 20:
                print_success("✅ Отлично! GPU работает на максимум!")
                print_info("JARVIS будет учиться в 50-100 раз быстрее!")
            elif speedup > 10:
                print_success("✅ Хорошо! GPU работает нормально")
                print_info("JARVIS получит ускорение ~50x")
            elif speedup > 5:
                print_warning("⚠️  Неплохо, но GPU может работать быстрее")
                print_info("Проверьте драйверы и настройки питания")
            elif speedup > 2:
                print_warning("⚠️  GPU работает медленнее ожидаемого")
                print_info("Возможно проблемы с драйверами или питанием")
            else:
                print_error("❌ GPU работает очень медленно!")
                print_info("Проверьте установку драйверов и PyTorch")
            
            return True
        
        except Exception as e:
            print_error(f"Ошибка теста: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_summary(self):
        """Итоговая информация"""
        print_header("ИТОГИ ТЕСТИРОВАНИЯ")
        
        print(f"{Colors.BOLD}Результаты:{Colors.ENDC}\n")
        
        # NVIDIA
        if self.nvidia_available:
            print_success("NVIDIA Driver: ✅ Работает")
            if self.cuda_version:
                print_info(f"  CUDA: {self.cuda_version}")
            if self.gpu_name:
                print_info(f"  GPU: {self.gpu_name}")
        else:
            print_error("NVIDIA Driver: ❌ Не работает")
        
        print()
        
        # PyTorch
        if self.pytorch_cuda:
            print_success("PyTorch CUDA: ✅ Работает")
        else:
            print_error("PyTorch CUDA: ❌ Не работает")
        
        print()
        
        # Вердикт
        if self.nvidia_available and self.pytorch_cuda:
            print(f"{Colors.GREEN}{Colors.BOLD}═══════════════════════════════════════{Colors.ENDC}")
            print(f"{Colors.GREEN}{Colors.BOLD}  🎉 ВСЁ ГОТОВО!{Colors.ENDC}")
            print(f"{Colors.GREEN}{Colors.BOLD}═══════════════════════════════════════{Colors.ENDC}")
            print()
            print("GPU полностью настроена и работает!")
            print("JARVIS будет учиться в 50-100 раз быстрее!")
            print()
            print(f"{Colors.BOLD}Можно запускать:{Colors.ENDC}")
            print(f"  {Colors.CYAN}python -m jarvis{Colors.ENDC}")
            print(f"  {Colors.CYAN}python jarvis/gui/learning_dashboard.py{Colors.ENDC}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}═══════════════════════════════════════{Colors.ENDC}")
            print(f"{Colors.RED}{Colors.BOLD}  ❌ НАСТРОЙКА НЕ ЗАВЕРШЕНА{Colors.ENDC}")
            print(f"{Colors.RED}{Colors.BOLD}═══════════════════════════════════════{Colors.ENDC}")
            print()
            
            if not self.nvidia_available:
                print("❌ Установите драйверы NVIDIA")
                print("   https://www.nvidia.com/Download/index.aspx")
                print()
            
            if not self.pytorch_cuda:
                print("❌ Установите PyTorch с CUDA")
                print("   См. инструкцию ниже ⬇️")
    
    def run(self):
        """Запуск всех тестов"""
        print_header("🧪 JARVIS GPU TESTER")
        print()
        print("Проверка GPU без установки")
        print("Только тесты!")
        print()
        
        input("Нажмите Enter для начала...")
        
        # Тест 1: NVIDIA
        nvidia_ok = self.test_nvidia_driver()
        print()
        input("Нажмите Enter для продолжения...")
        
        # Тест 2: PyTorch
        pytorch_ok = self.test_pytorch()
        print()
        
        if pytorch_ok:
            input("Нажмите Enter для теста производительности...")
            
            # Тест 3: Производительность
            self.test_gpu_performance()
        
        print()
        input("Нажмите Enter для итогов...")
        
        # Итоги
        self.show_summary()


def main():
    """Главная функция"""
    tester = GPUTester()
    tester.run()
    
    input("\n\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
