# 🖥️ Windows'ta Test Etme Kılavuzu

Bu kılavuz Raspberry Pi Engelli Destek Sistemi'ni Windows bilgisayarınızda test etmeniz için hazırlanmıştır.

## 🚀 Hızlı Başlangıç

### 1. Python Kurulumu
```bash
# Python 3.8+ gerekli
python --version
```
Python yoksa [python.org](https://www.python.org/downloads/) adresinden indirin.

### 2. Gerekli Kütüphaneleri Yükleyin
```bash
# Ana dizinde
pip install opencv-python numpy ultralytics pyttsx3

# Veya requirements.txt ile
pip install -r requirements.txt
```

### 3. Test Sistemini Çalıştırın
```bash
python test_windows.py
```

## 📋 Test Seçenekleri

Test scripti çalıştırıldığında 3 seçenek sunulur:

### **Seçenek 1: Sadece Görüntü Testi** ⚡
- En hızlı test
- Demo nesneleri ile simülasyon
- Kamera gerekmez
- YOLO indirmez

### **Seçenek 2: YOLO ile Nesne Algılama** 🎯
- YOLOv8 modelini indirir (ilk seferde ~6MB)
- Gerçek nesne algılama
- Kamera varsa gerçek görüntü, yoksa demo

### **Seçenek 3: Tam Sistem Testi** 🔊
- YOLO + Sesli uyarı
- Türkçe TTS testleri
- Tam fonksiyonalite

## 🎮 Klavye Kontrolleri

Test sırasında kullanabileceğiniz tuşlar:

- **`q`** - Çıkış
- **`s`** - Sesi aç/kapat (Seçenek 3'te)
- **`t`** - Test sesli mesajı (Seçenek 3'te)

## 🔧 Sorun Giderme

### Kamera Bulunamadı
```
⚠️ Kamera bulunamadı, demo modu kullanılacak
```
**Çözüm:** Normal durum, demo modunda çalışır.

### YOLO İndirme Hatası
```bash
# Manuel indirme
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### TTS Çalışmıyor
```bash
# Windows TTS test
python -c "import pyttsx3; e=pyttsx3.init(); e.say('test'); e.runAndWait()"
```

### Modül Import Hatası
```bash
# Temel kütüphaneleri yükle
pip install --upgrade opencv-python numpy
```

## 📊 Beklenen Çıktılar

### **Konsol Çıktısı:**
```
🖥️ Windows Test Sistemi başlatılıyor...
📹 Kamera testi...
⚠️ Kamera bulunamadı, demo modu kullanılacak
🎯 YOLO testi...
✅ YOLO modeli yüklendi: yolov8n.pt
🔊 TTS testi...
🎤 Test mesajı çalınıyor...
✅ TTS çalışıyor
✅ Tüm modüller yüklendi
🎬 Demo modu başlatılıyor...
```

### **Görüntü Penceresi:**
- Demo nesneleri (insan, araba)
- Bounding box'lar ve etiketler
- 3 bölge çizgileri (sol, orta, sağ)
- FPS ve nesne sayısı bilgisi
- "DEMO MODU - Windows Test" yazısı

### **Sesli Çıktılar:**
- "Windows test sistemi çalışıyor"
- "Önünüzde insan var"
- "Sağa dönün" / "Sola dönün"

## 🎯 Test Senaryoları

### **Senaryo 1: Temel Fonksiyonalite**
1. `python test_windows.py` çalıştır
2. Seçenek 1'i seç
3. Pencerede demo nesnelerini gör
4. `q` ile çık

### **Senaryo 2: Nesne Algılama**
1. Seçenek 2'yi seç
2. YOLO modelinin indirilmesini bekle
3. Demo nesnelerinin algılanmasını gözle
4. Konsoldaki algılama mesajlarını kontrol et

### **Senaryo 3: Sesli Uyarılar**
1. Seçenek 3'ü seç
2. "Windows test sistemi çalışıyor" sesini duy
3. Demo nesneleri için sesli uyarıları bekle
4. `s` ile sesi aç/kapat test et
5. `t` ile manuel ses testi yap

## 💡 İpuçları

### **Performans İyileştirme:**
- Gereksiz programları kapat
- Virüs tarayıcısını geçici durdur
- Güç tasarrufu modunu kapat

### **Kamera Kullanımı:**
- USB kamera takın
- Kamera uygulamalarını kapat
- Windows kamera izinlerini kontrol et

### **Ses Sorunları:**
- Hoparlör/kulaklık bağlantısını kontrol et
- Windows ses seviyesini ayarla
- Varsayılan ses cihazını ayarla

## 📈 Performans Beklentileri

| Bileşen | Windows PC | Raspberry Pi 4 |
|---------|------------|----------------|
| FPS | 25-60 | 10-15 |
| YOLO Hızı | <50ms | 100-200ms |
| RAM Kullanımı | ~200MB | ~400MB |
| İlk Yükleme | ~10sn | ~30sn |

## ✅ Başarı Kriterleri

Test başarılı sayılır eğer:

- [ ] Pencere açılıyor ve demo gösteriliyor
- [ ] Bounding box'lar çiziliyor
- [ ] FPS sayacı çalışıyor
- [ ] Bölge çizgileri görünüyor
- [ ] Klavye kontrolleri çalışıyor
- [ ] Sesli uyarılar duyuluyor (Seçenek 3)
- [ ] Çıkış düzgün çalışıyor

## 🔄 Sonraki Adımlar

Windows'ta test ettikten sonra:

1. **Raspberry Pi'ye Aktarım:**
   - Kodu Raspberry Pi'ye kopyala
   - `install.sh` scriptini çalıştır
   - Gerçek kamera ile test et

2. **Özelleştirmeler:**
   - `config.py`'da ayarları değiştir
   - Yeni nesne türleri ekle
   - Ses mesajlarını özelleştir

3. **Gerçek Kullanım:**
   - Donanım bağlantılarını yap
   - Sistem servisi kur
   - Performans optimizasyonu yap

## 📞 Yardım

Sorun yaşarsanız:

1. Hata mesajını not edin
2. Python ve kütüphane versiyonlarını kontrol edin
3. Konsol çıktısını paylaşın
4. GitHub Issues'da soru sorun

---

**İyi testler! 🚀**
