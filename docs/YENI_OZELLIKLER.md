# 🆕 Yeni Özellikler v1.1

## 🎉 **Eklenen Yeni Özellikler**

### **1. 🌍 Türkçe TTS Desteği**
- ✅ **Çift dil desteği:** İngilizce ve Türkçe
- ✅ **Otomatik ses seçimi:** Sistem diline göre uygun ses
- ✅ **Doğal Türkçe mesajlar:** "Önünüzde insan, 2.5 metre uzaklıkta"
- ✅ **Canlı dil değiştirme:** 'L' tuşu ile anlık geçiş

#### **Türkçe Sesli Uyarı Örnekleri:**
- **"Dikkat! Önünüzde insan, çok yakın, 1.5 metre"**
- **"Uyarı! Önünüzde araba, yakın, 3.5 metre"**
- **"Önünüzde bisiklet, 8.0 metre uzaklıkta"**
- **"Sola dönün" / "Sağa dönün"**

### **2. 🎯 Genişletilmiş Nesne Algılama**
**10 nesneden 30+ nesneye çıkarıldı!**

#### **İnsan ve Hayvanlar (10 tür)**
- İnsan, Kedi, Köpek, At, Koyun, İnek, Fil, Ayı, Zebra, Zürafa

#### **Araçlar (8 tür)** 
- Bisiklet, Araba, Motosiklet, Uçak, Otobüs, Tren, Kamyon, Tekne

#### **Trafik ve Şehir Nesneleri (5 tür)**
- Trafik ışığı, Yangın musluğu, Dur işareti, Parkometre, Bank

#### **Engeller ve Mobilyalar (7 tür)**
- Sandalye, Koltuk, Saksı, Yatak, Masa, Tuvalet, Televizyon

#### **Spor Ekipmanları (4 tür)**
- Top, Kaykay, Sörf tahtası, Tenis raketi

### **3. 🎮 Gelişmiş Kontroller**
**Yeni klavye kısayolları eklendi:**

- **`Q`** - Çıkış
- **`S`** - Sesi aç/kapat
- **`T`** - Ses testi (mevcut dilde)
- **`L`** - Dil değiştir (TR ↔ EN) **[YENİ]**
- **`D`** - Debug modu

### **4. 📊 Gelişmiş Görsel Bilgiler**
**Ekranda yeni bilgiler:**
- **Language: TR/EN** - Mevcut dil göstergesi
- **Nesne sayısı:** 30+ farklı nesne türü
- **Dil durumu:** Hangi dilde çalıştığı

---

## 🧪 **Test Etme**

### **Hızlı Test:**
```bash
python test_windows.py
# Seçenek 3'ü seç (tam sistem)
```

### **Özellik Testleri:**
1. **Türkçe TTS Test:**
   - `L` tuşuna bas → "Dil Türkçe olarak değiştirildi"
   - `T` tuşuna bas → "Ses testi. Sistem çalışıyor."

2. **İngilizce TTS Test:**
   - `L` tuşuna tekrar bas → "Language switched to English"
   - `T` tuşuna bas → "Voice test. System is working."

3. **Genişletilmiş Nesne Algılama:**
   - Daha fazla nesne türü algılanacak
   - Her nesne için Türkçe/İngilizce uyarı

---

## 🎯 **Kullanım Senaryoları**

### **Türkçe Kullanıcılar İçin:**
```python
# config.py dosyasında
TTS_LANGUAGE = 'tr'  # Varsayılan Türkçe
```

**Duyacağınız uyarılar:**
- "Önünüzde insan, 2.5 metre uzaklıkta"
- "Dikkat! Önünüzde araba, çok yakın, 1.2 metre"
- "Önünüzde bank, 4.5 metre uzaklıkta"
- "Sola dönün"

### **İngilizce Kullanıcılar İçin:**
```python
# config.py dosyasında  
TTS_LANGUAGE = 'en'  # Varsayılan İngilizce
```

**Duyacağınız uyarılar:**
- "Person ahead, 2.5 meters away"
- "Warning! Car ahead, very close, 1.2 meters"
- "Bench ahead, 4.5 meters away"
- "Turn left"

---

## 📈 **Performans İyileştirmeleri**

### **Nesne Algılama:**
- **30+ nesne türü** desteği
- **Aynı hız** (optimizasyon sayesinde)
- **Daha kapsamlı** çevre algılama

### **Ses Sistemi:**
- **Çift dil desteği** ek yük getirmedi
- **Anlık dil değiştirme** <1 saniye
- **Doğal Türkçe telaffuz**

---

## 🔧 **Teknik Detaylar**

### **Dil Sistemi Mimarisi:**
```python
messages = {
    'en': { 'person': "Person ahead", ... },
    'tr': { 'person': "Önünüzde insan", ... }
}
```

### **Otomatik Ses Seçimi:**
- **Türkçe:** Turkish/Türk ses arar
- **İngilizce:** English ses arar
- **Fallback:** Varsayılan sistem sesi

### **Genişletilmiş COCO Sınıfları:**
- **Toplam:** 30+ nesne sınıfı
- **Kategorize:** İnsan, Hayvan, Araç, Trafik, Mobilya, Spor
- **Optimize:** Hız kaybı olmadan

---

## 🚀 **Sonraki Adımlar**

### **Hemen Yapılabilecek İyileştirmeler:**
1. **🌙 Gece görüş modu** - Düşük ışık optimizasyonu
2. **🌦️ Hava durumu algılama** - Yağmur/kar/sis tespiti
3. **📱 Mobil uygulama** - Companion app
4. **🔊 3D ses** - Uzamsal audio

### **Orta Vadeli Hedefler:**
1. **🧠 Makine öğrenmesi** - Kişiselleştirilmiş uyarılar
2. **🗺️ GPS entegrasyonu** - Navigasyon desteği
3. **☁️ Bulut senkronizasyonu** - Ayar paylaşımı

---

## 🎉 **Özet**

### **v1.0 → v1.1 Karşılaştırması:**

| Özellik | v1.0 | v1.1 |
|---------|------|------|
| **Dil Desteği** | Sadece İngilizce | İngilizce + Türkçe |
| **Nesne Türleri** | 10 tür | 30+ tür |
| **Dil Değiştirme** | ❌ | ✅ (L tuşu) |
| **Ses Testi** | Basit | Dile özel |
| **Görsel Bilgi** | Temel | Dil + nesne sayısı |

### **Kullanıcı Deneyimi:**
- **%200 daha fazla** nesne türü algılama
- **Doğal Türkçe** sesli uyarılar
- **Anlık dil değiştirme** özelliği
- **Daha kapsamlı** çevre farkındalığı

**Artık sistem hem Türkçe hem İngilizce konuşabiliyor ve 30'dan fazla farklı nesne türünü algılayabiliyor!** 🎯🚀
