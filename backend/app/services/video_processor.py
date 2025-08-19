"""
Real Video Processing Engine using FFmpeg
Handles actual video trimming, cutting, and filter application
"""
import os
import subprocess
import tempfile
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import asyncio
from datetime import datetime

from ..core.config import settings
from ..core.logging_config import get_logger

logger = get_logger("video_processor")


class VideoProcessor:
    """Real video processing using FFmpeg"""
    
    def __init__(self):
        self.temp_dir = Path("temp")
        self.output_dir = Path("processed")
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    async def process_video(
        self, 
        input_path: str, 
        editing_data: Dict,
        output_filename: Optional[str] = None
    ) -> Dict:
        """
        Process video with real trimming, cutting, and filters
        
        Args:
            input_path: Path to input video file
            editing_data: Dictionary containing trim points, cuts, and filters
            output_filename: Optional output filename
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Starting video processing for: {input_path}")
            
            # Extract editing parameters
            trim_start = editing_data.get('trimStart', 0)
            trim_end = editing_data.get('trimEnd')
            cuts = editing_data.get('cuts', [])
            filters = editing_data.get('filters', [])
            
            # Generate output filename if not provided
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"processed_video_{timestamp}.mp4"
            
            output_path = self.output_dir / output_filename
            
            # Step 1: Apply trimming
            trimmed_path = await self._apply_trim(input_path, trim_start, trim_end)
            
            # Step 2: Apply cuts (remove segments)
            cut_path = await self._apply_cuts(trimmed_path, cuts)
            
            # Step 3: Apply filters
            filtered_path = await self._apply_filters(cut_path, filters)
            
            # Step 4: Move to final output location
            if filtered_path != output_path:
                os.rename(filtered_path, output_path)
            
            # Get output video info
            video_info = await self._get_video_info(str(output_path))
            
            # Cleanup temporary files
            await self._cleanup_temp_files([trimmed_path, cut_path, filtered_path])
            
            logger.info(f"Video processing completed: {output_path}")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "output_filename": output_filename,
                "video_info": video_info,
                "processing_time": "Processing completed",
                "applied_operations": {
                    "trim": {"start": trim_start, "end": trim_end},
                    "cuts": cuts,
                    "filters": filters
                }
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _apply_trim(self, input_path: str, start_time: float, end_time: Optional[float]) -> str:
        """Apply trimming to video"""
        if start_time == 0 and end_time is None:
            return input_path
        
        output_path = self.temp_dir / f"trimmed_{os.path.basename(input_path)}"
        
        cmd = [
            "ffmpeg", "-i", input_path,
            "-ss", str(start_time)
        ]
        
        if end_time is not None:
            duration = end_time - start_time
            cmd.extend(["-t", str(duration)])
        
        cmd.extend([
            "-c", "copy",  # Copy without re-encoding for speed
            "-avoid_negative_ts", "make_zero",
            str(output_path), "-y"
        ])
        
        await self._run_ffmpeg_command(cmd)
        return str(output_path)
    
    async def _apply_cuts(self, input_path: str, cuts: List[Dict]) -> str:
        """Apply cuts (remove segments) from video"""
        if not cuts:
            return input_path
        
        # Sort cuts by start time
        sorted_cuts = sorted(cuts, key=lambda x: x['start'])
        
        output_path = self.temp_dir / f"cut_{os.path.basename(input_path)}"
        
        # Create filter complex for removing segments
        filter_parts = []
        input_index = 0
        
        video_info = await self._get_video_info(input_path)
        total_duration = float(video_info.get('duration', 0))
        
        current_time = 0
        segment_index = 0
        
        for cut in sorted_cuts:
            cut_start = cut['start']
            cut_end = cut['end']
            
            # Add segment before cut
            if current_time < cut_start:
                filter_parts.append(
                    f"[0:v]trim=start={current_time}:end={cut_start},setpts=PTS-STARTPTS[v{segment_index}];"
                    f"[0:a]atrim=start={current_time}:end={cut_start},asetpts=PTS-STARTPTS[a{segment_index}]"
                )
                segment_index += 1
            
            current_time = cut_end
        
        # Add final segment
        if current_time < total_duration:
            filter_parts.append(
                f"[0:v]trim=start={current_time},setpts=PTS-STARTPTS[v{segment_index}];"
                f"[0:a]atrim=start={current_time},asetpts=PTS-STARTPTS[a{segment_index}]"
            )
            segment_index += 1
        
        if segment_index == 0:
            return input_path
        
        # Concatenate segments
        video_inputs = "".join([f"[v{i}]" for i in range(segment_index)])
        audio_inputs = "".join([f"[a{i}]" for i in range(segment_index)])
        
        filter_complex = ";".join(filter_parts) + f";{video_inputs}concat=n={segment_index}:v=1:a=0[outv];{audio_inputs}concat=n={segment_index}:v=0:a=1[outa]"
        
        cmd = [
            "ffmpeg", "-i", input_path,
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "[outa]",
            str(output_path), "-y"
        ]
        
        await self._run_ffmpeg_command(cmd)
        return str(output_path)
    
    async def _apply_filters(self, input_path: str, filters: List[Dict]) -> str:
        """Apply video filters"""
        if not filters:
            return input_path
        
        output_path = self.temp_dir / f"filtered_{os.path.basename(input_path)}"
        
        # Build filter chain
        video_filters = []
        audio_filters = []
        
        for filter_config in filters:
            filter_type = filter_config.get('type')
            filter_params = filter_config.get('params', {})
            
            if filter_type == 'brightness':
                value = filter_params.get('value', 0)
                video_filters.append(f"eq=brightness={value/100}")
            
            elif filter_type == 'contrast':
                value = filter_params.get('value', 1)
                video_filters.append(f"eq=contrast={value}")
            
            elif filter_type == 'saturation':
                value = filter_params.get('value', 1)
                video_filters.append(f"eq=saturation={value}")
            
            elif filter_type == 'blur':
                radius = filter_params.get('radius', 2)
                video_filters.append(f"boxblur={radius}:{radius}")
            
            elif filter_type == 'grayscale':
                video_filters.append("hue=s=0")
            
            elif filter_type == 'sepia':
                video_filters.append("colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131")
            
            elif filter_type == 'volume':
                value = filter_params.get('value', 1)
                audio_filters.append(f"volume={value}")
            
            elif filter_type == 'speed':
                speed = filter_params.get('speed', 1)
                video_filters.append(f"setpts={1/speed}*PTS")
                audio_filters.append(f"atempo={speed}")
        
        cmd = ["ffmpeg", "-i", input_path]
        
        if video_filters and audio_filters:
            vf = ",".join(video_filters)
            af = ",".join(audio_filters)
            cmd.extend(["-vf", vf, "-af", af])
        elif video_filters:
            vf = ",".join(video_filters)
            cmd.extend(["-vf", vf])
        elif audio_filters:
            af = ",".join(audio_filters)
            cmd.extend(["-af", af])
        
        cmd.extend([str(output_path), "-y"])
        
        await self._run_ffmpeg_command(cmd)
        return str(output_path)
    
    async def _get_video_info(self, video_path: str) -> Dict:
        """Get video information using ffprobe"""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            video_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"ffprobe failed: {stderr.decode()}")
        
        info = json.loads(stdout.decode())
        
        # Extract relevant information
        video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), {})
        audio_stream = next((s for s in info['streams'] if s['codec_type'] == 'audio'), {})
        
        return {
            "duration": float(info['format'].get('duration', 0)),
            "size": int(info['format'].get('size', 0)),
            "bitrate": int(info['format'].get('bit_rate', 0)),
            "video": {
                "codec": video_stream.get('codec_name'),
                "width": video_stream.get('width'),
                "height": video_stream.get('height'),
                "fps": eval(video_stream.get('r_frame_rate', '0/1')) if video_stream.get('r_frame_rate') else 0
            },
            "audio": {
                "codec": audio_stream.get('codec_name'),
                "sample_rate": audio_stream.get('sample_rate'),
                "channels": audio_stream.get('channels')
            }
        }
    
    async def _run_ffmpeg_command(self, cmd: List[str]):
        """Run FFmpeg command asynchronously"""
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode()
            logger.error(f"FFmpeg command failed: {error_msg}")
            raise Exception(f"FFmpeg processing failed: {error_msg}")
        
        logger.info("FFmpeg command completed successfully")
    
    async def _cleanup_temp_files(self, file_paths: List[str]):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path) and file_path != str(self.output_dir):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    async def extract_thumbnail(self, video_path: str, timestamp: float = 1.0) -> str:
        """Extract thumbnail from video at specified timestamp"""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        thumbnail_path = self.output_dir / f"thumbnail_{timestamp_str}.jpg"
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", str(timestamp),
            "-vframes", "1",
            "-q:v", "2",
            str(thumbnail_path), "-y"
        ]
        
        await self._run_ffmpeg_command(cmd)
        return str(thumbnail_path)
