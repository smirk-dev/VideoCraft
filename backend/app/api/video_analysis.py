"""
Video Analysis API endpoints using real AI models
"""
import os
import cv2
import torch
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.config import settings
from ..core.logging_config import get_logger
from ..services.ai_analysis import RealAIAnalysisService
from ..database import get_db
from ..models.database import AnalysisReport, Project

router = APIRouter()
logger = get_logger("video_analysis")

# Initialize real AI analysis service
ai_service = RealAIAnalysisService()


class AnalysisRequest(BaseModel):
    """Request model for video analysis"""
    video_filename: str
    analysis_types: Optional[List[str]] = ['objects', 'scenes', 'emotions', 'motion']
    project_id: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for video analysis"""
    success: bool
    analysis_id: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def load_object_detection_model():
    """Load object detection model (DETR)"""
    if "object_detection" not in model_cache:
        try:
            logger.info("Loading object detection model...")
            processor = AutoProcessor.from_pretrained("facebook/detr-resnet-50")
            model = AutoModelForObjectDetection.from_pretrained("facebook/detr-resnet-50")
            model_cache["object_detection"] = {"processor": processor, "model": model}
            logger.info("Object detection model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading object detection model: {str(e)}")
            raise
    return model_cache["object_detection"]


def load_scene_classification_model():
    """Load scene classification model"""
    if "scene_classification" not in model_cache:
        try:
            logger.info("Loading scene classification model...")
            classifier = pipeline(
                "image-classification",
                model="microsoft/resnet-50",
                device=0 if settings.DEVICE == "cuda" else -1
            )
            model_cache["scene_classification"] = classifier
            logger.info("Scene classification model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading scene classification model: {str(e)}")
            # Fallback to a simpler model
            classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
            model_cache["scene_classification"] = classifier
    return model_cache["scene_classification"]


def extract_frames(video_path: str, max_frames: int = 30, fps: Optional[float] = None) -> List[np.ndarray]:
    """Extract frames from video for analysis"""
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / video_fps if video_fps > 0 else 0
        
        # Calculate frame extraction interval
        if fps:
            interval = max(1, int(video_fps / fps))
        else:
            interval = max(1, total_frames // max_frames)
        
        frames = []
        frame_count = 0
        
        while cap.isOpened() and len(frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            
            frame_count += 1
        
        cap.release()
        
        logger.info(f"Extracted {len(frames)} frames from video (duration: {duration:.2f}s)")
        return frames
        
    except Exception as e:
        logger.error(f"Error extracting frames from {video_path}: {str(e)}")
        raise


def analyze_objects_in_frame(frame: np.ndarray, threshold: float = 0.7) -> List[Dict]:
    """Analyze objects in a single frame using DETR"""
    try:
        model_data = load_object_detection_model()
        processor = model_data["processor"]
        model = model_data["model"]
        
        # Prepare image
        inputs = processor(images=frame, return_tensors="pt")
        
        # Run inference
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Process results
        target_sizes = torch.tensor([frame.shape[:2]])
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=threshold)
        
        objects = []
        for score, label, box in zip(results[0]["scores"], results[0]["labels"], results[0]["boxes"]):
            objects.append({
                "label": model.config.id2label[label.item()],
                "confidence": score.item(),
                "bbox": box.tolist()
            })
        
        return objects
        
    except Exception as e:
        logger.error(f"Error analyzing objects in frame: {str(e)}")
        return []


def analyze_scene_in_frame(frame: np.ndarray, top_k: int = 5) -> List[Dict]:
    """Analyze scene/context in a frame"""
    try:
        classifier = load_scene_classification_model()
        
        # Convert numpy array to PIL Image
        from PIL import Image
        image = Image.fromarray(frame)
        
        # Run classification
        results = classifier(image, top_k=top_k)
        
        return [
            {
                "label": result["label"],
                "confidence": result["score"]
            }
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Error analyzing scene in frame: {str(e)}")
        return []


def detect_scene_changes(frames: List[np.ndarray], threshold: float = 0.3) -> List[Dict]:
    """Detect scene changes between frames"""
    try:
        scene_changes = []
        
        for i in range(1, len(frames)):
            # Calculate histogram difference
            hist1 = cv2.calcHist([frames[i-1]], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([frames[i]], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            
            # Correlation coefficient
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            if correlation < (1 - threshold):
                scene_changes.append({
                    "frame_index": i,
                    "change_score": 1 - correlation,
                    "timestamp": i / 30.0,  # Assuming 30 fps for timestamp calculation
                    "type": "scene_change"
                })
        
        return scene_changes
        
    except Exception as e:
        logger.error(f"Error detecting scene changes: {str(e)}")
        return []


def analyze_video_quality(video_path: str) -> Dict:
    """Analyze video quality metrics"""
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        # Sample frames for quality analysis
        frame_samples = []
        sample_count = min(10, total_frames)
        
        for i in range(sample_count):
            frame_pos = i * (total_frames // sample_count)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            
            if ret:
                # Calculate frame quality metrics
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Sharpness (Laplacian variance)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                # Brightness (mean intensity)
                brightness = np.mean(gray)
                
                # Contrast (standard deviation)
                contrast = np.std(gray)
                
                frame_samples.append({
                    "sharpness": sharpness,
                    "brightness": brightness,
                    "contrast": contrast
                })
        
        cap.release()
        
        # Calculate overall quality metrics
        avg_sharpness = np.mean([f["sharpness"] for f in frame_samples])
        avg_brightness = np.mean([f["brightness"] for f in frame_samples])
        avg_contrast = np.mean([f["contrast"] for f in frame_samples])
        
        # Quality score (0-100)
        quality_score = min(100, (avg_sharpness / 1000 + avg_contrast / 50) * 50)
        
        return {
            "resolution": {"width": width, "height": height},
            "fps": fps,
            "duration": duration,
            "total_frames": total_frames,
            "quality_metrics": {
                "sharpness": avg_sharpness,
                "brightness": avg_brightness,
                "contrast": avg_contrast,
                "quality_score": quality_score
            },
            "frame_samples": frame_samples
        }
        
    except Exception as e:
        logger.error(f"Error analyzing video quality: {str(e)}")
        raise


@router.post("/video")
async def analyze_video(
    filename: str,
    max_frames: int = 30,
    object_detection: bool = True,
    scene_classification: bool = True,
    scene_change_detection: bool = True,
    quality_analysis: bool = True
):
    """
    Comprehensive video analysis using AI models
    
    - **filename**: Name of uploaded video file
    - **max_frames**: Maximum number of frames to analyze
    - **object_detection**: Enable object detection
    - **scene_classification**: Enable scene classification
    - **scene_change_detection**: Enable scene change detection
    - **quality_analysis**: Enable video quality analysis
    """
    
    # Check if file exists
    video_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    try:
        logger.info(f"Starting video analysis for: {filename}")
        start_time = datetime.now()
        
        analysis_results = {
            "filename": filename,
            "analysis_timestamp": start_time.isoformat(),
            "parameters": {
                "max_frames": max_frames,
                "object_detection": object_detection,
                "scene_classification": scene_classification,
                "scene_change_detection": scene_change_detection,
                "quality_analysis": quality_analysis
            }
        }
        
        # Extract frames
        frames = extract_frames(video_path, max_frames)
        analysis_results["frames_analyzed"] = len(frames)
        
        # Video quality analysis
        if quality_analysis:
            logger.info("Analyzing video quality...")
            analysis_results["quality"] = analyze_video_quality(video_path)
        
        # Object detection
        if object_detection and frames:
            logger.info("Running object detection...")
            objects_per_frame = []
            all_objects = {}
            
            for i, frame in enumerate(frames):
                objects = analyze_objects_in_frame(frame)
                objects_per_frame.append({
                    "frame_index": i,
                    "objects": objects
                })
                
                # Count objects
                for obj in objects:
                    label = obj["label"]
                    if label not in all_objects:
                        all_objects[label] = 0
                    all_objects[label] += 1
            
            analysis_results["object_detection"] = {
                "objects_per_frame": objects_per_frame,
                "object_summary": all_objects,
                "total_objects_detected": sum(len(frame["objects"]) for frame in objects_per_frame)
            }
        
        # Scene classification
        if scene_classification and frames:
            logger.info("Running scene classification...")
            scenes_per_frame = []
            all_scenes = {}
            
            for i, frame in enumerate(frames):
                scenes = analyze_scene_in_frame(frame)
                scenes_per_frame.append({
                    "frame_index": i,
                    "scenes": scenes
                })
                
                # Count scene types
                for scene in scenes:
                    label = scene["label"]
                    if label not in all_scenes:
                        all_scenes[label] = {"count": 0, "avg_confidence": 0}
                    all_scenes[label]["count"] += 1
                    all_scenes[label]["avg_confidence"] += scene["confidence"]
            
            # Calculate average confidence
            for scene_type in all_scenes:
                all_scenes[scene_type]["avg_confidence"] /= all_scenes[scene_type]["count"]
            
            analysis_results["scene_classification"] = {
                "scenes_per_frame": scenes_per_frame,
                "scene_summary": all_scenes
            }
        
        # Scene change detection
        if scene_change_detection and frames:
            logger.info("Detecting scene changes...")
            scene_changes = detect_scene_changes(frames)
            analysis_results["scene_changes"] = {
                "changes": scene_changes,
                "total_changes": len(scene_changes),
                "change_frequency": len(scene_changes) / len(frames) if frames else 0
            }
        
        # Processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        analysis_results["processing_time"] = processing_time
        
        logger.info(f"Video analysis completed in {processing_time:.2f}s")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Video analysis completed successfully",
                "data": analysis_results
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing video {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing video: {str(e)}")


@router.post("/frame")
async def analyze_single_frame(
    filename: str,
    frame_index: int = 0,
    object_detection: bool = True,
    scene_classification: bool = True
):
    """
    Analyze a single frame from a video
    
    - **filename**: Name of uploaded video file
    - **frame_index**: Index of frame to analyze
    - **object_detection**: Enable object detection
    - **scene_classification**: Enable scene classification
    """
    
    video_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    try:
        # Extract specific frame
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=400, detail="Could not extract frame")
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        analysis_results = {
            "filename": filename,
            "frame_index": frame_index,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Object detection
        if object_detection:
            objects = analyze_objects_in_frame(frame_rgb)
            analysis_results["objects"] = objects
        
        # Scene classification
        if scene_classification:
            scenes = analyze_scene_in_frame(frame_rgb)
            analysis_results["scenes"] = scenes
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Frame analysis completed successfully",
                "data": analysis_results
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing frame {frame_index} from {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing frame: {str(e)}")


@router.get("/suggestions/{filename}")
async def get_edit_suggestions(filename: str):
    """
    Get AI-powered editing suggestions based on video analysis
    """
    
    video_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    try:
        # This would typically use cached analysis results
        # For now, we'll run a quick analysis
        frames = extract_frames(video_path, max_frames=15)
        scene_changes = detect_scene_changes(frames)
        
        suggestions = []
        
        # Scene-based suggestions
        if scene_changes:
            suggestions.append({
                "type": "scene_cuts",
                "description": f"Found {len(scene_changes)} potential cut points",
                "timestamps": [change["timestamp"] for change in scene_changes],
                "confidence": 0.8
            })
        
        # Quality-based suggestions
        quality_info = analyze_video_quality(video_path)
        quality_score = quality_info["quality_metrics"]["quality_score"]
        
        if quality_score < 50:
            suggestions.append({
                "type": "quality_enhancement",
                "description": "Video quality could be improved with sharpening and contrast adjustment",
                "recommended_filters": ["sharpen", "contrast", "brightness"],
                "confidence": 0.7
            })
        
        # Duration-based suggestions
        duration = quality_info["duration"]
        if duration > 300:  # 5 minutes
            suggestions.append({
                "type": "length_optimization",
                "description": "Consider shortening the video for better engagement",
                "suggested_duration": min(180, duration * 0.7),
                "confidence": 0.6
            })
        
        return {
            "filename": filename,
            "suggestions": suggestions,
            "analysis_summary": {
                "duration": duration,
                "quality_score": quality_score,
                "scene_changes": len(scene_changes)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating suggestions for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")


@router.post("/analyze-real", response_model=AnalysisResponse)
async def analyze_video_real(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    user_id: int = 1,  # For now, default user
    db: Session = Depends(get_db)
):
    """
    Perform real AI analysis on video using actual AI models
    
    This endpoint replaces mock analysis with genuine AI processing
    """
    try:
        logger.info(f"Starting real AI analysis for: {request.video_filename}")
        
        # Validate video file exists
        video_path = os.path.join(settings.UPLOAD_DIR, request.video_filename)
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Perform real AI analysis
        analysis_result = await ai_service.analyze_video(
            video_path=video_path,
            analysis_types=request.analysis_types
        )
        
        if not analysis_result['success']:
            # If real analysis fails, return error with fallback
            return AnalysisResponse(
                success=False,
                error=analysis_result.get('error', 'Analysis failed'),
                analysis=analysis_result.get('fallback_analysis')
            )
        
        # Save analysis to database if project_id is provided
        analysis_record = None
        if request.project_id:
            try:
                # Find project
                project = db.query(Project).filter(
                    Project.project_id == request.project_id
                ).first()
                
                if project:
                    # Create analysis record
                    analysis_record = AnalysisReport(
                        analysis_type="comprehensive",
                        analysis_data=analysis_result['analysis'],
                        confidence_score=85,  # Average confidence
                        processing_time=int(analysis_result['analysis'].get('processing_time_seconds', 0)),
                        project_id=project.id,
                        user_id=user_id
                    )
                    
                    db.add(analysis_record)
                    db.commit()
                    db.refresh(analysis_record)
                    
                    logger.info(f"Saved analysis record: {analysis_record.report_id}")
            
            except Exception as e:
                logger.warning(f"Failed to save analysis record: {str(e)}")
                # Continue without saving - analysis still succeeded
        
        return AnalysisResponse(
            success=True,
            analysis_id=analysis_record.report_id if analysis_record else None,
            analysis=analysis_result['analysis']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Real AI analysis failed: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )


@router.get("/analysis/{analysis_id}")
async def get_analysis_report(
    analysis_id: str,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Get saved analysis report by ID"""
    try:
        analysis = db.query(AnalysisReport).filter(
            AnalysisReport.report_id == analysis_id,
            AnalysisReport.user_id == user_id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis report not found")
        
        return JSONResponse(
            status_code=200,
            content={
                "analysis_id": analysis.report_id,
                "analysis_type": analysis.analysis_type,
                "analysis_data": analysis.analysis_data,
                "confidence_score": analysis.confidence_score,
                "processing_time": analysis.processing_time,
                "created_at": analysis.created_at.isoformat(),
                "project_id": analysis.project.project_id if analysis.project else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
