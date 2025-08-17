"""
Background Removal API using AI models
"""
import os
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import base64
from io import BytesIO

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from PIL import Image
import torch

from ..core.config import settings
from ..core.logging_config import get_logger

router = APIRouter()
logger = get_logger("background_removal")

# Global model cache
bg_removal_models = {}


def load_rembg_model(model_name: str = "u2net"):
    """Load background removal model using rembg"""
    if f"rembg_{model_name}" not in bg_removal_models:
        try:
            logger.info(f"Loading background removal model: {model_name}")
            from rembg import remove, new_session
            
            session = new_session(model_name)
            bg_removal_models[f"rembg_{model_name}"] = session
            logger.info(f"Background removal model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading rembg model {model_name}: {str(e)}")
            raise
    return bg_removal_models[f"rembg_{model_name}"]


def load_mediapipe_selfie_model():
    """Load MediaPipe selfie segmentation model"""
    if "mediapipe_selfie" not in bg_removal_models:
        try:
            logger.info("Loading MediaPipe selfie segmentation model...")
            import mediapipe as mp
            
            mp_selfie_segmentation = mp.solutions.selfie_segmentation
            model = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
            bg_removal_models["mediapipe_selfie"] = model
            logger.info("MediaPipe selfie segmentation model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading MediaPipe model: {str(e)}")
            bg_removal_models["mediapipe_selfie"] = None
    return bg_removal_models["mediapipe_selfie"]


def remove_background_rembg(image: np.ndarray, model_name: str = "u2net") -> np.ndarray:
    """Remove background using rembg library"""
    try:
        from rembg import remove
        
        session = load_rembg_model(model_name)
        
        # Convert numpy array to PIL Image
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        pil_image = Image.fromarray(image)
        
        # Remove background
        result = remove(pil_image, session=session)
        
        # Convert back to numpy array
        return np.array(result)
        
    except Exception as e:
        logger.error(f"Error removing background with rembg: {str(e)}")
        raise


