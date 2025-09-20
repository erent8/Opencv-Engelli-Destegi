# 🎯 Detectable Objects and Voice Settings

## 🔊 Voice Alert Intervals

**NEW:** All voice alerts now play every **10 seconds**:

- **Object Alerts:** Every 10 seconds ("Person ahead")
- **Direction Alerts:** Every 10 seconds ("Turn right")  
- **General Announcements:** Every 10 seconds ("Multiple obstacles detected")

### Special Cases:
- **Very Close Obstacles:** Every 5 seconds (emergency)
- **Emergency Alerts:** Immediate ("Warning! Very close obstacle")

## 🎯 Detectable Object Types

The system detects the following objects from the COCO dataset:

### 👥 **PEOPLE**
- **Code:** 0
- **English:** "person" 
- **Alert:** "Person ahead"
- **Proximity Threshold:** 15% of frame (very close)

### 🚲 **BICYCLES**
- **Code:** 1
- **English:** "bicycle"
- **Alert:** "Bicycle ahead"
- **Proximity Threshold:** 12% of frame

### 🚗 **VEHICLES**

#### Car
- **Code:** 2
- **English:** "car"
- **Alert:** "Car ahead"
- **Proximity Threshold:** 25% of frame (large object)

#### Motorcycle
- **Code:** 3
- **English:** "motorcycle" 
- **Alert:** "Motorcycle ahead"
- **Proximity Threshold:** 12% of frame

#### Bus
- **Code:** 5
- **English:** "bus"
- **Alert:** "Bus ahead"
- **Proximity Threshold:** 35% of frame (very large)

#### Truck
- **Code:** 7
- **English:** "truck"
- **Alert:** "Truck ahead"
- **Proximity Threshold:** 35% of frame (very large)

### 🚦 **TRAFFIC ELEMENTS**

#### Traffic Light
- **Code:** 9
- **English:** "traffic_light"
- **Alert:** "Traffic light ahead"
- **Proximity Threshold:** 12% of frame

#### Stop Sign
- **Code:** 11
- **English:** "stop_sign"
- **Alert:** "Stop sign ahead"
- **Proximity Threshold:** 12% of frame

### 🐕 **ANIMALS**

#### Cat
- **Code:** 15
- **English:** "cat"
- **Alert:** "Cat ahead"
- **Proximity Threshold:** 12% of frame

#### Dog
- **Code:** 16
- **English:** "dog"
- **Alert:** "Dog ahead"
- **Proximity Threshold:** 12% of frame

## 📏 Distance Levels

Three distance levels for each object:

### 🔴 **Very Close**
- **Alert:** "Warning! [object] very close!"
- **Voice Interval:** 5 seconds
- **Urgency:** High (Urgency: 3)

### 🟡 **Close**  
- **Alert:** "Warning! [object] ahead"
- **Voice Interval:** 10 seconds
- **Urgency:** Medium (Urgency: 2)

### 🟢 **Medium Distance**
- **Alert:** "[object] ahead"
- **Voice Interval:** 20 seconds
- **Urgency:** Low (Urgency: 1)

## 🎛️ Changing Voice Settings

### Code Modification:
```python
# In config.py file
ALERT_INTERVAL = 5.0          # Make it 5 seconds
DIRECTION_ALERT_INTERVAL = 8.0 # For direction alerts
```

### Runtime Changes:
```python
# While system is running
config.update_tts_settings(rate=120)  # Slower speech
voice_alert.set_volume(0.7)           # Lower volume
```

### Performance Mode:
```python
config.set_performance_mode('power_save')  # Less frequent alerts
config.set_performance_mode('high')        # More frequent alerts
```

## 📊 Object Priority Order

When multiple objects are detected, priority order:

1. **Person** (highest priority)
2. **Vehicles** (car, truck, bus)
3. **Bicycle/Motorcycle**
4. **Traffic Elements**
5. **Animals**

## 🔧 Adding New Objects

To add new object types, modify `object_detector.py`:

```python
self.target_classes = {
    0: 'person',
    # ... existing objects ...
    17: 'horse',       # New object
    18: 'sheep',       # New object
}
```

And add message in `voice_alert.py`:
```python
self.messages = {
    # ... existing messages ...
    'horse': "Horse ahead",
    'sheep': "Sheep ahead",
}
```

## 📈 Detection Statistics

The system tracks the following information for each object:

- **Confidence Score:** Detections above 50%
- **Bounding Box:** Object location and size
- **Center Point:** Which zone (left/center/right)
- **Area:** For proximity calculation
- **Last Seen:** For alert throttling

## 🎯 Optimization Tips

### For Fewer Alerts:
```python
ALERT_INTERVAL = 15.0          # 15 seconds
CONFIDENCE_THRESHOLD = 0.7     # More precise detections
```

### For More Alerts:
```python
ALERT_INTERVAL = 5.0           # 5 seconds
CONFIDENCE_THRESHOLD = 0.3     # More sensitive detections
```

### Critical Objects Only:
```python
target_classes = {
    0: 'person',       # Only person
    2: 'car',          # and car
}
```

## 🎬 Testing Voice Alerts

### Windows Test:
```bash
python test_windows.py
# Choose option 3 for full system test with English voice
```

### Expected Voice Outputs:
- "Windows test system is running"
- "Person ahead"
- "Turn right" / "Turn left"
- "Warning! Very close obstacle"

## 📱 Voice Settings

### English Voice Selection:
The system automatically selects English voice:
```python
# Automatic English voice detection
if 'en' in voice.id.lower() or 'english' in voice.name.lower():
    engine.setProperty('voice', voice.id)
```

### Speech Rate:
- **Default:** 150 words per minute
- **Slow:** 120 words per minute
- **Fast:** 180 words per minute

### Volume Levels:
- **Quiet:** 0.5 (50%)
- **Normal:** 0.9 (90%) - default
- **Loud:** 1.0 (100%)

---

**All settings can be modified in `config.py` or during runtime.**
