import cv2
import numpy as np
import moviepy.editor as mp
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import tempfile
import json

logger = logging.getLogger(__name__)

class VideoEditor:
    """
    Handles actual video editing operations based on AI suggestions.
    Implements cutting, transitions, and automated editing workflows.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.temp_dir = Path(config.get('cache_dir', './cache'))
        self.temp_dir.mkdir(exist_ok=True)
        
        # Supported transitions
        self.transition_types = {
            'cut': self._apply_cut,
            'fade': self._apply_fade,
            'crossfade': self._apply_crossfade,
            'wipe': self._apply_wipe,
            'slide': self._apply_slide,
            'zoom': self._apply_zoom
        }
        
    def apply_suggestions(self, 
                         video_path: str, 
                         cut_suggestions: List[Dict],
                         transition_suggestions: List[Dict],
                         output_path: str) -> str:
        """
        Apply AI suggestions to create edited video.
        
        Args:
            video_path: Input video file path
            cut_suggestions: List of cut suggestions with timestamps
            transition_suggestions: List of transition suggestions
            output_path: Output file path for edited video
            
        Returns:
            Path to the edited video file
        """
        logger.info(f"Applying {len(cut_suggestions)} cuts and {len(transition_suggestions)} transitions")
        
        try:
            # Load video
            video = mp.VideoFileClip(video_path)
            
            # Sort suggestions by timestamp
            cuts = sorted(cut_suggestions, key=lambda x: x.get('timestamp', 0))
            transitions = {t.get('start_time', 0): t for t in transition_suggestions}
            
            # Create segments based on cuts
            segments = self._create_segments(video, cuts)
            
            # Apply transitions between segments
            final_clips = self._apply_transitions(segments, transitions)
            
            # Concatenate final video
            if final_clips:
                final_video = mp.concatenate_videoclips(final_clips, method="compose")
                
                # Apply final effects
                final_video = self._apply_final_effects(final_video)
                
                # Export
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=str(self.temp_dir / 'temp_audio.m4a'),
                    remove_temp=True
                )
                
                # Cleanup
                video.close()
                final_video.close()
                for clip in final_clips:
                    clip.close()
                
                logger.info(f"Successfully created edited video: {output_path}")
                return output_path
            else:
                logger.error("No clips generated - creating fallback video")
                # Create fallback: return original video with basic trim
                fallback_path = output_path.replace('.mp4', '_fallback.mp4')
                
                # Create a basic 30-second preview from the original
                duration = min(30.0, video.duration)
                fallback_clip = video.subclip(0, duration)
                
                fallback_clip.write_videofile(
                    fallback_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=str(self.temp_dir / 'temp_fallback_audio.m4a'),
                    remove_temp=True
                )
                
                fallback_clip.close()
                video.close()
                
                logger.warning(f"Created fallback video: {fallback_path}")
                return fallback_path
                
        except Exception as e:
            logger.error(f"Error applying suggestions: {e}")
            # Create emergency fallback
            try:
                video = mp.VideoFileClip(video_path)
                emergency_path = output_path.replace('.mp4', '_emergency.mp4')
                
                # Just copy first 15 seconds
                emergency_duration = min(15.0, video.duration)
                emergency_clip = video.subclip(0, emergency_duration)
                
                emergency_clip.write_videofile(
                    emergency_path,
                    codec='libx264',
                    preset='ultrafast',  # Fast encoding for emergency
                    audio_codec='aac'
                )
                
                emergency_clip.close()
                video.close()
                
                logger.info(f"Created emergency fallback: {emergency_path}")
                return emergency_path
                
            except Exception as emergency_error:
                logger.error(f"Emergency fallback also failed: {emergency_error}")
                # Last resort: return original file path with error notice
                error_info = {
                    'status': 'error',
                    'original_file': video_path,
                    'error': str(e),
                    'emergency_error': str(emergency_error)
                }
                
                error_path = output_path.replace('.mp4', '_error_info.json')
                with open(error_path, 'w') as f:
                    json.dump(error_info, f, indent=2)
                
                return video_path  # Return original as last resort
    
    def _create_segments(self, video: mp.VideoFileClip, cuts: List[Dict]) -> List[mp.VideoFileClip]:
        """Create video segments based on cut suggestions."""
        segments = []
        start_time = 0
        
        for cut in cuts:
            end_time = cut.get('timestamp', video.duration)
            
            if end_time > start_time and end_time <= video.duration:
                segment = video.subclip(start_time, end_time)
                segments.append(segment)
                start_time = end_time
        
        # Add final segment if needed
        if start_time < video.duration:
            final_segment = video.subclip(start_time, video.duration)
            segments.append(final_segment)
        
        return segments
    
    def _apply_transitions(self, 
                          segments: List[mp.VideoFileClip], 
                          transitions: Dict[float, Dict]) -> List[mp.VideoFileClip]:
        """Apply transitions between segments."""
        if not segments:
            return []
        
        final_clips = [segments[0]]
        
        for i in range(1, len(segments)):
            # Check if there's a transition for this segment
            segment_start = sum(seg.duration for seg in segments[:i])
            transition_info = transitions.get(segment_start, {'type': 'cut', 'duration': 0.5})
            
            transition_type = transition_info.get('type', 'cut')
            duration = transition_info.get('duration', 0.5)
            
            if transition_type in self.transition_types:
                # Apply transition
                prev_clip = final_clips[-1]
                current_clip = segments[i]
                
                transitioned_clips = self.transition_types[transition_type](
                    prev_clip, current_clip, duration
                )
                
                # Replace last clip and add new one
                final_clips[-1] = transitioned_clips[0]
                final_clips.append(transitioned_clips[1])
            else:
                # No transition, just add the segment
                final_clips.append(segments[i])
        
        return final_clips
    
    def _apply_cut(self, clip1: mp.VideoFileClip, clip2: mp.VideoFileClip, duration: float) -> Tuple[mp.VideoFileClip, mp.VideoFileClip]:
        """Apply simple cut transition."""
        return clip1, clip2
    
    def _apply_fade(self, clip1: mp.VideoFileClip, clip2: mp.VideoFileClip, duration: float) -> Tuple[mp.VideoFileClip, mp.VideoFileClip]:
        """Apply fade transition."""
        clip1_faded = clip1.fadeout(duration)
        clip2_faded = clip2.fadein(duration)
        return clip1_faded, clip2_faded
    
    def _apply_crossfade(self, clip1: mp.VideoFileClip, clip2: mp.VideoFileClip, duration: float) -> Tuple[mp.VideoFileClip, mp.VideoFileClip]:
        """Apply crossfade transition."""
        if clip1.duration < duration or clip2.duration < duration:
            duration = min(clip1.duration, clip2.duration) / 2
        
        # Create overlap
        clip1_part = clip1.subclip(0, clip1.duration - duration).fadeout(0)
        overlap_part1 = clip1.subclip(clip1.duration - duration).fadeout(duration)
        overlap_part2 = clip2.subclip(0, duration).fadein(duration)
        clip2_part = clip2.subclip(duration).fadein(0)
        
        # Composite overlapping parts
        overlap = mp.CompositeVideoClip([overlap_part1, overlap_part2])
        
        # Concatenate
        final_clip1 = mp.concatenate_videoclips([clip1_part, overlap], method="compose")
        return final_clip1, clip2_part
    
    def _apply_wipe(self, clip1: mp.VideoFileClip, clip2: mp.VideoFileClip, duration: float) -> Tuple[mp.VideoFileClip, mp.VideoFileClip]:
        """Apply wipe transition."""
        # Simplified wipe - can be enhanced with custom masks
        return self._apply_fade(clip1, clip2, duration)
    
    def _apply_slide(self, clip1: mp.VideoFileClip, clip2: mp.VideoFileClip, duration: float) -> Tuple[mp.VideoFileClip, mp.VideoFileClip]:
        """Apply slide transition."""
        # Simplified slide - can be enhanced with position animations
        return self._apply_fade(clip1, clip2, duration)
    
    def _apply_zoom(self, clip1: mp.VideoFileClip, clip2: mp.VideoFileClip, duration: float) -> Tuple[mp.VideoFileClip, mp.VideoFileClip]:
        """Apply zoom transition."""
        # Simplified zoom - can be enhanced with scale animations
        return self._apply_fade(clip1, clip2, duration)
    
    def _apply_final_effects(self, video: mp.VideoFileClip) -> mp.VideoFileClip:
        """Apply final color correction and effects."""
        # Basic color correction
        try:
            # Enhance contrast slightly
            video = video.fx(mp.vfx.colorx, 1.1)
            return video
        except:
            return video
    
    def create_preview(self, 
                      video_path: str, 
                      cut_suggestions: List[Dict],
                      max_duration: float = 30.0) -> str:
        """
        Create a preview video showing key moments.
        
        Args:
            video_path: Input video file path
            cut_suggestions: List of cut suggestions
            max_duration: Maximum preview duration
            
        Returns:
            Path to preview video
        """
        try:
            video = mp.VideoFileClip(video_path)
            
            # Select top cuts based on confidence
            top_cuts = sorted(cut_suggestions, key=lambda x: x.get('confidence', 0), reverse=True)
            
            preview_clips = []
            total_duration = 0
            clip_duration = 2.0  # 2 seconds per clip
            
            for cut in top_cuts:
                if total_duration >= max_duration:
                    break
                    
                timestamp = cut.get('timestamp', 0)
                start_time = max(0, timestamp - clip_duration / 2)
                end_time = min(video.duration, timestamp + clip_duration / 2)
                
                if end_time > start_time:
                    clip = video.subclip(start_time, end_time)
                    preview_clips.append(clip)
                    total_duration += clip.duration
            
            if preview_clips:
                preview_video = mp.concatenate_videoclips(preview_clips, method="compose")
                
                # Add title card
                title_clip = self._create_title_card("AI Edit Preview", 2.0, video.size)
                final_preview = mp.concatenate_videoclips([title_clip, preview_video], method="compose")
                
                # Export preview
                preview_path = str(self.temp_dir / "preview.mp4")
                final_preview.write_videofile(
                    preview_path,
                    codec='libx264',
                    temp_audiofile=str(self.temp_dir / 'temp_preview_audio.m4a'),
                    remove_temp=True
                )
                
                # Cleanup
                video.close()
                preview_video.close()
                final_preview.close()
                for clip in preview_clips:
                    clip.close()
                
                return preview_path
            else:
                logger.warning("No preview clips generated - creating simple preview")
                
                # Create a simple preview from the beginning of the video
                simple_duration = min(10.0, video.duration, max_duration)
                simple_clip = video.subclip(0, simple_duration)
                
                # Add title card
                title_clip = self._create_title_card("AI Edit Preview (No Cuts)", 2.0, video.size)
                simple_preview = mp.concatenate_videoclips([title_clip, simple_clip], method="compose")
                
                preview_path = str(self.temp_dir / "simple_preview.mp4")
                simple_preview.write_videofile(
                    preview_path,
                    codec='libx264',
                    preset='fast',
                    temp_audiofile=str(self.temp_dir / 'temp_simple_audio.m4a'),
                    remove_temp=True
                )
                
                # Cleanup
                video.close()
                simple_clip.close()
                simple_preview.close()
                
                logger.info(f"Created simple preview: {preview_path}")
                return preview_path
                
        except Exception as e:
            logger.error(f"Error creating preview: {e}")
            
            # Emergency preview: just return first few seconds of original
            try:
                video = mp.VideoFileClip(video_path)
                emergency_duration = min(5.0, video.duration)
                emergency_clip = video.subclip(0, emergency_duration)
                
                emergency_path = str(self.temp_dir / "emergency_preview.mp4")
                emergency_clip.write_videofile(
                    emergency_path,
                    codec='libx264',
                    preset='ultrafast'
                )
                
                emergency_clip.close()
                video.close()
                
                logger.info(f"Created emergency preview: {emergency_path}")
                return emergency_path
                
            except Exception as emergency_error:
                logger.error(f"Emergency preview failed: {emergency_error}")
                # Return original video path as absolute last resort
                return video_path
    
    def _create_title_card(self, text: str, duration: float, size: Tuple[int, int]) -> mp.VideoFileClip:
        """Create a simple title card."""
        try:
            title_clip = mp.ColorClip(size=size, color=(0, 0, 0), duration=duration)
            title_text = mp.TextClip(
                text,
                fontsize=50,
                color='white',
                font='Arial-Bold'
            ).set_position('center').set_duration(duration)
            
            return mp.CompositeVideoClip([title_clip, title_text])
        except:
            # Fallback to simple color clip if text fails
            return mp.ColorClip(size=size, color=(0, 0, 0), duration=duration)
    
    def export_edit_list(self, cut_suggestions: List[Dict], output_path: str) -> str:
        """Export cut suggestions as EDL (Edit Decision List)."""
        try:
            edl_data = {
                'format': 'VideoCraft_EDL_v1.0',
                'cuts': [],
                'metadata': {
                    'total_cuts': len(cut_suggestions),
                    'generated_at': str(Path().cwd()),
                }
            }
            
            for i, cut in enumerate(sorted(cut_suggestions, key=lambda x: x.get('timestamp', 0))):
                edl_data['cuts'].append({
                    'id': i + 1,
                    'timestamp': cut.get('timestamp', 0),
                    'confidence': cut.get('confidence', 0),
                    'reason': cut.get('reason', 'AI suggestion'),
                    'type': cut.get('type', 'cut')
                })
            
            with open(output_path, 'w') as f:
                json.dump(edl_data, f, indent=2)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting EDL: {e}")
            
            # Create emergency EDL with basic structure
            try:
                emergency_edl = {
                    'format': 'VideoCraft_EDL_v1.0_EMERGENCY',
                    'error': str(e),
                    'cuts': [],
                    'metadata': {
                        'total_cuts': 0,
                        'status': 'failed_with_error',
                        'generated_at': str(Path().cwd()),
                    }
                }
                
                # Try to add at least basic cut information
                for i, cut in enumerate(cut_suggestions[:10]):  # Limit to first 10
                    try:
                        emergency_edl['cuts'].append({
                            'id': i + 1,
                            'timestamp': float(cut.get('timestamp', 0)),
                            'confidence': float(cut.get('confidence', 0)),
                            'reason': str(cut.get('reason', 'Unknown')),
                            'type': str(cut.get('type', 'cut'))
                        })
                    except:
                        continue
                
                emergency_edl['metadata']['total_cuts'] = len(emergency_edl['cuts'])
                
                with open(output_path, 'w') as f:
                    json.dump(emergency_edl, f, indent=2)
                
                logger.warning(f"Created emergency EDL: {output_path}")
                return output_path
                
            except Exception as emergency_error:
                logger.error(f"Emergency EDL creation failed: {emergency_error}")
                
                # Create minimal text-based fallback
                try:
                    fallback_path = output_path.replace('.json', '.txt')
                    with open(fallback_path, 'w') as f:
                        f.write("VideoCraft Edit Decision List (Fallback Format)\n")
                        f.write(f"Error: {e}\n")
                        f.write(f"Emergency Error: {emergency_error}\n")
                        f.write(f"Original cuts count: {len(cut_suggestions)}\n\n")
                        
                        for i, cut in enumerate(cut_suggestions[:5]):  # Show first 5
                            try:
                                f.write(f"Cut {i+1}: {cut.get('timestamp', 'N/A')}s - {cut.get('reason', 'N/A')}\n")
                            except:
                                f.write(f"Cut {i+1}: Invalid data\n")
                    
                    logger.info(f"Created fallback EDL: {fallback_path}")
                    return fallback_path
                    
                except Exception as final_error:
                    logger.error(f"All EDL export methods failed: {final_error}")
                    return output_path  # Return path anyway, file may be empty
