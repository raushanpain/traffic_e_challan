import cv2
import numpy as np
import tensorflow as tf
import os
import time
from django.conf import settings
from django.utils import timezone
import threading
import json

class ObjectDetector:
    """Object detection class for processing video streams"""
    
    def __init__(self):
        self.model_name = 'ssd_mobilenet_v1_coco_11_06_2017'
        self.model_path = os.path.join(settings.BASE_DIR, 'models', self.model_name)
        self.labels_path = os.path.join(settings.BASE_DIR, 'data', 'mscoco_label_map.pbtxt')
        self.detection_graph = None
        self.category_index = None
        self.is_processing = False
        
        # Initialize the model
        self._load_model()
    
    def _load_model(self):
        """Load the TensorFlow model and labels"""
        try:
            # Check if model exists
            model_file = os.path.join(self.model_path, 'frozen_inference_graph.pb')
            if not os.path.exists(model_file):
                print(f"Model file not found: {model_file}")
                print("Please download the model first")
                return False
            
            # Load the model
            self.detection_graph = tf.Graph()
            with self.detection_graph.as_default():
                od_graph_def = tf.GraphDef()
                with tf.gfile.GFile(model_file, 'rb') as fid:
                    serialized_graph = fid.read()
                    od_graph_def.ParseFromString(serialized_graph)
                    tf.import_graph_def(od_graph_def, name='')
            
            # Load labels
            if os.path.exists(self.labels_path):
                from utils import label_map_util
                label_map = label_map_util.load_labelmap(self.labels_path)
                categories = label_map_util.convert_label_map_to_categories(
                    label_map, max_num_classes=90, use_display_name=True)
                self.category_index = label_map_util.create_category_index(categories)
            else:
                # Create a basic category index if labels file doesn't exist
                self.category_index = {i: {'name': f'Class_{i}'} for i in range(90)}
            
            print("Model loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def start_detection(self, session, video_source):
        """Start object detection on a video source"""
        if not self.detection_graph:
            raise Exception("Model not loaded")
        
        # Start detection in a separate thread
        detection_thread = threading.Thread(
            target=self._process_video,
            args=(session, video_source)
        )
        detection_thread.daemon = True
        detection_thread.start()
        
        return True
    
    def _process_video(self, session, video_source):
        """Process video for object detection"""
        try:
            self.is_processing = True
            
            # Open video source
            if video_source.source_type == 'CAMERA':
                cap = cv2.VideoCapture(video_source.source_url)
            elif video_source.source_type == 'FILE':
                cap = cv2.VideoCapture(video_source.file_path)
            else:
                raise Exception(f"Unsupported source type: {video_source.source_type}")
            
            if not cap.isOpened():
                raise Exception("Could not open video source")
            
            frame_count = 0
            total_detections = 0
            
            with self.detection_graph.as_default():
                with tf.Session(graph=self.detection_graph) as sess:
                    # Get tensors
                    image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                    detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                    detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                    detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                    num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
                    
                    while self.is_processing and session.status == 'ACTIVE':
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        frame_count += 1
                        start_time = time.time()
                        
                        # Process frame
                        detection_result = self._detect_objects(
                            frame, sess, image_tensor, detection_boxes,
                            detection_scores, detection_classes, num_detections
                        )
                        
                        processing_time = time.time() - start_time
                        
                        if detection_result:
                            # Save detection result to database
                            from object_detection.models import DetectionResult
                            
                            DetectionResult.objects.create(
                                session=session,
                                video_source=video_source,
                                frame_number=frame_count,
                                timestamp=timezone.now(),
                                detected_objects=detection_result['objects'],
                                confidence_scores=detection_result['scores'],
                                bounding_boxes=detection_result['boxes'],
                                processing_time=processing_time
                            )
                            
                            total_detections += len(detection_result['objects'])
                        
                        # Update session statistics
                        session.total_frames_processed = frame_count
                        session.total_detections = total_detections
                        session.save()
                        
                        # Process every 5th frame to avoid overwhelming the database
                        if frame_count % 5 != 0:
                            continue
                        
                        # Check if session should be stopped
                        session.refresh_from_db()
                        if session.status != 'ACTIVE':
                            break
            
            # Clean up
            cap.release()
            session.status = 'COMPLETED'
            session.ended_at = timezone.now()
            session.save()
            
        except Exception as e:
            print(f"Error in video processing: {str(e)}")
            session.status = 'ERROR'
            session.processing_notes = str(e)
            session.save()
        
        finally:
            self.is_processing = False
    
    def _detect_objects(self, frame, sess, image_tensor, detection_boxes,
                        detection_scores, detection_classes, num_detections):
        """Detect objects in a single frame"""
        try:
            # Preprocess frame
            frame_expanded = np.expand_dims(frame, axis=0)
            
            # Run detection
            (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections],
                feed_dict={image_tensor: frame_expanded}
            )
            
            # Filter detections by confidence
            confidence_threshold = 0.5
            valid_detections = scores[0] > confidence_threshold
            
            if not np.any(valid_detections):
                return None
            
            # Extract valid detections
            valid_boxes = boxes[0][valid_detections]
            valid_scores = scores[0][valid_detections]
            valid_classes = classes[0][valid_detections]
            
            # Convert to list format for JSON serialization
            detection_result = {
                'objects': valid_classes.tolist(),
                'scores': valid_scores.tolist(),
                'boxes': valid_boxes.tolist()
            }
            
            return detection_result
            
        except Exception as e:
            print(f"Error in object detection: {str(e)}")
            return None
    
    def stop_detection(self):
        """Stop the detection process"""
        self.is_processing = False
    
    def get_detection_statistics(self):
        """Get current detection statistics"""
        return {
            'is_processing': self.is_processing,
            'model_loaded': self.detection_graph is not None,
            'model_name': self.model_name
        }
    
    def process_single_image(self, image_path):
        """Process a single image for object detection"""
        if not self.detection_graph:
            raise Exception("Model not loaded")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise Exception(f"Could not load image: {image_path}")
        
        # Process image
        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:
                image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
                
                detection_result = self._detect_objects(
                    image, sess, image_tensor, detection_boxes,
                    detection_scores, detection_classes, num_detections
                )
        
        return detection_result
    
    def draw_detections(self, frame, detection_result):
        """Draw detection boxes on a frame"""
        if not detection_result:
            return frame
        
        frame_with_boxes = frame.copy()
        
        for i, (box, score, class_id) in enumerate(zip(
            detection_result['boxes'],
            detection_result['scores'],
            detection_result['objects']
        )):
            # Convert normalized coordinates to pixel coordinates
            h, w, _ = frame.shape
            ymin, xmin, ymax, xmax = box
            
            x1 = int(xmin * w)
            y1 = int(ymin * h)
            x2 = int(xmax * w)
            y2 = int(ymax * h)
            
            # Draw bounding box
            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            class_name = self.category_index.get(int(class_id), {}).get('name', f'Class_{class_id}')
            label = f"{class_name}: {score:.2f}"
            
            # Calculate text position
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame_with_boxes, (x1, y1 - text_size[1] - 10), 
                         (x1 + text_size[0], y1), (0, 255, 0), -1)
            cv2.putText(frame_with_boxes, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame_with_boxes
