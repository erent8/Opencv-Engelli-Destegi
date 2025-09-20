# 📋 Technical Specifications & Requirements

## 🏗️ **Current System Architecture (v1.0)**

### **Core Components**
```
Assistive Vision Runtime
+-- src/assistive_vision/system.py        # System orchestrator
+-- src/assistive_vision/config.py        # Configuration management
+-- src/assistive_vision/object_detector.py # YOLOv8 detection engine
+-- src/assistive_vision/object_tracker.py  # Multi-object tracking
+-- src/assistive_vision/distance_checker.py # Proximity analysis
+-- src/assistive_vision/voice_alert.py      # Audio notification system
+-- src/assistive_vision/navigation_guide.py # 3-zone spatial analysis
+-- src/assistive_vision/detection_logger.py # CSV logging system
+-- scripts/run_system.py                   # Launch helper
+-- tests/test_windows.py                   # Desktop validation suite
```

### **Data Flow Architecture**
```
Camera Input → Object Detection → Object Tracking → Distance Analysis
                                        ↓
CSV Logging ← Voice Alerts ← Navigation Analysis ← Proximity Check
```

---

## 💻 **Hardware Requirements**

### **Minimum Requirements**
- **Processor:** ARM Cortex-A72 (Raspberry Pi 4) or equivalent
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 32GB microSD card (Class 10)
- **Camera:** USB webcam or Raspberry Pi Camera Module v2
- **Audio:** 3.5mm audio output or USB audio device
- **Power:** 5V 3A USB-C power supply

### **Recommended Hardware**
- **Processor:** ARM Cortex-A78 (Raspberry Pi 5) or NVIDIA Jetson Nano
- **RAM:** 8GB LPDDR4
- **Storage:** 64GB microSD card (Class 10) + USB 3.0 storage
- **Camera:** Raspberry Pi Camera Module v3 (12MP) or stereo camera
- **Audio:** Bone conduction headphones or directional speakers
- **Sensors:** Optional LiDAR, ultrasonic sensors
- **Display:** 7" touchscreen for configuration (optional)

### **Performance Specifications**
| Platform | FPS | Latency | Power | Cost |
|----------|-----|---------|-------|------|
| Raspberry Pi 3B+ | 5-8 | 200-300ms | 5W | $35 |
| Raspberry Pi 4 | 10-15 | 100-150ms | 8W | $55 |
| Raspberry Pi 5 | 20-25 | 50-100ms | 12W | $75 |
| Jetson Nano | 30-40 | 30-50ms | 15W | $99 |
| PC/Laptop | 60+ | 10-30ms | 50W+ | $500+ |

---

## 🛠️ **Software Requirements**

### **Operating System**
- **Primary:** Raspberry Pi OS (Bullseye 64-bit or later)
- **Alternative:** Ubuntu 20.04+ LTS
- **Development:** Windows 10/11, macOS 10.15+, Linux

### **Python Dependencies**
```txt
# Core ML/CV Libraries
opencv-python>=4.5.0
ultralytics>=8.0.0
numpy>=1.21.0
torch>=1.12.0
torchvision>=0.13.0

# Audio Processing
pyttsx3>=2.90

# System Utilities
pathlib2>=2.3.6
psutil>=5.8.0
```

### **System Libraries**
```bash
# Computer Vision
libopencv-dev
python3-opencv

# Audio System
espeak
espeak-data
libespeak1
libespeak-dev
portaudio19-dev
python3-pyaudio

# Camera Support
v4l-utils
libv4l-dev
```

---

## 🎯 **Detection Capabilities**

### **Supported Object Classes**
| ID | Class | Confidence Threshold | Distance Range | Priority |
|----|-------|---------------------|----------------|----------|
| 0 | Person | 0.5 | 1-20m | High |
| 1 | Bicycle | 0.6 | 2-15m | Medium |
| 2 | Car | 0.7 | 3-30m | High |
| 3 | Motorcycle | 0.6 | 2-20m | Medium |
| 5 | Bus | 0.7 | 5-50m | High |
| 7 | Truck | 0.7 | 5-50m | High |
| 9 | Traffic Light | 0.8 | 5-30m | Medium |
| 11 | Stop Sign | 0.8 | 3-20m | Medium |
| 15 | Cat | 0.5 | 1-10m | Low |
| 16 | Dog | 0.5 | 1-15m | Low |

### **Detection Performance**
- **Accuracy:** 85-95% (varies by object type and conditions)
- **Processing Time:** 50-200ms per frame
- **Maximum Objects:** 20 simultaneous tracks
- **Minimum Object Size:** 32x32 pixels
- **Maximum Distance:** 50 meters (estimated)

---

## 🔊 **Audio System Specifications**

### **Voice Alert Characteristics**
- **Language:** English (primary), Turkish (planned)
- **Voice Type:** Synthetic TTS (pyttsx3)
- **Speech Rate:** 120-180 words per minute
- **Volume Range:** 0.0-1.0 (adjustable)
- **Alert Intervals:** 3-20 seconds (distance-based)

### **Audio Processing**
- **Sample Rate:** 22.05 kHz
- **Bit Depth:** 16-bit
- **Channels:** Mono/Stereo
- **Latency:** <100ms from detection to audio output
- **Queue Size:** 10 messages maximum

### **Message Types**
1. **Object Alerts:** "Person ahead, 2.5 meters"
2. **Distance Details:** "Closest object: car at 8.0 meters. Safe distance."
3. **Direction Guidance:** "Turn left" / "Turn right"
4. **System Messages:** "System ready" / "Sound on"

---

## 📊 **Data Logging Specifications**

### **CSV Output Format**

