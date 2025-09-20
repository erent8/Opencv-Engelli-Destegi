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
from pathlib import Path
import sys
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Module imports (with error handling)
try:
    from assistive_vision.object_detector import ObjectDetector
    from assistive_vision.distance_checker import DistanceChecker
    from assistive_vision.voice_alert import VoiceAlert
    from assistive_vision.navigation_guide import NavigationGuide
    from assistive_vision.object_tracker import ObjectTracker
    from assistive_vision.detection_logger import DetectionLogger
    from assistive_vision.config import Config
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module import error: {e}")
    print("Running in basic test mode...")
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
        print("\n🎬 Demo mode starting...")
        print("Keyboard controls:")
        print("  'q' - Exit")
        print("  's' - Toggle sound on/off")
        print("  't' - Test voice")
        print("  'l' - Switch language (Turkish/English)")
        print("  'd' - Toggle debug mode")
        print("🔊 Continuous voice alerts enabled - objects will alert every few seconds while visible")
        
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
        
        # Test modules
        if MODULES_AVAILABLE:
            try:
                detector = ObjectDetector(self.config) if with_yolo else None
                distance_checker = DistanceChecker(self.config)
                voice_alert = VoiceAlert(self.config) if with_tts else None
                nav_guide = NavigationGuide(self.config)
                tracker = ObjectTracker(self.config)  # Add object tracker
                logger = DetectionLogger(self.config)  # Add CSV logger
                print("✅ All modules loaded including object tracker and CSV logger")
            except Exception as e:
                print(f"⚠️ Module loading error: {e}")
                detector = None
                distance_checker = None
                voice_alert = None
                nav_guide = None
                tracker = None
                logger = None
        
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
                
                # YOLO detection (if available)
                raw_detections = []
                if detector and yolo_model and frame_count % 10 == 0:  # Every 10 frames
                    try:
                        raw_detections = detector.detect_objects(frame)
                    except Exception as e:
                        print(f"Detection error: {e}")
                
                # Use demo data if no YOLO
                if not raw_detections and frame_count % 30 == 0:
                    raw_detections = self.demo_detections
                
                # Update object tracker with detections
                tracked_detections = []
                if tracker and raw_detections:
                    try:
                        tracked_detections = tracker.update(raw_detections)
                        
                        # Draw tracked objects with stability indicators
                        for detection in tracked_detections:
                            if detector:
                                frame = detector.draw_detections(frame, [detection])
                            
                            # Add tracking info to display
                            track_id = detection.get('track_id', 0)
                            age = detection.get('age', 0)
                            x, y = detection['center']
                            
                            # Show tracking ID and age
                            cv2.putText(frame, f"ID:{track_id} Age:{age:.1f}s", 
                                       (x-30, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                            
                            # Show stability indicator
                            if detection.get('is_stable', False):
                                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)  # Green dot for stable
                            else:
                                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)  # Red dot for unstable
                    
                    except Exception as e:
                        print(f"Tracking error: {e}")
                        tracked_detections = raw_detections
                
                # Use tracked detections for further processing
                detections = tracked_detections if tracked_detections else raw_detections
                
                # Log all detections to CSV
                if logger and detections:
                    logger.log_detections_batch(detections, frame_count, frame.shape[1])
                
                # Distance and navigation analysis
                if detections and MODULES_AVAILABLE:
                    try:
                        # Distance control
                        if distance_checker:
                            close_objects = distance_checker.check_distances(detections, frame.shape)
                            
                            # Continuous alerts for all stable tracked objects
                            if tracker and voice_alert:
                                # Get all stable objects, not just those ready for alerts
                                for detection in detections:
                                    if detection.get('is_stable', False):
                                        # Force continuous alerts for stable objects
                                        detection['should_alert'] = True
                                        detection['should_distance_alert'] = True
                                        
                                        # Check if enough time has passed for this specific object
                                        track_id = detection.get('track_id', 0)
                                        distance = detection.get('distance_meters', 10)
                                        
                                        # Determine alert interval based on distance
                                        if distance < 3:
                                            alert_interval = 3.0  # Very close - every 3 seconds
                                        elif distance < 6:
                                            alert_interval = 6.0  # Close - every 6 seconds
                                        else:
                                            alert_interval = 10.0  # Far - every 10 seconds
                                        
                                        # Check last alert time for this specific object
                                        alert_key = f"track_{track_id}"
                                        last_time = getattr(self, 'last_track_alerts', {}).get(alert_key, 0)
                                        
                                        if (current_time - last_time) >= alert_interval:
                                            # Update last alert time
                                            if not hasattr(self, 'last_track_alerts'):
                                                self.last_track_alerts = {}
                                            self.last_track_alerts[alert_key] = current_time
                                            
                                            # Send alert
                                            threading.Thread(
                                                target=voice_alert.alert_close_object,
                                                args=(detection,),
                                                daemon=True
                                            ).start()
                                            
                                            # Log alert to CSV
                                            if logger:
                                                logger.log_alert(
                                                    detection, 
                                                    'continuous_alert', 
                                                    f"{detection['class_name']} at {distance:.1f}m",
                                                    3 if distance < 3 else 2 if distance < 6 else 1
                                                )
                                            
                                            print(f"🔊 Alert sent for {detection['class_name']} ID:{track_id} at {distance:.1f}m")
                            
                            # Fallback for non-tracked objects
                            elif close_objects and voice_alert and (current_time - last_alert_time) > 5:
                                threading.Thread(
                                    target=voice_alert.alert_close_object,
                                    args=(close_objects[0],),
                                    daemon=True
                                ).start()
                                last_alert_time = current_time
                            
                            # Add detailed distance announcements for visually impaired users
                            if voice_alert and detections:
                                threading.Thread(
                                    target=voice_alert.announce_distance_details,
                                    args=(detections,),
                                    daemon=True
                                ).start()
                        
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
                
                # Show FPS
                fps = frame_count / max(current_time - time.time() + 1, 1)
                cv2.putText(frame, f"FPS: {fps:.1f}", (1000, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show object count and tracking stats
                cv2.putText(frame, f"Objects: {len(detections)}", (1000, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show tracking statistics
                if tracker:
                    stats = tracker.get_tracking_stats()
                    cv2.putText(frame, f"Tracked: {stats['stable_tracks']}/{stats['total_tracks']}", 
                               (1000, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show distance info for each object
                for i, detection in enumerate(detections[:3]):  # Show first 3 objects
                    distance = detection.get('distance_meters', 0)
                    class_name = detection.get('class_name', 'unknown')
                    track_id = detection.get('track_id', 'N/A')
                    is_stable = detection.get('is_stable', False)
                    
                    # Show stability status
                    stability_text = "STABLE" if is_stable else "UNSTABLE"
                    color = (0, 255, 0) if is_stable else (0, 0, 255)
                    
                    info_text = f"{class_name} ID:{track_id} - {distance:.1f}m [{stability_text}]"
                    cv2.putText(frame, info_text, (20, 100 + i*25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Show alert status and logging info
                if hasattr(self, 'last_track_alerts') and self.last_track_alerts:
                    alert_count = len(self.last_track_alerts)
                    cv2.putText(frame, f"Active Alerts: {alert_count}", (20, 200),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                # Show logging status and language
                if logger:
                    stats = logger.get_session_stats()
                    cv2.putText(frame, f"Logged: {stats['total_detections']} detections", (20, 230),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    cv2.putText(frame, f"Session: {stats['duration_formatted']}", (20, 260),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Show current language
                if voice_alert:
                    current_lang = voice_alert.get_current_language().upper()
                    cv2.putText(frame, f"Language: {current_lang}", (20, 290),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
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
                elif key == ord('t') and voice_alert:
                    # Test voice in current language
                    threading.Thread(
                        target=voice_alert.test_voice,
                        daemon=True
                    ).start()
                elif key == ord('l') and voice_alert:
                    # Switch language
                    threading.Thread(
                        target=voice_alert.switch_language,
                        daemon=True
                    ).start()
                
                # CPU'yu rahatlatmak için kısa bekleme
                time.sleep(0.033)  # ~30 FPS
        
        except KeyboardInterrupt:
            print("\n🛑 Demo durduruldu")
        
        finally:
            # Cleanup logger first to generate summary
            if 'logger' in locals() and logger:
                logger.cleanup()
            
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