def remove_background_mediapipe(image: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Remove background using MediaPipe selfie segmentation"""
    try:
        model = load_mediapipe_selfie_model()
        
        if model is None:
            raise ValueError("MediaPipe model not available")
        
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Run segmentation
        results = model.process(image_rgb)
        
        if results.segmentation_mask is not None:
            # Create mask
            mask = results.segmentation_mask > threshold
            
            # Create RGBA image
            h, w = image.shape[:2]
            result = np.zeros((h, w, 4), dtype=np.uint8)
            
            # Copy RGB channels
            if len(image.shape) == 3:
                result[:, :, :3] = image_rgb
            else:
                result[:, :, :3] = np.stack([image, image, image], axis=2)
            
            # Set alpha channel based on mask
            result[:, :, 3] = (mask * 255).astype(np.uint8)
            
            return result
        else:
            raise ValueError("Segmentation failed")
            
    except Exception as e:
        logger.error(f"Error removing background with MediaPipe: {str(e)}")
        raise


def apply_background_replacement(foreground: np.ndarray, background: np.ndarray) -> np.ndarray:
    """Apply new background to foreground image"""
    try:
        if foreground.shape[2] != 4:
            raise ValueError("Foreground image must have alpha channel")
        
        # Resize background to match foreground
        fg_h, fg_w = foreground.shape[:2]
        background_resized = cv2.resize(background, (fg_w, fg_h))
        
        # Ensure background has 3 channels
        if len(background_resized.shape) == 2:
            background_resized = cv2.cvtColor(background_resized, cv2.COLOR_GRAY2RGB)
        elif background_resized.shape[2] == 4:
            background_resized = background_resized[:, :, :3]
        
        # Extract alpha channel
        alpha = foreground[:, :, 3:4] / 255.0
        
        # Blend foreground and background
        result = foreground[:, :, :3] * alpha + background_resized * (1 - alpha)
        
        return result.astype(np.uint8)
        
    except Exception as e:
        logger.error(f"Error applying background replacement: {str(e)}")
        raise


def generate_gradient_background(width: int, height: int, color1: tuple = (70, 130, 180), color2: tuple = (25, 25, 112)) -> np.ndarray:
    """Generate a gradient background"""
    try:
        # Create gradient from top to bottom
        gradient = np.zeros((height, width, 3), dtype=np.uint8)
        
        for y in range(height):
            ratio = y / height
            color = [
                int(color1[i] * (1 - ratio) + color2[i] * ratio)
                for i in range(3)
            ]
            gradient[y, :] = color
        
        return gradient
        
    except Exception as e:
        logger.error(f"Error generating gradient background: {str(e)}")
        raise


def create_blur_background(original_image: np.ndarray, blur_strength: int = 50) -> np.ndarray:
    """Create a blurred version of the original image as background"""
    try:
        # Remove alpha channel if present
        if original_image.shape[2] == 4:
            image = original_image[:, :, :3]
        else:
            image = original_image
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(image, (blur_strength, blur_strength), 0)
        
        return blurred
        
    except Exception as e:
        logger.error(f"Error creating blur background: {str(e)}")
        raise


def process_video_background_removal(video_path: str, output_path: str, model_name: str = "u2net", 
                                   background_type: str = "transparent", background_image: Optional[str] = None) -> Dict:
    """Process entire video for background removal"""
    try:
        logger.info(f"Starting video background removal: {video_path}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Load background image if provided
        background = None
        if background_type == "image" and background_image:
            if os.path.exists(background_image):
                background = cv2.imread(background_image)
                background = cv2.resize(background, (width, height))
            else:
                logger.warning(f"Background image not found: {background_image}")
                background_type = "gradient"
        
        # Generate default background
        if background is None:
            if background_type == "gradient":
                background = generate_gradient_background(width, height)
            elif background_type == "solid":
                background = np.full((height, width, 3), (0, 255, 0), dtype=np.uint8)  # Green screen
        
        processed_frames = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            try:
                # Remove background
                if model_name.startswith("mediapipe"):
                    result = remove_background_mediapipe(frame)
                else:
                    result = remove_background_rembg(frame, model_name)
                
                # Apply background
                if background_type == "transparent":
                    # Keep transparent background (RGBA)
                    final_frame = result
                elif background_type == "blur":
                    # Create blurred background from original frame
                    bg = create_blur_background(frame)
                    final_frame = apply_background_replacement(result, bg)
                else:
                    # Use provided/generated background
                    final_frame = apply_background_replacement(result, background)
                
                # Convert to BGR for video writer (if not transparent)
                if background_type != "transparent":
                    if final_frame.shape[2] == 4:
                        final_frame = final_frame[:, :, :3]
                    final_frame = cv2.cvtColor(final_frame, cv2.COLOR_RGB2BGR)
                
                out.write(final_frame)
                processed_frames += 1
                
                # Log progress
                if processed_frames % 30 == 0:
                    progress = (processed_frames / total_frames) * 100
                    logger.info(f"Processing progress: {progress:.1f}% ({processed_frames}/{total_frames})")
                
            except Exception as e:
                logger.warning(f"Error processing frame {processed_frames}: {str(e)}")
                # Write original frame if processing fails
                out.write(frame)
                processed_frames += 1
        
        cap.release()
        out.release()
        
        return {
            "processed_frames": processed_frames,
            "total_frames": total_frames,
            "success_rate": processed_frames / total_frames if total_frames > 0 else 0,
            "output_path": output_path
        }
        
    except Exception as e:
        logger.error(f"Error processing video background removal: {str(e)}")
        raise


@router.post("/remove")
async def remove_background_from_image(
    filename: str,
    model: str = "u2net",
    output_format: str = "png"
):
    """
    Remove background from a single image
    
    - **filename**: Name of uploaded image file
    - **model**: Background removal model ("u2net", "u2netp", "silueta", "isnet-general-use", "mediapipe")
    - **output_format**: Output format ("png", "jpg")
    """
    
    # Check if file exists
    image_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    try:
        logger.info(f"Removing background from image: {filename}")
        start_time = datetime.now()
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not load image")
        
        # Remove background
        if model == "mediapipe":
            result = remove_background_mediapipe(image)
        else:
            result = remove_background_rembg(image, model)
        
        # Generate output filename
        output_filename = f"no_bg_{Path(filename).stem}.{output_format}"
        output_path = os.path.join(settings.PROCESSED_DIR, output_filename)
        
        # Ensure processed directory exists
        os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
        
        # Save result
        if output_format.lower() == "png":
            cv2.imwrite(output_path, result)
        else:
            # Convert RGBA to RGB for JPEG
            if result.shape[2] == 4:
                rgb_result = cv2.cvtColor(result, cv2.COLOR_RGBA2RGB)
                cv2.imwrite(output_path, rgb_result)
            else:
                cv2.imwrite(output_path, result)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Background removal completed successfully",
                "data": {
                    "original_filename": filename,
                    "output_filename": output_filename,
                    "output_path": output_path,
                    "model_used": model,
                    "output_format": output_format,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error removing background from {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error removing background: {str(e)}")


@router.post("/replace")
async def replace_background(
    filename: str,
    background_type: str = "gradient",
    background_image: Optional[str] = None,
    model: str = "u2net",
    blur_strength: int = 50
):
    """
    Remove background and replace with new background
    
    - **filename**: Name of uploaded image file
    - **background_type**: Type of background ("gradient", "solid", "blur", "image")
    - **background_image**: Filename of background image (if background_type="image")
    - **model**: Background removal model
    - **blur_strength**: Blur strength for blur background
    """
    
    image_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    try:
        logger.info(f"Replacing background for image: {filename}")
        start_time = datetime.now()
        
        # Load original image
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError("Could not load image")
        
        height, width = original_image.shape[:2]
        
        # Remove background
        if model == "mediapipe":
            foreground = remove_background_mediapipe(original_image)
        else:
            foreground = remove_background_rembg(original_image, model)
        
        # Prepare background
        if background_type == "gradient":
            background = generate_gradient_background(width, height)
        elif background_type == "solid":
            background = np.full((height, width, 3), (0, 255, 0), dtype=np.uint8)  # Green
        elif background_type == "blur":
            background = create_blur_background(original_image, blur_strength)
        elif background_type == "image" and background_image:
            bg_path = os.path.join(settings.UPLOAD_DIR, background_image)
            if os.path.exists(bg_path):
                background = cv2.imread(bg_path)
                background = cv2.resize(background, (width, height))
            else:
                raise HTTPException(status_code=404, detail="Background image not found")
        else:
            background = generate_gradient_background(width, height)
        
        # Apply new background
        result = apply_background_replacement(foreground, background)
        
        # Generate output filename
        output_filename = f"new_bg_{Path(filename).stem}.jpg"
        output_path = os.path.join(settings.PROCESSED_DIR, output_filename)
        
        # Ensure processed directory exists
        os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
        
        # Save result
        cv2.imwrite(output_path, cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Background replacement completed successfully",
                "data": {
                    "original_filename": filename,
                    "output_filename": output_filename,
                    "output_path": output_path,
                    "background_type": background_type,
                    "background_image": background_image,
                    "model_used": model,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error replacing background for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error replacing background: {str(e)}")


@router.post("/video")
async def remove_background_from_video(
    background_tasks: BackgroundTasks,
    filename: str,
    background_type: str = "transparent",
    background_image: Optional[str] = None,
    model: str = "u2net"
):
    """
    Remove background from video (background task)
    
    - **filename**: Name of uploaded video file
    - **background_type**: Type of background ("transparent", "gradient", "solid", "blur", "image")
    - **background_image**: Filename of background image
    - **model**: Background removal model
    """
    
    video_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    try:
        # Generate output filename
        output_filename = f"no_bg_{Path(filename).stem}.mp4"
        output_path = os.path.join(settings.PROCESSED_DIR, output_filename)
        
        # Ensure processed directory exists
        os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
        
        # Start background processing
        background_tasks.add_task(
            process_video_background_removal,
            video_path,
            output_path,
            model,
            background_type,
            background_image
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "Video background removal started (processing in background)",
                "data": {
                    "original_filename": filename,
                    "output_filename": output_filename,
                    "output_path": output_path,
                    "background_type": background_type,
                    "model_used": model,
                    "status": "processing",
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting video background removal for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting video processing: {str(e)}")


@router.get("/models")
async def get_available_models():
    """Get list of available background removal models"""
    
    return JSONResponse(
        status_code=200,
        content={
            "message": "Available background removal models",
            "data": {
                "models": [
                    {
                        "name": "u2net",
                        "description": "General purpose background removal (recommended)",
                        "type": "rembg",
                        "speed": "medium",
                        "quality": "high"
                    },
                    {
                        "name": "u2netp",
                        "description": "Lightweight version of U2-Net",
                        "type": "rembg",
                        "speed": "fast",
                        "quality": "medium"
                    },
                    {
                        "name": "silueta",
                        "description": "Good for people and objects",
                        "type": "rembg",
                        "speed": "medium",
                        "quality": "high"
                    },
                    {
                        "name": "isnet-general-use",
                        "description": "High accuracy general purpose model",
                        "type": "rembg",
                        "speed": "slow",
                        "quality": "very high"
                    },
                    {
                        "name": "mediapipe",
                        "description": "Fast person segmentation",
                        "type": "mediapipe",
                        "speed": "very fast",
                        "quality": "medium"
                    }
                ],
                "background_types": [
                    "transparent",
                    "gradient",
                    "solid",
                    "blur",
                    "image"
                ]
            }
        }
    )


@router.get("/status/{filename}")
async def get_processing_status(filename: str):
    """Check processing status of a video background removal task"""
    
    output_filename = f"no_bg_{Path(filename).stem}.mp4"
    output_path = os.path.join(settings.PROCESSED_DIR, output_filename)
    
    if os.path.exists(output_path):
        file_stat = os.stat(output_path)
        return {
            "status": "completed",
            "output_filename": output_filename,
            "output_path": output_path,
            "file_size": file_stat.st_size,
            "completed_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        }
    else:
        return {
            "status": "processing",
            "message": "Video is still being processed"
        }
