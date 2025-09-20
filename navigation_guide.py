#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Navigasyon Rehberi Modülü
Görüntüyü 3 bölgeye ayırarak yönlendirme analizi yapar
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import cv2


class NavigationGuide:
    """
    3 bölgeli navigasyon analizi ve yönlendirme sistemi
    Sol, orta, sağ bölgelerde engel analizi yapar
    """
    
    def __init__(self, config):
        """
        Navigasyon rehberini başlat
        
        Args:
            config: Konfigürasyon nesnesi
        """
        self.config = config
        
        # Bölge ağırlıkları (orta bölge daha kritik)
        self.zone_weights = {
            'left': 0.7,
            'center': 1.0,
            'right': 0.7
        }
        
        # Engel yoğunluk eşikleri
        self.density_thresholds = {
            'low': 0.1,      # Frame alanının %10'u
            'medium': 0.2,   # Frame alanının %20'si
            'high': 0.4      # Frame alanının %40'ı
        }
    
    def analyze_regions(self, detections: List[Dict], 
                       frame_shape: Tuple[int, int, int]) -> Dict:
        """
        3 bölgeli navigasyon analizi yap
        
        Args:
            detections: Algılanan nesneler
            frame_shape: Frame boyutları (height, width, channels)
            
        Returns:
            Dict: Navigasyon analiz sonuçları
        """
        if not detections:
            return self._get_empty_analysis(frame_shape)
        
        height, width = frame_shape[:2]
        
        # Bölge sınırlarını hesapla
        zones = self._calculate_zone_boundaries(width, height)
        
        # Her bölge için analiz yap
        zone_analysis = {}
        for zone_name, zone_bounds in zones.items():
            zone_analysis[zone_name] = self._analyze_zone(
                detections, zone_bounds, frame_shape
            )
        
        # Genel navigasyon kararı ver
        navigation_decision = self._make_navigation_decision(zone_analysis)
        
        return {
            'zones': zone_analysis,
            'center_blocked': zone_analysis['center']['blocked'],
            'recommended_direction': navigation_decision['direction'],
            'confidence': navigation_decision['confidence'],
            'safe_zones': navigation_decision['safe_zones'],
            'risk_level': navigation_decision['risk_level'],
            'total_objects': len(detections)
        }
    
    def _calculate_zone_boundaries(self, width: int, height: int) -> Dict:
        """
        Bölge sınırlarını hesapla
        
        Args:
            width: Frame genişliği
            height: Frame yüksekliği
            
        Returns:
            Dict: Bölge sınırları
        """
        # Esnek bölge ayırma (orta bölge biraz daha geniş)
        left_boundary = int(width * 0.33)
        right_boundary = int(width * 0.67)
        
        return {
            'left': {
                'x_min': 0,
                'x_max': left_boundary,
                'y_min': 0,
                'y_max': height,
                'center_x': left_boundary // 2
            },
            'center': {
                'x_min': left_boundary,
                'x_max': right_boundary,
                'y_min': 0,
                'y_max': height,
                'center_x': (left_boundary + right_boundary) // 2
            },
            'right': {
                'x_min': right_boundary,
                'x_max': width,
                'y_min': 0,
                'y_max': height,
                'center_x': (right_boundary + width) // 2
            }
        }
    
    def _analyze_zone(self, detections: List[Dict], zone_bounds: Dict, 
                     frame_shape: Tuple[int, int, int]) -> Dict:
        """
        Tek bir bölgeyi analiz et
        
        Args:
            detections: Algılanan nesneler
            zone_bounds: Bölge sınırları
            frame_shape: Frame boyutları
            
        Returns:
            Dict: Bölge analiz sonuçları
        """
        zone_objects = []
        total_area = 0
        risk_scores = []
        
        # Bölge alanını hesapla
        zone_area = (zone_bounds['x_max'] - zone_bounds['x_min']) * \
                   (zone_bounds['y_max'] - zone_bounds['y_min'])
        
        # Bu bölgedeki nesneleri bul
        for detection in detections:
            if self._is_object_in_zone(detection, zone_bounds):
                zone_objects.append(detection)
                total_area += detection['area']
                
                # Risk skoru hesapla (mesafe bilgisi varsa)
                if 'urgency' in detection:
                    risk_scores.append(detection['urgency'])
                else:
                    # Nesne boyutuna göre risk skoru
                    relative_size = detection['area'] / (frame_shape[0] * frame_shape[1])
                    if relative_size > 0.15:
                        risk_scores.append(3)
                    elif relative_size > 0.08:
                        risk_scores.append(2)
                    else:
                        risk_scores.append(1)
        
        # Yoğunluk hesapla
        density = total_area / zone_area if zone_area > 0 else 0
        
        # Bölge durumunu belirle
        blocked = self._is_zone_blocked(zone_objects, density, risk_scores)
        
        # Risk seviyesi
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        if avg_risk >= 2.5 or density > self.density_thresholds['high']:
            risk_level = 'high'
        elif avg_risk >= 1.5 or density > self.density_thresholds['medium']:
            risk_level = 'medium'
        elif avg_risk >= 0.5 or density > self.density_thresholds['low']:
            risk_level = 'low'
        else:
            risk_level = 'safe'
        
        return {
            'object_count': len(zone_objects),
            'objects': zone_objects,
            'total_area': total_area,
            'density': density,
            'blocked': blocked,
            'risk_level': risk_level,
            'avg_risk_score': avg_risk,
            'passable': not blocked and risk_level in ['safe', 'low']
        }
    
    def _is_object_in_zone(self, detection: Dict, zone_bounds: Dict) -> bool:
        """
        Nesne belirtilen bölgede mi kontrol et
        
        Args:
            detection: Algılanan nesne
            zone_bounds: Bölge sınırları
            
        Returns:
            bool: Nesne bölgede mi
        """
        center_x, center_y = detection['center']
        x1, y1, x2, y2 = detection['bbox']
        
        # Nesne merkezinin bölgede olması yeterli
        if (zone_bounds['x_min'] <= center_x <= zone_bounds['x_max'] and
            zone_bounds['y_min'] <= center_y <= zone_bounds['y_max']):
            return True
        
        # Alternatif: Nesne bounding box'ının bölge ile kesişimi
        overlap_x = max(0, min(x2, zone_bounds['x_max']) - max(x1, zone_bounds['x_min']))
        overlap_y = max(0, min(y2, zone_bounds['y_max']) - max(y1, zone_bounds['y_min']))
        overlap_area = overlap_x * overlap_y
        
        # Nesne alanının %50'sinden fazlası bölgede ise bölgeye ait
        object_area = (x2 - x1) * (y2 - y1)
        return (overlap_area / object_area) > 0.5 if object_area > 0 else False
    
    def _is_zone_blocked(self, zone_objects: List[Dict], 
                        density: float, risk_scores: List[int]) -> bool:
        """
        Bölge engelli mi kontrol et
        
        Args:
            zone_objects: Bölgedeki nesneler
            density: Yoğunluk oranı
            risk_scores: Risk skorları
            
        Returns:
            bool: Bölge engelli mi
        """
        if not zone_objects:
            return False
        
        # Yüksek yoğunluk = engelli
        if density > self.density_thresholds['high']:
            return True
        
        # Yüksek risk nesnesi varsa engelli
        if risk_scores and max(risk_scores) >= 3:
            return True
        
        # Çok sayıda nesne varsa engelli
        if len(zone_objects) >= self.config.MAX_OBJECTS_PER_ZONE:
            return True
        
        # Orta yoğunluk + orta risk = engelli
        if (density > self.density_thresholds['medium'] and
            risk_scores and sum(risk_scores) / len(risk_scores) >= 2):
            return True
        
        return False
    
    def _make_navigation_decision(self, zone_analysis: Dict) -> Dict:
        """
        Navigasyon kararı ver
        
        Args:
            zone_analysis: Bölge analiz sonuçları
            
        Returns:
            Dict: Navigasyon kararı
        """
        left_zone = zone_analysis['left']
        center_zone = zone_analysis['center']
        right_zone = zone_analysis['right']
        
        # Güvenli bölgeleri belirle
        safe_zones = []
        if left_zone['passable']:
            safe_zones.append('left')
        if center_zone['passable']:
            safe_zones.append('center')
        if right_zone['passable']:
            safe_zones.append('right')
        
        # Genel risk seviyesi
        risk_levels = [zone['risk_level'] for zone in zone_analysis.values()]
        if 'high' in risk_levels:
            overall_risk = 'high'
        elif 'medium' in risk_levels:
            overall_risk = 'medium'
        elif 'low' in risk_levels:
            overall_risk = 'low'
        else:
            overall_risk = 'safe'
        
        # Yön kararı
        direction = None
        confidence = 0.0
        
        # Orta bölge açık ise ileri git
        if center_zone['passable']:
            direction = 'forward'
            confidence = 0.9
        
        # Orta bölge kapalı ise alternatif yön bul
        elif center_zone['blocked']:
            left_score = self._calculate_zone_score(left_zone)
            right_score = self._calculate_zone_score(right_zone)
            
            if left_score > right_score and left_zone['passable']:
                direction = 'left'
                confidence = min(0.8, left_score)
            elif right_score > left_score and right_zone['passable']:
                direction = 'right'
                confidence = min(0.8, right_score)
            elif left_zone['passable']:
                direction = 'left'
                confidence = 0.6
            elif right_zone['passable']:
                direction = 'right'
                confidence = 0.6
            else:
                # Hiçbir yön güvenli değil
                direction = 'stop'
                confidence = 0.9
        
        return {
            'direction': direction,
            'confidence': confidence,
            'safe_zones': safe_zones,
            'risk_level': overall_risk
        }
    
    def _calculate_zone_score(self, zone_data: Dict) -> float:
        """
        Bölge skoru hesapla (yüksek = daha güvenli)
        
        Args:
            zone_data: Bölge analiz verileri
            
        Returns:
            float: Bölge skoru (0.0-1.0)
        """
        if zone_data['blocked']:
            return 0.0
        
        # Temel skor
        base_score = 1.0
        
        # Risk seviyesine göre azalt
        risk_penalties = {
            'safe': 0.0,
            'low': 0.1,
            'medium': 0.3,
            'high': 0.6
        }
        
        base_score -= risk_penalties.get(zone_data['risk_level'], 0.5)
        
        # Nesne sayısına göre azalt
        object_penalty = min(0.2, zone_data['object_count'] * 0.05)
        base_score -= object_penalty
        
        # Yoğunluğa göre azalt
        density_penalty = min(0.3, zone_data['density'] * 0.5)
        base_score -= density_penalty
        
        return max(0.0, base_score)
    
    def _get_empty_analysis(self, frame_shape: Tuple[int, int, int]) -> Dict:
        """
        Nesne olmadığında boş analiz döndür
        
        Args:
            frame_shape: Frame boyutları
            
        Returns:
            Dict: Boş analiz sonucu
        """
        empty_zone = {
            'object_count': 0,
            'objects': [],
            'total_area': 0,
            'density': 0.0,
            'blocked': False,
            'risk_level': 'safe',
            'avg_risk_score': 0.0,
            'passable': True
        }
        
        return {
            'zones': {
                'left': empty_zone.copy(),
                'center': empty_zone.copy(),
                'right': empty_zone.copy()
            },
            'center_blocked': False,
            'recommended_direction': 'forward',
            'confidence': 1.0,
            'safe_zones': ['left', 'center', 'right'],
            'risk_level': 'safe',
            'total_objects': 0
        }
    
    def visualize_zones(self, frame: np.ndarray, analysis: Dict) -> np.ndarray:
        """
        Bölgeleri görselleştir (debug için)
        
        Args:
            frame: Görüntü frame'i
            analysis: Navigasyon analizi
            
        Returns:
            np.ndarray: Görselleştirilmiş frame
        """
        height, width = frame.shape[:2]
        zones = self._calculate_zone_boundaries(width, height)
        
        # Bölge çizgileri
        left_line = zones['center']['x_min']
        right_line = zones['center']['x_max']
        
        cv2.line(frame, (left_line, 0), (left_line, height), (255, 255, 0), 2)
        cv2.line(frame, (right_line, 0), (right_line, height), (255, 255, 0), 2)
        
        # Bölge etiketleri ve durumları
        zone_colors = {
            'safe': (0, 255, 0),      # Yeşil
            'low': (0, 255, 255),     # Sarı
            'medium': (0, 165, 255),  # Turuncu
            'high': (0, 0, 255)       # Kırmızı
        }
        
        for i, (zone_name, zone_data) in enumerate(analysis['zones'].items()):
            # Bölge merkezi
            if zone_name == 'left':
                center_x = zones['left']['center_x']
            elif zone_name == 'center':
                center_x = zones['center']['center_x']
            else:
                center_x = zones['right']['center_x']
            
            center_y = 50
            
            # Risk seviyesine göre renk
            color = zone_colors.get(zone_data['risk_level'], (128, 128, 128))
            
            # Bölge durumu metni
            status = "❌" if zone_data['blocked'] else "✅"
            text = f"{zone_name.upper()}: {status}"
            
            cv2.putText(frame, text, (center_x - 40, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Nesne sayısı
            count_text = f"Obj: {zone_data['object_count']}"
            cv2.putText(frame, count_text, (center_x - 30, center_y + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Önerilen yön
        direction = analysis['recommended_direction']
        if direction:
            direction_text = f"Yön: {direction.upper()}"
            cv2.putText(frame, direction_text, (10, height - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
    
    def get_path_recommendation(self, analysis: Dict) -> Dict:
        """
        Detaylı yol önerisi al
        
        Args:
            analysis: Navigasyon analizi
            
        Returns:
            Dict: Yol önerisi detayları
        """
        direction = analysis['recommended_direction']
        confidence = analysis['confidence']
        safe_zones = analysis['safe_zones']
        
        # Önerilen hareket
        if direction == 'forward':
            action = "İleri devam edin"
            urgency = "normal"
        elif direction in ['left', 'right']:
            action = f"{'Sola' if direction == 'left' else 'Sağa'} dönün"
            urgency = "medium"
        elif direction == 'stop':
            action = "Durun ve bekleyin"
            urgency = "high"
        else:
            action = "Dikkatli ilerleyin"
            urgency = "low"
        
        return {
            'action': action,
            'direction': direction,
            'confidence': confidence,
            'urgency': urgency,
            'safe_zone_count': len(safe_zones),
            'alternative_paths': [zone for zone in safe_zones if zone != 'center']
        }
