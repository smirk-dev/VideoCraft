"""
Video Editing API with AI-powered features and real video processing
"""
import os
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
import moviepy.editor as mp
from moviepy.video.fx import resize, crop
from pydantic import BaseModel

from ..core.config import settings
from ..core.logging_config import get_logger
from ..services.video_processor import VideoProcessor

router = APIRouter()
logger = get_logger("video_editing")

# Initialize video processor
video_processor = VideoProcessor()


class VideoProcessingRequest(BaseModel):
    """Request model for video processing"""
    video_filename: str
    editing_data: Dict[str, Any]
    output_filename: Optional[str] = None


class VideoProcessingResponse(BaseModel):
    """Response model for video processing"""
    success: bool
    output_path: Optional[str] = None
    output_filename: Optional[str] = None
    video_info: Optional[Dict] = None
    processing_time: Optional[str] = None
    applied_operations: Optional[Dict] = None
    error: Optional[str] = None


def validate_video_file(filename: str) -> str:
    """Validate video file exists and return full path"""
    video_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    return video_path


def generate_output_path(filename: str, suffix: str = "edited") -> str:
    """Generate output path for processed video"""
    output_filename = f"{suffix}_{Path(filename).stem}.mp4"
    output_path = os.path.join(settings.PROCESSED_DIR, output_filename)
    
    # Ensure processed directory exists
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    
    return output_path


def trim_video(input_path: str, output_path: str, start_time: float, end_time: float) -> Dict:
    """Trim video to specified time range"""
    try:
        logger.info(f"Trimming video from {start_time}s to {end_time}s")
        
        clip = mp.VideoFileClip(input_path)
        
        # Validate time range
        if end_time > clip.duration:
            end_time = clip.duration
        if start_time < 0:
            start_time = 0
        if start_time >= end_time:
            raise ValueError("Start time must be less than end time")
        
        # Trim clip
        trimmed_clip = clip.subclip(start_time, end_time)
        
        # Write output
        trimmed_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        trimmed_clip.close()
        clip.close()
        
        return {
            "original_duration": clip.duration,
            "new_duration": end_time - start_time,
            "start_time": start_time,
            "end_time": end_time
        }
        
    except Exception as e:
        logger.error(f"Error trimming video: {str(e)}")
        raise


def merge_videos(input_paths: List[str], output_path: str, transition_duration: float = 0.5) -> Dict:
    """Merge multiple videos with optional transitions"""
    try:
        logger.info(f"Merging {len(input_paths)} videos")
        
        clips = []
        total_duration = 0
        
        for i, path in enumerate(input_paths):
            clip = mp.VideoFileClip(path)
            
            # Add fade transition (except for first clip)
            if i > 0 and transition_duration > 0:
                clip = clip.fadein(transition_duration)
            
            # Add fade out (except for last clip)
            if i < len(input_paths) - 1 and transition_duration > 0:
                clip = clip.fadeout(transition_duration)
            
            clips.append(clip)
            total_duration += clip.duration
        
        # Concatenate clips
        final_clip = mp.concatenate_videoclips(clips)
        
        # Write output
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        return {
            "merged_clips": len(input_paths),
            "total_duration": total_duration,
            "transition_duration": transition_duration
        }
        
    except Exception as e:
        logger.error(f"Error merging videos: {str(e)}")
        raise


def resize_video(input_path: str, output_path: str, width: int, height: int, method: str = "crop") -> Dict:
    """Resize video to specified dimensions"""
    try:
        logger.info(f"Resizing video to {width}x{height} using {method}")
        
        clip = mp.VideoFileClip(input_path)
        original_size = (clip.w, clip.h)
        
        if method == "crop":
            # Crop to maintain aspect ratio
            resized_clip = crop(clip, width=width, height=height, 
                              x_center=clip.w/2, y_center=clip.h/2)
        elif method == "stretch":
            # Stretch to exact dimensions
            resized_clip = resize(clip, newsize=(width, height))
        else:
            # Scale maintaining aspect ratio
            resized_clip = resize(clip, height=height) if clip.h > clip.w else resize(clip, width=width)
        
        # Write output
        resized_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        resized_clip.close()
        clip.close()
        
        return {
            "original_size": original_size,
            "new_size": (resized_clip.w, resized_clip.h),
            "method": method
        }
        
    except Exception as e:
        logger.error(f"Error resizing video: {str(e)}")
        raise


