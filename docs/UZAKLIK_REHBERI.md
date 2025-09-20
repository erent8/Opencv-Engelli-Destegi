# 📏 Uzaklık Ölçümü ve Görsel Rehber

## 🖥️ YENİ: HD Tam Ekran Görüntü

Artık sistem **1280x720 HD çözünürlükte** çalışıyor:
- ✅ **Eski:** 640x480 (küçük pencere)
- 🆕 **Yeni:** 1280x720 (HD tam ekran)
- 📱 **Pencere:** Yeniden boyutlandırılabilir

## 📐 Uzaklık Ölçüm Sistemi

### **Uzaklık Hesaplama Yöntemi**
Sistem nesne boyutuna göre uzaklık tahmin eder:

```
Uzaklık = (Gerçek_Boyut × Kamera_Odak) / Piksel_Boyutu
```

### **Demo Nesneleri ve Uzaklıkları**
1. **İnsan:** 2.5 metre (YAKIN - Tehlikeli)
2. **Bisiklet:** 5.0 metre (ORTA - Dikkatli)  
3. **Araba:** 8.0 metre (UZAK - Güvenli)

## 🎨 Görsel Uzaklık Göstergeleri

### **Renk Kodları**
- 🔴 **Kırmızı Çember:** <3m (Tehlikeli)
- 🟡 **Sarı Çember:** 3-6m (Dikkatli)
- 🟢 **Yeşil Çember:** >6m (Güvenli)

### **Çerçeve Kalınlığı**
- **Kalın (4px):** <3m uzaklık
- **Orta (3px):** 3-6m uzaklık  
- **İnce (2px):** >6m uzaklık

### **Çember Boyutu**
- **Büyük (30px):** Çok yakın
- **Orta (20px):** Orta mesafe
- **Küçük (15px):** Uzak

## 📊 HD Ekran Bilgi Paneli

### **Sol Alt Köşe - Uzaklık Rehberi:**
```
UZAKLIK BİLGİLERİ:
🔴 <3m: TEHLİKELİ
🟡 3-6m: DİKKATLİ  
🟢 >6m: GÜVENLİ
```

### **Alt Çubuk - Bölge Durumu:**
```
Sol: Bisiklet (5.0m) | Orta: İnsan (2.5m) | Sağ: Araba (8.0m)
```

### **Üst Çubuk - Sistem Bilgisi:**
```
DEMO MODU - Windows Test (1280x720)
FPS: 30.0
Nesneler: 3
```

## 🎯 Nesne Etiket Formatı

Her nesne için detaylı bilgi gösterilir:
```
[nesne_adı] [güven_oranı] - [uzaklık]
Örnek: "insan 0.85 - 2.5m"
```

## 📏 Gerçek Dünya Uzaklık Referansları

### **1-3 Metre (Tehlikeli Bölge)**
- Kol uzunluğu: ~0.7m
- Bir adım: ~0.8m
- Kapı genişliği: ~1m
- Masa uzunluğu: ~2m

### **3-6 Metre (Dikkat Bölgesi)**  
- Oda genişliği: ~4m
- Araç uzunluğu: ~4.5m
- Küçük bahçe: ~5m

### **6+ Metre (Güvenli Bölge)**
- Sokak genişliği: ~7m
- Basketbol potası yüksekliği: ~3m (referans)
- Büyük oda: ~8m

## ⚙️ Uzaklık Kalibrasyonu

### **Hassasiyet Ayarları**
```python
# config.py dosyasında
CLOSE_DISTANCE_THRESHOLD = 0.15    # %15 frame = yakın
VERY_CLOSE_THRESHOLD = 0.25        # %25 frame = çok yakın
MEDIUM_DISTANCE_THRESHOLD = 0.08   # %8 frame = orta
```

### **Nesne Türüne Göre Eşikler**
```python
distance_thresholds = {
    'insan': {'very_close': 0.15, 'close': 0.08},
    'araba': {'very_close': 0.25, 'close': 0.15},
    'bisiklet': {'very_close': 0.12, 'close': 0.06}
}
```

## 🔊 Uzaklık Tabanlı Sesli Uyarılar

### **Çok Yakın (<3m)**
- **Mesaj:** "Dikkat! [nesne] çok yakın!"
- **Aralık:** 5 saniye
- **Ton:** Acil/Hızlı

### **Yakın (3-6m)**
- **Mesaj:** "Uyarı! Önünüzde [nesne] var"
- **Aralık:** 10 saniye  
- **Ton:** Normal

### **Uzak (>6m)**
- **Mesaj:** "Önünüzde [nesne] var"
- **Aralık:** 20 saniye
- **Ton:** Sakin

## 🎮 HD Test Kontrolleri

### **Klavye Kısayolları**
- **`q`** - Çıkış
- **`s`** - Ses aç/kapat
- **`t`** - Test sesli mesajı
- **`f`** - Tam ekran aç/kapat (yeni)

### **Mouse Kontrolleri**
- **Sağ tık:** Pencereyi yeniden boyutlandır
- **Çift tık:** Tam ekran geçiş

## 📱 Farklı Ekran Boyutları

### **Desteklenen Çözünürlükler**
- **HD:** 1280x720 (varsayılan)
- **Full HD:** 1920x1080 (büyük ekranlar)
- **4K:** 3840x2160 (ultra yüksek çözünürlük)

### **Otomatik Ölçeklendirme**
Sistem ekran boyutuna göre otomatik ölçeklenir:
```python
# Farklı çözünürlükler için
width, height = 1920, 1080  # Full HD
width, height = 1280, 720   # HD (varsayılan)
width, height = 640, 480    # Düşük çözünürlük
```

## 🔬 Hassasiyet Testi

### **Test Senaryoları**
1. **Yakın Nesne:** 1-2 metre mesafede test
2. **Orta Mesafe:** 3-5 metre mesafede test  
3. **Uzak Nesne:** 6+ metre mesafede test

### **Beklenen Sonuçlar**
- Yakın nesneler kalın kırmızı çerçeve
- Orta mesafe sarı çember
- Uzak nesneler ince yeşil çerçeve

## 💡 Performans İpuçları

### **HD Görüntü için Öneriler**
- **RAM:** En az 4GB önerilir
- **CPU:** i5 veya daha üst işlemci
- **GPU:** Entegre grafik yeterli

### **Optimizasyon**
```python
# Daha hızlı işleme için
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30  # Yüksek FPS
```

---

**Artık HD kalitede, uzaklık bilgileri ile zenginleştirilmiş görüntü deneyimi!** 🚀
