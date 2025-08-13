import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union
import csv
from pathlib import Path
import logging
from datetime import datetime, timedelta
import zipfile
import tempfile

logger = logging.getLogger(__name__)

class ProfessionalExporter:
    """
    Export video editing suggestions to professional formats compatible with
    major video editing software (Adobe Premiere, DaVinci Resolve, Final Cut Pro, etc.)
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.temp_dir = Path(config.get('cache_dir', './cache'))
        self.temp_dir.mkdir(exist_ok=True)
        
        # Supported export formats
        self.export_formats = {
            'edl': self.export_edl,
            'xml': self.export_xml,
            'csv': self.export_csv,
            'json': self.export_json,
            'fcpxml': self.export_fcpxml,
            'aaf': self.export_aaf_metadata,
            'premiere': self.export_premiere_xml,
            'resolve': self.export_resolve_drp,
            'avid': self.export_avid_edl
        }
    
    def export_suggestions(self, 
                          cut_suggestions: List[Dict],
                          transition_suggestions: List[Dict],
                          video_metadata: Dict,
                          output_format: str,
                          output_path: str,
                          project_settings: Optional[Dict] = None) -> str:
        """
        Export editing suggestions to professional format.
        
        Args:
            cut_suggestions: List of cut suggestions with timestamps
            transition_suggestions: List of transition suggestions
            video_metadata: Video file metadata
            output_format: Target export format
            output_path: Output file path
            project_settings: Optional project settings
            
        Returns:
            Path to exported file
        """
        if output_format not in self.export_formats:
            raise ValueError(f"Unsupported format: {output_format}")
        
        try:
            # Prepare data for export
            export_data = self._prepare_export_data(
                cut_suggestions, transition_suggestions, video_metadata, project_settings
            )
            
            # Export using appropriate method
            result_path = self.export_formats[output_format](export_data, output_path)
            
            logger.info(f"Successfully exported {len(cut_suggestions)} suggestions to {output_format}")
            return result_path
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise
    
    def export_edl(self, data: Dict, output_path: str) -> str:
        """Export as EDL (Edit Decision List) format."""
        
        edl_content = []
        edl_content.append("TITLE: VideoCraft AI Editing Suggestions")
        edl_content.append("FCM: NON-DROP FRAME")
        edl_content.append("")
        
        # Add cuts as EDL events
        for i, cut in enumerate(data['cuts'], 1):
            timecode_in = self._frames_to_timecode(cut['frame_in'], data['fps'])
            timecode_out = self._frames_to_timecode(cut['frame_out'], data['fps'])
            source_in = timecode_in
            source_out = timecode_out
            
            # EDL event line
            edl_content.append(f"{i:03d}  001      V     C        {source_in} {source_out} {timecode_in} {timecode_out}")
            
            # Add comment with AI confidence
            edl_content.append(f"* FROM CLIP NAME: AI_CUT_CONFIDENCE_{cut['confidence']:.2f}")
            edl_content.append(f"* COMMENT: {cut.get('reason', 'AI suggestion')}")
            edl_content.append("")
        
        # Write EDL file
        with open(output_path, 'w') as f:
            f.write('\n'.join(edl_content))
        
        return output_path
    
    def export_xml(self, data: Dict, output_path: str) -> str:
        """Export as XML format for general compatibility."""
        
        root = ET.Element("videocraft_export")
        root.set("version", "1.0")
        root.set("exported_at", datetime.now().isoformat())
        
        # Metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "source_video").text = data['source_file']
        ET.SubElement(metadata, "duration").text = str(data['duration'])
        ET.SubElement(metadata, "fps").text = str(data['fps'])
        ET.SubElement(metadata, "resolution").text = f"{data['width']}x{data['height']}"
        
        # Cuts
        cuts_elem = ET.SubElement(root, "cuts")
        for cut in data['cuts']:
            cut_elem = ET.SubElement(cuts_elem, "cut")
            cut_elem.set("id", str(cut['id']))
            cut_elem.set("timestamp", str(cut['timestamp']))
            cut_elem.set("confidence", str(cut['confidence']))
            cut_elem.set("type", cut.get('type', 'standard'))
            
            ET.SubElement(cut_elem, "reason").text = cut.get('reason', '')
            ET.SubElement(cut_elem, "frame_number").text = str(cut.get('frame_number', 0))
        
        # Transitions
        transitions_elem = ET.SubElement(root, "transitions")
        for transition in data['transitions']:
            trans_elem = ET.SubElement(transitions_elem, "transition")
            trans_elem.set("type", transition['type'])
            trans_elem.set("duration", str(transition['duration']))
            trans_elem.set("start_time", str(transition['start_time']))
            trans_elem.set("confidence", str(transition.get('confidence', 1.0)))
        
        # Write XML
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        return output_path
    
    def export_fcpxml(self, data: Dict, output_path: str) -> str:
        """Export as Final Cut Pro XML format."""
        
        # FCPXML namespace
        ns = "http://apple.com/fcp/xml/latest"
        ET.register_namespace("", ns)
        
        root = ET.Element(f"{{{ns}}}fcpxml")
        root.set("version", "1.8")
        
        # Resources
        resources = ET.SubElement(root, f"{{{ns}}}resources")
        
        # Format resource
        format_elem = ET.SubElement(resources, f"{{{ns}}}format")
        format_elem.set("id", "r1")
        format_elem.set("name", f"FFVideoFormat{data['width']}x{data['height']}p{data['fps']}")
        format_elem.set("frameDuration", f"{1001}s/{int(data['fps'] * 1001)}")
        format_elem.set("width", str(data['width']))
        format_elem.set("height", str(data['height']))
        
        # Asset resource
        asset = ET.SubElement(resources, f"{{{ns}}}asset")
        asset.set("id", "r2")
        asset.set("name", Path(data['source_file']).stem)
        asset.set("start", "0s")
        asset.set("duration", f"{data['duration']}s")
        asset.set("format", "r1")
        
        # Media representation
        media = ET.SubElement(asset, f"{{{ns}}}media-rep")
        media.set("kind", "original-media")
        media.set("src", data['source_file'])
        
        # Library
        library = ET.SubElement(root, f"{{{ns}}}library")
        library.set("location", str(Path(output_path).parent))
        
        # Event
        event = ET.SubElement(library, f"{{{ns}}}event")
        event.set("name", "VideoCraft AI Edits")
        
        # Project
        project = ET.SubElement(event, f"{{{ns}}}project")
        project.set("name", "AI Editing Suggestions")
        
        # Sequence
        sequence = ET.SubElement(project, f"{{{ns}}}sequence")
        sequence.set("format", "r1")
        sequence.set("duration", f"{data['duration']}s")
        
        # Spine (main timeline)
        spine = ET.SubElement(sequence, f"{{{ns}}}spine")
        
        # Add clips based on cuts
        for i, cut in enumerate(data['cuts']):
            if i == 0:
                start_time = 0
            else:
                start_time = data['cuts'][i-1]['timestamp']
            
            end_time = cut['timestamp']
            duration = end_time - start_time
            
            if duration > 0:
                clip = ET.SubElement(spine, f"{{{ns}}}asset-clip")
                clip.set("ref", "r2")
                clip.set("offset", f"{start_time}s")
                clip.set("start", f"{start_time}s")
                clip.set("duration", f"{duration}s")
                clip.set("name", f"AI_Segment_{i+1}")
                
                # Add marker for AI suggestion
                marker = ET.SubElement(clip, f"{{{ns}}}marker")
                marker.set("start", "0s")
                marker.set("duration", "1/30s")
                marker.set("value", f"AI Cut Confidence: {cut['confidence']:.2f}")
        
        # Write FCPXML
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        return output_path
    
    def export_premiere_xml(self, data: Dict, output_path: str) -> str:
        """Export as Adobe Premiere Pro XML format."""
        
        root = ET.Element("xmeml")
        root.set("version", "4")
        
        # Project
        project = ET.SubElement(root, "project")
        
        # Name
        ET.SubElement(project, "name").text = "VideoCraft AI Project"
        
        # Children
        children = ET.SubElement(project, "children")
        
        # Bin
        bin_elem = ET.SubElement(children, "bin")
        
        # Bin children
        bin_children = ET.SubElement(bin_elem, "children")
        
        # Clip
        clip = ET.SubElement(bin_children, "clip")
        clip.set("id", "clip1")
        
        ET.SubElement(clip, "name").text = Path(data['source_file']).stem
        ET.SubElement(clip, "duration").text = str(int(data['duration'] * data['fps']))
        ET.SubElement(clip, "rate")
        
        rate = clip.find("rate")
        ET.SubElement(rate, "timebase").text = str(int(data['fps']))
        ET.SubElement(rate, "ntsc").text = "FALSE"
        
        # Media
        media = ET.SubElement(clip, "media")
        video_elem = ET.SubElement(media, "video")
        
        track = ET.SubElement(video_elem, "track")
        
        # Add cuts as clips on timeline
        for i, cut in enumerate(data['cuts']):
            if i == 0:
                start_frame = 0
            else:
                start_frame = int(data['cuts'][i-1]['timestamp'] * data['fps'])
            
            end_frame = int(cut['timestamp'] * data['fps'])
            duration_frames = end_frame - start_frame
            
            if duration_frames > 0:
                clip_item = ET.SubElement(track, "clipitem")
                clip_item.set("id", f"clipitem{i+1}")
                
                ET.SubElement(clip_item, "name").text = f"AI_Segment_{i+1}"
                ET.SubElement(clip_item, "start").text = str(start_frame)
                ET.SubElement(clip_item, "end").text = str(end_frame)
                ET.SubElement(clip_item, "in").text = str(start_frame)
                ET.SubElement(clip_item, "out").text = str(end_frame)
        
        # Write XML
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        return output_path
    
    def export_resolve_drp(self, data: Dict, output_path: str) -> str:
        """Export as DaVinci Resolve project format (simplified)."""
        
        # DaVinci Resolve uses a complex binary format, so we'll export
        # a compatible XML that can be imported
        resolve_data = {
            "project_name": "VideoCraft AI Project",
            "timeline_name": "AI Edited Timeline",
            "fps": data['fps'],
            "resolution": {"width": data['width'], "height": data['height']},
            "clips": []
        }
        
        # Convert cuts to Resolve-compatible clips
        for i, cut in enumerate(data['cuts']):
            if i == 0:
                start_time = 0
            else:
                start_time = data['cuts'][i-1]['timestamp']
            
            end_time = cut['timestamp']
            duration = end_time - start_time
            
            if duration > 0:
                clip_data = {
                    "name": f"AI_Clip_{i+1}",
                    "start_time": start_time,
                    "duration": duration,
                    "source_file": data['source_file'],
                    "source_in": start_time,
                    "source_out": end_time,
                    "ai_confidence": cut['confidence'],
                    "ai_reason": cut.get('reason', 'AI suggestion')
                }
                resolve_data["clips"].append(clip_data)
        
        # Add transitions
        resolve_data["transitions"] = data['transitions']
        
        # Export as JSON (can be converted to DRP format by custom tools)
        with open(output_path, 'w') as f:
            json.dump(resolve_data, f, indent=2)
        
        return output_path
    
    def export_csv(self, data: Dict, output_path: str) -> str:
        """Export as CSV format for spreadsheet analysis."""
        
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Type', 'ID', 'Timestamp', 'Timecode', 'Confidence', 
                'Reason', 'Frame_Number', 'Duration', 'Additional_Info'
            ])
            
            # Cuts
            for cut in data['cuts']:
                timecode = self._seconds_to_timecode(cut['timestamp'], data['fps'])
                writer.writerow([
                    'Cut',
                    cut['id'],
                    cut['timestamp'],
                    timecode,
                    cut['confidence'],
                    cut.get('reason', ''),
                    cut.get('frame_number', ''),
                    '',
                    f"Method: {cut.get('method', 'AI')}"
                ])
            
            # Transitions
            for i, transition in enumerate(data['transitions']):
                timecode = self._seconds_to_timecode(transition['start_time'], data['fps'])
                writer.writerow([
                    'Transition',
                    f"T{i+1}",
                    transition['start_time'],
                    timecode,
                    transition.get('confidence', 1.0),
                    f"Type: {transition['type']}",
                    '',
                    transition['duration'],
                    f"Auto-generated transition"
                ])
        
        return output_path
    
    def export_json(self, data: Dict, output_path: str) -> str:
        """Export as JSON format with full metadata."""
        
        export_data = {
            "export_info": {
                "created_by": "VideoCraft AI",
                "version": "1.0",
                "export_date": datetime.now().isoformat(),
                "format": "json"
            },
            "project_settings": {
                "fps": data['fps'],
                "resolution": {"width": data['width'], "height": data['height']},
                "duration": data['duration'],
                "source_file": data['source_file']
            },
            "ai_analysis": {
                "total_cuts": len(data['cuts']),
                "total_transitions": len(data['transitions']),
                "average_confidence": sum(c['confidence'] for c in data['cuts']) / len(data['cuts']) if data['cuts'] else 0,
                "processing_time": data.get('processing_time', 0)
            },
            "cuts": data['cuts'],
            "transitions": data['transitions'],
            "metadata": data.get('metadata', {})
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_path
    
    def export_aaf_metadata(self, data: Dict, output_path: str) -> str:
        """Export AAF-compatible metadata (simplified)."""
        
        # AAF is a complex binary format, so we'll export metadata
        # that can be used with AAF conversion tools
        aaf_metadata = {
            "composition": {
                "name": "VideoCraft AI Composition",
                "length": int(data['duration'] * data['fps']),
                "sample_rate": {
                    "numerator": int(data['fps'] * 1001),
                    "denominator": 1001
                }
            },
            "master_mob": {
                "name": "VideoCraft Master",
                "slots": []
            },
            "source_mob": {
                "name": Path(data['source_file']).stem,
                "essence_descriptor": {
                    "sample_rate": f"{data['fps']}",
                    "frame_layout": "FullFrame",
                    "stored_width": data['width'],
                    "stored_height": data['height']
                }
            },
            "sequence": {
                "components": []
            }
        }
        
        # Add components (clips) based on cuts
        for i, cut in enumerate(data['cuts']):
            if i == 0:
                start_time = 0
            else:
                start_time = data['cuts'][i-1]['timestamp']
            
            end_time = cut['timestamp']
            duration = end_time - start_time
            
            if duration > 0:
                component = {
                    "class": "SourceClip",
                    "length": int(duration * data['fps']),
                    "start_time": int(start_time * data['fps']),
                    "source_mob_slot": 1,
                    "user_comments": {
                        "AI_Confidence": str(cut['confidence']),
                        "AI_Reason": cut.get('reason', ''),
                        "VideoCraft_ID": str(cut['id'])
                    }
                }
                aaf_metadata["sequence"]["components"].append(component)
        
        # Export as JSON metadata
        with open(output_path, 'w') as f:
            json.dump(aaf_metadata, f, indent=2)
        
        return output_path
    
    def export_avid_edl(self, data: Dict, output_path: str) -> str:
        """Export as Avid-compatible EDL format."""
        
        edl_content = []
        edl_content.append("TITLE: VideoCraft AI for Avid")
        edl_content.append("FCM: NON-DROP FRAME")
        edl_content.append("")
        
        # Avid-specific EDL format
        for i, cut in enumerate(data['cuts'], 1):
            source_start = self._frames_to_timecode(0, data['fps'])
            source_end = self._frames_to_timecode(int(cut['timestamp'] * data['fps']), data['fps'])
            record_start = source_start
            record_end = source_end
            
            # Event line with Avid-specific formatting
            edl_content.append(f"{i:03d}  AX       V     C        {source_start} {source_end} {record_start} {record_end}")
            
            # Avid comments
            edl_content.append(f"* FROM CLIP NAME: {Path(data['source_file']).stem}")
            edl_content.append(f"* TO CLIP NAME: AI_CUT_{i:03d}")
            edl_content.append(f"* COMMENT: CONFIDENCE={cut['confidence']:.3f} REASON={cut.get('reason', 'AI')}")
            
            # Avid locator for AI metadata
            edl_content.append(f"* LOC: {source_start} WHITE AI_MARKER_CONF_{cut['confidence']:.2f}")
            edl_content.append("")
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(edl_content))
        
        return output_path
    
    def create_project_package(self, 
                              cut_suggestions: List[Dict],
                              transition_suggestions: List[Dict],
                              video_metadata: Dict,
                              output_dir: str,
                              formats: List[str] = None) -> str:
        """
        Create a complete project package with multiple export formats.
        
        Args:
            cut_suggestions: Cut suggestions
            transition_suggestions: Transition suggestions  
            video_metadata: Video metadata
            output_dir: Output directory
            formats: List of formats to export (default: all)
            
        Returns:
            Path to project package zip file
        """
        if formats is None:
            formats = ['edl', 'xml', 'csv', 'json', 'fcpxml']
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        project_name = f"videocraft_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir = output_path / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Export in all requested formats
        exported_files = []
        for format_name in formats:
            if format_name in self.export_formats:
                format_file = project_dir / f"{project_name}.{format_name}"
                try:
                    self.export_suggestions(
                        cut_suggestions,
                        transition_suggestions,
                        video_metadata,
                        format_name,
                        str(format_file)
                    )
                    exported_files.append(format_file)
                except Exception as e:
                    logger.warning(f"Failed to export {format_name}: {e}")
        
        # Create README file
        readme_content = self._create_readme(cut_suggestions, transition_suggestions, video_metadata)
        readme_file = project_dir / "README.txt"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        # Create ZIP package
        zip_path = output_path / f"{project_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in exported_files + [readme_file]:
                zipf.write(file_path, file_path.name)
        
        # Cleanup temporary directory
        import shutil
        shutil.rmtree(project_dir)
        
        logger.info(f"Created project package: {zip_path}")
        return str(zip_path)
    
    def _prepare_export_data(self, 
                           cut_suggestions: List[Dict],
                           transition_suggestions: List[Dict],
                           video_metadata: Dict,
                           project_settings: Optional[Dict]) -> Dict:
        """Prepare data for export."""
        
        # Sort cuts by timestamp
        sorted_cuts = sorted(cut_suggestions, key=lambda x: x.get('timestamp', 0))
        
        # Prepare cut data
        cuts = []
        for i, cut in enumerate(sorted_cuts):
            cut_data = {
                'id': i + 1,
                'timestamp': cut.get('timestamp', 0),
                'confidence': cut.get('confidence', 0.5),
                'reason': cut.get('reason', 'AI suggestion'),
                'type': cut.get('type', 'cut'),
                'frame_number': int(cut.get('timestamp', 0) * video_metadata.get('fps', 30)),
                'frame_in': int(cut.get('timestamp', 0) * video_metadata.get('fps', 30)),
                'frame_out': int(cut.get('timestamp', 0) * video_metadata.get('fps', 30)) + 1,
                'method': cut.get('method', 'AI')
            }
            cuts.append(cut_data)
        
        # Prepare transition data
        transitions = []
        for transition in transition_suggestions:
            trans_data = {
                'type': transition.get('type', 'cut'),
                'duration': transition.get('duration', 0.5),
                'start_time': transition.get('start_time', 0),
                'confidence': transition.get('confidence', 1.0)
            }
            transitions.append(trans_data)
        
        return {
            'cuts': cuts,
            'transitions': transitions,
            'source_file': video_metadata.get('file_path', ''),
            'duration': video_metadata.get('duration', 0),
            'fps': video_metadata.get('fps', 30),
            'width': video_metadata.get('width', 1920),
            'height': video_metadata.get('height', 1080),
            'processing_time': video_metadata.get('processing_time', 0),
            'metadata': project_settings or {}
        }
    
    def _frames_to_timecode(self, frame: int, fps: float) -> str:
        """Convert frame number to timecode."""
        seconds = frame / fps
        return self._seconds_to_timecode(seconds, fps)
    
    def _seconds_to_timecode(self, seconds: float, fps: float) -> str:
        """Convert seconds to timecode (HH:MM:SS:FF)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds % 1) * fps)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"
    
    def _create_readme(self, cuts: List[Dict], transitions: List[Dict], metadata: Dict) -> str:
        """Create README file for project package."""
        
        readme = f"""VideoCraft AI Editing Project
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PROJECT SUMMARY
===============
Source Video: {metadata.get('file_path', 'Unknown')}
Duration: {metadata.get('duration', 0):.2f} seconds
Resolution: {metadata.get('width', 0)}x{metadata.get('height', 0)}
Frame Rate: {metadata.get('fps', 30)} fps
Total Cuts: {len(cuts)}
Total Transitions: {len(transitions)}

AI ANALYSIS RESULTS
==================
Average Cut Confidence: {sum(c.get('confidence', 0) for c in cuts) / len(cuts) * 100:.1f}% (if cuts else 0)
Processing Method: Advanced Multi-Modal AI Analysis

EXPORTED FORMATS
===============
- EDL: Industry standard Edit Decision List
- XML: General purpose XML format
- CSV: Spreadsheet-compatible format for analysis
- JSON: Complete metadata with full AI analysis
- FCPXML: Final Cut Pro import format
- Premiere XML: Adobe Premiere Pro compatible

USAGE INSTRUCTIONS
=================
1. Import the appropriate format into your video editing software
2. Review AI suggestions and adjust as needed
3. Use confidence scores to prioritize which cuts to apply
4. Consider the AI reasoning provided for each suggestion

CONFIDENCE LEVELS
================
90-100%: Very High - Strong recommendation
70-89%:  High - Good recommendation
50-69%:  Medium - Consider carefully
30-49%:  Low - Use with caution
0-29%:   Very Low - Manual review recommended

For support and documentation, visit: https://github.com/your-repo/videocraft
"""
        return readme
