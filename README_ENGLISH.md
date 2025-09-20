# 🦽 Raspberry Pi Disability Assistance System

A real-time object detection and voice alert system running on Raspberry Pi. Provides navigation assistance for visually impaired individuals using YOLOv8.

## 🌟 Features

- **Real-time Object Detection**: Detects people, vehicles, bicycles, etc. using YOLOv8
- **Voice Alert System**: English voice alerts and navigation guidance
- **3-Zone Navigation**: Left, center, right zone analysis with directional guidance
- **Proximity Detection**: Distance estimation based on object size
- **Raspberry Pi Optimization**: Low power consumption and high performance
- **Modular Architecture**: Easy customization and development

## 📋 Requirements

### Hardware
- Raspberry Pi 4 (recommended) or Raspberry Pi 3B+
- USB Camera or Raspberry Pi Camera Module
- Speaker or Headphones
- MicroSD Card (32GB+)

### Software
- Raspberry Pi OS (Bullseye or later)
- Python 3.8+
- OpenCV 4.5+

## 🚀 Installation

### 1. System Update
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python Libraries
```bash
# System libraries
sudo apt install python3-pip python3-venv
sudo apt install libopencv-dev python3-opencv
sudo apt install espeak espeak-data libespeak1 libespeak-dev
sudo apt install portaudio19-dev python3-pyaudio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
pip install -r requirements.txt
```

### 3. Download YOLOv8 Model
```bash
# Lightweight model (recommended)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Or automatic download with Python
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### 4. Enable Camera
```bash
# For Raspberry Pi camera
sudo raspi-config
# Interface Options > Camera > Enable

# Check USB camera
lsusb
v4l2-ctl --list-devices
```

## 🎮 Usage

### Basic Run
```bash
python main.py
```

### Keyboard Shortcuts
- `q`: Exit
- `s`: Toggle sound on/off
- `d`: Toggle debug mode

### Configuration
You can modify settings in `config.py`:

```python
# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 15

# Detection sensitivity
CONFIDENCE_THRESHOLD = 0.5

# Voice alert settings
TTS_RATE = 150  # Speech rate
TTS_VOLUME = 0.9  # Volume level
```

## 📁 Project Structure

```
├── main.py                 # Main system file
├── config.py              # Configuration settings
├── object_detector.py     # YOLOv8 object detection
├── distance_checker.py    # Distance control
├── voice_alert.py         # Voice alert system
├── navigation_guide.py    # 3-zone navigation
├── requirements.txt       # Python requirements
├── README.md             # This file
├── models/               # YOLO model files
├── logs/                 # Log files
└── data/                 # Data files
```

## 🔧 Performance Optimization

### For Raspberry Pi 4
```python
# In config.py
config.set_performance_mode('high')
```

### For Raspberry Pi 3
```python
# In config.py
config.set_performance_mode('balanced')
```

### Power Saving
```python
# In config.py
config.set_performance_mode('power_save')
```

## 🎯 Detectable Objects

- **People**: Pedestrians, children
- **Vehicles**: Car, bus, truck, motorcycle
- **Bicycles**: Bicycle, scooter
- **Traffic Elements**: Traffic light, stop sign
- **Animals**: Cat, dog

## 🔊 Voice Alert Examples

- "Person ahead"
- "Warning! Very close obstacle"
- "Turn right"
- "Path is clear"
- "Stop"

## ⚙️ Advanced Settings

### Camera Settings
```python
config.update_camera_settings(
    width=320,    # Faster processing
    height=240,
    fps=10
)
```

### Detection Sensitivity
```python
config.update_detection_settings(
    confidence=0.3,  # More sensitive detection
    interval=0.05    # More frequent detection
)
```

### TTS Settings
```python
config.update_tts_settings(
    rate=120,      # Slower speech
    volume=0.8     # Lower volume
)
```

## 🐛 Troubleshooting

### Camera Won't Open
```bash
# Check camera permissions
sudo usermod -a -G video $USER
sudo reboot

# Test camera
raspistill -o test.jpg  # Raspberry Pi camera
fswebcam test.jpg       # USB camera
```

### No Sound Output
```bash
# Check sound card
aplay -l

# Adjust volume
alsamixer

# Test TTS
espeak "Test message"
```

### Low FPS
- Reduce camera resolution (320x240)
- Increase detection interval (0.2 seconds)
- Use lighter model instead of YOLOv8n

### High CPU Usage
```bash
# Check CPU frequency
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq

# Set GPU memory split
sudo raspi-config
# Advanced Options > Memory Split > 128
```

## 📊 Performance Metrics

| Model | Raspberry Pi 4 | Raspberry Pi 3B+ |
|-------|---------------|------------------|
| YOLOv8n | 10-15 FPS | 5-8 FPS |
| YOLOv8s | 6-10 FPS | 3-5 FPS |
| CPU Usage | 60-80% | 80-95% |
| RAM Usage | ~400MB | ~350MB |

## 🎬 Windows Testing

Test the system on Windows before deploying to Raspberry Pi:

```bash
python test_windows.py
```

Choose from 3 test modes:
1. **Visual Test** - Fast demo with simulated objects
2. **YOLO Detection** - Real object detection
3. **Full System** - YOLO + English voice alerts

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License. See `LICENSE` file for details.

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [OpenCV](https://opencv.org/)
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3)

## 📞 Contact

For questions:
- Use GitHub Issues
- Email: [project-email@example.com]

---

**Note**: This project is for educational and research purposes. Additional safety measures should be taken for real-world usage.
