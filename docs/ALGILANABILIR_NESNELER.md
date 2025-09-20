# 🎯 Algılanabilir Nesneler ve Ses Ayarları

## 🔊 Ses Aralığı Ayarları

**YENİ:** Tüm sesli uyarılar artık **10 saniye** aralıklarla çalıyor:

- **Nesne Uyarıları:** 10 saniyede bir ("Önünüzde insan var")
- **Yön Uyarıları:** 10 saniyede bir ("Sağa dönün")  
- **Genel Duyurular:** 10 saniyede bir ("Birden fazla engel tespit edildi")

### Özel Durumlar:
- **Çok Yakın Engel:** 5 saniyede bir (acil durum)
- **Acil Uyarılar:** Anında ("Dikkat! Çok yakın engel")

## 🎯 Algılanabilir Nesne Türleri

Sistem COCO dataset'indeki şu nesneleri algılar:

### 👥 **İNSANLAR**
- **Kod:** 0
- **Türkçe:** "insan" 
- **Uyarı:** "Önünüzde insan var"
- **Yakınlık Eşiği:** Frame'in %15'i (çok yakın)

### 🚲 **BİSİKLETLER**
- **Kod:** 1
- **Türkçe:** "bisiklet"
- **Uyarı:** "Önünüzde bisiklet var"
- **Yakınlık Eşiği:** Frame'in %12'si

### 🚗 **ARAÇLAR**

#### Araba
- **Kod:** 2
- **Türkçe:** "araba"
- **Uyarı:** "Önünüzde araç var"
- **Yakınlık Eşiği:** Frame'in %25'i (büyük nesne)

#### Motosiklet
- **Kod:** 3
- **Türkçe:** "motosiklet" 
- **Uyarı:** "Önünüzde motosiklet var"
- **Yakınlık Eşiği:** Frame'in %12'si

#### Otobüs
- **Kod:** 5
- **Türkçe:** "otobüs"
- **Uyarı:** "Önünüzde otobüs var"
- **Yakınlık Eşiği:** Frame'in %35'i (çok büyük)

#### Kamyon
- **Kod:** 7
- **Türkçe:** "kamyon"
- **Uyarı:** "Önünüzde kamyon var"
- **Yakınlık Eşiği:** Frame'in %35'i (çok büyük)

### 🚦 **TRAFİK ELEMENTLERİ**

#### Trafik Lambası
- **Kod:** 9
- **Türkçe:** "trafik_lambası"
- **Uyarı:** "Önünüzde trafik lambası var"
- **Yakınlık Eşiği:** Frame'in %12'si

#### Dur İşareti
- **Kod:** 11
- **Türkçe:** "dur_işareti"
- **Uyarı:** "Önünüzde dur işareti var"
- **Yakınlık Eşiği:** Frame'in %12'si

### 🐕 **HAYVANLAR**

#### Kedi
- **Kod:** 15
- **Türkçe:** "kedi"
- **Uyarı:** "Önünüzde kedi var"
- **Yakınlık Eşiği:** Frame'in %12'si

#### Köpek
- **Kod:** 16
- **Türkçe:** "köpek"
- **Uyarı:** "Önünüzde köpek var"
- **Yakınlık Eşiği:** Frame'in %12'si

## 📏 Mesafe Seviyeleri

Her nesne için 3 mesafe seviyesi:

### 🔴 **Çok Yakın (Very Close)**
- **Uyarı:** "Dikkat! [nesne] çok yakın!"
- **Ses Aralığı:** 5 saniye
- **Aciliyet:** Yüksek (Urgency: 3)

### 🟡 **Yakın (Close)**  
- **Uyarı:** "Uyarı! Önünüzde [nesne] var"
- **Ses Aralığı:** 10 saniye
- **Aciliyet:** Orta (Urgency: 2)

### 🟢 **Orta Mesafe (Medium)**
- **Uyarı:** "Önünüzde [nesne] var"
- **Ses Aralığı:** 20 saniye
- **Aciliyet:** Düşük (Urgency: 1)

## 🎛️ Ses Ayarlarını Değiştirme

### Kod ile Değiştirme:
```python
# config.py dosyasında
ALERT_INTERVAL = 5.0          # 5 saniye yapmak için
DIRECTION_ALERT_INTERVAL = 8.0 # Yön uyarıları için
```

### Çalışma Anında:
```python
# Sistem çalışırken
config.update_tts_settings(rate=120)  # Daha yavaş konuşma
voice_alert.set_volume(0.7)           # Daha düşük ses
```

### Performans Modu ile:
```python
config.set_performance_mode('power_save')  # Daha az sık uyarı
config.set_performance_mode('high')        # Daha sık uyarı
```

## 📊 Nesne Öncelik Sıralaması

Sistem birden fazla nesne algıladığında öncelik sırası:

1. **İnsan** (en yüksek öncelik)
2. **Araçlar** (araba, kamyon, otobüs)
3. **Bisiklet/Motosiklet**
4. **Trafik Elemanları**
5. **Hayvanlar**

## 🔧 Yeni Nesne Ekleme

Yeni nesne türü eklemek için `object_detector.py` dosyasında:

```python
self.target_classes = {
    0: 'insan',
    # ... mevcut nesneler ...
    17: 'at',          # Yeni nesne
    18: 'koyun',       # Yeni nesne
}
```

Ve `voice_alert.py` dosyasında mesaj ekle:
```python
self.messages = {
    # ... mevcut mesajlar ...
    'at': "Önünüzde at var",
    'koyun': "Önünüzde koyun var",
}
```

## 📈 Algılama İstatistikleri

Sistem her nesne için şu bilgileri tutar:

- **Güven Skoru:** %50 üzeri algılamalar
- **Bounding Box:** Nesne konumu ve boyutu
- **Merkez Noktası:** Hangi bölgede (sol/orta/sağ)
- **Alan:** Yakınlık hesaplama için
- **Son Görülme:** Uyarı throttling için

## 🎯 Optimizasyon İpuçları

### Daha Az Uyarı İçin:
```python
ALERT_INTERVAL = 15.0          # 15 saniye
CONFIDENCE_THRESHOLD = 0.7     # Daha kesin algılamalar
```

### Daha Çok Uyarı İçin:
```python
ALERT_INTERVAL = 5.0           # 5 saniye
CONFIDENCE_THRESHOLD = 0.3     # Daha hassas algılamalar
```

### Sadece Kritik Nesneler:
```python
target_classes = {
    0: 'insan',        # Sadece insan
    2: 'araba',        # ve araba
}
```

---

**Not:** Tüm ayarlar `config.py` dosyasından veya çalışma anında değiştirilebilir.
