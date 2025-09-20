#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mesafe Kontrolü Modülü
Algılanan nesnelerin yakınlığını kontrol eder
"""

import numpy as np
from typing import List, Dict, Tuple
import math


class DistanceChecker:
    """
    Nesne mesafe kontrolü ve yaklaşma algısı sınıfı
    Bounding box boyutuna göre yakınlık hesaplar
    """
    
    def __init__(self, config):
        """
        Mesafe kontrolcüsünü başlat
        
        Args:
            config: Konfigürasyon nesnesi
        """
        self.config = config
        
        # Critical distance thresholds by object type (based on bounding box area)
        self.distance_thresholds = {
            'person': {
                'very_close': 0.15,    # Very close (15% of frame)
                'close': 0.08,         # Close (8% of frame)
                'medium': 0.04         # Medium distance (4% of frame)
            },
            'car': {
                'very_close': 0.25,    # Larger threshold for vehicles
                'close': 0.15,
                'medium': 0.08
            },
            'bicycle': {
                'very_close': 0.12,
                'close': 0.06,
                'medium': 0.03
            },
            'motorcycle': {
                'very_close': 0.12,
                'close': 0.06,
                'medium': 0.03
            },
            'bus': {
                'very_close': 0.35,    # Larger threshold for big vehicles
                'close': 0.25,
                'medium': 0.15
            },
            'truck': {
                'very_close': 0.35,
                'close': 0.25,
                'medium': 0.15
            },
            'default': {
                'very_close': 0.12,
                'close': 0.06,
                'medium': 0.03
            }
        }
    
    def check_distances(self, detections: List[Dict], frame_shape: Tuple[int, int, int]) -> List[Dict]:
        """
        Algılanan nesnelerin mesafelerini kontrol et
        
        Args:
            detections: Algılanan nesneler
            frame_shape: Frame boyutları (height, width, channels)
            
        Returns:
            List[Dict]: Yakın nesneler listesi
        """
        if not detections:
            return []
        
        height, width = frame_shape[:2]
        frame_area = height * width
        close_objects = []
        
        for detection in detections:
            distance_info = self.calculate_distance_info(detection, frame_area)
            
            # Yakın nesne kontrolü
            if distance_info['is_close']:
                close_object = detection.copy()
                close_object.update(distance_info)
                close_objects.append(close_object)
        
        # Yakınlık derecesine göre sırala (en yakın önce)
        close_objects.sort(key=lambda x: x['relative_size'], reverse=True)
        
        return close_objects
    
    def calculate_distance_info(self, detection: Dict, frame_area: int) -> Dict:
        """
        Bir nesne için mesafe bilgilerini hesapla
        
        Args:
            detection: Algılanan nesne
            frame_area: Frame toplam alanı
            
        Returns:
            Dict: Mesafe bilgileri
        """
        class_name = detection['class_name']
        object_area = detection['area']
        
        # Nesne alanının frame alanına oranı
        relative_size = object_area / frame_area
        
        # Nesne türüne göre eşik değerleri al
        thresholds = self.distance_thresholds.get(class_name, 
                                                 self.distance_thresholds['default'])
        
        # Mesafe seviyesini belirle
        distance_level = 'far'
        is_close = False
        urgency = 0
        
        if relative_size >= thresholds['very_close']:
            distance_level = 'very_close'
            is_close = True
            urgency = 3
        elif relative_size >= thresholds['close']:
            distance_level = 'close'
            is_close = True
            urgency = 2
        elif relative_size >= thresholds['medium']:
            distance_level = 'medium'
            is_close = True
            urgency = 1
        
        return {
            'relative_size': relative_size,
            'distance_level': distance_level,
            'is_close': is_close,
            'urgency': urgency,
            'size_percentage': relative_size * 100
        }
    
    def get_closest_object(self, detections: List[Dict], frame_shape: Tuple[int, int, int]) -> Dict:
        """
        En yakın nesneyi bul
        
        Args:
            detections: Algılanan nesneler
            frame_shape: Frame boyutları
            
        Returns:
            Dict: En yakın nesne (yoksa None)
        """
        close_objects = self.check_distances(detections, frame_shape)
        
        if close_objects:
            return close_objects[0]  # En yakın (en büyük relative_size)
        
        return None
    
    def check_collision_risk(self, detections: List[Dict], frame_shape: Tuple[int, int, int]) -> Dict:
        """
        Çarpışma riski analizi yap
        
        Args:
            detections: Algılanan nesneler
            frame_shape: Frame boyutları
            
        Returns:
            Dict: Risk analizi sonuçları
        """
        height, width = frame_shape[:2]
        frame_area = height * width
        
        # Risk kategorileri
        high_risk_objects = []
        medium_risk_objects = []
        moving_objects = []  # Gelecekte hareket algısı eklenebilir
        
        for detection in detections:
            distance_info = self.calculate_distance_info(detection, frame_area)
            
            if distance_info['urgency'] >= 3:
                high_risk_objects.append(detection)
            elif distance_info['urgency'] >= 2:
                medium_risk_objects.append(detection)
        
        # Genel risk seviyesi
        overall_risk = 'low'
        if high_risk_objects:
            overall_risk = 'high'
        elif medium_risk_objects:
            overall_risk = 'medium'
        
        return {
            'overall_risk': overall_risk,
            'high_risk_count': len(high_risk_objects),
            'medium_risk_count': len(medium_risk_objects),
            'high_risk_objects': high_risk_objects,
            'medium_risk_objects': medium_risk_objects,
            'total_objects': len(detections)
        }
    
    def calculate_object_velocity(self, current_detection: Dict, 
                                previous_detection: Dict, 
                                time_delta: float) -> Dict:
        """
        Nesne hızını hesapla (gelecekte kullanım için)
        
        Args:
            current_detection: Mevcut algılama
            previous_detection: Önceki algılama
            time_delta: Zaman farkı (saniye)
            
        Returns:
            Dict: Hız bilgileri
        """
        if time_delta <= 0:
            return {'velocity': 0, 'direction': None, 'approaching': False}
        
        # Merkez noktaları arasındaki mesafe
        curr_center = current_detection['center']
        prev_center = previous_detection['center']
        
        # Piksel cinsinden hareket
        dx = curr_center[0] - prev_center[0]
        dy = curr_center[1] - prev_center[1]
        
        # Hız (piksel/saniye)
        velocity = math.sqrt(dx*dx + dy*dy) / time_delta
        
        # Yön açısı
        direction = math.atan2(dy, dx) if velocity > 0 else None
        
        # Yaklaşma kontrolü (nesne büyüyor mu?)
        curr_area = current_detection['area']
        prev_area = previous_detection['area']
        
        area_change_rate = (curr_area - prev_area) / time_delta
        approaching = area_change_rate > 0
        
        return {
            'velocity': velocity,
            'direction': direction,
            'approaching': approaching,
            'area_change_rate': area_change_rate,
            'movement': {
                'dx': dx,
                'dy': dy
            }
        }
    
    def get_safe_zones(self, detections: List[Dict], 
                      frame_shape: Tuple[int, int, int]) -> Dict:
        """
        Güvenli alanları belirle
        
        Args:
            detections: Algılanan nesneler
            frame_shape: Frame boyutları
            
        Returns:
            Dict: Güvenli alan bilgileri
        """
        height, width = frame_shape[:2]
        
        # Frame'i 3 bölgeye ayır
        left_zone = (0, width // 3)
        center_zone = (width // 3, 2 * width // 3)
        right_zone = (2 * width // 3, width)
        
        zones = {
            'left': {'safe': True, 'object_count': 0, 'risk_level': 'low'},
            'center': {'safe': True, 'object_count': 0, 'risk_level': 'low'},
            'right': {'safe': True, 'object_count': 0, 'risk_level': 'low'}
        }
        
        # Her nesne için hangi bölgede olduğunu kontrol et
        for detection in detections:
            center_x = detection['center'][0]
            distance_info = self.calculate_distance_info(detection, height * width)
            
            # Hangi bölgede
            zone = None
            if center_x < left_zone[1]:
                zone = 'left'
            elif center_x < center_zone[1]:
                zone = 'center'
            else:
                zone = 'right'
            
            if zone:
                zones[zone]['object_count'] += 1
                
                # Risk seviyesini güncelle
                if distance_info['urgency'] >= 3:
                    zones[zone]['safe'] = False
                    zones[zone]['risk_level'] = 'high'
                elif distance_info['urgency'] >= 2:
                    if zones[zone]['risk_level'] != 'high':
                        zones[zone]['risk_level'] = 'medium'
                elif distance_info['urgency'] >= 1:
                    if zones[zone]['risk_level'] == 'low':
                        zones[zone]['risk_level'] = 'low-medium'
        
        return zones
    
    def should_alert(self, detection: Dict, frame_area: int, 
                    last_alert_time: float = 0, 
                    min_alert_interval: float = 2.0) -> bool:
        """
        Uyarı verilmeli mi kontrol et
        
        Args:
            detection: Algılanan nesne
            frame_area: Frame alanı
            last_alert_time: Son uyarı zamanı
            min_alert_interval: Minimum uyarı aralığı (saniye)
            
        Returns:
            bool: Uyarı verilmeli mi
        """
        import time
        
        distance_info = self.calculate_distance_info(detection, frame_area)
        current_time = time.time()
        
        # Çok yakın nesneler için sürekli uyarı
        if distance_info['urgency'] >= 3:
            return (current_time - last_alert_time) >= (min_alert_interval / 2)
        
        # Yakın nesneler için normal uyarı
        elif distance_info['urgency'] >= 2:
            return (current_time - last_alert_time) >= min_alert_interval
        
        # Orta mesafe nesneler için seyrek uyarı
        elif distance_info['urgency'] >= 1:
            return (current_time - last_alert_time) >= (min_alert_interval * 2)
        
        return False
