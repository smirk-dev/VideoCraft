import jsPDF from 'jspdf';

// Export Service - Handle video export functionality
const API_BASE_URL = 'http://localhost:8000';

class ExportService {
  // Real video export with backend processing
  static async exportVideo(videoFile, editingData, quality = '720p', onProgress = null) {
    try {
      if (onProgress) onProgress(0);
      
      // Get the filename - handle different input types
      let filename;
      
      if (typeof videoFile === 'string') {
        // If it's a string, check if it's a blob URL or a filename
        if (videoFile.startsWith('blob:')) {
          // This is a blob URL from demo/test data
          throw new Error('Cannot export demo video. Please upload a real video file first, or try exporting the analysis report instead.');
        } else {
          // This should be a filename
          filename = videoFile;
        }
      } else if (videoFile?.name) {
        // This is a File object
        filename = videoFile.name;
      } else {
        throw new Error('No video file selected. Please upload a video first.');
      }

      if (onProgress) onProgress(10);

      // First, check if the video file exists on the server using our backend API
      const checkResponse = await fetch(`${API_BASE_URL}/video/${encodeURIComponent(filename)}`);
      
      if (!checkResponse.ok) {
        // Video file not found - provide helpful error message
        throw new Error('Video file not found on server. Please upload the video file first, or try exporting the analysis report instead.');
      }

      if (onProgress) onProgress(100);
      
      // Since we don't have video processing backend yet, 
      // just download the original video file
      const blob = await checkResponse.blob();
      
      // Create download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `exported_${filename}`;
      a.click();
      
      URL.revokeObjectURL(url);
      
      return {
        success: true,
        fileName: `exported_${filename}`,
        message: 'Video exported successfully! (Note: Advanced editing features require video processing backend)',
        videoInfo: { originalFile: filename },
        appliedOperations: ['download']
      };
      
    } catch (error) {
      console.error('Export failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  // Export project report as PDF
  static async exportProjectReport(projectData, editingData) {
    try {
      const pdf = new jsPDF();
      
      // Title
      pdf.setFontSize(20);
      pdf.text('VideoCraft Project Report', 20, 30);
      
      // Project Info
      pdf.setFontSize(14);
      pdf.text('Project Information', 20, 50);
      pdf.setFontSize(10);
      pdf.text(`Video: ${projectData.videoName || 'Untitled Video'}`, 20, 60);
      pdf.text(`Export Date: ${new Date().toLocaleDateString()}`, 20, 70);
      pdf.text(`Export Time: ${new Date().toLocaleTimeString()}`, 20, 80);
      
      // Editing Summary
      pdf.setFontSize(14);
      pdf.text('Editing Summary', 20, 100);
      pdf.setFontSize(10);
      
      let yPos = 110;
      
      // Duration info
      const originalDuration = this.formatTime(projectData.duration || 0);
      const trimmedDuration = this.formatTime((editingData.trimEnd || projectData.duration) - editingData.trimStart);
      
      pdf.text(`Original Duration: ${originalDuration}`, 20, yPos);
      yPos += 10;
      pdf.text(`Trimmed Duration: ${trimmedDuration}`, 20, yPos);
      yPos += 10;
      
      // Trim points
      if (editingData.trimStart > 0 || editingData.trimEnd < projectData.duration) {
        pdf.text(`Trim Start: ${this.formatTime(editingData.trimStart)}`, 20, yPos);
        yPos += 10;
        pdf.text(`Trim End: ${this.formatTime(editingData.trimEnd || projectData.duration)}`, 20, yPos);
        yPos += 10;
      }
      
      // Cut points
      if (editingData.cuts && editingData.cuts.length > 0) {
        pdf.text(`Cut Points (${editingData.cuts.length}):`, 20, yPos);
        yPos += 10;
        editingData.cuts.forEach((cut, index) => {
          pdf.text(`  ${index + 1}. ${this.formatTime(cut)}`, 25, yPos);
          yPos += 8;
        });
      }
      
      // Filters applied
      yPos += 10;
      pdf.setFontSize(14);
      pdf.text('Filters Applied', 20, yPos);
      yPos += 10;
      pdf.setFontSize(10);
      
      const filters = editingData.filters || {};
      Object.entries(filters).forEach(([filterName, value]) => {
        if (value !== 100 && value !== 0) { // Show only modified filters
          pdf.text(`${filterName}: ${value}${filterName === 'blur' ? 'px' : '%'}`, 20, yPos);
          yPos += 8;
        }
      });
      
      // Timeline visualization (simple text representation)
      yPos += 20;
      pdf.setFontSize(14);
      pdf.text('Timeline Overview', 20, yPos);
      yPos += 10;
      pdf.setFontSize(8);
      
      const timelineText = this.generateTimelineVisualization(editingData, projectData.duration);
      pdf.text(timelineText, 20, yPos);
      
      // Save PDF
      const fileName = `project_report_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);
      
      return {
        success: true,
        fileName,
        message: 'Project report exported successfully!'
      };
      
    } catch (error) {
      console.error('Report export failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  // Export project data as JSON
  static async exportProjectData(projectData, editingData) {
    try {
      const exportData = {
        exportInfo: {
          version: '1.0',
          exportDate: new Date().toISOString(),
          application: 'VideoCraft'
        },
        project: {
          name: projectData.name || 'Untitled Project',
          videoName: projectData.videoName,
          duration: projectData.duration,
          createdAt: projectData.createdAt || new Date().toISOString()
        },
        editing: {
          trimStart: editingData.trimStart,
          trimEnd: editingData.trimEnd,
          cuts: editingData.cuts || [],
          filters: editingData.filters || {}
        },
        stats: {
          originalDuration: projectData.duration,
          finalDuration: this.calculateFinalDuration(editingData, projectData.duration),
          cutsCount: (editingData.cuts || []).length,
          filtersApplied: Object.keys(editingData.filters || {}).length
        }
      };
      
      const jsonString = JSON.stringify(exportData, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const fileName = `project_data_${new Date().toISOString().split('T')[0]}.json`;
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      a.click();
      
      URL.revokeObjectURL(url);
      
      return {
        success: true,
        fileName,
        message: 'Project data exported successfully!'
      };
      
    } catch (error) {
      console.error('Data export failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  // Utility methods
  static getQualityDimensions(quality) {
    const qualities = {
      '480p': { width: 854, height: 480 },
      '720p': { width: 1280, height: 720 },
      '1080p': { width: 1920, height: 1080 },
      'original': { width: null, height: null }
    };
    return qualities[quality] || qualities['720p'];
  }
  
  static generateEditSummary(editingData) {
    const parts = [];
    
    if (editingData.trimStart > 0 || editingData.trimEnd) {
      parts.push('trimmed');
    }
    
    if (editingData.cuts && editingData.cuts.length > 0) {
      parts.push(`${editingData.cuts.length}cuts`);
    }
    
    const filters = editingData.filters || {};
    const modifiedFilters = Object.entries(filters).filter(([_, value]) => 
      value !== 100 && value !== 0
    );
    
    if (modifiedFilters.length > 0) {
      parts.push('filtered');
    }
    
    return parts.join('_') || 'edited';
  }
  
  static formatTime(time) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }
  
  static calculateFinalDuration(editingData, originalDuration) {
    let duration = (editingData.trimEnd || originalDuration) - editingData.trimStart;
    
    // Subtract cut segments (simplified)
    if (editingData.cuts) {
      duration -= editingData.cuts.length * 0.1; // Rough estimate
    }
    
    return Math.max(0, duration);
  }
  
  static generateTimelineVisualization(editingData, duration) {
    const width = 60; // Character width for timeline
    const timeline = Array(width).fill('-');
    
    // Mark trim start
    const trimStartPos = Math.floor((editingData.trimStart / duration) * width);
    if (trimStartPos < width) timeline[trimStartPos] = '[';
    
    // Mark trim end
    const trimEndPos = Math.floor(((editingData.trimEnd || duration) / duration) * width);
    if (trimEndPos < width) timeline[trimEndPos] = ']';
    
    // Mark cuts
    if (editingData.cuts) {
      editingData.cuts.forEach(cut => {
        const cutPos = Math.floor((cut / duration) * width);
        if (cutPos < width && cutPos > 0) {
          timeline[cutPos] = '|';
        }
      });
    }
    
    return timeline.join('') + '\n' +
           '0:00' + ' '.repeat(width - 8) + this.formatTime(duration) + '\n' +
           'Legend: [ = trim start, ] = trim end, | = cut point';
  }

  // Export analysis report as PDF
  static async exportAnalysisReport(videoData, analysisData) {
    try {
      const pdf = new jsPDF();
      
      // Title
      pdf.setFontSize(20);
      pdf.text('Video Analysis Report', 20, 30);
      
      // Video Information
      pdf.setFontSize(14);
      pdf.text('Video Information', 20, 50);
      pdf.setFontSize(10);
      pdf.text(`Video: ${videoData.filename || 'Untitled Video'}`, 20, 60);
      pdf.text(`Analysis Date: ${new Date().toLocaleDateString()}`, 20, 70);
      pdf.text(`Analysis Time: ${new Date().toLocaleTimeString()}`, 20, 80);
      
      let yPos = 90;
      
      // Video Metrics
      if (analysisData.videoMetrics) {
        pdf.setFontSize(14);
        pdf.text('Video Metrics', 20, yPos);
        yPos += 10;
        pdf.setFontSize(10);
        
        pdf.text(`Duration: ${analysisData.videoMetrics.duration}`, 20, yPos);
        yPos += 10;
        pdf.text(`Resolution: ${analysisData.videoMetrics.resolution}`, 20, yPos);
        yPos += 10;
        pdf.text(`File Size: ${analysisData.videoMetrics.fileSize}`, 20, yPos);
        yPos += 10;
        pdf.text(`Frame Rate: ${analysisData.videoMetrics.fps} FPS`, 20, yPos);
        yPos += 20;
      }
      
      // Emotion Analysis
      if (analysisData.emotions) {
        pdf.setFontSize(14);
        pdf.text('Emotion Analysis', 20, yPos);
        yPos += 10;
        pdf.setFontSize(10);
        
        analysisData.emotions.forEach(emotion => {
          pdf.text(`• ${emotion.emotion} (${(emotion.confidence * 100).toFixed(1)}% confidence) at ${emotion.timestamp}`, 20, yPos);
          yPos += 10;
        });
        yPos += 10;
      }
      
      // Scene Changes
      if (analysisData.sceneChanges) {
        pdf.setFontSize(14);
        pdf.text('Scene Detection', 20, yPos);
        yPos += 10;
        pdf.setFontSize(10);
        
        analysisData.sceneChanges.forEach(scene => {
          pdf.text(`• ${scene.type} at ${scene.timestamp} (${(scene.confidence * 100).toFixed(1)}% confidence)`, 20, yPos);
          yPos += 10;
        });
        yPos += 10;
      }
      
      // Check if we need a new page
      if (yPos > 250) {
        pdf.addPage();
        yPos = 30;
      }
      
      // Audio Analysis
      if (analysisData.audioAnalysis) {
        pdf.setFontSize(14);
        pdf.text('Audio Analysis', 20, yPos);
        yPos += 10;
        pdf.setFontSize(10);
        
        const audio = analysisData.audioAnalysis;
        pdf.text(`• Average Volume: ${audio.avgVolume}%`, 20, yPos);
        yPos += 10;
        pdf.text(`• Peak Volume: ${audio.peakVolume}%`, 20, yPos);
        yPos += 10;
        pdf.text(`• Silent Segments: ${audio.silentSegments}`, 20, yPos);
        yPos += 10;
        pdf.text(`• Music Detected: ${audio.musicDetected ? 'Yes' : 'No'}`, 20, yPos);
        yPos += 10;
        pdf.text(`• Speech Quality: ${audio.speechQuality}`, 20, yPos);
        yPos += 20;
      }
      
      // AI Suggestions
      if (analysisData.aiSuggestions) {
        pdf.setFontSize(14);
        pdf.text('AI Suggestions', 20, yPos);
        yPos += 10;
        pdf.setFontSize(10);
        
        analysisData.aiSuggestions.forEach(suggestion => {
          pdf.text(`• ${suggestion.type}: ${suggestion.reason}`, 20, yPos);
          yPos += 10;
          pdf.text(`  At ${suggestion.timestamp} (${(suggestion.confidence * 100).toFixed(0)}% confidence)`, 20, yPos);
          yPos += 10;
        });
      }
      
      // Save the PDF
      const fileName = `analysis_report_${videoData.filename.replace(/\.[^/.]+$/, "")}_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);
      
      return {
        success: true,
        fileName,
        message: 'Analysis report exported successfully!'
      };
      
    } catch (error) {
      console.error('Analysis export error:', error);
      throw new Error('Failed to export analysis report: ' + error.message);
    }
  }
}

export default ExportService;
