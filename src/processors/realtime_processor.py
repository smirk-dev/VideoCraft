import asyncio
import concurrent.futures
import multiprocessing as mp
from typing import Dict, List, Optional, Callable, Any
import logging
import time
import numpy as np
from dataclasses import dataclass
from enum import Enum
import queue
import threading

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProcessingTask:
    id: str
    type: str
    data: Any
    priority: int = 0
    callback: Optional[Callable] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: float = 0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class RealTimeProcessor:
    """
    High-performance real-time video processing system with parallel execution,
    caching, and optimized memory management.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.max_workers = config.get('max_workers', mp.cpu_count())
        self.batch_size = config.get('batch_size', 8)
        self.cache_size = config.get('cache_size', 1000)
        
        # Processing queues
        self.task_queue = queue.PriorityQueue()
        self.result_cache = {}
        self.active_tasks = {}
        
        # Thread pool for I/O operations
        self.io_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        # Process pool for CPU-intensive tasks
        self.cpu_executor = concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers)
        
        # Real-time streaming support
        self.stream_processors = {}
        self.is_running = False
        
        # Performance monitoring
        self.performance_stats = {
            'tasks_processed': 0,
            'average_processing_time': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
    async def start_processing(self):
        """Start the real-time processing system."""
        self.is_running = True
        
        # Start background tasks
        asyncio.create_task(self._process_task_queue())
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._cleanup_cache())
        
        logger.info("Real-time processor started")
    
    async def stop_processing(self):
        """Stop the processing system and cleanup resources."""
        self.is_running = False
        
        # Shutdown executors
        self.io_executor.shutdown(wait=True)
        self.cpu_executor.shutdown(wait=True)
        
        logger.info("Real-time processor stopped")
    
    async def submit_task(self, 
                         task_type: str, 
                         data: Any, 
                         priority: int = 0,
                         callback: Optional[Callable] = None) -> str:
        """
        Submit a task for processing.
        
        Args:
            task_type: Type of task (video_analysis, audio_analysis, etc.)
            data: Task data
            priority: Task priority (higher = more urgent)
            callback: Optional callback function for results
            
        Returns:
            Task ID for tracking
        """
        task_id = f"{task_type}_{int(time.time() * 1000000)}"
        
        task = ProcessingTask(
            id=task_id,
            type=task_type,
            data=data,
            priority=priority,
            callback=callback,
            created_at=time.time()
        )
        
        # Check cache first
        cache_key = self._generate_cache_key(task_type, data)
        if cache_key in self.result_cache:
            task.result = self.result_cache[cache_key]
            task.status = ProcessingStatus.COMPLETED
            self.performance_stats['cache_hits'] += 1
            
            if callback:
                await self._execute_callback(callback, task.result)
        else:
            self.performance_stats['cache_misses'] += 1
            self.task_queue.put((priority, time.time(), task))
            self.active_tasks[task_id] = task
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[ProcessingTask]:
        """Get status of a specific task."""
        return self.active_tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = ProcessingStatus.CANCELLED
            return True
        return False
    
    async def process_video_stream(self, 
                                  stream_source: str,
                                  processors: List[str],
                                  callback: Callable) -> str:
        """
        Process real-time video stream.
        
        Args:
            stream_source: Video stream source (file, webcam, network)
            processors: List of processors to apply
            callback: Callback for streaming results
            
        Returns:
            Stream ID for management
        """
        stream_id = f"stream_{int(time.time() * 1000)}"
        
        stream_processor = StreamProcessor(
            stream_id=stream_id,
            source=stream_source,
            processors=processors,
            callback=callback,
            config=self.config
        )
        
        self.stream_processors[stream_id] = stream_processor
        
        # Start processing in background
        asyncio.create_task(stream_processor.start())
        
        return stream_id
    
    async def stop_video_stream(self, stream_id: str) -> bool:
        """Stop a video stream."""
        if stream_id in self.stream_processors:
            await self.stream_processors[stream_id].stop()
            del self.stream_processors[stream_id]
            return True
        return False
    
    async def _process_task_queue(self):
        """Background task to process the task queue."""
        while self.is_running:
            try:
                # Get task from queue (blocking with timeout)
                try:
                    priority, timestamp, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process task
                await self._execute_task(task)
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in task processing: {e}")
                await asyncio.sleep(0.1)
    
    async def _execute_task(self, task: ProcessingTask):
        """Execute a single task."""
        task.status = ProcessingStatus.PROCESSING
        task.started_at = time.time()
        
        try:
            # Route task to appropriate processor
            if task.type == 'video_analysis':
                result = await self._process_video_analysis(task.data)
            elif task.type == 'audio_analysis':
                result = await self._process_audio_analysis(task.data)
            elif task.type == 'emotion_analysis':
                result = await self._process_emotion_analysis(task.data)
            elif task.type == 'scene_detection':
                result = await self._process_scene_detection(task.data)
            else:
                raise ValueError(f"Unknown task type: {task.type}")
            
            task.result = result
            task.status = ProcessingStatus.COMPLETED
            
            # Cache result
            cache_key = self._generate_cache_key(task.type, task.data)
            self._update_cache(cache_key, result)
            
            # Execute callback if provided
            if task.callback:
                await self._execute_callback(task.callback, result)
                
        except Exception as e:
            task.error = str(e)
            task.status = ProcessingStatus.FAILED
            logger.error(f"Task {task.id} failed: {e}")
        
        finally:
            task.completed_at = time.time()
            processing_time = task.completed_at - task.started_at
            
            # Update performance stats
            self._update_performance_stats(processing_time)
            
            # Remove from active tasks after a delay
            asyncio.create_task(self._cleanup_task(task.id, delay=300))  # 5 minutes
    
    async def _process_video_analysis(self, data: Dict) -> Dict:
        """Process video analysis task."""
        video_path = data['video_path']
        frame_interval = data.get('frame_interval', 1.0)
        
        # Use process pool for CPU-intensive video processing
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.cpu_executor,
            self._cpu_video_analysis,
            video_path,
            frame_interval
        )
        
        return result
    
    async def _process_audio_analysis(self, data: Dict) -> Dict:
        """Process audio analysis task."""
        audio_path = data['audio_path']
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.cpu_executor,
            self._cpu_audio_analysis,
            audio_path
        )
        
        return result
    
    async def _process_emotion_analysis(self, data: Dict) -> Dict:
        """Process emotion analysis task."""
        # Use GPU if available for AI models
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.io_executor,  # I/O bound due to model inference
            self._gpu_emotion_analysis,
            data
        )
        
        return result
    
    async def _process_scene_detection(self, data: Dict) -> Dict:
        """Process scene detection task."""
        video_path = data['video_path']
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.cpu_executor,
            self._cpu_scene_detection,
            video_path
        )
        
        return result
    
    def _cpu_video_analysis(self, video_path: str, frame_interval: float) -> Dict:
        """CPU-intensive video analysis (runs in process pool)."""
        import cv2
        
        # This is a simplified version - implement full analysis
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        results = {
            'fps': fps,
            'frame_count': frame_count,
            'duration': frame_count / fps if fps > 0 else 0,
            'frames_analyzed': 0,
            'visual_features': []
        }
        
        frame_step = int(fps * frame_interval)
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_step == 0:
                # Simplified feature extraction
                features = self._extract_frame_features(frame)
                results['visual_features'].append({
                    'timestamp': frame_idx / fps,
                    'features': features
                })
                results['frames_analyzed'] += 1
            
            frame_idx += 1
        
        cap.release()
        return results
    
    def _extract_frame_features(self, frame: np.ndarray) -> Dict:
        """Extract basic visual features from frame."""
        # Simplified feature extraction
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        return {
            'brightness': np.mean(gray),
            'contrast': np.std(gray),
            'edges': cv2.Laplacian(gray, cv2.CV_64F).var(),
            'size': frame.shape[:2]
        }
    
    def _cpu_audio_analysis(self, audio_path: str) -> Dict:
        """CPU-intensive audio analysis."""
        try:
            import librosa
            
            y, sr = librosa.load(audio_path)
            
            # Extract audio features
            features = {
                'duration': len(y) / sr,
                'sample_rate': sr,
                'rms_energy': librosa.feature.rms(y=y)[0],
                'spectral_centroid': librosa.feature.spectral_centroid(y=y, sr=sr)[0],
                'zero_crossing_rate': librosa.feature.zero_crossing_rate(y)[0],
                'tempo': librosa.beat.tempo(y=y, sr=sr)[0]
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {'error': str(e)}
    
    def _gpu_emotion_analysis(self, data: Dict) -> Dict:
        """GPU-accelerated emotion analysis."""
        # This would use your AdvancedEmotionDetector
        # Simplified implementation
        return {
            'dominant_emotion': 'neutral',
            'confidence': 0.8,
            'all_emotions': {'neutral': 0.8, 'happy': 0.2}
        }
    
    def _cpu_scene_detection(self, video_path: str) -> Dict:
        """CPU-intensive scene detection."""
        # Simplified scene detection
        return {
            'scene_changes': [0.0, 10.5, 25.3, 45.7],
            'confidence': 0.85,
            'method': 'combined'
        }
    
    def _generate_cache_key(self, task_type: str, data: Any) -> str:
        """Generate cache key for task."""
        import hashlib
        
        # Create a hash of the task type and data
        data_str = str(sorted(data.items())) if isinstance(data, dict) else str(data)
        key_string = f"{task_type}:{data_str}"
        
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _update_cache(self, key: str, result: Any):
        """Update result cache with size management."""
        if len(self.result_cache) >= self.cache_size:
            # Remove oldest entry (simplified LRU)
            oldest_key = next(iter(self.result_cache))
            del self.result_cache[oldest_key]
        
        self.result_cache[key] = result
    
    async def _execute_callback(self, callback: Callable, result: Any):
        """Execute callback function safely."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(result)
            else:
                callback(result)
        except Exception as e:
            logger.error(f"Callback execution failed: {e}")
    
    def _update_performance_stats(self, processing_time: float):
        """Update performance statistics."""
        self.performance_stats['tasks_processed'] += 1
        
        # Update rolling average
        current_avg = self.performance_stats['average_processing_time']
        task_count = self.performance_stats['tasks_processed']
        
        self.performance_stats['average_processing_time'] = (
            (current_avg * (task_count - 1) + processing_time) / task_count
        )
    
    async def _cleanup_task(self, task_id: str, delay: float = 300):
        """Cleanup completed task after delay."""
        await asyncio.sleep(delay)
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
    
    async def _monitor_performance(self):
        """Monitor and log performance statistics."""
        while self.is_running:
            await asyncio.sleep(60)  # Log every minute
            
            stats = self.performance_stats.copy()
            cache_hit_rate = (
                stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses'])
                if (stats['cache_hits'] + stats['cache_misses']) > 0 else 0
            )
            
            logger.info(f"Performance: {stats['tasks_processed']} tasks, "
                       f"avg time: {stats['average_processing_time']:.2f}s, "
                       f"cache hit rate: {cache_hit_rate:.1%}")
    
    async def _cleanup_cache(self):
        """Periodic cache cleanup."""
        while self.is_running:
            await asyncio.sleep(3600)  # Cleanup every hour
            
            # Remove old cache entries (simplified)
            if len(self.result_cache) > self.cache_size * 0.8:
                keys_to_remove = list(self.result_cache.keys())[:int(self.cache_size * 0.2)]
                for key in keys_to_remove:
                    del self.result_cache[key]
                
                logger.info(f"Cache cleanup: removed {len(keys_to_remove)} entries")
    
    def get_performance_stats(self) -> Dict:
        """Get current performance statistics."""
        stats = self.performance_stats.copy()
        stats['active_tasks'] = len(self.active_tasks)
        stats['cache_size'] = len(self.result_cache)
        stats['queue_size'] = self.task_queue.qsize()
        
        return stats


