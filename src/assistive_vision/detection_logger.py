#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detection Logger Module
Logs all object detections to CSV files for analysis
"""

import csv
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import threading


class DetectionLogger:
    """
    CSV logging system for object detections
    """
    
    def __init__(self, config, log_dir: str = "logs"):
        """
        Initialize detection logger
        
        Args:
            config: Configuration object
            log_dir: Directory to store log files
        """
        self.config = config
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Generate unique session ID
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV file paths
        self.detections_file = self.log_dir / f"detections_{self.session_id}.csv"
        self.alerts_file = self.log_dir / f"alerts_{self.session_id}.csv"
        self.session_file = self.log_dir / f"session_{self.session_id}.csv"
        
        # Threading for file operations
        self.write_lock = threading.Lock()
        self.log_queue = []
        
        # Session statistics
        self.session_stats = {
            'start_time': time.time(),
            'total_detections': 0,
            'total_alerts': 0,
            'objects_detected': set(),
            'frame_count': 0
        }
        
        self.initialize_csv_files()
        print(f"📊 Detection logging started: Session {self.session_id}")
    
    def initialize_csv_files(self):
        """Initialize CSV files with headers"""
        
        # Detections CSV header
        detections_header = [
            'timestamp',
            'session_id',
            'frame_number',
            'track_id',
            'class_id',
            'class_name',
            'confidence',
            'bbox_x1',
            'bbox_y1', 
            'bbox_x2',
            'bbox_y2',
            'center_x',
            'center_y',
            'width',
            'height',
            'area',
            'distance_meters',
            'is_stable',
            'age_seconds',
            'zone'  # left, center, right
        ]
        
        # Alerts CSV header
        alerts_header = [
            'timestamp',
            'session_id',
            'track_id',
            'class_name',
            'alert_type',
            'message',
            'distance_meters',
            'urgency',
            'zone'
        ]
        
        # Session CSV header
        session_header = [
            'timestamp',
            'session_id',
            'event_type',
            'data'
        ]
        
        try:
            # Write headers
            with open(self.detections_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(detections_header)
            
            with open(self.alerts_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(alerts_header)
            
            with open(self.session_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(session_header)
            
            # Log session start
            self.log_session_event('session_start', {
                'session_id': self.session_id,
                'start_time': datetime.now().isoformat(),
                'config': {
                    'camera_width': self.config.CAMERA_WIDTH,
                    'camera_height': self.config.CAMERA_HEIGHT,
                    'confidence_threshold': self.config.CONFIDENCE_THRESHOLD
                }
            })
            
        except Exception as e:
            print(f"❌ CSV initialization error: {e}")
    
    def determine_zone(self, center_x: int, frame_width: int) -> str:
        """
        Determine which zone the object is in
        
        Args:
            center_x: Object center X coordinate
            frame_width: Frame width
            
        Returns:
            str: Zone name (left, center, right)
        """
        left_boundary = frame_width // 3
        right_boundary = 2 * frame_width // 3
        
        if center_x < left_boundary:
            return 'left'
        elif center_x < right_boundary:
            return 'center'
        else:
            return 'right'
    
    def log_detection(self, detection: Dict, frame_number: int, frame_width: int):
        """
        Log a single detection to CSV
        
        Args:
            detection: Detection data
            frame_number: Current frame number
            frame_width: Frame width for zone calculation
        """
        if not self.config.LOG_DETECTIONS:
            return
        
        try:
            timestamp = datetime.now().isoformat()
            zone = self.determine_zone(detection['center'][0], frame_width)
            
            # Prepare row data
            row = [
                timestamp,
                self.session_id,
                frame_number,
                detection.get('track_id', ''),
                detection.get('class_id', ''),
                detection.get('class_name', ''),
                detection.get('confidence', 0),
                detection['bbox'][0] if 'bbox' in detection else '',
                detection['bbox'][1] if 'bbox' in detection else '',
                detection['bbox'][2] if 'bbox' in detection else '',
                detection['bbox'][3] if 'bbox' in detection else '',
                detection['center'][0] if 'center' in detection else '',
                detection['center'][1] if 'center' in detection else '',
                detection.get('width', ''),
                detection.get('height', ''),
                detection.get('area', ''),
                detection.get('distance_meters', ''),
                detection.get('is_stable', False),
                detection.get('age', ''),
                zone
            ]
            
            # Write to CSV
            with self.write_lock:
                with open(self.detections_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
            
            # Update statistics
            self.session_stats['total_detections'] += 1
            self.session_stats['objects_detected'].add(detection.get('class_name', 'unknown'))
            
        except Exception as e:
            print(f"❌ Detection logging error: {e}")
    
    def log_detections_batch(self, detections: List[Dict], frame_number: int, frame_width: int):
        """
        Log multiple detections in batch
        
        Args:
            detections: List of detections
            frame_number: Current frame number
            frame_width: Frame width
        """
        if not detections:
            return
        
        for detection in detections:
            self.log_detection(detection, frame_number, frame_width)
        
        # Update frame count
        self.session_stats['frame_count'] = frame_number
    
    def log_alert(self, detection: Dict, alert_type: str, message: str, urgency: int):
        """
        Log voice alert to CSV
        
        Args:
            detection: Detection that triggered alert
            alert_type: Type of alert
            message: Alert message
            urgency: Alert urgency level
        """
        try:
            timestamp = datetime.now().isoformat()
            
            row = [
                timestamp,
                self.session_id,
                detection.get('track_id', ''),
                detection.get('class_name', ''),
                alert_type,
                message,
                detection.get('distance_meters', ''),
                urgency,
                'unknown'  # Zone can be calculated if needed
            ]
            
            # Write to CSV
            with self.write_lock:
                with open(self.alerts_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
            
            # Update statistics
            self.session_stats['total_alerts'] += 1
            
        except Exception as e:
            print(f"❌ Alert logging error: {e}")
    
    def log_session_event(self, event_type: str, data: Dict):
        """
        Log session events (start, stop, errors, etc.)
        
        Args:
            event_type: Type of event
            data: Event data
        """
        try:
            timestamp = datetime.now().isoformat()
            
            row = [
                timestamp,
                self.session_id,
                event_type,
                str(data)
            ]
            
            with self.write_lock:
                with open(self.session_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
                    
        except Exception as e:
            print(f"❌ Session logging error: {e}")
    
    def get_session_stats(self) -> Dict:
        """
        Get current session statistics
        
        Returns:
            Dict: Session statistics
        """
        current_time = time.time()
        duration = current_time - self.session_stats['start_time']
        
        return {
            'session_id': self.session_id,
            'duration_seconds': duration,
            'duration_formatted': f"{int(duration//60)}:{int(duration%60):02d}",
            'total_detections': self.session_stats['total_detections'],
            'total_alerts': self.session_stats['total_alerts'],
            'frame_count': self.session_stats['frame_count'],
            'unique_objects': len(self.session_stats['objects_detected']),
            'objects_list': list(self.session_stats['objects_detected']),
            'avg_detections_per_frame': (
                self.session_stats['total_detections'] / max(self.session_stats['frame_count'], 1)
            )
        }
    
    def generate_summary_report(self) -> str:
        """
        Generate text summary report
        
        Returns:
            str: Summary report
        """
        stats = self.get_session_stats()
        
        report = f"""
