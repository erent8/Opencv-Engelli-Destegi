#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistem Çalıştırma Scripti
Raspberry Pi Engelli Destek Sistemi için kolay başlatma
"""

import sys
import os
import time
import argparse
import signal
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"


def check_dependencies():
    """Gerekli bağımlılıkları kontrol et"""
    print("🔍 Bağımlılıklar kontrol ediliyor...")
    
    missing_deps = []
    
    # Python kütüphaneleri
    try:
        import cv2
        print("✅ OpenCV")
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import numpy
        print("✅ NumPy")
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        from ultralytics import YOLO
        print("✅ YOLOv8")
    except ImportError:
        missing_deps.append("ultralytics")
    
    try:
        import pyttsx3
        print("✅ pyttsx3")
    except ImportError:
        missing_deps.append("pyttsx3")
    
    if missing_deps:
        print(f"❌ Eksik bağımlılıklar: {', '.join(missing_deps)}")
        print("Kurulum için: pip install -r requirements.txt")
        return False
    
    print("✅ Tüm bağımlılıklar mevcut")
    return True


def check_hardware():
    """Donanım kontrolü"""
    print("\n🔧 Donanım kontrol ediliyor...")
    
    # Kamera kontrolü
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Kamera erişilebilir")
            cap.release()
        else:
            print("⚠️ Kamera açılamadı")
    except Exception as e:
        print(f"❌ Kamera hatası: {e}")
    
    # Model dosyası kontrolü
    model_paths = ["yolov8n.pt", "models/yolov8n.pt"]
    model_found = False
    for path in model_paths:
        if os.path.exists(path):
            print(f"✅ YOLO modeli bulundu: {path}")
            model_found = True
            break
    
    if not model_found:
        print("⚠️ YOLO modeli bulunamadı")
        print("Model indirmek için: python -c \"from ultralytics import YOLO; YOLO('yolov8n.pt')\"")


def run_system(args):
    """Ana sistemi çalıştır"""
    print("\n🚀 Sistem başlatılıyor...")
    
    # Konfigürasyon ayarları
    env = os.environ.copy()
    src_path = str(SRC_DIR.resolve())
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else src_path
    
    if args.debug:
        env['DEBUG_MODE'] = 'true'
        print("🐛 Debug modu aktif")
    
    if args.no_display:
        env['SHOW_DISPLAY'] = 'false'
        print("📺 Görüntü kapalı")
    
    if args.performance:
        env['PERFORMANCE_MODE'] = args.performance
        print(f"⚡ Performans modu: {args.performance}")
    
    # Ana sistemi başlat
    try:
                cmd = [sys.executable, "-m", "assistive_vision"]
                process = subprocess.Popen(cmd, env=env, cwd=str(PROJECT_ROOT))
        
        # Graceful shutdown için signal handler
        def signal_handler(sig, frame):
            print("\n🛑 Sistem kapatılıyor...")
            process.terminate()
            process.wait()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Process'i bekle
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Sistem hatası: {e}")


def run_test():
    """Test modunu çalıştır"""
    print("🧪 Test modu çalıştırılıyor...")
    
    if os.path.exists("test_system.py"):
        subprocess.run([sys.executable, "test_system.py"])
    else:
        print("❌ Test scripti bulunamadı")


def show_system_info():
    """Sistem bilgilerini göster"""
    print("ℹ️ Sistem Bilgileri")
    print("=" * 30)
    
    # Python versiyonu
    print(f"Python: {sys.version}")
    
    # İşletim sistemi
    import platform
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Makine: {platform.machine()}")
    
    # Raspberry Pi kontrolü
    if os.path.exists("/proc/device-tree/model"):
        with open("/proc/device-tree/model", "r") as f:
            model = f.read().strip()
            print(f"Model: {model}")
    
    # Bellek bilgisi
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"RAM: {memory.total // 1024 // 1024} MB")
        print(f"Kullanılabilir: {memory.available // 1024 // 1024} MB")
    except ImportError:
        print("Bellek bilgisi alınamadı (psutil gerekli)")
    
    # CPU bilgisi
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    cpu = line.split(":")[1].strip()
                    print(f"CPU: {cpu}")
                    break
    except:
        pass


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="Raspberry Pi Engelli Destek Sistemi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python run_system.py                    # Normal başlatma
  python run_system.py --debug           # Debug modu ile
  python run_system.py --no-display      # Görüntü olmadan
  python run_system.py --test            # Test modu
  python run_system.py --info            # Sistem bilgileri
  python run_system.py --performance high # Yüksek performans
        """
    )
    
    parser.add_argument("--debug", "-d", action="store_true",
                       help="Debug modunu etkinleştir")
    
    parser.add_argument("--no-display", "-n", action="store_true",
                       help="Görüntü gösterimini kapat")
    
    parser.add_argument("--test", "-t", action="store_true",
                       help="Test modunu çalıştır")
    
    parser.add_argument("--info", "-i", action="store_true",
                       help="Sistem bilgilerini göster")
    
    parser.add_argument("--performance", "-p", 
                       choices=["high", "balanced", "power_save"],
                       help="Performans modunu ayarla")
    
    parser.add_argument("--check", "-c", action="store_true",
                       help="Bağımlılık kontrolü yap")
    
    args = parser.parse_args()
    
    # Logo yazdır
    print("""
🦽 Raspberry Pi Engelli Destek Sistemi
=====================================
    """)
    
    # Komut seçenekleri
    if args.info:
        show_system_info()
        return
    
    if args.test:
        run_test()
        return
    
    if args.check or len(sys.argv) == 1:
        # Varsayılan olarak kontrol yap
        if not check_dependencies():
            sys.exit(1)
        check_hardware()
        
        if args.check:
            return
    
    # Ana sistemi çalıştır
    run_system(args)


if __name__ == "__main__":
    main()
