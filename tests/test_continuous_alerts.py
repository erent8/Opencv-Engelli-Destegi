#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Continuous Alerts Test Script
Simple test to verify continuous voice alerts are working
"""

import time
import threading
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from assistive_vision.voice_alert import VoiceAlert
from assistive_vision.config import Config

def test_continuous_alerts():
    """Test continuous voice alerts with simulated objects"""
    
    print("🧪 Testing Continuous Voice Alerts")
    print("=" * 40)
    
    # Initialize components
    config = Config()
    voice_alert = VoiceAlert(config)
    
    # Test objects with different distances
    test_objects = [
        {
            'track_id': 1,
            'class_name': 'person',
            'distance_meters': 2.0,  # Very close
            'should_alert': True,
            'should_distance_alert': True,
            'is_stable': True
        },
        {
            'track_id': 2,
            'class_name': 'car',
            'distance_meters': 5.0,  # Close
            'should_alert': True,
            'should_distance_alert': True,
            'is_stable': True
        },
        {
            'track_id': 3,
            'class_name': 'bicycle',
            'distance_meters': 10.0,  # Far
            'should_alert': True,
            'should_distance_alert': True,
            'is_stable': True
        }
    ]
    
    print("🔊 Starting continuous alerts test...")
    print("You should hear alerts every few seconds for each object:")
    print("- Person at 2.0m (every 3-5 seconds)")
    print("- Car at 5.0m (every 6-8 seconds)")
    print("- Bicycle at 10.0m (every 10-12 seconds)")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Run for 60 seconds
        start_time = time.time()
        last_alerts = {}
        
        while (time.time() - start_time) < 60:
            current_time = time.time()
            
            for obj in test_objects:
                track_id = obj['track_id']
                distance = obj['distance_meters']
                
                # Determine alert interval based on distance
                if distance < 3:
                    alert_interval = 3.0
                elif distance < 6:
                    alert_interval = 6.0
                else:
                    alert_interval = 10.0
                
                # Check if it's time to alert
                last_time = last_alerts.get(track_id, 0)
                if (current_time - last_time) >= alert_interval:
                    last_alerts[track_id] = current_time
                    
                    # Send alert in separate thread
                    threading.Thread(
                        target=voice_alert.alert_close_object,
                        args=(obj,),
                        daemon=True
                    ).start()
                    
                    print(f"🔊 Alert sent: {obj['class_name']} ID:{track_id} at {distance}m")
            
            time.sleep(0.5)  # Check every 0.5 seconds
    
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    
    finally:
        voice_alert.cleanup()
        print("✅ Test completed")

if __name__ == "__main__":
    test_continuous_alerts()