#### **Detections Log (detections_YYYYMMDD_HHMMSS.csv)**
```csv
timestamp,session_id,frame_number,track_id,class_id,class_name,confidence,
bbox_x1,bbox_y1,bbox_x2,bbox_y2,center_x,center_y,width,height,area,
distance_meters,is_stable,age_seconds,zone
```

#### **Alerts Log (alerts_YYYYMMDD_HHMMSS.csv)**
```csv
timestamp,session_id,track_id,class_name,alert_type,message,
distance_meters,urgency,zone
```

#### **Session Log (session_YYYYMMDD_HHMMSS.csv)**
```csv
timestamp,session_id,event_type,data
```

### **Storage Requirements**
- **Typical Session (1 hour):** 10-50 MB CSV data
- **Daily Usage (8 hours):** 80-400 MB storage
- **Monthly Archive:** 2-12 GB storage
- **Log Retention:** Configurable (default: 30 days)

---

## 🔧 **Configuration Parameters**

### **Camera Settings**
```python
CAMERA_WIDTH = 1280        # Video width (pixels)
CAMERA_HEIGHT = 720        # Video height (pixels)
CAMERA_FPS = 15           # Frames per second
CAMERA_DEVICE = 0         # Camera device index
```

### **Detection Settings**
```python
CONFIDENCE_THRESHOLD = 0.5    # Minimum detection confidence
IOU_THRESHOLD = 0.45         # Non-maximum suppression threshold
MIN_DETECTION_AREA = 500     # Minimum object area (pixels²)
DETECTION_INTERVAL = 0.1     # Processing interval (seconds)
```

### **Alert Settings**
```python
ALERT_INTERVAL = 10.0           # Base alert interval (seconds)
DIRECTION_ALERT_INTERVAL = 10.0 # Direction alert interval
TTS_RATE = 150                  # Speech rate (words/minute)
TTS_VOLUME = 0.9               # Volume level (0.0-1.0)
```

### **Performance Settings**
```python
MAX_FPS = 20                # Maximum processing FPS
PROCESSING_THREADS = 1      # Number of processing threads
MEMORY_LIMIT_MB = 512      # Memory usage limit
```

---

## 🚀 **Performance Optimization**

### **CPU Optimization**
- **Multi-threading:** Separate threads for detection, audio, logging
- **Frame Skipping:** Process every Nth frame based on performance
- **Memory Management:** Circular buffers for detection history
- **CPU Affinity:** Pin threads to specific cores

### **Memory Optimization**
- **Model Loading:** Load YOLO model once at startup
- **Frame Buffers:** Reuse frame memory to reduce allocation
- **Detection Cache:** Cache recent detections for stability
- **Garbage Collection:** Explicit memory cleanup for long sessions

### **Algorithm Optimization**
- **ROI Processing:** Focus detection on relevant image regions
- **Temporal Filtering:** Use previous frames for stability
- **Confidence Thresholding:** Early rejection of low-confidence detections
- **NMS Optimization:** Efficient non-maximum suppression

---

## 🔒 **Security & Privacy**

### **Data Protection**
- **Local Processing:** All AI processing on-device
- **No Cloud Dependency:** System works offline
- **Encrypted Logs:** Optional log encryption
- **User Consent:** Clear data usage policies

### **Privacy Measures**
- **No Image Storage:** Frames processed and discarded
- **Anonymized Logs:** No personally identifiable information
- **Configurable Logging:** User can disable logging
- **Data Retention:** Automatic log cleanup

---

## 🧪 **Testing & Validation**

### **Unit Testing**
- **Detection Accuracy:** Automated testing with labeled datasets
- **Audio Latency:** Timing measurements for alert delivery
- **Memory Leaks:** Long-running stability tests
- **Configuration Validation:** Parameter boundary testing

### **Integration Testing**
- **End-to-End Workflows:** Complete detection-to-alert pipelines
- **Hardware Compatibility:** Testing across different platforms
- **Performance Benchmarking:** FPS and latency measurements
- **Error Handling:** Graceful failure recovery testing

### **User Acceptance Testing**
- **Accessibility Compliance:** WCAG 2.1 AA standards
- **Real-World Scenarios:** Testing in various environments
- **User Feedback:** Iterative improvement based on user input
- **Safety Validation:** Ensuring reliable obstacle detection

---

## 📈 **Scalability Considerations**

### **Horizontal Scaling**
- **Multi-Camera Support:** Process multiple camera feeds
- **Distributed Processing:** Split workload across devices
- **Cloud Integration:** Optional cloud-based processing
- **Load Balancing:** Dynamic resource allocation

### **Vertical Scaling**
- **GPU Acceleration:** CUDA/OpenVINO support
- **Model Optimization:** Quantization and pruning
- **Hardware Upgrades:** Support for more powerful platforms
- **Memory Expansion:** Efficient use of additional RAM

---

## 🔮 **Future Technical Roadmap**

### **Short-term Enhancements (3 months)**
- **TensorRT Integration:** 3x inference speedup
- **Stereo Vision:** Real depth measurement
- **Advanced Tracking:** DeepSORT implementation
- **Mobile App:** Companion application

### **Medium-term Features (6 months)**
- **Custom Model Training:** Domain-specific optimization
- **Multi-language TTS:** Turkish, Spanish, French support
- **IoT Integration:** Smart city infrastructure connection
- **AR Visualization:** Augmented reality overlay

### **Long-term Vision (12 months)**
- **Edge AI Optimization:** Dedicated AI accelerator support
- **Semantic Segmentation:** Detailed scene understanding
- **Natural Language Interface:** Voice command processing
- **Predictive Analytics:** Proactive hazard detection

---

*This technical specification is a living document that evolves with system development and user feedback.*
