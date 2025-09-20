#!/bin/bash
# Raspberry Pi Engelli Destek Sistemi Kurulum Scripti

set -e  # Hata durumunda scripti durdur

echo "🚀 Raspberry Pi Engelli Destek Sistemi Kurulumu Başlıyor..."
echo "=================================================="

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonksiyonlar
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Sistem kontrolü
check_system() {
    print_status "Sistem kontrolü yapılıyor..."
    
    # Raspberry Pi kontrolü
    if [ ! -f /proc/device-tree/model ]; then
        print_warning "Raspberry Pi tespit edilemedi, devam ediliyor..."
    else
        PI_MODEL=$(cat /proc/device-tree/model)
        print_success "Tespit edilen sistem: $PI_MODEL"
    fi
    
    # Python versiyonu kontrolü
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(echo "$PYTHON_VERSION >= 3.8" | bc -l)" -eq 1 ]; then
        print_success "Python $PYTHON_VERSION ✓"
    else
        print_error "Python 3.8+ gerekli. Mevcut versiyon: $PYTHON_VERSION"
        exit 1
    fi
}

# Sistem güncellemesi
update_system() {
    print_status "Sistem güncelleniyor..."
    sudo apt update -qq
    sudo apt upgrade -y -qq
    print_success "Sistem güncellendi"
}

# Sistem bağımlılıklarını yükle
install_system_deps() {
    print_status "Sistem bağımlılıkları yükleniyor..."
    
    # Temel paketler
    sudo apt install -y -qq \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        cmake \
        pkg-config
    
    # OpenCV bağımlılıkları
    sudo apt install -y -qq \
        libopencv-dev \
        python3-opencv \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev
    
    # Ses bağımlılıkları
    sudo apt install -y -qq \
        espeak \
        espeak-data \
        libespeak1 \
        libespeak-dev \
        portaudio19-dev \
        python3-pyaudio \
        alsa-utils
    
    # Kamera bağımlılıkları
    sudo apt install -y -qq \
        v4l-utils \
        fswebcam
    
    print_success "Sistem bağımlılıkları yüklendi"
}

# Python sanal ortamı oluştur
create_venv() {
    print_status "Python sanal ortamı oluşturuluyor..."
    
    if [ -d "venv" ]; then
        print_warning "Mevcut sanal ortam siliniyor..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    # pip güncelle
    pip install --upgrade pip setuptools wheel
    
    print_success "Python sanal ortamı oluşturuldu"
}

# Python paketlerini yükle
install_python_deps() {
    print_status "Python paketleri yükleniyor..."
    
    source venv/bin/activate
    
    # Önce torch'u yükle (Raspberry Pi için özel)
    if [[ $(uname -m) == "armv7l" ]] || [[ $(uname -m) == "aarch64" ]]; then
        print_status "ARM işlemci için PyTorch yükleniyor..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    fi
    
    # Diğer paketleri yükle
    pip install -r requirements.txt
    
    print_success "Python paketleri yüklendi"
}

# YOLOv8 modelini indir
download_model() {
    print_status "YOLOv8 modeli indiriliyor..."
    
    source venv/bin/activate
    
    # Models dizinini oluştur
    mkdir -p models
    
    # Model indir
    python3 -c "
from ultralytics import YOLO
import os

model_path = 'models/yolov8n.pt'
if not os.path.exists(model_path):
    print('YOLOv8n modeli indiriliyor...')
    model = YOLO('yolov8n.pt')
    # Modeli models dizinine taşı
    import shutil
    if os.path.exists('yolov8n.pt'):
        shutil.move('yolov8n.pt', model_path)
    print('Model indirildi: ' + model_path)
else:
    print('Model zaten mevcut: ' + model_path)
"
    
    print_success "YOLOv8 modeli hazır"
}

# Kamera ayarlarını kontrol et
setup_camera() {
    print_status "Kamera ayarları kontrol ediliyor..."
    
    # Raspberry Pi kamerası kontrolü
    if [ -f /boot/config.txt ]; then
        if ! grep -q "camera_auto_detect=1" /boot/config.txt; then
            print_status "Raspberry Pi kamerası etkinleştiriliyor..."
            echo "camera_auto_detect=1" | sudo tee -a /boot/config.txt
            echo "dtoverlay=vc4-kms-v3d" | sudo tee -a /boot/config.txt
            print_warning "Kamera ayarları için yeniden başlatma gerekebilir"
        fi
    fi
    
    # USB kamera kontrolü
    if lsusb | grep -i "camera\|video" > /dev/null; then
        print_success "USB kamera tespit edildi"
    fi
    
    # Video cihazları listele
    if ls /dev/video* > /dev/null 2>&1; then
        CAMERAS=$(ls /dev/video*)
        print_success "Kamera cihazları: $CAMERAS"
    else
        print_warning "Kamera cihazı bulunamadı"
    fi
}