def add_text_overlay(input_path: str, output_path: str, text: str, position: Tuple[int, int], 
                    duration: Optional[float] = None, font_size: int = 50, color: str = "white") -> Dict:
    """Add text overlay to video"""
    try:
        logger.info(f"Adding text overlay: '{text}'")
        
        clip = mp.VideoFileClip(input_path)
        
        # Create text clip
        text_clip = mp.TextClip(
            text,
            fontsize=font_size,
            color=color,
            font='Arial-Bold'
        )
        
        # Set position and duration
        text_clip = text_clip.set_position(position)
        
        if duration:
            text_clip = text_clip.set_duration(duration)
        else:
            text_clip = text_clip.set_duration(clip.duration)
        
        # Composite text over video
        final_clip = mp.CompositeVideoClip([clip, text_clip])
        
        # Write output
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_clip.close()
        text_clip.close()
        clip.close()
        
        return {
            "text": text,
            "position": position,
            "duration": duration or clip.duration,
            "font_size": font_size,
            "color": color
        }
        
    except Exception as e:
        logger.error(f"Error adding text overlay: {str(e)}")
        raise


def apply_video_filters(input_path: str, output_path: str, filters: Dict) -> Dict:
    """Apply various video filters"""
    try:
        logger.info(f"Applying video filters: {list(filters.keys())}")
        
        clip = mp.VideoFileClip(input_path)
        processed_clip = clip
        
        applied_filters = []
        
        # Brightness adjustment
        if "brightness" in filters:
            brightness = filters["brightness"]  # -1.0 to 1.0
            processed_clip = processed_clip.fx(mp.vfx.colorx, brightness + 1.0)
            applied_filters.append(f"brightness: {brightness}")
        
        # Speed adjustment
        if "speed" in filters:
            speed = filters["speed"]  # 0.5 = half speed, 2.0 = double speed
            processed_clip = processed_clip.fx(mp.vfx.speedx, speed)
            applied_filters.append(f"speed: {speed}x")
        
        # Fade in/out
        if "fade_in" in filters:
            fade_in_duration = filters["fade_in"]
            processed_clip = processed_clip.fadein(fade_in_duration)
            applied_filters.append(f"fade_in: {fade_in_duration}s")
        
        if "fade_out" in filters:
            fade_out_duration = filters["fade_out"]
            processed_clip = processed_clip.fadeout(fade_out_duration)
            applied_filters.append(f"fade_out: {fade_out_duration}s")
        
        # Mirror effect
        if filters.get("mirror_x", False):
            processed_clip = processed_clip.fx(mp.vfx.mirror_x)
            applied_filters.append("mirror_x")
        
        if filters.get("mirror_y", False):
            processed_clip = processed_clip.fx(mp.vfx.mirror_y)
            applied_filters.append("mirror_y")
        
        # Write output
        processed_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        processed_clip.close()
        clip.close()
        
        return {
            "applied_filters": applied_filters,
            "original_duration": clip.duration,
            "new_duration": processed_clip.duration
        }
        
    except Exception as e:
        logger.error(f"Error applying video filters: {str(e)}")
        raise


def extract_audio_from_video(input_path: str, output_path: str) -> Dict:
    """Extract audio from video file"""
    try:
        logger.info("Extracting audio from video")
        
        clip = mp.VideoFileClip(input_path)
        
        if clip.audio is None:
            raise ValueError("Video has no audio track")
        
        # Extract audio
        audio = clip.audio
        audio.write_audiofile(output_path, verbose=False, logger=None)
        
        # Get audio properties
        duration = audio.duration
        
        # Clean up
        audio.close()
        clip.close()
        
        return {
            "duration": duration,
            "output_path": output_path
        }
        
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        raise


def add_background_music(input_path: str, output_path: str, music_path: str, 
                        volume: float = 0.3, loop: bool = True) -> Dict:
    """Add background music to video"""
    try:
        logger.info("Adding background music to video")
        
        # Load video and music
        video_clip = mp.VideoFileClip(input_path)
        music_clip = mp.AudioFileClip(music_path)
        
        # Adjust music volume
        music_clip = music_clip.volumex(volume)
        
        # Loop music if needed and video is longer
        if loop and music_clip.duration < video_clip.duration:
            music_clip = music_clip.loop(duration=video_clip.duration)
        elif music_clip.duration > video_clip.duration:
            music_clip = music_clip.subclip(0, video_clip.duration)
        
        # Combine with existing audio if present
        if video_clip.audio is not None:
            final_audio = mp.CompositeAudioClip([video_clip.audio, music_clip])
        else:
            final_audio = music_clip
        
        # Set the audio to the video
        final_clip = video_clip.set_audio(final_audio)
        
        # Write output
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_clip.close()
        music_clip.close()
        video_clip.close()
        
        return {
            "music_duration": music_clip.duration,
            "video_duration": video_clip.duration,
            "volume": volume,
            "looped": loop
        }
        
    except Exception as e:
        logger.error(f"Error adding background music: {str(e)}")
        raise


