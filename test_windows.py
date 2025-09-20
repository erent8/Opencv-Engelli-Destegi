#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Test Scripti
Raspberry Pi Engelli Destek Sistemi'ni Windows'ta test etmek için
"""

import cv2
import numpy as np
import time
import threading
from typing import Dict, List
import sys
import os

# Modül importları (hata kontrolü ile)
try:
    from object_detector import ObjectDetector
    from distance_checker import DistanceChecker
    from voice_alert import VoiceAlert
    from navigation_guide import NavigationGuide
    from config import Config
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Modül import hatası: {e}")
    print("Temel test modunda çalışılacak...")
    MODULES_AVAILABLE = False


class WindowsTestSystem:
    """Windows'ta test için basitleştirilmiş sistem"""
    
    def __init__(self):
        """Test sistemini başlat"""
        print("🖥️ Windows Test Sistemi başlatılıyor...")
        
        self.cap = None
        self.running = False
        
        # Konfigürasyon
        if MODULES_AVAILABLE:
            self.config = Config()
            self.config.SHOW_DISPLAY = True
            self.config.DEBUG_MODE = True
        
        # Demo verisi
        self.demo_detections = [
            {
                'class_id': 0,
                'class_name': 'person',
                'confidence': 0.85,
                'bbox': (200, 250, 400, 550),  # Yakın insan
                'center': (300, 400),
                'width': 200,
                'height': 300,
                'area': 60000,
                'distance_meters': 2.5  # 2.5 metre uzaklık
            },
            {
                'class_id': 2,
                'class_name': 'car',
                'confidence': 0.92,
                'bbox': (600, 350, 1000, 550),  # Uzak araba
                'center': (800, 450),
                'width': 400,
                'height': 200,
                'area': 80000,
                'distance_meters': 8.0  # 8 metre uzaklık
            },
            {
                'class_id': 1,
                'class_name': 'bicycle',
                'confidence': 0.78,
                'bbox': (50, 400, 150, 500),  # Sol tarafta bisiklet
                'center': (100, 450),
                'width': 100,
                'height': 100,
                'area': 10000,
                'distance_meters': 5.0  # 5 metre uzaklık
            }
        ]
    
    def test_camera(self):
        """Kamera testi"""
        print("\n📹 Kamera testi...")
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("⚠️ Kamera bulunamadı, demo modu kullanılacak")
                return False
            
            # Kamera ayarları - HD çözünürlük
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            # Test frame'i al
            ret, frame = self.cap.read()
            if ret:
                print(f"✅ Kamera çalışıyor: {frame.shape}")
                return True
            else:
                print("❌ Frame alınamadı")
                return False
                
        except Exception as e:
            print(f"❌ Kamera hatası: {e}")
            return False
    
    def test_yolo(self):
        """YOLO testi"""
        print("\n🎯 YOLO testi...")
        
        try:
            from ultralytics import YOLO
            
            # Model yolu kontrol
            model_paths = ["yolov8n.pt", "models/yolov8n.pt"]
            model_path = None
            
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if not model_path:
                print("⚠️ YOLO modeli bulunamadı, indiriliyor...")
                model = YOLO('yolov8n.pt')  # Otomatik indir
                model_path = 'yolov8n.pt'
            else:
                model = YOLO(model_path)
            
            print(f"✅ YOLO modeli yüklendi: {model_path}")
            
            # Test görüntüsü ile test
            test_image = np.zeros((480, 640, 3), dtype=np.uint8)
            results = model(test_image, verbose=False)
            print("✅ YOLO algılama testi başarılı")
            
            return True, model
            
        except Exception as e:
            print(f"❌ YOLO hatası: {e}")
            return False, None
    
    def test_tts(self):
        """TTS testi"""
        print("\n🔊 TTS testi...")
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # Türkçe ses ayarları
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'tr' in voice.id.lower() or 'turkish' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.8)
            
            print("🎤 Playing test message...")
            engine.say("Windows test system is running")
            engine.runAndWait()
            
            print("✅ TTS çalışıyor")
            return True, engine
            
        except Exception as e:
            print(f"❌ TTS hatası: {e}")
            return False, None
    
    def create_demo_frame(self, width=1280, height=720):
        """Demo frame oluştur"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Arka plan gradyanı
        for i in range(height):
            intensity = int(50 + (i / height) * 100)
            frame[i, :] = [intensity, intensity//2, intensity//3]
        
        # Demo nesneleri çiz
        for detection in self.demo_detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            distance = detection.get('distance_meters', 0)
            
            # Color by object type
            if class_name == 'person':
                color = (0, 255, 0)  # Green
            elif class_name == 'car':
                color = (0, 0, 255)  # Red
            elif class_name == 'bicycle':
                color = (255, 0, 0)  # Blue
            else:
                color = (128, 128, 128)  # Gray
            
            # Uzaklığa göre çerçeve kalınlığı (yakın = kalın)
            thickness = 4 if distance < 3 else 3 if distance < 6 else 2
            
            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Label - nesne adı, güven ve uzaklık
            label = f"{class_name} {confidence:.2f} - {distance:.1f}m"
            
            # Label arka planı
            (label_width, label_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
            )
            cv2.rectangle(frame, (x1, y1-label_height-15), 
                         (x1+label_width+10, y1), color, -1)
            
            # Label metni
            cv2.putText(frame, label, (x1+5, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Merkez noktası
            center = detection['center']
            cv2.circle(frame, center, 8, color, -1)
            
            # Draw distance circles (close = large circle)
            if distance < 3:
                cv2.circle(frame, center, 30, (0, 0, 255), 3)  # Red - dangerous
            elif distance < 6:
                cv2.circle(frame, center, 20, (0, 255, 255), 2)  # Yellow - caution
            else:
                cv2.circle(frame, center, 15, (0, 255, 0), 2)   # Green - safe
        
        # Bölge çizgileri
        left_line = width // 3
        right_line = 2 * width // 3
        cv2.line(frame, (left_line, 0), (left_line, height), (255, 255, 0), 2)
        cv2.line(frame, (right_line, 0), (right_line, height), (255, 255, 0), 2)
        
        # Information texts - scaled for HD
        cv2.putText(frame, "DEMO MODE - Windows Test (1280x720)", (20, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        
        # Distance information panel
        cv2.putText(frame, "DISTANCE INFO:", (20, height-150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, "Red <3m: DANGEROUS", (20, height-120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, "Yellow 3-6m: CAUTION", (20, height-90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, "Green >6m: SAFE", (20, height-60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Zone information
        cv2.putText(frame, "Left: Bicycle (5.0m) | Center: Person (2.5m) | Right: Car (8.0m)", 
                   (20, height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        return frame
    
    def run_demo(self, with_yolo=False, with_tts=False):
        """Demo modu çalıştır"""
        print("\n🎬 Demo modu başlatılıyor...")
        print("Çıkmak için 'q' tuşuna basın")
        
        yolo_model = None
        tts_engine = None
        
        if with_yolo:
            success, yolo_model = self.test_yolo()
            if not success:
                with_yolo = False
        
        if with_tts:
            success, tts_engine = self.test_tts()
            if not success:
                with_tts = False
        
        # Modülleri test et
        if MODULES_AVAILABLE:
            try:
                detector = ObjectDetector(self.config) if with_yolo else None
                distance_checker = DistanceChecker(self.config)
                voice_alert = VoiceAlert(self.config) if with_tts else None
                nav_guide = NavigationGuide(self.config)
                print("✅ Tüm modüller yüklendi")
            except Exception as e:
                print(f"⚠️ Modül yükleme hatası: {e}")
                detector = None
                distance_checker = None
                voice_alert = None
                nav_guide = None
        
        self.running = True
        frame_count = 0
        last_alert_time = 0
        
        try:
            while self.running:
                # Frame al (kamera varsa gerçek, yoksa demo)
                if self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if not ret:
                        frame = self.create_demo_frame()
                else:
                    frame = self.create_demo_frame()
                
                frame_count += 1
                current_time = time.time()
                
                # YOLO ile algılama (varsa)
                detections = []
                if detector and yolo_model and frame_count % 10 == 0:  # Her 10 frame'de bir
                    try:
                        detections = detector.detect_objects(frame)
                        if detections:
                            frame = detector.draw_detections(frame, detections)
                    except Exception as e:
                        print(f"Algılama hatası: {e}")
                
                # Demo verileri kullan (YOLO yoksa)
                if not detections and frame_count % 30 == 0:
                    detections = self.demo_detections
                
                # Mesafe ve navigasyon analizi
                if detections and MODULES_AVAILABLE:
                    try:
                        # Mesafe kontrolü
                        if distance_checker:
                            close_objects = distance_checker.check_distances(detections, frame.shape)
                            
                            # Yakın nesne uyarısı (10 saniye aralık)
                            if close_objects and voice_alert and (current_time - last_alert_time) > 10:
                                threading.Thread(
                                    target=voice_alert.alert_close_object,
                                    args=(close_objects[0],),
                                    daemon=True
                                ).start()
                                last_alert_time = current_time
                        
                        # Navigasyon analizi
                        if nav_guide:
                            nav_info = nav_guide.analyze_regions(detections, frame.shape)
                            
                            # Navigasyon bilgilerini ekranda göster
                            direction = nav_info.get('recommended_direction', 'forward')
                            cv2.putText(frame, f"Yon: {direction.upper()}", (10, 60),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            # Yön uyarısı (10 saniye aralık)
                            if (nav_info.get('center_blocked', False) and 
                                voice_alert and 
                                direction in ['left', 'right'] and 
                                (current_time - last_alert_time) > 10):
                                
                                threading.Thread(
                                    target=voice_alert.give_direction,
                                    args=(direction,),
                                    daemon=True
                                ).start()
                                last_alert_time = current_time
                    
                    except Exception as e:
                        print(f"Analiz hatası: {e}")
                
                # FPS göster
                fps = frame_count / max(current_time - time.time() + 1, 1)
                cv2.putText(frame, f"FPS: {fps:.1f}", (500, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Nesne sayısı göster
                cv2.putText(frame, f"Nesneler: {len(detections)}", (500, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Frame'i tam ekran göster
                cv2.namedWindow('Raspberry Pi Engelli Destek Sistemi - HD Test', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Raspberry Pi Engelli Destek Sistemi - HD Test', 1280, 720)
                cv2.imshow('Raspberry Pi Engelli Destek Sistemi - HD Test', frame)
                
                # Klavye kontrolü
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s') and voice_alert:
                    voice_alert.toggle_sound()
                elif key == ord('t') and tts_engine:
                    threading.Thread(
                        target=lambda: tts_engine.say("Test mesajı") or tts_engine.runAndWait(),
                        daemon=True
                    ).start()
                
                # CPU'yu rahatlatmak için kısa bekleme
                time.sleep(0.033)  # ~30 FPS
        
        except KeyboardInterrupt:
            print("\n🛑 Demo durduruldu")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Kaynakları temizle"""
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        print("✅ Kaynaklar temizlendi")


def main():
    """Ana fonksiyon"""
    print("🖥️ Windows Test Sistemi")
    print("=" * 40)
    
    test_system = WindowsTestSystem()
    
    # Kamera testi
    has_camera = test_system.test_camera()
    
    # Kullanıcı seçenekleri
    print("\n📋 Test Seçenekleri:")
    print("1. Sadece görüntü testi (hızlı)")
    print("2. YOLO ile nesne algılama")
    print("3. Tam sistem testi (YOLO + TTS)")
    
    choice = input("\nSeçiminiz (1-3): ").strip()
    
    if choice == "1":
        test_system.run_demo(with_yolo=False, with_tts=False)
    elif choice == "2":
        test_system.run_demo(with_yolo=True, with_tts=False)
    elif choice == "3":
        test_system.run_demo(with_yolo=True, with_tts=True)
    else:
        print("Varsayılan olarak görüntü testi çalıştırılıyor...")
        test_system.run_demo(with_yolo=False, with_tts=False)


if __name__ == "__main__":
    main()