# Ses ayarlarını kontrol et
setup_audio() {
    print_status "Ses ayarları kontrol ediliyor..."
    
    # Ses kartlarını listele
    if aplay -l > /dev/null 2>&1; then
        print_success "Ses kartı tespit edildi"
        
        # Varsayılan ses kartını ayarla
        if [ ! -f ~/.asoundrc ]; then
            cat > ~/.asoundrc << EOF
pcm.!default {
    type hw
    card 0
}
ctl.!default {
    type hw
    card 0
}
EOF
            print_status "Varsayılan ses kartı ayarlandı"
        fi
        
        # TTS testi
        if command -v espeak > /dev/null; then
            print_status "TTS testi yapılıyor..."
            espeak "Sistem hazır" 2>/dev/null || print_warning "TTS testi başarısız"
        fi
    else
        print_warning "Ses kartı bulunamadı"
    fi
}

# İzinleri ayarla
setup_permissions() {
    print_status "Kullanıcı izinleri ayarlanıyor..."
    
    # Video grubuna ekle
    sudo usermod -a -G video $USER
    
    # Audio grubuna ekle
    sudo usermod -a -G audio $USER
    
    # Dialout grubuna ekle (seri port için)
    sudo usermod -a -G dialout $USER
    
    print_success "Kullanıcı izinleri ayarlandı"
}

# Servis dosyası oluştur (opsiyonel)
create_service() {
    read -p "Sistem servisi oluşturulsun mu? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Sistem servisi oluşturuluyor..."
        
        CURRENT_DIR=$(pwd)
        SERVICE_FILE="/etc/systemd/system/engelli-destek.service"
        
        sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Raspberry Pi Engelli Destek Sistemi
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=DISPLAY=:0
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable engelli-destek.service
        
        print_success "Sistem servisi oluşturuldu"
        print_status "Servis komutları:"
        echo "  Başlat: sudo systemctl start engelli-destek"
        echo "  Durdur: sudo systemctl stop engelli-destek"
        echo "  Durum:  sudo systemctl status engelli-destek"
    fi
}

# Test scripti oluştur
create_test_script() {
    print_status "Test scripti oluşturuluyor..."
    
    cat > test_system.py << 'EOF'
#!/usr/bin/env python3
"""
Sistem test scripti
Tüm bileşenlerin çalışıp çalışmadığını kontrol eder
"""

import sys
import cv2
import numpy as np

def test_camera():
    """Kamera testi"""
    print("📹 Kamera testi...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Kamera açılamadı")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame alınamadı")
            return False
        
        print(f"✅ Kamera çalışıyor: {frame.shape}")
        cap.release()
        return True
    except Exception as e:
        print(f"❌ Kamera hatası: {e}")
        return False

def test_yolo():
    """YOLO testi"""
    print("🎯 YOLO testi...")
    try:
        from ultralytics import YOLO
        model = YOLO('models/yolov8n.pt')
        print("✅ YOLO modeli yüklendi")
        return True
    except Exception as e:
        print(f"❌ YOLO hatası: {e}")
        return False

def test_tts():
    """TTS testi"""
    print("🔊 TTS testi...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say("Test")
        engine.runAndWait()
        print("✅ TTS çalışıyor")
        return True
    except Exception as e:
        print(f"❌ TTS hatası: {e}")
        return False

def main():
    print("🧪 Sistem Testi Başlıyor...")
    print("=" * 30)
    
    tests = [
        ("Kamera", test_camera),
        ("YOLO", test_yolo),
        ("TTS", test_tts)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        print()
    
    print("📊 Test Sonuçları:")
    print("-" * 20)
    all_passed = True
    for name, result in results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Tüm testler başarılı! Sistem hazır.")
    else:
        print("\n⚠️ Bazı testler başarısız. Kurulumu kontrol edin.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF
    
    chmod +x test_system.py
    print_success "Test scripti oluşturuldu: test_system.py"
}

# Ana kurulum fonksiyonu
main() {
    echo
    print_status "Kurulum başlıyor..."
    
    # Kullanıcı onayı
    read -p "Kuruluma devam etmek istiyor musunuz? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Kurulum iptal edildi."
        exit 0
    fi
    
    # Kurulum adımları
    check_system
    update_system
    install_system_deps
    create_venv
    install_python_deps
    download_model
    setup_camera
    setup_audio
    setup_permissions
    create_test_script
    create_service
    
    echo
    print_success "🎉 Kurulum tamamlandı!"
    echo
    print_status "Sonraki adımlar:"
    echo "1. Yeniden başlatın: sudo reboot"
    echo "2. Test çalıştırın: python test_system.py"
    echo "3. Sistemi başlatın: python main.py"
    echo
    print_status "Kullanım kılavuzu: README.md"
    
    # Yeniden başlatma önerisi
    read -p "Şimdi yeniden başlatmak istiyor musunuz? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo reboot
    fi
}

# Scripti çalıştır
main "$@"
