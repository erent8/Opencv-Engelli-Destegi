#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Object Tracking Module
Tracks objects across frames to maintain stability and persistence
"""

import time
import math
from typing import List, Dict, Optional, Tuple
import numpy as np


class TrackedObject:
    """Represents a tracked object with history and stability"""
    
    def __init__(self, detection: Dict, track_id: int):
        """
        Initialize tracked object
        
        Args:
            detection: Initial detection data
            track_id: Unique tracking ID
        """
        self.track_id = track_id
        self.class_id = detection['class_id']
        self.class_name = detection['class_name']
        
        # Position and size tracking
        self.positions = [detection['center']]
        self.bboxes = [detection['bbox']]
        self.areas = [detection['area']]
        self.confidences = [detection['confidence']]
        
        # Time tracking
        self.first_seen = time.time()
        self.last_seen = time.time()
        self.last_alert_time = 0
        
        # Stability tracking
        self.consecutive_detections = 1
        self.missed_frames = 0
        self.is_stable = False
        self.min_stable_frames = 3  # Minimum frames to be considered stable
        
        # Distance tracking
        self.distances = []
        self.distance_history = []
        
        # Alert tracking
        self.alert_count = 0
        self.last_distance_alert = 0
    
    def update(self, detection: Dict):
        """
        Update tracked object with new detection
        
        Args:
            detection: New detection data
        """
        current_time = time.time()
        
        # Update position history (keep last 10 positions)
        self.positions.append(detection['center'])
        if len(self.positions) > 10:
            self.positions.pop(0)
        
        # Update other attributes
        self.bboxes.append(detection['bbox'])
        if len(self.bboxes) > 10:
            self.bboxes.pop(0)
            
        self.areas.append(detection['area'])
        if len(self.areas) > 10:
            self.areas.pop(0)
            
        self.confidences.append(detection['confidence'])
        if len(self.confidences) > 10:
            self.confidences.pop(0)
        
        # Update time and stability
        self.last_seen = current_time
        self.consecutive_detections += 1
        self.missed_frames = 0
        
        # Check if object is stable
        if self.consecutive_detections >= self.min_stable_frames:
            self.is_stable = True
        
        # Update distance if available
        if 'distance_meters' in detection:
            self.distances.append(detection['distance_meters'])
            if len(self.distances) > 5:
                self.distances.pop(0)
    
    def miss_frame(self):
        """Mark that object was missed in current frame"""
        self.missed_frames += 1
        self.consecutive_detections = 0
    
    def get_current_detection(self) -> Dict:
        """
        Get current detection data
        
        Returns:
            Dict: Current detection information
        """
        if not self.positions:
            return None
        
        # Use smoothed/averaged values for stability
        avg_confidence = sum(self.confidences) / len(self.confidences)
        current_bbox = self.bboxes[-1]
        current_center = self.positions[-1]
        current_area = self.areas[-1]
        
        # Calculate average distance if available
        avg_distance = None
        if self.distances:
            avg_distance = sum(self.distances) / len(self.distances)
        
        return {
            'track_id': self.track_id,
            'class_id': self.class_id,
            'class_name': self.class_name,
            'confidence': avg_confidence,
            'bbox': current_bbox,
            'center': current_center,
            'width': current_bbox[2] - current_bbox[0],
            'height': current_bbox[3] - current_bbox[1],
            'area': current_area,
            'distance_meters': avg_distance,
            'is_stable': self.is_stable,
            'age': time.time() - self.first_seen,
            'consecutive_detections': self.consecutive_detections,
            'alert_count': self.alert_count
        }
    
    def should_alert(self, alert_interval: float = 10.0) -> bool:
        """
        Check if object should trigger alert
        
        Args:
            alert_interval: Minimum seconds between alerts
            
        Returns:
            bool: Whether to alert
        """
        current_time = time.time()
        
        # Only alert for stable objects
        if not self.is_stable:
            return False
        
        # Check time interval
        if (current_time - self.last_alert_time) >= alert_interval:
            self.last_alert_time = current_time
            self.alert_count += 1
            return True
        
        return False
    
    def should_distance_alert(self, distance_alert_interval: float = 5.0) -> bool:
        """
        Check if object should trigger distance-specific alert
        
        Args:
            distance_alert_interval: Minimum seconds between distance alerts
            
        Returns:
            bool: Whether to give distance alert
        """
        current_time = time.time()
        
        if not self.is_stable or not self.distances:
            return False
        
        avg_distance = sum(self.distances) / len(self.distances)
        
        # More frequent alerts for closer objects
        if avg_distance < 3:  # Very close
            interval = distance_alert_interval / 2
        elif avg_distance < 6:  # Close
            interval = distance_alert_interval
        else:  # Far
            interval = distance_alert_interval * 2
        
        if (current_time - self.last_distance_alert) >= interval:
            self.last_distance_alert = current_time
            return True
        
        return False
    
    def is_expired(self, max_age: float = 5.0, max_missed: int = 10) -> bool:
        """
        Check if tracked object should be removed
        
        Args:
            max_age: Maximum age without updates (seconds)
            max_missed: Maximum consecutive missed frames
            
        Returns:
            bool: Whether object is expired
        """
        current_time = time.time()
        age_expired = (current_time - self.last_seen) > max_age
        missed_expired = self.missed_frames > max_missed
        
        return age_expired or missed_expired


class ObjectTracker:
    """
    Multi-object tracker for maintaining object persistence
    """
    
    def __init__(self, config):
        """
        Initialize object tracker
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.tracked_objects = {}  # track_id -> TrackedObject
        self.next_track_id = 1
        self.max_distance_threshold = 100  # Maximum pixel distance for matching
        
    def calculate_iou(self, box1: Tuple, box2: Tuple) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes
        
        Args:
            box1: First bounding box (x1, y1, x2, y2)
            box2: Second bounding box (x1, y1, x2, y2)
            
        Returns:
            float: IoU value between 0 and 1
        """
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_distance(self, center1: Tuple, center2: Tuple) -> float:
        """
        Calculate Euclidean distance between two centers
        
        Args:
            center1: First center point (x, y)
            center2: Second center point (x, y)
            
        Returns:
            float: Distance in pixels
        """
        return math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def match_detections(self, detections: List[Dict]) -> Dict:
        """
        Match new detections with existing tracked objects
        
        Args:
            detections: List of new detections
            
        Returns:
            Dict: Matching results
        """
        matches = {}
        unmatched_detections = []
        unmatched_tracks = list(self.tracked_objects.keys())
        
        if not detections:
            return {
                'matches': matches,
                'unmatched_detections': unmatched_detections,
                'unmatched_tracks': unmatched_tracks
            }
        
        # Calculate similarity matrix
        similarity_matrix = []
        for detection in detections:
            row = []
            for track_id in self.tracked_objects:
                tracked_obj = self.tracked_objects[track_id]
                last_detection = tracked_obj.get_current_detection()
                
                if last_detection and detection['class_id'] == last_detection['class_id']:
                    # Calculate IoU similarity
                    iou = self.calculate_iou(detection['bbox'], last_detection['bbox'])
                    
                    # Calculate distance similarity
                    distance = self.calculate_distance(detection['center'], last_detection['center'])
                    distance_similarity = max(0, 1 - distance / self.max_distance_threshold)
                    
                    # Combined similarity
                    similarity = (iou * 0.7) + (distance_similarity * 0.3)
                else:
                    similarity = 0.0
                
                row.append(similarity)
            similarity_matrix.append(row)
        
        # Find best matches using greedy approach
        used_tracks = set()
        for i, detection in enumerate(detections):
            best_similarity = 0.3  # Minimum threshold
            best_track_idx = -1
            
            for j, track_id in enumerate(self.tracked_objects):
                if track_id not in used_tracks and similarity_matrix[i][j] > best_similarity:
                    best_similarity = similarity_matrix[i][j]
                    best_track_idx = j
            
            if best_track_idx >= 0:
                track_id = list(self.tracked_objects.keys())[best_track_idx]
                matches[i] = track_id
                used_tracks.add(track_id)
                if track_id in unmatched_tracks:
                    unmatched_tracks.remove(track_id)
            else:
                unmatched_detections.append(i)
        
        return {
            'matches': matches,
            'unmatched_detections': unmatched_detections,
            'unmatched_tracks': unmatched_tracks
        }
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        """
        Update tracker with new detections
        
        Args:
            detections: List of new detections
            
        Returns:
            List[Dict]: List of tracked objects
        """
        # Add distance estimation if not present
        for detection in detections:
            if 'distance_meters' not in detection:
                # Simple distance estimation based on object size
                detection['distance_meters'] = self.estimate_distance(detection)
        
        # Match detections with existing tracks
        matching_result = self.match_detections(detections)
        
        # Update matched tracks
        for det_idx, track_id in matching_result['matches'].items():
            self.tracked_objects[track_id].update(detections[det_idx])
        
        # Create new tracks for unmatched detections
        for det_idx in matching_result['unmatched_detections']:
            new_track = TrackedObject(detections[det_idx], self.next_track_id)
            self.tracked_objects[self.next_track_id] = new_track
            self.next_track_id += 1
        
        # Mark unmatched tracks as missed
        for track_id in matching_result['unmatched_tracks']:
            self.tracked_objects[track_id].miss_frame()
        
        # Remove expired tracks
        expired_tracks = []
        for track_id, tracked_obj in self.tracked_objects.items():
            if tracked_obj.is_expired():
                expired_tracks.append(track_id)
        
        for track_id in expired_tracks:
            del self.tracked_objects[track_id]
        
        # Return stable tracked objects
        stable_objects = []
        for tracked_obj in self.tracked_objects.values():
            if tracked_obj.is_stable:
                detection = tracked_obj.get_current_detection()
                if detection:
                    stable_objects.append(detection)
        
        return stable_objects
    
    def estimate_distance(self, detection: Dict) -> float:
        """
        Estimate distance based on object size and type
        
        Args:
            detection: Detection data
            
        Returns:
            float: Estimated distance in meters
        """
        class_name = detection['class_name']
        area = detection['area']
        
        # Rough distance estimation based on typical object sizes
        # These are approximations and would need calibration for real use
        typical_areas = {
            'person': 50000,     # Person at ~3m distance
            'car': 80000,        # Car at ~10m distance  
            'bicycle': 25000,    # Bicycle at ~5m distance
            'motorcycle': 30000, # Motorcycle at ~6m distance
            'bus': 120000,       # Bus at ~15m distance
            'truck': 100000,     # Truck at ~12m distance
        }
        
        if class_name in typical_areas:
            typical_area = typical_areas[class_name]
            # Distance inversely proportional to square root of area
            estimated_distance = math.sqrt(typical_area / max(area, 1000)) * 3
            return max(1.0, min(50.0, estimated_distance))  # Clamp between 1-50m
        
        # Default estimation
        return 5.0
    
    def get_objects_for_alerts(self) -> List[Dict]:
        """
        Get objects that should trigger alerts
        
        Returns:
            List[Dict]: Objects ready for alerts
        """
        alert_objects = []
        
        for tracked_obj in self.tracked_objects.values():
            if tracked_obj.should_alert(self.config.ALERT_INTERVAL):
                detection = tracked_obj.get_current_detection()
                if detection:
                    detection['should_alert'] = True
                    detection['should_distance_alert'] = tracked_obj.should_distance_alert()
                    alert_objects.append(detection)
        
        return alert_objects
    
    def get_tracking_stats(self) -> Dict:
        """
        Get tracking statistics
        
        Returns:
            Dict: Tracking statistics
        """
        total_tracks = len(self.tracked_objects)
        stable_tracks = sum(1 for obj in self.tracked_objects.values() if obj.is_stable)
        
        return {
            'total_tracks': total_tracks,
            'stable_tracks': stable_tracks,
            'next_id': self.next_track_id
        }
