#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raspberry Pi Engelli Destek Sistemi
Gerçek zamanlı nesne algılama ve sesli uyarı sistemi

Gereksinimler:
- OpenCV
- YOLOv8 (ultralytics)
- pyttsx3
- numpy
"""

import cv2
import numpy as np
import time
import threading
from typing import Tuple, List, Dict, Optional

# Modül importları
from object_detector import ObjectDetector
from distance_checker import DistanceChecker
from voice_alert import VoiceAlert
from navigation_guide import NavigationGuide
from config import Config


class DisabilityAssistanceSystem:
    """
    Engelli destek sistemi ana sınıfı
    Kamera görüntüsünden nesne algılama ve sesli uyarı sağlar
    """
    
    def __init__(self):
        """Sistem bileşenlerini başlat"""
        print("🚀 Engelli Destek Sistemi başlatılıyor...")
        
        # Konfigürasyon yükle
        self.config = Config()
        
        # Kamera başlat
        self.cap = None
        self.initialize_camera()
        
        # Sistem bileşenlerini başlat
        self.detector = ObjectDetector(self.config)
        self.distance_checker = DistanceChecker(self.config)
        self.voice_alert = VoiceAlert(self.config)
        self.navigation_guide = NavigationGuide(self.config)
        
        # Sistem durumu
        self.running = False
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        print("✅ Sistem başarıyla başlatıldı!")
    
    def initialize_camera(self) -> bool:
        """
        Kamerayı başlat ve ayarlarını yap
        
        Returns:
            bool: Kamera başlatma durumu
        """
        try:
            # Kamerayı aç (genellikle 0, USB kamera varsa 1 olabilir)
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                print("❌ Kamera açılamadı!")
                return False
            
            # Kamera ayarları (Raspberry Pi için optimize edilmiş)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.CAMERA_FPS)
            
            # Buffer size'ı azalt (gecikmeyi önlemek için)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            print(f"📹 Kamera başlatıldı: {self.config.CAMERA_WIDTH}x{self.config.CAMERA_HEIGHT} @ {self.config.CAMERA_FPS}fps")
            return True
            
        except Exception as e:
            print(f"❌ Kamera başlatma hatası: {e}")
            return False
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        Kameradan frame oku
        
        Returns:
            Optional[np.ndarray]: Okunan frame veya None
        """
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            print("⚠️ Frame okunamadı!")
            return None
        
        return frame
    
    def calculate_fps(self) -> float:
        """
        FPS hesapla (performans takibi için)
        
        Returns:
            float: Mevcut FPS değeri
        """
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps_counter = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
        
        return self.fps_counter
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Frame'i işle: nesne algılama ve analiz
        
        Args:
            frame: İşlenecek görüntü frame'i
            
        Returns:
            Tuple[np.ndarray, List[Dict]]: İşlenmiş frame ve algılanan nesneler
        """
        # Nesne algılama yap
        detections = self.detector.detect_objects(frame)
        
        # Debug için bounding box'ları çiz
        annotated_frame = self.detector.draw_detections(frame.copy(), detections)
        
        # Mesafe kontrolü yap
        close_objects = self.distance_checker.check_distances(detections, frame.shape)
        
        # Navigasyon analizi yap
        navigation_info = self.navigation_guide.analyze_regions(detections, frame.shape)
        
        return annotated_frame, detections, close_objects, navigation_info
    
    def handle_alerts(self, detections: List[Dict], close_objects: List[Dict], 
                     navigation_info: Dict):
        """
        Sesli uyarıları ve yönlendirmeleri işle
        
        Args:
            detections: Algılanan nesneler
            close_objects: Yakın nesneler
            navigation_info: Navigasyon bilgileri
        """
        # Yakın nesne uyarıları
        for obj in close_objects:
            self.voice_alert.alert_close_object(obj)
        
        # Navigasyon yönlendirmeleri
        if navigation_info['center_blocked']:
            direction = navigation_info['recommended_direction']
            if direction:
                self.voice_alert.give_direction(direction)
        
        # Genel nesne bildirimleri (throttled)
        self.voice_alert.announce_objects(detections)
    
    def display_info(self, frame: np.ndarray, detections: List[Dict], 
                    navigation_info: Dict) -> np.ndarray:
        """
        Frame üzerine bilgi metinlerini ekle
        
        Args:
            frame: Görüntü frame'i
            detections: Algılanan nesneler
            navigation_info: Navigasyon bilgileri
            
        Returns:
            np.ndarray: Bilgi eklenmiş frame
        """
        # FPS göster
        fps = self.calculate_fps()
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Algılanan nesne sayısını göster
        cv2.putText(frame, f"Nesneler: {len(detections)}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Navigasyon durumunu göster
        if navigation_info['center_blocked']:
            direction = navigation_info['recommended_direction']
            if direction:
                cv2.putText(frame, f"Yön: {direction}", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Bölge çizgileri (debug için)
        height, width = frame.shape[:2]
        left_line = width // 3
        right_line = 2 * width // 3
        
        cv2.line(frame, (left_line, 0), (left_line, height), (255, 255, 0), 2)
        cv2.line(frame, (right_line, 0), (right_line, height), (255, 255, 0), 2)
        
        return frame
    
    def run(self):
        """Ana sistem döngüsü"""
        print("🎯 Sistem çalışmaya başladı. Çıkmak için 'q' tuşuna basın.")
        self.running = True
        
        try:
            while self.running:
                # Frame oku
                frame = self.read_frame()
                if frame is None:
                    print("⚠️ Frame alınamadı, yeniden denenecek...")
                    time.sleep(0.1)
                    continue
                
                # Frame'i işle
                annotated_frame, detections, close_objects, navigation_info = self.process_frame(frame)
                
                # Uyarıları işle (ayrı thread'de çalışabilir)
                if len(detections) > 0 or len(close_objects) > 0:
                    # Sesli uyarıları non-blocking şekilde çal
                    threading.Thread(
                        target=self.handle_alerts,
                        args=(detections, close_objects, navigation_info),
                        daemon=True
                    ).start()
                
                # Bilgileri ekle
                display_frame = self.display_info(annotated_frame, detections, navigation_info)
                
                # Görüntüyü göster (debug için)
                if self.config.SHOW_DISPLAY:
                    cv2.imshow('Engelli Destek Sistemi', display_frame)
                
                # Çıkış kontrolü
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("🛑 Çıkış yapılıyor...")
                    break
                elif key == ord('s'):
                    # Ses ayarlarını değiştir
                    self.voice_alert.toggle_sound()
                elif key == ord('d'):
                    # Debug modunu aç/kapat
                    self.config.DEBUG_MODE = not self.config.DEBUG_MODE
                    print(f"Debug modu: {'AÇIK' if self.config.DEBUG_MODE else 'KAPALI'}")
                
                # CPU'yu rahatlatmak için kısa bekleme
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n🛑 Klavye ile durduruldu.")
        
        except Exception as e:
            print(f"❌ Sistem hatası: {e}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Sistem kaynaklarını temizle"""
        print("🧹 Sistem kapatılıyor...")
        
        self.running = False
        
        # Kamerayı kapat
        if self.cap:
            self.cap.release()
        
        # OpenCV pencerelerini kapat
        cv2.destroyAllWindows()
        
        # Sesli uyarı sistemini kapat
        if hasattr(self, 'voice_alert'):
            self.voice_alert.cleanup()
        
        print("✅ Sistem başarıyla kapatıldı.")


def main():
    """Ana fonksiyon"""
    try:
        # Sistem oluştur ve çalıştır
        system = DisabilityAssistanceSystem()
        system.run()
        
    except Exception as e:
        print(f"❌ Sistem başlatma hatası: {e}")
        print("🔧 Lütfen kamera bağlantısını ve gerekli kütüphaneleri kontrol edin.")


if __name__ == "__main__":
    main()