def create_video_collage(input_paths: List[str], output_path: str, grid_size: Tuple[int, int]) -> Dict:
    """Create a video collage with multiple videos in a grid"""
    try:
        logger.info(f"Creating video collage with {len(input_paths)} videos in {grid_size[0]}x{grid_size[1]} grid")
        
        if len(input_paths) > grid_size[0] * grid_size[1]:
            raise ValueError("Too many videos for specified grid size")
        
        # Load all video clips
        clips = [mp.VideoFileClip(path) for path in input_paths]
        
        # Find minimum duration
        min_duration = min(clip.duration for clip in clips)
        
        # Resize clips to fit grid
        grid_width = 1920 // grid_size[1]
        grid_height = 1080 // grid_size[0]
        
        resized_clips = []
        for clip in clips:
            resized_clip = resize(clip.subclip(0, min_duration), newsize=(grid_width, grid_height))
            resized_clips.append(resized_clip)
        
        # Arrange clips in grid
        rows = []
        for i in range(grid_size[0]):
            row_clips = []
            for j in range(grid_size[1]):
                idx = i * grid_size[1] + j
                if idx < len(resized_clips):
                    row_clips.append(resized_clips[idx])
                else:
                    # Create black clip for empty slots
                    black_clip = mp.ColorClip(size=(grid_width, grid_height), color=(0, 0, 0), duration=min_duration)
                    row_clips.append(black_clip)
            
            row = mp.clips_array([row_clips])
            rows.append(row)
        
        # Combine rows
        final_clip = mp.clips_array(rows)
        
        # Write output
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_clip.close()
        for clip in clips + resized_clips:
            clip.close()
        
        return {
            "input_videos": len(input_paths),
            "grid_size": grid_size,
            "duration": min_duration,
            "output_resolution": (1920, 1080)
        }
        
    except Exception as e:
        logger.error(f"Error creating video collage: {str(e)}")
        raise


