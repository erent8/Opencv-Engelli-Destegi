# 🦽 Raspberry Pi Disability Assistance System

Real-time object detection and voice alert system running on Raspberry Pi. Provides navigation support for visually impaired individuals using YOLOv8.

## 🌟 Features

- **Real-Time Object Detection**: YOLOv8 allows you to detect people, vehicles, bicycles, etc. Detects objects
- **Voice Warning System**: Voice prompts and directions in Turkish
- **3-Zone Navigation**: Directions are given using left, center, and right zone analysis
- **Proximity Sense**: Distance calculation based on object size
- **Raspberry Pi Optimization**: Low power consumption and high performance
- **Modular Structure**: Easy customization and development

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

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
pip install -r requirements.txt
```

### 3. Download the YOLOv8 Model
```bash
# Lightweight model (recommended)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -P models/

# Or automatic download with Python
python -c "from ultralytics import YOLO; YOLO('models/yolov8n.pt')"
```

### 4. Enable the Camera
```bash
# For Raspberry Pi camera
sudo raspi-config
# Interface Options > Camera > Enable

# USB camera control
lsusb
v4l2-ctl --list-devices
```

## 🎮 Usage

### Basic Operation
```bash
PYTHONPATH=src python -m assistive_vision
```

For Windows PowerShell:
```powershell
$env:PYTHONPATH="src"
python -m assistive_vision
```

### Keyboard Shortcuts
- `q`: Exit
- `s`: Toggle sound
- `d`: Toggle debug mode

### Configuration
You can change the settings in the `src/assistive_vision/config.py` file:

```python
# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 15

# Detection sensitivity
CONFIDENCE_THRESHOLD = 0.5

# Sound alert settings
TTS_RATE = 150 # Speech rate
TTS_VOLUME = 0.9 # Volume
```

## 📁 Project Structure

```
.
+-- docs/
+-- scripts/
| +-- install.sh
| +-- run_system.py
+-- src/
| +-- assistive_vision/
| +-- __init__.py
| +-- __main__.py
| +-- system.py
| +-- config.py
| +-- detection_logger.py
| +--distance_checker.py
| +-- navigation_guide.py
| +-- object_detector.py
| +-- object_tracker.py
| +-- voice_alert.py
+-- tests/
| +-- test_continuous_alerts.py
| +-- test_windows.py
+--data/
+--logs/
+-- models/
| +-- yolov8n.pt
+-- requirements.txt
+-- README.md
+-- AGENTS.md
```

## 🔧 Performance Optimization

### For Raspberry Pi 4
```python
# in config.py
config.set_performance_mode('high')
```

### For Raspberry Pi 3
```python
# in config.py
config.set_performance_mode('balanced')
```

### Power Saving
```python
# in config.py
config.set_performance_mode('power_save')
```

## 🎯 Detectable Objects

- **People**: Pedestrians, children
- **Vehicle**: Car, bus, truck, motorcycle
- **Bicycles**: Bicycle, scooter
- **Traffic Elements**: Traffic light, stop sign
- **Animals**: Cat, dog

## 🔊 Audio Warning Examples

- "Person in front of you"
- "Caution! Very close obstacle"
- "Turn right"
- "Road is clear"
- "Stop"

## ⚙️ Advanced Settings

### Camera Settings
```python
config.update_camera_settings(
width=320, # For faster processing
height=240,
fps=10
)
```

### Detection Sensitivity
```python
config.update_detection_settings(
confidence=0.3, # More sensitive detection
interval=0.05 # More frequent detection
)
```

### TTS Settings
```python
config.update_tts_settings(
rate=120, # Speak slower

volume=0.8 # Lower volume
)
```

## 🐛 Troubleshooting

### Camera Won't Open
````bash
# Check camera permissions
sudo usermod -a -G video $USER
sudo reboot

# Camera test
raspistill -o test.jpg # Raspberry Pi camera
fswebcam test.jpg # USB camera
```

### No Sound
````bash
# Check sound card
aplay -l

# Adjust volume
alsamixer

# TTS test
espeak "Test message"
```

### Low FPS
- Lower camera resolution (320x240)
- Increase detection interval (0.2 seconds)
- Use lighter version instead of YOLOv8n

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
|-------|------------|------------------|
| YOLOv8n | 10-15 FPS | 5-8 FPS |
| YOLOv8s | 6-10 FPS | 3-5 FPS |
| CPU Usage | 60-80% | 80-95% |
| RAM Usage | ~400MB | ~350MB |

## 🤝 Contributing

1. Fork
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'New feature added'`)
4. Push the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🙏 Thanks

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [OpenCV](https://opencv.org/)
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3)

## 📞 Contact

For questions:
- Use GitHub Issues
- Email: [erenterzi@protonmail.com]

---

**Note**: This project is for educational and research purposes. Additional security measures should be taken in real-world use.
