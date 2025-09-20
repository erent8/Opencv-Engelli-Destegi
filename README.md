# 🦽 Raspberry Pi Engelli Destek Sistemi

Raspberry Pi üzerinde çalışan gerçek zamanlı nesne algılama ve sesli uyarı sistemi. YOLOv8 kullanarak görme engelli bireyler için navigasyon desteği sağlar.

## 🌟 Özellikler

- **Gerçek Zamanlı Nesne Algılama**: YOLOv8 ile insan, araç, bisiklet vb. nesneleri algılar
- **Sesli Uyarı Sistemi**: Türkçe sesli uyarılar ve yönlendirmeler
- **3 Bölgeli Navigasyon**: Sol, orta, sağ bölge analizi ile yön tarifi
- **Yakınlık Algısı**: Nesne boyutuna göre mesafe hesaplama
- **Raspberry Pi Optimizasyonu**: Düşük güç tüketimi ve yüksek performans
- **Modüler Yapı**: Kolay özelleştirme ve geliştirme

## 📋 Gereksinimler

### Donanım
- Raspberry Pi 4 (önerilen) veya Raspberry Pi 3B+
- USB Kamera veya Raspberry Pi Kamera Modülü
- Hoparlör veya Kulaklık
- MicroSD Kart (32GB+)

### Yazılım
- Raspberry Pi OS (Bullseye veya sonrası)
- Python 3.8+
- OpenCV 4.5+

## 🚀 Kurulum

### 1. Sistem Güncellemesi
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Python Kütüphanelerini Yükle
```bash
# Sistem kütüphaneleri
sudo apt install python3-pip python3-venv
sudo apt install libopencv-dev python3-opencv
sudo apt install espeak espeak-data libespeak1 libespeak-dev
sudo apt install portaudio19-dev python3-pyaudio

# Sanal ortam oluştur
python3 -m venv venv
source venv/bin/activate

# Python gereksinimlerini yükle
pip install -r requirements.txt
```

### 3. YOLOv8 Modelini İndir
```bash
# Hafif model (önerilen)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -P models/

# Veya Python ile otomatik indirme
python -c "from ultralytics import YOLO; YOLO('models/yolov8n.pt')"
```

### 4. Kamerayı Etkinleştir
```bash
# Raspberry Pi kamerası için
sudo raspi-config
# Interface Options > Camera > Enable

# USB kamera kontrolü
lsusb
v4l2-ctl --list-devices
```

## 🎮 Kullanım

### Temel Çalıştırma
```bash
PYTHONPATH=src python -m assistive_vision
```

Windows PowerShell icin:
```powershell
$env:PYTHONPATH="src"
python -m assistive_vision
```

### Klavye Kısayolları
- `q`: Çıkış
- `s`: Sesi aç/kapat
- `d`: Debug modunu aç/kapat

### Konfigürasyon
`src/assistive_vision/config.py` dosyasından ayarları değiştirebilirsiniz:

```python
# Kamera ayarları
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 15

# Algılama hassasiyeti
CONFIDENCE_THRESHOLD = 0.5

# Sesli uyarı ayarları
TTS_RATE = 150  # Konuşma hızı
TTS_VOLUME = 0.9  # Ses seviyesi
```

## 📁 Proje Yapısı

```
.
+-- docs/
+-- scripts/
|   +-- install.sh
|   +-- run_system.py
+-- src/
|   +-- assistive_vision/
|       +-- __init__.py
|       +-- __main__.py
|       +-- system.py
|       +-- config.py
|       +-- detection_logger.py
|       +-- distance_checker.py
|       +-- navigation_guide.py
|       +-- object_detector.py
|       +-- object_tracker.py
|       +-- voice_alert.py
+-- tests/
|   +-- test_continuous_alerts.py
|   +-- test_windows.py
+-- data/
+-- logs/
+-- models/
|   +-- yolov8n.pt
+-- requirements.txt
+-- README.md
+-- AGENTS.md
```

## 🔧 Performans Optimizasyonu

### Raspberry Pi 4 için
```python
# config.py içinde
config.set_performance_mode('high')
```

### Raspberry Pi 3 için
```python
# config.py içinde
config.set_performance_mode('balanced')
```

### Güç Tasarrufu
```python
# config.py içinde
config.set_performance_mode('power_save')
```

## 🎯 Algılanabilen Nesneler

- **İnsanlar**: Yayalar, çocuklar
- **Araçlar**: Araba, otobüs, kamyon, motosiklet
- **Bisikletler**: Bisiklet, scooter
- **Trafik Elemanları**: Trafik lambası, dur işareti
- **Hayvanlar**: Kedi, köpek

## 🔊 Sesli Uyarı Örnekleri

- "Önünüzde insan var"
- "Dikkat! Çok yakın engel"
- "Sağa dönün"
- "Yol açık"
- "Durun"

## ⚙️ Gelişmiş Ayarlar

### Kamera Ayarları
```python
config.update_camera_settings(
    width=320,    # Daha hızlı işleme için
    height=240,
    fps=10
)
```

### Algılama Hassasiyeti
```python
config.update_detection_settings(
    confidence=0.3,  # Daha hassas algılama
    interval=0.05    # Daha sık algılama
)
```

### TTS Ayarları
```python
config.update_tts_settings(
    rate=120,      # Daha yavaş konuşma
    volume=0.8     # Daha düşük ses
)
```

## 🐛 Sorun Giderme

### Kamera Açılmıyor
```bash
# Kamera izinlerini kontrol et
sudo usermod -a -G video $USER
sudo reboot

# Kamera testı
raspistill -o test.jpg  # Raspberry Pi kamerası
fswebcam test.jpg       # USB kamera
```

### Ses Çıkmıyor
```bash
# Ses kartını kontrol et
aplay -l

# Ses seviyesini ayarla
alsamixer

# TTS testı
espeak "Test mesajı"
```

### Düşük FPS
- Kamera çözünürlüğünü düşürün (320x240)
- Detection interval'ı artırın (0.2 saniye)
- YOLOv8n yerine daha hafif model kullanın

### Yüksek CPU Kullanımı
```bash
# CPU frekansını kontrol et
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq

# GPU memory split ayarla
sudo raspi-config
# Advanced Options > Memory Split > 128
```

## 📊 Performans Metrikleri

| Model | Raspberry Pi 4 | Raspberry Pi 3B+ |
|-------|---------------|------------------|
| YOLOv8n | 10-15 FPS | 5-8 FPS |
| YOLOv8s | 6-10 FPS | 3-5 FPS |
| CPU Kullanımı | %60-80 | %80-95 |
| RAM Kullanımı | ~400MB | ~350MB |

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [OpenCV](https://opencv.org/)
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3)

## 📞 İletişim

Sorularınız için:
- GitHub Issues kullanın
- E-posta: [proje-email@example.com]

---

**Not**: Bu proje eğitim ve araştırma amaçlıdır. Gerçek kullanımda ek güvenlik önlemleri alınmalıdır.