@router.post("/trim")
async def trim_video_endpoint(
    filename: str,
    start_time: float,
    end_time: float
):
    """
    Trim video to specified time range
    
    - **filename**: Name of uploaded video file
    - **start_time**: Start time in seconds
    - **end_time**: End time in seconds
    """
    
    input_path = validate_video_file(filename)
    output_path = generate_output_path(filename, "trimmed")
    
    try:
        logger.info(f"Trimming video: {filename}")
        start_time_processing = datetime.now()
        
        result = trim_video(input_path, output_path, start_time, end_time)
        
        processing_time = (datetime.now() - start_time_processing).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Video trimmed successfully",
                "data": {
                    "original_filename": filename,
                    "output_filename": Path(output_path).name,
                    "output_path": output_path,
                    **result,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error trimming video {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error trimming video: {str(e)}")


@router.post("/merge")
async def merge_videos_endpoint(
    filenames: List[str],
    transition_duration: float = 0.5
):
    """
    Merge multiple videos with transitions
    
    - **filenames**: List of video filenames to merge
    - **transition_duration**: Transition duration between videos (seconds)
    """
    
    if len(filenames) < 2:
        raise HTTPException(status_code=400, detail="At least 2 videos required for merging")
    
    # Validate all files exist
    input_paths = [validate_video_file(filename) for filename in filenames]
    output_path = generate_output_path("merged_videos", "merged")
    
    try:
        logger.info(f"Merging {len(filenames)} videos")
        start_time = datetime.now()
        
        result = merge_videos(input_paths, output_path, transition_duration)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Videos merged successfully",
                "data": {
                    "input_filenames": filenames,
                    "output_filename": Path(output_path).name,
                    "output_path": output_path,
                    **result,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error merging videos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error merging videos: {str(e)}")


@router.post("/resize")
async def resize_video_endpoint(
    filename: str,
    width: int,
    height: int,
    method: str = "crop"
):
    """
    Resize video to specified dimensions
    
    - **filename**: Name of uploaded video file
    - **width**: Target width in pixels
    - **height**: Target height in pixels
    - **method**: Resize method ("crop", "stretch", "scale")
    """
    
    if width <= 0 or height <= 0:
        raise HTTPException(status_code=400, detail="Width and height must be positive")
    
    if method not in ["crop", "stretch", "scale"]:
        raise HTTPException(status_code=400, detail="Method must be 'crop', 'stretch', or 'scale'")
    
    input_path = validate_video_file(filename)
    output_path = generate_output_path(filename, f"resized_{width}x{height}")
    
    try:
        logger.info(f"Resizing video: {filename}")
        start_time = datetime.now()
        
        result = resize_video(input_path, output_path, width, height, method)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Video resized successfully",
                "data": {
                    "original_filename": filename,
                    "output_filename": Path(output_path).name,
                    "output_path": output_path,
                    **result,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error resizing video {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resizing video: {str(e)}")


@router.post("/add-text")
async def add_text_overlay_endpoint(
    filename: str,
    text: str,
    x_position: int = 100,
    y_position: int = 100,
    duration: Optional[float] = None,
    font_size: int = 50,
    color: str = "white"
):
    """
    Add text overlay to video
    
    - **filename**: Name of uploaded video file
    - **text**: Text to overlay
    - **x_position**: X position of text
    - **y_position**: Y position of text
    - **duration**: Duration of text overlay (None = entire video)
    - **font_size**: Font size
    - **color**: Text color
    """
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    input_path = validate_video_file(filename)
    output_path = generate_output_path(filename, "with_text")
    
    try:
        logger.info(f"Adding text overlay to video: {filename}")
        start_time = datetime.now()
        
        result = add_text_overlay(
            input_path, output_path, text, (x_position, y_position),
            duration, font_size, color
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Text overlay added successfully",
                "data": {
                    "original_filename": filename,
                    "output_filename": Path(output_path).name,
                    "output_path": output_path,
                    **result,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error adding text overlay to {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding text overlay: {str(e)}")


@router.post("/apply-filters")
async def apply_filters_endpoint(
    filename: str,
    brightness: Optional[float] = None,
    speed: Optional[float] = None,
    fade_in: Optional[float] = None,
    fade_out: Optional[float] = None,
    mirror_x: bool = False,
    mirror_y: bool = False
):
    """
    Apply various video filters
    
    - **filename**: Name of uploaded video file
    - **brightness**: Brightness adjustment (-1.0 to 1.0)
    - **speed**: Speed multiplier (0.5 = half speed, 2.0 = double speed)
    - **fade_in**: Fade in duration (seconds)
    - **fade_out**: Fade out duration (seconds)
    - **mirror_x**: Mirror horizontally
    - **mirror_y**: Mirror vertically
    """
    
    input_path = validate_video_file(filename)
    output_path = generate_output_path(filename, "filtered")
    
    # Build filters dictionary
    filters = {}
    if brightness is not None:
        if not -1.0 <= brightness <= 1.0:
            raise HTTPException(status_code=400, detail="Brightness must be between -1.0 and 1.0")
        filters["brightness"] = brightness
    
    if speed is not None:
        if not 0.1 <= speed <= 10.0:
            raise HTTPException(status_code=400, detail="Speed must be between 0.1 and 10.0")
        filters["speed"] = speed
    
    if fade_in is not None:
        if fade_in < 0:
            raise HTTPException(status_code=400, detail="Fade in duration must be positive")
        filters["fade_in"] = fade_in
    
    if fade_out is not None:
        if fade_out < 0:
            raise HTTPException(status_code=400, detail="Fade out duration must be positive")
        filters["fade_out"] = fade_out
    
    if mirror_x:
        filters["mirror_x"] = True
    
    if mirror_y:
        filters["mirror_y"] = True
    
    if not filters:
        raise HTTPException(status_code=400, detail="No filters specified")
    
    try:
        logger.info(f"Applying filters to video: {filename}")
        start_time = datetime.now()
        
        result = apply_video_filters(input_path, output_path, filters)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Video filters applied successfully",
                "data": {
                    "original_filename": filename,
                    "output_filename": Path(output_path).name,
                    "output_path": output_path,
                    **result,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error applying filters to {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error applying filters: {str(e)}")


@router.post("/extract-audio")
async def extract_audio_endpoint(filename: str):
    """
    Extract audio from video file
    
    - **filename**: Name of uploaded video file
    """
    
    input_path = validate_video_file(filename)
    audio_filename = f"audio_{Path(filename).stem}.wav"
    output_path = os.path.join(settings.PROCESSED_DIR, audio_filename)
    
    # Ensure processed directory exists
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    
    try:
        logger.info(f"Extracting audio from video: {filename}")
        start_time = datetime.now()
        
        result = extract_audio_from_video(input_path, output_path)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Audio extracted successfully",
                "data": {
                    "original_filename": filename,
                    "audio_filename": audio_filename,
                    "output_path": output_path,
                    **result,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error extracting audio from {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting audio: {str(e)}")


@router.post("/add-music")
async def add_background_music_endpoint(
    filename: str,
    music_filename: str,
    volume: float = 0.3,
    loop: bool = True
):
    """
    Add background music to video
    
    - **filename**: Name of uploaded video file
    - **music_filename**: Name of uploaded music file
    - **volume**: Music volume (0.0 - 1.0)
    - **loop**: Loop music if shorter than video
    """
    
    if not 0.0 <= volume <= 1.0:
        raise HTTPException(status_code=400, detail="Volume must be between 0.0 and 1.0")
    
    input_path = validate_video_file(filename)
    music_path = os.path.join(settings.UPLOAD_DIR, music_filename)
    
    if not os.path.exists(music_path):
        raise HTTPException(status_code=404, detail="Music file not found")
    
    output_path = generate_output_path(filename, "with_music")
    
    try:
        logger.info(f"Adding background music to video: {filename}")
        start_time = datetime.now()
        
        result = add_background_music(input_path, output_path, music_path, volume, loop)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Background music added successfully",
                "data": {
                    "original_filename": filename,
                    "music_filename": music_filename,
                    "output_filename": Path(output_path).name,
                    "output_path": output_path,
                    **result,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error adding background music to {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding background music: {str(e)}")


@router.post("/collage")
async def create_video_collage_endpoint(
    filenames: List[str],
    grid_rows: int = 2,
    grid_cols: int = 2
):
    """
    Create a video collage with multiple videos in a grid
    
    - **filenames**: List of video filenames
    - **grid_rows**: Number of rows in grid
    - **grid_cols**: Number of columns in grid
    """
    
    if len(filenames) < 2:
        raise HTTPException(status_code=400, detail="At least 2 videos required for collage")
    
    if grid_rows * grid_cols < len(filenames):
        raise HTTPException(status_code=400, detail="Grid size too small for number of videos")
    
    if grid_rows <= 0 or grid_cols <= 0:
        raise HTTPException(status_code=400, detail="Grid dimensions must be positive")
    
    # Validate all files exist
    input_paths = [validate_video_file(filename) for filename in filenames]
    output_path = generate_output_path("video_collage", "collage")
    
    try:
        logger.info(f"Creating video collage with {len(filenames)} videos")
        start_time = datetime.now()
        
        result = create_video_collage(input_paths, output_path, (grid_rows, grid_cols))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Video collage created successfully",
                "data": {
                    "input_filenames": filenames,
                    "output_filename": Path(output_path).name,
                    "output_path": output_path,
                    **result,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating video collage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating video collage: {str(e)}")


@router.post("/process", response_model=VideoProcessingResponse)
async def process_video_real(request: VideoProcessingRequest):
    """
    Process video with real trimming, cutting, and filters using FFmpeg
    
    This endpoint replaces the simulation-based processing with actual video manipulation.
    """
    try:
        logger.info(f"Processing video: {request.video_filename}")
        
        # Validate input file exists
        input_path = validate_video_file(request.video_filename)
        
        # Process video with real operations
        result = await video_processor.process_video(
            input_path=input_path,
            editing_data=request.editing_data,
            output_filename=request.output_filename
        )
        
        return VideoProcessingResponse(**result)
        
    except Exception as e:
        logger.error(f"Video processing failed: {str(e)}")
        return VideoProcessingResponse(
            success=False,
            error=str(e)
        )


@router.get("/download/{filename}")
async def download_processed_video(filename: str):
    """Download processed video file"""
    try:
        file_path = Path("processed") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="video/mp4"
        )
        
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-thumbnail/{filename}")
async def extract_video_thumbnail(filename: str, timestamp: float = 1.0):
    """Extract thumbnail from video at specified timestamp"""
    try:
        input_path = validate_video_file(filename)
        
        thumbnail_path = await video_processor.extract_thumbnail(
            video_path=input_path,
            timestamp=timestamp
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Thumbnail extracted successfully",
                "thumbnail_path": thumbnail_path,
                "timestamp": timestamp
            }
        )
        
    except Exception as e:
        logger.error(f"Thumbnail extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