📊 DETECTION SESSION SUMMARY
{'='*50}
Session ID: {stats['session_id']}
Duration: {stats['duration_formatted']} (mm:ss)
Total Frames: {stats['frame_count']}
Total Detections: {stats['total_detections']}
Total Alerts: {stats['total_alerts']}
Unique Objects: {stats['unique_objects']}
Objects Detected: {', '.join(stats['objects_list'])}
Avg Detections/Frame: {stats['avg_detections_per_frame']:.2f}

📁 Log Files:
- Detections: {self.detections_file.name}
- Alerts: {self.alerts_file.name}  
- Session: {self.session_file.name}
{'='*50}
        """
        
        return report
    
    def cleanup(self):
        """Clean up and finalize logging"""
        try:
            # Log session end
            stats = self.get_session_stats()
            self.log_session_event('session_end', stats)
            
            # Generate and save summary
            summary = self.generate_summary_report()
            summary_file = self.log_dir / f"summary_{self.session_id}.txt"
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"📊 Logging session ended: {self.session_id}")
            print(summary)
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
    
    def export_to_json(self) -> str:
        """
        Export session data to JSON format
        
        Returns:
            str: JSON file path
        """
        try:
            import json
            
            json_file = self.log_dir / f"session_{self.session_id}.json"
            stats = self.get_session_stats()
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
            
            return str(json_file)
            
        except Exception as e:
            print(f"❌ JSON export error: {e}")
            return ""
