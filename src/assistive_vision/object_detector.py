#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nesne Algılama Modülü
YOLOv8 kullanarak gerçek zamanlı nesne algılama
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import time

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    print("⚠️ Ultralytics YOLOv8 bulunamadı. pip install ultralytics ile yükleyin.")
    YOLO_AVAILABLE = False


class ObjectDetector:
    """
    YOLOv8 tabanlı nesne algılama sınıfı
    Raspberry Pi için optimize edilmiş
    """
    
    def __init__(self, config):
        """
        Nesne algılayıcıyı başlat
        
        Args:
            config: Konfigürasyon nesnesi
        """
        self.config = config
        self.model = None
        self.last_detection_time = 0
        self.detection_cache = []
        
        # Expanded target object classes (COCO dataset)
        self.target_classes = {
            # People and animals
            0: 'person',        # person
            15: 'cat',          # cat
            16: 'dog',          # dog
            17: 'horse',        # horse
            18: 'sheep',        # sheep
            19: 'cow',          # cow
            20: 'elephant',     # elephant
            21: 'bear',         # bear
            22: 'zebra',        # zebra
            23: 'giraffe',      # giraffe
            
            # Vehicles
            1: 'bicycle',       # bicycle
            2: 'car',           # car
            3: 'motorcycle',    # motorcycle
            4: 'airplane',      # airplane
            5: 'bus',           # bus
            6: 'train',         # train
            7: 'truck',         # truck
            8: 'boat',          # boat
            
            # Traffic and urban objects
            9: 'traffic_light', # traffic light
            10: 'fire_hydrant', # fire hydrant
            11: 'stop_sign',    # stop sign
            12: 'parking_meter',# parking meter
            13: 'bench',        # bench
            
            # Obstacles and furniture
            56: 'chair',        # chair
            57: 'couch',        # couch
            58: 'potted_plant', # potted plant
            59: 'bed',          # bed
            60: 'dining_table', # dining table
            61: 'toilet',       # toilet
            62: 'tv',           # tv
            
            # Sports equipment (potential obstacles)
            32: 'sports_ball',  # sports ball
            37: 'skateboard',   # skateboard
            38: 'surfboard',    # surfboard
            39: 'tennis_racket',# tennis racket
            
            # Construction and barriers
            # Note: These are approximations as COCO doesn't have specific construction classes
        }
        
        self.initialize_model()
    
    def initialize_model(self) -> bool:
        """
        YOLOv8 modelini yükle
        
        Returns:
            bool: Model yükleme durumu
        """
        if not YOLO_AVAILABLE:
            print("❌ YOLOv8 kütüphanesi mevcut değil!")
            return False
        
        try:
            print("🔄 YOLOv8 modeli yükleniyor...")
            
            # Hafif model kullan (Raspberry Pi için)
            model_path = self.config.YOLO_MODEL_PATH
            self.model = YOLO(model_path)
            
            # Model ayarları
            self.model.overrides['verbose'] = False  # Ayrıntılı çıktıyı kapat
            
            print(f"✅ YOLOv8 modeli yüklendi: {model_path}")
            return True
            
        except Exception as e:
            print(f"❌ Model yükleme hatası: {e}")
            return False
    
    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """
        Frame'de nesne algılama yap
        
        Args:
            frame: İşlenecek görüntü frame'i
            
        Returns:
            List[Dict]: Algılanan nesneler listesi
        """
        if not self.model:
            return []
        
        current_time = time.time()
        
        # Performans optimizasyonu: Belirli aralıklarla algılama yap
        if (current_time - self.last_detection_time) < self.config.DETECTION_INTERVAL:
            return self.detection_cache
        
        try:
            # YOLOv8 ile tahmin yap
            results = self.model(
                frame,
                conf=self.config.CONFIDENCE_THRESHOLD,
                iou=self.config.IOU_THRESHOLD,
                verbose=False,
                device='cpu'  # Raspberry Pi için CPU kullan
            )
            
            detections = []
            
            # Sonuçları işle
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None:
                    boxes = result.boxes.cpu().numpy()
                    
                    for box in boxes:
                        # Bounding box koordinatları
                        x1, y1, x2, y2 = box.xyxy[0].astype(int)
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        
                        # Sadece ilgilenilen sınıfları al
                        if class_id in self.target_classes:
                            detection = {
                                'class_id': class_id,
                                'class_name': self.target_classes[class_id],
                                'confidence': confidence,
                                'bbox': (x1, y1, x2, y2),
                                'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                                'width': x2 - x1,
                                'height': y2 - y1,
                                'area': (x2 - x1) * (y2 - y1)
                            }
                            detections.append(detection)
            
            # Cache'i güncelle
            self.detection_cache = detections
            self.last_detection_time = current_time
            
            if self.config.DEBUG_MODE and detections:
                print(f"🎯 {len(detections)} nesne algılandı")
            
            return detections
            
        except Exception as e:
            print(f"❌ Algılama hatası: {e}")
            return []
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Algılanan nesneleri frame üzerine çiz
        
        Args:
            frame: Görüntü frame'i
            detections: Algılanan nesneler
            
        Returns:
            np.ndarray: Çizimli frame
        """
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # Nesne türüne göre renk seç
            color = self.get_class_color(detection['class_id'])
            
            # Bounding box çiz
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Label oluştur
            label = f"{class_name} {confidence:.2f}"
            
            # Label arka planı
            (label_width, label_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            cv2.rectangle(
                frame,
                (x1, y1 - label_height - 10),
                (x1 + label_width, y1),
                color,
                -1
            )
            
            # Label metni
            cv2.putText(
                frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            
            # Merkez noktası çiz
            center_x, center_y = detection['center']
            cv2.circle(frame, (center_x, center_y), 5, color, -1)
        
        return frame
    
    def get_class_color(self, class_id: int) -> Tuple[int, int, int]:
        """
        Nesne sınıfına göre renk döndür
        
        Args:
            class_id: Nesne sınıf ID'si
            
        Returns:
            Tuple[int, int, int]: BGR renk değeri
        """
        colors = {
            0: (0, 255, 0),     # insan - yeşil
            1: (255, 0, 0),     # bisiklet - mavi
            2: (0, 0, 255),     # araba - kırmızı
            3: (255, 255, 0),   # motosiklet - cyan
            5: (0, 255, 255),   # otobüs - sarı
            7: (255, 0, 255),   # kamyon - magenta
            9: (128, 0, 128),   # trafik lambası - mor
            11: (255, 128, 0),  # dur işareti - turuncu
            15: (0, 128, 255),  # kedi - açık mavi
            16: (128, 255, 0),  # köpek - açık yeşil
        }
        
        return colors.get(class_id, (128, 128, 128))  # Varsayılan gri
    
    def filter_detections_by_size(self, detections: List[Dict], 
                                 min_area: int = None) -> List[Dict]:
        """
        Algılamaları boyuta göre filtrele
        
        Args:
            detections: Algılanan nesneler
            min_area: Minimum alan (piksel²)
            
        Returns:
            List[Dict]: Filtrelenmiş algılamalar
        """
        if min_area is None:
            min_area = self.config.MIN_DETECTION_AREA
        
        filtered = []
        for detection in detections:
            if detection['area'] >= min_area:
                filtered.append(detection)
        
        return filtered
    
    def get_detection_statistics(self, detections: List[Dict]) -> Dict:
        """
        Algılama istatistiklerini hesapla
        
        Args:
            detections: Algılanan nesneler
            
        Returns:
            Dict: İstatistik bilgileri
        """
        if not detections:
            return {
                'total_count': 0,
                'class_counts': {},
                'avg_confidence': 0.0,
                'largest_object': None
            }
        
        class_counts = {}
        confidences = []
        largest_area = 0
        largest_object = None
        
        for detection in detections:
            class_name = detection['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            confidences.append(detection['confidence'])
            
            if detection['area'] > largest_area:
                largest_area = detection['area']
                largest_object = detection
        
        return {
            'total_count': len(detections),
            'class_counts': class_counts,
            'avg_confidence': sum(confidences) / len(confidences),
            'largest_object': largest_object
        }
    
    def is_model_loaded(self) -> bool:
        """
        Model yüklü mü kontrol et
        
        Returns:
            bool: Model durumu
        """
        return self.model is not None
    
    def get_supported_classes(self) -> Dict[int, str]:
        """
        Desteklenen nesne sınıflarını döndür
        
        Returns:
            Dict[int, str]: Sınıf ID ve isimleri
        """
        return self.target_classes.copy()