class StreamProcessor:
    """Real-time video stream processor."""
    
    def __init__(self, stream_id: str, source: str, processors: List[str], callback: Callable, config: dict):
        self.stream_id = stream_id
        self.source = source
        self.processors = processors
        self.callback = callback
        self.config = config
        self.is_running = False
        self.frame_buffer = queue.Queue(maxsize=30)  # 1 second buffer at 30fps
    
    async def start(self):
        """Start stream processing."""
        self.is_running = True
        
        # Start capture and processing tasks
        capture_task = asyncio.create_task(self._capture_frames())
        process_task = asyncio.create_task(self._process_frames())
        
        await asyncio.gather(capture_task, process_task)
    
    async def stop(self):
        """Stop stream processing."""
        self.is_running = False
    
    async def _capture_frames(self):
        """Capture frames from video source."""
        import cv2
        
        cap = cv2.VideoCapture(self.source)
        
        try:
            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break
                
                timestamp = time.time()
                
                try:
                    self.frame_buffer.put((timestamp, frame), timeout=0.1)
                except queue.Full:
                    # Drop frame if buffer is full
                    continue
                
                await asyncio.sleep(0.001)  # Small delay to yield control
                
        finally:
            cap.release()
    
    async def _process_frames(self):
        """Process captured frames."""
        while self.is_running:
            try:
                timestamp, frame = self.frame_buffer.get(timeout=1.0)
                
                # Process frame with selected processors
                results = await self._apply_processors(frame, timestamp)
                
                # Send results via callback
                await self.callback(self.stream_id, timestamp, results)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Stream processing error: {e}")
    
    async def _apply_processors(self, frame: np.ndarray, timestamp: float) -> Dict:
        """Apply selected processors to frame."""
        results = {'timestamp': timestamp}
        
        for processor in self.processors:
            if processor == 'face_detection':
                results['faces'] = self._detect_faces(frame)
            elif processor == 'emotion_analysis':
                results['emotions'] = self._analyze_emotions(frame)
            elif processor == 'object_detection':
                results['objects'] = self._detect_objects(frame)
        
        return results
    
    def _detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """Detect faces in frame."""
        # Simplified face detection
        return [{'bbox': [100, 100, 50, 50], 'confidence': 0.9}]
    
    def _analyze_emotions(self, frame: np.ndarray) -> Dict:
        """Analyze emotions in frame."""
        # Simplified emotion analysis
        return {'dominant': 'neutral', 'confidence': 0.8}
    
    def _detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """Detect objects in frame."""
        # Simplified object detection
        return [{'class': 'person', 'confidence': 0.85, 'bbox': [50, 50, 100, 200]}]
