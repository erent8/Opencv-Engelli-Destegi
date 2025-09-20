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
        
        # English voice messages
        self.messages = {
            # Object alerts
            'person': "Person ahead",
            'car': "Car ahead", 
            'bicycle': "Bicycle ahead",
            'motorcycle': "Motorcycle ahead",
            'bus': "Bus ahead",
            'truck': "Truck ahead",
            'traffic_light': "Traffic light ahead",
            'stop_sign': "Stop sign ahead",
            'cat': "Cat ahead",
            'dog': "Dog ahead",
            
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
            
            # Use English voice if available, otherwise default
            english_voice = None
            for voice in voices:
                if 'en' in voice.id.lower() or 'english' in voice.name.lower():
                    english_voice = voice
                    break
            
            if english_voice:
                self.engine.setProperty('voice', english_voice.id)
                print(f"🎤 Using English voice: {english_voice.name}")
            else:
                print("⚠️ English voice not found, using default voice")
            
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
        Yakın nesne için uyarı ver
        
        Args:
            detection: Algılanan nesne (mesafe bilgileri ile)
        """
        if not self.is_enabled:
            return
        
        class_name = detection['class_name']
        distance_level = detection.get('distance_level', 'medium')
        urgency = detection.get('urgency', 1)
        
        current_time = time.time()
        
        # Throttling kontrolü
        last_alert_key = f"{class_name}_{distance_level}"
        if last_alert_key in self.last_alerts:
            time_since_last = current_time - self.last_alerts[last_alert_key]
            
            # Urgency'ye göre minimum bekleme süresi
            min_interval = self.config.ALERT_INTERVAL / max(urgency, 1)
            
            if time_since_last < min_interval:
                return
        
        # Mesaj oluştur
        base_message = self.messages.get(class_name, f"Önünüzde {class_name} var")
        
        # Yakınlık derecesine göre mesajı güçlendir
        if distance_level == 'very_close':
            message = f"Dikkat! {base_message}. Çok yakın!"
        elif distance_level == 'close':
            message = f"Uyarı! {base_message}"
        else:
            message = base_message
        
        # Kuyruğa ekle
        self.alert_queue.put({
            'text': message,
            'priority': urgency,
            'type': 'object_alert'
        })
        
        # Son uyarı zamanını güncelle
        self.last_alerts[last_alert_key] = current_time
    
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
        Acil durum uyarısı (en yüksek öncelik)
        
        Args:
            message: Acil durum mesajı
        """
        if not self.is_enabled:
            return
        
        # Acil durum mesajı - hemen kuyruğa ekle
        self.alert_queue.put({
            'text': f"ACİL! {message}",
            'priority': 3,
            'type': 'emergency'
        })
    
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
        
        test_message = "Ses testi. Sistem çalışıyor."
        self.alert_queue.put({
            'text': test_message,
            'priority': 2,
            'type': 'test'
        })
        
        print("🧪 Ses testi başlatıldı")
