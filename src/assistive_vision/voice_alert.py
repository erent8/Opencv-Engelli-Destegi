#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sesli Uyarı Modülü
pyttsx3 kullanarak sesli uyarı ve yönlendirme sistemi
"""

import time
import threading
from typing import List, Dict, Optional
from queue import Queue, Empty
import logging

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    print("⚠️ pyttsx3 bulunamadı. pip install pyttsx3 ile yükleyin.")
    TTS_AVAILABLE = False


class VoiceAlert:
    """
    Sesli uyarı ve yönlendirme sistemi
    Raspberry Pi için optimize edilmiş TTS
    """
    
    def __init__(self, config):
        """
        Sesli uyarı sistemini başlat
        
        Args:
            config: Konfigürasyon nesnesi
        """
        self.config = config
        self.engine = None
        self.is_enabled = True
        self.is_speaking = False
        
        # Uyarı kuyruğu ve threading
        self.alert_queue = Queue()
        self.worker_thread = None
        self.stop_thread = False
        
        # Uyarı throttling için
        self.last_alerts = {}  # nesne_türü: son_uyarı_zamanı
        self.last_direction_alert = 0
        
        # Dual language voice messages (English & Turkish)
        self.language = config.TTS_LANGUAGE if hasattr(config, 'TTS_LANGUAGE') else 'en'
        
        self.messages = {
            'en': {
                # People and animals
                'person': "Person ahead",
                'cat': "Cat ahead",
                'dog': "Dog ahead",
                'horse': "Horse ahead",
                'sheep': "Sheep ahead",
                'cow': "Cow ahead",
                'elephant': "Elephant ahead",
                'bear': "Bear ahead",
                'zebra': "Zebra ahead",
                'giraffe': "Giraffe ahead",
                
                # Vehicles
                'bicycle': "Bicycle ahead",
                'car': "Car ahead",
                'motorcycle': "Motorcycle ahead",
                'airplane': "Airplane ahead",
                'bus': "Bus ahead",
                'train': "Train ahead",
                'truck': "Truck ahead",
                'boat': "Boat ahead",
                
                # Traffic and urban objects
                'traffic_light': "Traffic light ahead",
                'fire_hydrant': "Fire hydrant ahead",
                'stop_sign': "Stop sign ahead",
                'parking_meter': "Parking meter ahead",
                'bench': "Bench ahead",
                
                # Obstacles and furniture
                'chair': "Chair ahead",
                'couch': "Couch ahead",
                'potted_plant': "Plant ahead",
                'bed': "Bed ahead",
                'dining_table': "Table ahead",
                'toilet': "Toilet ahead",
                'tv': "Television ahead",
                
                # Sports equipment
                'sports_ball': "Ball ahead",
                'skateboard': "Skateboard ahead",
                'surfboard': "Surfboard ahead",
                'tennis_racket': "Tennis racket ahead",
                
                # Distance alerts
                'very_close': "Warning! Very close obstacle",
                'close': "Close obstacle",
                'medium': "Obstacle detected",
                
                # Direction alerts
                'turn_left': "Turn left",
                'turn_right': "Turn right",
                'stop': "Stop",
                'clear_ahead': "Path is clear",
                
                # System messages
                'system_ready': "System ready",
                'sound_on': "Sound on",
                'sound_off': "Sound off",
                'multiple_objects': "Multiple obstacles detected"
            },
            'tr': {
                # İnsan ve hayvan uyarıları
                'person': "Önünüzde insan",
                'cat': "Önünüzde kedi",
                'dog': "Önünüzde köpek",
                'horse': "Önünüzde at",
                'sheep': "Önünüzde koyun",
                'cow': "Önünüzde inek",
                'elephant': "Önünüzde fil",
                'bear': "Önünüzde ayı",
                'zebra': "Önünüzde zebra",
                'giraffe': "Önünüzde zürafa",
                
                # Araç uyarıları
                'bicycle': "Önünüzde bisiklet",
                'car': "Önünüzde araba",
                'motorcycle': "Önünüzde motosiklet",
                'airplane': "Önünüzde uçak",
                'bus': "Önünüzde otobüs",
                'train': "Önünüzde tren",
                'truck': "Önünüzde kamyon",
                'boat': "Önünüzde tekne",
                
                # Trafik ve şehir nesneleri
                'traffic_light': "Önünüzde trafik ışığı",
                'fire_hydrant': "Önünüzde yangın musluğu",
                'stop_sign': "Önünüzde dur işareti",
                'parking_meter': "Önünüzde parkometre",
                'bench': "Önünüzde bank",
                
                # Engeller ve mobilyalar
                'chair': "Önünüzde sandalye",
                'couch': "Önünüzde koltuk",
                'potted_plant': "Önünüzde saksı",
                'bed': "Önünüzde yatak",
                'dining_table': "Önünüzde masa",
                'toilet': "Önünüzde tuvalet",
                'tv': "Önünüzde televizyon",
                
                # Spor ekipmanları
                'sports_ball': "Önünüzde top",
                'skateboard': "Önünüzde kaykay",
                'surfboard': "Önünüzde sörf tahtası",
                'tennis_racket': "Önünüzde tenis raketi",
                
                # Mesafe uyarıları
                'very_close': "Dikkat! Çok yakın engel",
                'close': "Yakın engel",
                'medium': "Engel tespit edildi",
                
                # Yön uyarıları
                'turn_left': "Sola dönün",
                'turn_right': "Sağa dönün",
                'stop': "Durun",
                'clear_ahead': "Yol açık",
                
                # Sistem mesajları
                'system_ready': "Sistem hazır",
                'sound_on': "Ses açık",
                'sound_off': "Ses kapalı",
                'multiple_objects': "Birden fazla engel tespit edildi"
            }
        }
        
        self.initialize_tts()
        self.start_worker_thread()
    
    def initialize_tts(self) -> bool:
        """
        TTS motorunu başlat
        
        Returns:
            bool: Başlatma durumu
        """
        if not TTS_AVAILABLE:
            print("❌ TTS kütüphanesi mevcut değil!")
            return False
        
        try:
            print("🔊 TTS motoru başlatılıyor...")
            self.engine = pyttsx3.init()
            
            # TTS ayarları (Raspberry Pi için optimize)
            voices = self.engine.getProperty('voices')
            
            # Select voice based on language setting
            selected_voice = None
            
            if self.language == 'tr':
                # Look for Turkish voice first
                for voice in voices:
                    if 'tr' in voice.id.lower() or 'turkish' in voice.name.lower() or 'türk' in voice.name.lower():
                        selected_voice = voice
                        print(f"🎤 Using Turkish voice: {voice.name}")
                        break
                
                if not selected_voice:
                    print("⚠️ Turkish voice not found, using default voice for Turkish text")
                    selected_voice = voices[0] if voices else None
            
            else:
                # Look for English voice
                for voice in voices:
                    if 'en' in voice.id.lower() or 'english' in voice.name.lower():
                        selected_voice = voice
                        print(f"🎤 Using English voice: {voice.name}")
                        break
                
                if not selected_voice:
                    print("⚠️ English voice not found, using default voice")
                    selected_voice = voices[0] if voices else None
            
            if selected_voice:
                self.engine.setProperty('voice', selected_voice.id)
            
            # Konuşma hızı ve ses seviyesi
            self.engine.setProperty('rate', self.config.TTS_RATE)
            self.engine.setProperty('volume', self.config.TTS_VOLUME)
            
            print("✅ TTS motoru başarıyla başlatıldı")
            return True
            
        except Exception as e:
            print(f"❌ TTS başlatma hatası: {e}")
            return False
    
    def start_worker_thread(self):
        """Sesli uyarı işleme thread'ini başlat"""
        if self.worker_thread and self.worker_thread.is_alive():
            return
        
        self.stop_thread = False
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print("🔧 Sesli uyarı thread'i başlatıldı")
    
    def _worker_loop(self):
        """Sesli uyarı işleme döngüsü"""
        while not self.stop_thread:
            try:
                # Kuyruktan mesaj al (1 saniye timeout)
                alert_data = self.alert_queue.get(timeout=1.0)
                
                if alert_data and self.is_enabled and self.engine:
                    self._speak_text(alert_data['text'], alert_data.get('priority', 1))
                
                self.alert_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                print(f"❌ Sesli uyarı thread hatası: {e}")
    
    def _speak_text(self, text: str, priority: int = 1):
        """
        Metni sesli olarak oku
        
        Args:
            text: Okunacak metin
            priority: Öncelik seviyesi (1=düşük, 3=yüksek)
        """
        if not self.engine or not self.is_enabled:
            return
        
        try:
            # Eğer konuşuyorsa ve düşük öncelikli mesajsa bekle
            if self.is_speaking and priority < 3:
                return
            
            # Yüksek öncelikli mesaj varsa mevcut konuşmayı durdur
            if priority >= 3 and self.is_speaking:
                self.engine.stop()
            
            self.is_speaking = True
            
            if self.config.DEBUG_MODE:
                print(f"🔊 Sesli uyarı: {text}")
            
            # Metni oku
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"❌ TTS hatası: {e}")
        
        finally:
            self.is_speaking = False
    
    def alert_close_object(self, detection: Dict):
        """
        Alert for close object with distance information
        
        Args:
            detection: Detected object (with distance information)
        """
        if not self.is_enabled:
            return
        
        class_name = detection['class_name']
        distance_level = detection.get('distance_level', 'medium')
        urgency = detection.get('urgency', 1)
        distance_meters = detection.get('distance_meters', None)
        
        current_time = time.time()
        
        # Check if this is a continuous alert for tracked object
        track_id = detection.get('track_id', None)
        should_alert = detection.get('should_alert', False)
        should_distance_alert = detection.get('should_distance_alert', False)
        
        # For tracked objects, always allow if marked for alert
        if track_id and not should_alert and not should_distance_alert:
            return
        
        # Legacy throttling for non-tracked objects
        if not track_id:
            last_alert_key = f"{class_name}_{distance_level}"
            if last_alert_key in self.last_alerts:
                time_since_last = current_time - self.last_alerts[last_alert_key]
                min_interval = self.config.ALERT_INTERVAL / max(urgency, 1)
                
                if time_since_last < min_interval:
                    return
            
            self.last_alerts[last_alert_key] = current_time
        
        # Create message with distance information (language-aware)
        lang_messages = self.messages.get(self.language, self.messages['en'])
        base_message = lang_messages.get(class_name, f"{class_name} ahead" if self.language == 'en' else f"Önünüzde {class_name}")
        
        # Add detailed distance information to message (language-aware)
        if distance_meters:
            # Round distance to nearest 0.5 meters for clearer speech
            rounded_distance = round(distance_meters * 2) / 2
            
            if self.language == 'tr':
                # Turkish distance messages
                if distance_meters < 1:
                    distance_desc = f"çok yakın, bir metreden az"
                    message = f"Tehlike! {base_message}, {distance_desc}"
                    urgency = 3
                elif distance_meters < 2:
                    distance_desc = f"çok yakın, {rounded_distance} metre"
                    message = f"Dikkat! {base_message}, {distance_desc}"
                    urgency = 3
                elif distance_meters < 4:
                    distance_desc = f"yakın, {rounded_distance} metre"
                    message = f"Uyarı! {base_message}, {distance_desc}"
                    urgency = 2
                elif distance_meters < 8:
                    distance_desc = f"{rounded_distance} metre uzaklıkta"
                    message = f"{base_message}, {distance_desc}"
                    urgency = 1
                else:
                    distance_desc = f"uzak, {rounded_distance} metre"
                    message = f"{base_message}, {distance_desc}"
                    urgency = 1
            else:
                # English distance messages
                if distance_meters < 1:
                    distance_desc = f"very close, less than one meter"
                    message = f"Danger! {base_message}, {distance_desc}"
                    urgency = 3
                elif distance_meters < 2:
                    distance_desc = f"very close, {rounded_distance} meters"
                    message = f"Warning! {base_message}, {distance_desc}"
                    urgency = 3
                elif distance_meters < 4:
                    distance_desc = f"close, {rounded_distance} meters"
                    message = f"Caution! {base_message}, {distance_desc}"
                    urgency = 2
                elif distance_meters < 8:
                    distance_desc = f"{rounded_distance} meters away"
                    message = f"{base_message}, {distance_desc}"
                    urgency = 1
                else:
                    distance_desc = f"far, {rounded_distance} meters away"
                    message = f"{base_message}, {distance_desc}"
                    urgency = 1
        else:
            # Fallback to distance level
            if distance_level == 'very_close':
                message = f"Warning! {base_message}, very close"
                urgency = 3
            elif distance_level == 'close':
                message = f"Caution! {base_message}"
                urgency = 2
            else:
                message = base_message
                urgency = 1
        
        # Add to queue
        self.alert_queue.put({
            'text': message,
            'priority': urgency,
            'type': 'object_alert',
            'track_id': track_id
        })
        
        if self.config.DEBUG_MODE:
            print(f"🔊 Voice alert: {message}")
    
    def give_direction(self, direction: str):
        """
        Yön tarifi ver
        
        Args:
            direction: Yön ('left', 'right', 'stop', vb.)
        """
        if not self.is_enabled:
            return
        
        current_time = time.time()
        
        # Yön uyarıları için throttling
        if (current_time - self.last_direction_alert) < self.config.DIRECTION_ALERT_INTERVAL:
            return
        
        message_key = f'turn_{direction}' if direction in ['left', 'right'] else direction
        message = self.messages.get(message_key, f"{direction} yönüne gidin")
        
        # Kuyruğa ekle (yüksek öncelik)
        self.alert_queue.put({
            'text': message,
            'priority': 3,
            'type': 'direction_alert'
        })
        
        self.last_direction_alert = current_time
    
    def announce_objects(self, detections: List[Dict]):
        """
        Algılanan nesneleri duyur (throttled)
        
        Args:
            detections: Algılanan nesneler listesi
        """
        if not self.is_enabled or not detections:
            return
        
        current_time = time.time()
        
        # Genel nesne duyurusu için throttling
        if (current_time - self.last_alerts.get('general_announce', 0)) < self.config.GENERAL_ANNOUNCE_INTERVAL:
            return
        
        # Nesne türlerini say
        object_types = {}
        for detection in detections:
            class_name = detection['class_name']
            object_types[class_name] = object_types.get(class_name, 0) + 1
        
        # Mesaj oluştur
        if len(object_types) == 1:
            class_name = list(object_types.keys())[0]
            count = object_types[class_name]
            
            if count == 1:
                message = self.messages.get(class_name, f"Önünüzde {class_name} var")
            else:
                message = f"Önünüzde {count} adet {class_name} var"
        
        elif len(object_types) <= 3:
            # Az sayıda nesne türü varsa hepsini söyle
            object_list = []
            for class_name, count in object_types.items():
                if count == 1:
                    object_list.append(class_name)
                else:
                    object_list.append(f"{count} {class_name}")
            
            message = f"Önünüzde {', '.join(object_list)} var"
        
        else:
            # Çok fazla nesne türü varsa genel mesaj
            total_count = sum(object_types.values())
            message = f"Önünüzde {total_count} farklı nesne tespit edildi"
        
        # Kuyruğa ekle (düşük öncelik)
        self.alert_queue.put({
            'text': message,
            'priority': 1,
            'type': 'general_announce'
        })
        
        self.last_alerts['general_announce'] = current_time
    
    def emergency_alert(self, message: str):
        """
        Emergency alert (highest priority)
        
        Args:
            message: Emergency message
        """
        if not self.is_enabled:
            return
        
        # Emergency message - add to queue immediately
        self.alert_queue.put({
            'text': f"EMERGENCY! {message}",
            'priority': 3,
            'type': 'emergency'
        })
    
    def announce_distance_details(self, detections: List[Dict]):
        """
        Announce detailed distance information for visually impaired users
        
        Args:
            detections: List of detected objects with distance info
        """
        if not self.is_enabled or not detections:
            return
        
        current_time = time.time()
        
        # Throttle detailed distance announcements
        if (current_time - self.last_alerts.get('distance_details', 0)) < 15:
            return
        
        # Find closest object
        closest_obj = min(detections, key=lambda x: x.get('distance_meters', 999))
        distance = closest_obj.get('distance_meters', 0)
        class_name = closest_obj.get('class_name', 'object')
        
        if distance > 0:
            rounded_distance = round(distance * 2) / 2
            
            # Create detailed distance announcement
            if distance < 2:
                message = f"Closest object: {class_name} at {rounded_distance} meters. Very close, be careful."
            elif distance < 5:
                message = f"Closest object: {class_name} at {rounded_distance} meters. Moderate distance."
            else:
                message = f"Closest object: {class_name} at {rounded_distance} meters. Safe distance."
            
            # Add to queue with medium priority
            self.alert_queue.put({
                'text': message,
                'priority': 2,
                'type': 'distance_details'
            })
            
            self.last_alerts['distance_details'] = current_time
            
            if self.config.DEBUG_MODE:
                print(f"🔊 Distance details: {message}")
    
    def system_message(self, message_key: str):
        """
        Sistem mesajı ver
        
        Args:
            message_key: Mesaj anahtarı
        """
        message = self.messages.get(message_key, message_key)
        
        self.alert_queue.put({
            'text': message,
            'priority': 2,
            'type': 'system'
        })
    
    def toggle_sound(self):
        """Sesi aç/kapat"""
        self.is_enabled = not self.is_enabled
        
        if self.is_enabled:
            self.system_message('sound_on')
        else:
            self.system_message('sound_off')
        
        print(f"🔊 Ses durumu: {'AÇIK' if self.is_enabled else 'KAPALI'}")
    
    def set_volume(self, volume: float):
        """
        Ses seviyesini ayarla
        
        Args:
            volume: Ses seviyesi (0.0 - 1.0)
        """
        if self.engine:
            volume = max(0.0, min(1.0, volume))  # 0-1 arası sınırla
            self.engine.setProperty('volume', volume)
            self.config.TTS_VOLUME = volume
            print(f"🔊 Ses seviyesi ayarlandı: {volume:.2f}")
    
    def set_rate(self, rate: int):
        """
        Konuşma hızını ayarla
        
        Args:
            rate: Konuşma hızı (kelime/dakika)
        """
        if self.engine:
            rate = max(50, min(300, rate))  # 50-300 arası sınırla
            self.engine.setProperty('rate', rate)
            self.config.TTS_RATE = rate
            print(f"🗣️ Konuşma hızı ayarlandı: {rate} kelime/dakika")
    
    def clear_queue(self):
        """Uyarı kuyruğunu temizle"""
        while not self.alert_queue.empty():
            try:
                self.alert_queue.get_nowait()
                self.alert_queue.task_done()
            except Empty:
                break
        
        print("🧹 Sesli uyarı kuyruğu temizlendi")
    
    def is_queue_full(self) -> bool:
        """
        Kuyruk dolu mu kontrol et
        
        Returns:
            bool: Kuyruk durumu
        """
        return self.alert_queue.qsize() >= self.config.MAX_ALERT_QUEUE_SIZE
    
    def get_queue_size(self) -> int:
        """
        Kuyruk boyutunu döndür
        
        Returns:
            int: Kuyruktaki mesaj sayısı
        """
        return self.alert_queue.qsize()
    
    def cleanup(self):
        """Kaynakları temizle"""
        print("🧹 Sesli uyarı sistemi kapatılıyor...")
        
        # Thread'i durdur
        self.stop_thread = True
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        
        # Kuyruğu temizle
        self.clear_queue()
        
        # TTS motorunu kapat
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        
        print("✅ Sesli uyarı sistemi kapatıldı")
    
    def test_voice(self):
        """Ses testi yap"""
        if not self.is_enabled:
            print("⚠️ Ses kapalı, test yapılamıyor")
            return
        
        # Dile göre test mesajı
        if self.language == 'tr':
            test_message = "Ses testi. Sistem çalışıyor."
        else:
            test_message = "Voice test. System is working."
            
        self.alert_queue.put({
            'text': test_message,
            'priority': 2,
            'type': 'test'
        })
        
        print("🧪 Ses testi başlatıldı")
    
    def switch_language(self, language: str = None):
        """
        Dili değiştir
        
        Args:
            language: 'en' veya 'tr', None ise toggle
        """
        if language:
            if language in ['en', 'tr']:
                self.language = language
            else:
                print("⚠️ Geçersiz dil. 'en' veya 'tr' kullanın.")
                return
        else:
            # Toggle between languages
            self.language = 'tr' if self.language == 'en' else 'en'
        
        # Reinitialize TTS with new language
        self.initialize_tts()
        
        # Announce language change
        lang_messages = self.messages.get(self.language, self.messages['en'])
        if self.language == 'tr':
            announce_msg = "Dil Türkçe olarak değiştirildi"
        else:
            announce_msg = "Language switched to English"
            
        self.alert_queue.put({
            'text': announce_msg,
            'priority': 2,
            'type': 'language_change'
        })
        
        print(f"🌐 Dil değiştirildi: {self.language.upper()}")
    
    def get_current_language(self) -> str:
        """Mevcut dili döndür"""
        return self.language
