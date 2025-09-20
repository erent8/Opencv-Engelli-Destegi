#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfigürasyon Modülü
Tüm sistem ayarları ve parametreleri
"""

import os
from pathlib import Path


class Config:
    """
    Sistem konfigürasyon sınıfı
    Raspberry Pi için optimize edilmiş ayarlar
    """
    
    def __init__(self):
        """Konfigürasyonu başlat"""
        
        # === KAMERA AYARLARI ===
        self.CAMERA_WIDTH = 640          # Kamera genişliği (piksel)
        self.CAMERA_HEIGHT = 480         # Kamera yüksekliği (piksel)
        self.CAMERA_FPS = 15             # Kamera FPS (Raspberry Pi için düşük)
        self.CAMERA_DEVICE = 0           # Kamera cihaz numarası
        
        # === YOLO MODEL AYARLARI ===
        self.YOLO_MODEL_PATH = "yolov8n.pt"  # Hafif YOLOv8 nano modeli
        self.CONFIDENCE_THRESHOLD = 0.5      # Güven eşiği
        self.IOU_THRESHOLD = 0.45           # IoU eşiği (NMS için)
        self.MIN_DETECTION_AREA = 500       # Minimum algılama alanı (piksel²)
        self.DETECTION_INTERVAL = 0.1       # Algılama aralığı (saniye)
        
        # === MESAFE KONTROLÜ AYARLARI ===
        self.CLOSE_DISTANCE_THRESHOLD = 0.15    # Yakın mesafe eşiği (frame oranı)
        self.VERY_CLOSE_THRESHOLD = 0.25        # Çok yakın eşiği (frame oranı)
        self.MEDIUM_DISTANCE_THRESHOLD = 0.08   # Orta mesafe eşiği
        
        # === SESLİ UYARI AYARLARI ===
        self.TTS_RATE = 150                 # Konuşma hızı (kelime/dakika)
        self.TTS_VOLUME = 0.9               # Ses seviyesi (0.0-1.0)
        self.ALERT_INTERVAL = 10.0          # Uyarı aralığı (saniye)
        self.DIRECTION_ALERT_INTERVAL = 10.0  # Yön uyarısı aralığı (saniye)
        self.GENERAL_ANNOUNCE_INTERVAL = 10.0  # Genel duyuru aralığı (saniye)
        self.MAX_ALERT_QUEUE_SIZE = 10      # Maksimum uyarı kuyruğu boyutu
        
        # === NAVİGASYON AYARLARI ===
        self.MAX_OBJECTS_PER_ZONE = 3      # Bölge başına maksimum nesne sayısı
        self.ZONE_DIVISION_RATIO = 0.33    # Bölge ayırma oranı (sol/sağ)
        self.CENTER_ZONE_RATIO = 0.34      # Orta bölge oranı
        
        # === PERFORMANS AYARLARI ===
        self.MAX_FPS = 20                  # Maksimum FPS sınırı
        self.PROCESSING_THREADS = 1        # İşleme thread sayısı
        self.MEMORY_LIMIT_MB = 512         # Bellek sınırı (MB)
        
        # === DEBUG VE GÖRÜNTÜ AYARLARI ===
        self.DEBUG_MODE = False            # Debug modu
        self.SHOW_DISPLAY = True           # Görüntü gösterimi
        self.SAVE_FRAMES = False           # Frame kaydetme
        self.LOG_DETECTIONS = False        # Algılama loglaması
        
        # === DOSYA YOLLARı ===
        self.BASE_DIR = Path(__file__).parent
        self.MODELS_DIR = self.BASE_DIR / "models"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        self.DATA_DIR = self.BASE_DIR / "data"
        
        # Dizinleri oluştur
        self._create_directories()
        
        # Ortam değişkenlerinden ayarları yükle
        self._load_from_environment()
    
    def _create_directories(self):
        """Gerekli dizinleri oluştur"""
        directories = [
            self.MODELS_DIR,
            self.LOGS_DIR,
            self.DATA_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_from_environment(self):
        """Ortam değişkenlerinden ayarları yükle"""
        
        # Kamera ayarları
        self.CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", self.CAMERA_WIDTH))
        self.CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", self.CAMERA_HEIGHT))
        self.CAMERA_FPS = int(os.getenv("CAMERA_FPS", self.CAMERA_FPS))
        
        # YOLO ayarları
        self.YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", self.YOLO_MODEL_PATH)
        self.CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 
                                                   self.CONFIDENCE_THRESHOLD))
        
        # Debug modu
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.SHOW_DISPLAY = os.getenv("SHOW_DISPLAY", "true").lower() == "true"
    
    def get_camera_config(self) -> dict:
        """
        Kamera konfigürasyonunu döndür
        
        Returns:
            dict: Kamera ayarları
        """
        return {
            'width': self.CAMERA_WIDTH,
            'height': self.CAMERA_HEIGHT,
            'fps': self.CAMERA_FPS,
            'device': self.CAMERA_DEVICE
        }
    
    def get_yolo_config(self) -> dict:
        """
        YOLO konfigürasyonunu döndür
        
        Returns:
            dict: YOLO ayarları
        """
        return {
            'model_path': self.YOLO_MODEL_PATH,
            'confidence': self.CONFIDENCE_THRESHOLD,
            'iou': self.IOU_THRESHOLD,
            'min_area': self.MIN_DETECTION_AREA,
            'interval': self.DETECTION_INTERVAL
        }
    
    def get_tts_config(self) -> dict:
        """
        TTS konfigürasyonunu döndür
        
        Returns:
            dict: TTS ayarları
        """
        return {
            'rate': self.TTS_RATE,
            'volume': self.TTS_VOLUME,
            'alert_interval': self.ALERT_INTERVAL,
            'direction_interval': self.DIRECTION_ALERT_INTERVAL,
            'general_interval': self.GENERAL_ANNOUNCE_INTERVAL
        }
    
    def get_navigation_config(self) -> dict:
        """
        Navigasyon konfigürasyonunu döndür
        
        Returns:
            dict: Navigasyon ayarları
        """
        return {
            'max_objects_per_zone': self.MAX_OBJECTS_PER_ZONE,
            'zone_division_ratio': self.ZONE_DIVISION_RATIO,
            'center_zone_ratio': self.CENTER_ZONE_RATIO
        }
    
    def update_camera_settings(self, width: int = None, height: int = None, 
                              fps: int = None):
        """
        Kamera ayarlarını güncelle
        
        Args:
            width: Yeni genişlik
            height: Yeni yükseklik
            fps: Yeni FPS
        """
        if width:
            self.CAMERA_WIDTH = width
        if height:
            self.CAMERA_HEIGHT = height
        if fps:
            self.CAMERA_FPS = fps
        
        print(f"📹 Kamera ayarları güncellendi: {self.CAMERA_WIDTH}x{self.CAMERA_HEIGHT} @ {self.CAMERA_FPS}fps")
    
    def update_detection_settings(self, confidence: float = None, 
                                 iou: float = None, interval: float = None):
        """
        Algılama ayarlarını güncelle
        
        Args:
            confidence: Yeni güven eşiği
            iou: Yeni IoU eşiği
            interval: Yeni algılama aralığı
        """
        if confidence:
            self.CONFIDENCE_THRESHOLD = confidence
        if iou:
            self.IOU_THRESHOLD = iou
        if interval:
            self.DETECTION_INTERVAL = interval
        
        print(f"🎯 Algılama ayarları güncellendi: conf={self.CONFIDENCE_THRESHOLD}, iou={self.IOU_THRESHOLD}")
    
    def update_tts_settings(self, rate: int = None, volume: float = None):
        """
        TTS ayarlarını güncelle
        
        Args:
            rate: Yeni konuşma hızı
            volume: Yeni ses seviyesi
        """
        if rate:
            self.TTS_RATE = rate
        if volume:
            self.TTS_VOLUME = max(0.0, min(1.0, volume))
        
        print(f"🔊 TTS ayarları güncellendi: rate={self.TTS_RATE}, volume={self.TTS_VOLUME}")
    
    def set_performance_mode(self, mode: str):
        """
        Performans modunu ayarla
        
        Args:
            mode: 'high', 'balanced', 'power_save'
        """
        if mode == 'high':
            # Yüksek performans
            self.CAMERA_FPS = 20
            self.DETECTION_INTERVAL = 0.05
            self.MAX_FPS = 25
            print("🚀 Yüksek performans modu aktif")
            
        elif mode == 'balanced':
            # Dengeli mod
            self.CAMERA_FPS = 15
            self.DETECTION_INTERVAL = 0.1
            self.MAX_FPS = 20
            print("⚖️ Dengeli performans modu aktif")
            
        elif mode == 'power_save':
            # Güç tasarrufu
            self.CAMERA_FPS = 10
            self.DETECTION_INTERVAL = 0.2
            self.MAX_FPS = 15
            print("🔋 Güç tasarrufu modu aktif")
        
        else:
            print("⚠️ Geçersiz performans modu. Kullanılabilir: 'high', 'balanced', 'power_save'")
    
    def enable_debug_mode(self, enable: bool = True):
        """
        Debug modunu aç/kapat
        
        Args:
            enable: Debug modu durumu
        """
        self.DEBUG_MODE = enable
        self.LOG_DETECTIONS = enable
        
        print(f"🐛 Debug modu: {'AÇIK' if enable else 'KAPALI'}")
    
    def get_model_path(self, model_name: str = None) -> Path:
        """
        Model dosya yolunu döndür
        
        Args:
            model_name: Model dosya adı
            
        Returns:
            Path: Model dosya yolu
        """
        if model_name:
            return self.MODELS_DIR / model_name
        return self.MODELS_DIR / self.YOLO_MODEL_PATH
    
    def get_log_path(self, log_name: str = "system.log") -> Path:
        """
        Log dosya yolunu döndür
        
        Args:
            log_name: Log dosya adı
            
        Returns:
            Path: Log dosya yolu
        """
        return self.LOGS_DIR / log_name
    
    def validate_settings(self) -> bool:
        """
        Ayarları doğrula
        
        Returns:
            bool: Ayarlar geçerli mi
        """
        errors = []
        
        # Kamera ayarları kontrolü
        if self.CAMERA_WIDTH <= 0 or self.CAMERA_HEIGHT <= 0:
            errors.append("Geçersiz kamera boyutları")
        
        if self.CAMERA_FPS <= 0 or self.CAMERA_FPS > 60:
            errors.append("Geçersiz kamera FPS değeri")
        
        # YOLO ayarları kontrolü
        if not (0.0 <= self.CONFIDENCE_THRESHOLD <= 1.0):
            errors.append("Güven eşiği 0.0-1.0 arasında olmalı")
        
        if not (0.0 <= self.IOU_THRESHOLD <= 1.0):
            errors.append("IoU eşiği 0.0-1.0 arasında olmalı")
        
        # TTS ayarları kontrolü
        if not (0.0 <= self.TTS_VOLUME <= 1.0):
            errors.append("TTS ses seviyesi 0.0-1.0 arasında olmalı")
        
        if self.TTS_RATE <= 0:
            errors.append("TTS konuşma hızı pozitif olmalı")
        
        if errors:
            print("❌ Konfigürasyon hataları:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("✅ Konfigürasyon doğrulandı")
        return True
    
    def save_to_file(self, file_path: str = None):
        """
        Ayarları dosyaya kaydet
        
        Args:
            file_path: Kayıt dosya yolu
        """
        if not file_path:
            file_path = self.BASE_DIR / "config_backup.py"
        
        import time
        config_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otomatik oluşturulan konfigürasyon yedeki
Oluşturulma zamanı: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

# Kamera ayarları
CAMERA_WIDTH = {self.CAMERA_WIDTH}
CAMERA_HEIGHT = {self.CAMERA_HEIGHT}
CAMERA_FPS = {self.CAMERA_FPS}

# YOLO ayarları
YOLO_MODEL_PATH = "{self.YOLO_MODEL_PATH}"
CONFIDENCE_THRESHOLD = {self.CONFIDENCE_THRESHOLD}
IOU_THRESHOLD = {self.IOU_THRESHOLD}

# TTS ayarları
TTS_RATE = {self.TTS_RATE}
TTS_VOLUME = {self.TTS_VOLUME}
ALERT_INTERVAL = {self.ALERT_INTERVAL}

# Debug ayarları
DEBUG_MODE = {self.DEBUG_MODE}
SHOW_DISPLAY = {self.SHOW_DISPLAY}
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            print(f"💾 Konfigürasyon kaydedildi: {file_path}")
        except Exception as e:
            print(f"❌ Konfigürasyon kaydetme hatası: {e}")
    
    def print_current_settings(self):
        """Mevcut ayarları yazdır"""
        print("\n📋 Mevcut Sistem Ayarları:")
        print("=" * 40)
        
        print(f"📹 Kamera: {self.CAMERA_WIDTH}x{self.CAMERA_HEIGHT} @ {self.CAMERA_FPS}fps")
        print(f"🎯 YOLO: {self.YOLO_MODEL_PATH} (conf: {self.CONFIDENCE_THRESHOLD})")
        print(f"🔊 TTS: {self.TTS_RATE} wpm, volume: {self.TTS_VOLUME}")
        print(f"🐛 Debug: {'AÇIK' if self.DEBUG_MODE else 'KAPALI'}")
        print(f"📺 Görüntü: {'AÇIK' if self.SHOW_DISPLAY else 'KAPALI'}")
        print("=" * 40 + "\n")


# Global konfigürasyon instance'ı
config = Config()

if __name__ == "__main__":
    # Test ve örnek kullanım
    import time
    
    config.print_current_settings()
    config.validate_settings()
    
    # Performans modu testi
    print("\n🧪 Performans modu testleri:")
    for mode in ['power_save', 'balanced', 'high']:
        config.set_performance_mode(mode)
        time.sleep(1)
    
    print("\n✅ Konfigürasyon testi tamamlandı")
