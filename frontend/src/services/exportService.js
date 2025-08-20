import jsPDF from 'jspdf';

// Export Service - Handle video export functionality
const API_BASE_URL = 'http://localhost:8000';

class ExportService {
  // Export video with backend processing
  static async exportVideo(videoData, editingData, quality = '720p', onProgress = null) {
    try {
      if (onProgress) onProgress(0);
      
      // Extract filename from different possible sources
      let filename = this.extractFilename(videoData);
      
      if (!filename) {
        throw new Error('No video file available for export. Please upload a video first.');
      }

      if (onProgress) onProgress(20);

      // Try backend export first, fallback to direct download if API not available
      try {
        // Send export request to backend
        const response = await fetch(`${API_BASE_URL}/export/video`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            video_filename: filename,
            export_type: 'video',
            editing_data: editingData || {},
            quality: quality
          })
        });

        if (onProgress) onProgress(60);

        if (!response.ok) {
          throw new Error(`Backend export failed: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();

        if (!result.success) {
          throw new Error(result.message || 'Video export failed');
        }

        if (onProgress) onProgress(80);

        // Download the video file
        const downloadUrl = `${API_BASE_URL}${result.download_url}`;
        await this.downloadFile(downloadUrl, result.filename);

        if (onProgress) onProgress(100);
        
        return {
          success: true,
          fileName: result.filename,
          message: result.message || 'Video exported successfully!',
          editingApplied: result.editing_applied || false
        };

      } catch (backendError) {
        console.warn('Backend export failed, trying direct download:', backendError);
        
        // Fallback: try direct download
        if (onProgress) onProgress(70);
        
        const directUrl = `${API_BASE_URL}/video/${encodeURIComponent(filename)}`;
        const checkResponse = await fetch(directUrl);
        
        if (!checkResponse.ok) {
          throw new Error('Video file not found on server. Please upload a video file first.');
        }
        
        if (onProgress) onProgress(90);
        
        const blob = await checkResponse.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `exported_${filename}`;
        a.click();
        URL.revokeObjectURL(url);

        if (onProgress) onProgress(100);
        
        return {
          success: true,
          fileName: `exported_${filename}`,
          message: 'Video exported successfully! (Direct download - editing features not applied)',
          editingApplied: false
        };
      }
      
    } catch (error) {
      console.error('Export failed:', error);
      throw error;
    }
  }
  
  // Export project report as PDF
  static async exportProjectReport(videoData, editingData) {
    try {
      const filename = this.extractFilename(videoData) || 'unknown-video';
      
      // Try backend first, fallback to local generation
      try {
        const response = await fetch(`${API_BASE_URL}/export/report`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            video_filename: filename,
            export_type: 'report',
            editing_data: editingData || {}
          })
        });

        if (response.ok) {
          const result = await response.json();

          if (result.success) {
            // Generate PDF from the report data
            const pdf = new jsPDF();
            const reportData = result.report_data;
            
            // Title
            pdf.setFontSize(20);
            pdf.text('VideoCraft Project Report', 20, 30);
            
            // Video Information
            pdf.setFontSize(14);
            pdf.text('Video Information', 20, 50);
            pdf.setFontSize(10);
            pdf.text(`Video: ${reportData.video_name}`, 20, 60);
            pdf.text(`Export Date: ${new Date(reportData.export_date).toLocaleDateString()}`, 20, 70);
            
            let yPos = 90;
            
            // Editing Summary
            if (reportData.editing_summary && Object.keys(reportData.editing_summary).length > 0) {
              pdf.setFontSize(14);
              pdf.text('Editing Summary', 20, yPos);
              yPos += 10;
              pdf.setFontSize(10);
              
              Object.entries(reportData.editing_summary).forEach(([key, value]) => {
                if (yPos > 250) {
                  pdf.addPage();
                  yPos = 30;
                }
                pdf.text(`${key}: ${JSON.stringify(value)}`, 20, yPos);
                yPos += 10;
              });
              yPos += 10;
            }
            
            // Recommendations
            if (reportData.recommendations && reportData.recommendations.length > 0) {
              pdf.setFontSize(14);
              pdf.text('AI Recommendations', 20, yPos);
              yPos += 10;
              pdf.setFontSize(10);
              
              reportData.recommendations.slice(0, 5).forEach((rec, index) => {
                if (yPos > 250) {
                  pdf.addPage();
                  yPos = 30;
                }
                pdf.text(`${index + 1}. ${rec.type}: ${rec.reason}`, 20, yPos);
                yPos += 8;
              });
            }
            
            // Save PDF
            const fileName = `project_report_${filename.replace('.mp4', '')}_${new Date().toISOString().split('T')[0]}.pdf`;
            pdf.save(fileName);
            
            return {
              success: true,
              fileName,
              message: 'Project report exported successfully!'
            };
          }
        }
      } catch (backendError) {
        console.warn('Backend report generation failed, using fallback:', backendError);
      }

      // Fallback: Generate local PDF report
      const pdf = new jsPDF();
      
      // Title
      pdf.setFontSize(20);
      pdf.text('VideoCraft Project Report', 20, 30);
      
      // Project Info
      pdf.setFontSize(14);
      pdf.text('Project Information', 20, 50);
      pdf.setFontSize(10);
      pdf.text(`Video: ${filename}`, 20, 60);
      pdf.text(`Export Date: ${new Date().toLocaleDateString()}`, 20, 70);
      pdf.text(`Export Time: ${new Date().toLocaleTimeString()}`, 20, 80);
      
      // Editing Summary
      pdf.setFontSize(14);
      pdf.text('Editing Summary', 20, 100);
      pdf.setFontSize(10);
      
      let yPos = 110;
      
      if (editingData && Object.keys(editingData).length > 0) {
        Object.entries(editingData).forEach(([key, value]) => {
          if (yPos > 250) {
            pdf.addPage();
            yPos = 30;
          }
          pdf.text(`${key}: ${JSON.stringify(value)}`, 20, yPos);
          yPos += 10;
        });
      } else {
        pdf.text('No editing data available', 20, yPos);
      }
      
      // Save PDF
      const fileName = `project_report_${filename.replace('.mp4', '')}_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);
      
      return {
        success: true,
        fileName,
        message: 'Project report exported successfully! (Local generation)'
      };
      
    } catch (error) {
      console.error('Report export failed:', error);
      throw error;
    }
  }
  
  // Export analysis report
  static async exportAnalysisReport(videoData, analysisData) {
    try {
      const filename = this.extractFilename(videoData) || 'unknown-video';
      
      // Try backend first, fallback to local generation
      try {
        const response = await fetch(`${API_BASE_URL}/export/analysis`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            video_filename: filename,
            export_type: 'analysis',
            editing_data: {}
          })
        });

        if (response.ok) {
          const result = await response.json();

          if (result.success) {
            // Generate PDF from analysis data
            const pdf = new jsPDF();
            const analysis = result.analysis_data.analysis_results;
            
            // Title
            pdf.setFontSize(20);
            pdf.text('Video Analysis Report', 20, 30);
            
            // Video Information
            pdf.setFontSize(14);
            pdf.text('Video Information', 20, 50);
            pdf.setFontSize(10);
            pdf.text(`Video: ${filename}`, 20, 60);
            pdf.text(`Analysis Date: ${new Date().toLocaleDateString()}`, 20, 70);
            
            let yPos = 90;
            
            // Video Info
            if (analysis.video_info) {
              pdf.setFontSize(14);
              pdf.text('Video Metrics', 20, yPos);
              yPos += 10;
              pdf.setFontSize(10);
              pdf.text(`Duration: ${analysis.video_info.duration || 'N/A'}`, 20, yPos);
              yPos += 8;
              pdf.text(`Resolution: ${analysis.video_info.resolution || 'N/A'}`, 20, yPos);
              yPos += 8;
              pdf.text(`Frame Rate: ${analysis.video_info.fps || 'N/A'} fps`, 20, yPos);
              yPos += 16;
            }
            
            // AI Analysis sections
            if (analysis.scene_analysis) {
              pdf.setFontSize(14);
              pdf.text('Scene Analysis', 20, yPos);
              yPos += 10;
              pdf.setFontSize(10);
              
              analysis.scene_analysis.slice(0, 5).forEach((scene, index) => {
                if (yPos > 250) {
                  pdf.addPage();
                  yPos = 30;
                }
                pdf.text(`Scene ${index + 1}: ${scene.description}`, 20, yPos);
                yPos += 8;
              });
              yPos += 10;
            }
            
            // Save PDF
            const fileName = `analysis_report_${filename.replace('.mp4', '')}_${new Date().toISOString().split('T')[0]}.pdf`;
            pdf.save(fileName);
            
            return {
              success: true,
              fileName,
              message: 'Analysis report exported successfully!'
            };
          }
        }
      } catch (backendError) {
        console.warn('Backend analysis export failed, using fallback:', backendError);
      }

      // Fallback: Generate local analysis report
      const pdf = new jsPDF();
      
      // Title
      pdf.setFontSize(20);
      pdf.text('Video Analysis Report', 20, 30);
      
      // Video Information
      pdf.setFontSize(14);
      pdf.text('Video Information', 20, 50);
      pdf.setFontSize(10);
      pdf.text(`Video: ${filename}`, 20, 60);
      pdf.text(`Analysis Date: ${new Date().toLocaleDateString()}`, 20, 70);
      
      let yPos = 90;
      
      // Basic Analysis (fallback data)
      pdf.setFontSize(14);
      pdf.text('Analysis Summary', 20, yPos);
      yPos += 10;
      pdf.setFontSize(10);
      pdf.text('Video processed with local analysis', 20, yPos);
      yPos += 8;
      pdf.text('Format: MP4', 20, yPos);
      yPos += 8;
      
      if (analysisData && Object.keys(analysisData).length > 0) {
        yPos += 10;
        pdf.setFontSize(14);
        pdf.text('Analysis Data', 20, yPos);
        yPos += 10;
        pdf.setFontSize(10);
        
        Object.entries(analysisData).forEach(([key, value]) => {
          if (yPos > 250) {
            pdf.addPage();
            yPos = 30;
          }
          pdf.text(`${key}: ${JSON.stringify(value).substring(0, 50)}`, 20, yPos);
          yPos += 8;
        });
      }
      
      // Save PDF
      const fileName = `analysis_report_${filename.replace('.mp4', '')}_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);
      
      return {
        success: true,
        fileName,
        message: 'Analysis report exported successfully! (Local generation)'
      };
      
    } catch (error) {
      console.error('Analysis report export failed:', error);
      throw error;
    }
  }
        
        pdf.text(`Duration: ${analysis.video_info.duration || 'N/A'}`, 20, yPos);
        yPos += 10;
        pdf.text(`Resolution: ${analysis.video_info.resolution || 'N/A'}`, 20, yPos);
        yPos += 10;
        pdf.text(`Format: ${analysis.video_info.format || 'N/A'}`, 20, yPos);
        yPos += 20;
      }
      
      // Emotion Analysis
      if (analysis.emotion_analysis && analysis.emotion_analysis.detected_emotions) {
        pdf.setFontSize(14);
        pdf.text('Emotion Analysis', 20, yPos);
        yPos += 10;
        pdf.setFontSize(10);
        
        analysis.emotion_analysis.detected_emotions.slice(0, 5).forEach(emotion => {
          pdf.text(`• ${emotion.emotion} (${(emotion.confidence * 100).toFixed(1)}% confidence) at ${emotion.timestamp}s`, 20, yPos);
          yPos += 10;
        });
        yPos += 10;
      }
      
      // Scene Analysis
      if (analysis.scene_analysis && analysis.scene_analysis.scene_changes) {
        if (yPos > 200) {
          pdf.addPage();
          yPos = 30;
        }
        
        pdf.setFontSize(14);
        pdf.text('Scene Detection', 20, yPos);
        yPos += 10;
        pdf.setFontSize(10);
        
        analysis.scene_analysis.scene_changes.slice(0, 5).forEach(scene => {
          pdf.text(`• ${scene.scene_type} at ${scene.timestamp}s (${(scene.confidence * 100).toFixed(1)}% confidence)`, 20, yPos);
          yPos += 10;
        });
      }
      
      // Save the PDF
      const fileName = `analysis_report_${filename.replace('.mp4', '')}_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);
      
      return {
        success: true,
        fileName,
        message: 'Analysis report exported successfully!'
      };
      
    } catch (error) {
      console.error('Analysis export error:', error);
      throw error;
    }
  }
  
  // Export project data as JSON
  static async exportProjectData(videoData, editingData) {
    try {
      const filename = this.extractFilename(videoData) || 'unknown-video';
      
      // Get project data from backend
      const response = await fetch(`${API_BASE_URL}/export/data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_filename: filename,
          export_type: 'data',
          editing_data: editingData || {}
        })
      });

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.message || 'Data export failed');
      }

      // Download as JSON file
      const jsonString = JSON.stringify(result.project_data, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = result.filename;
      a.click();
      
      URL.revokeObjectURL(url);
      
      return {
        success: true,
        fileName: result.filename,
        message: result.message || 'Project data exported successfully!'
      };
      
    } catch (error) {
      console.error('Data export failed:', error);
      throw error;
    }
  }
  
  // Helper method to extract filename from various video data formats
  static extractFilename(videoData) {
    if (!videoData) return null;
    
    // Try different possible sources for filename
    if (typeof videoData === 'string') {
      // If it's a string, it might be a filename or blob URL
      if (videoData.startsWith('blob:')) {
        return 'demo-video.mp4'; // Fallback for demo data
      }
      return videoData;
    }
    
    // Check various properties that might contain the filename
    if (videoData.filename) return videoData.filename;
    if (videoData.name) return videoData.name;
    if (videoData.original_filename) return videoData.original_filename;
    if (videoData.videoName) return videoData.videoName;
    
    // If we have a URL, try to extract filename
    if (videoData.url && !videoData.url.startsWith('blob:')) {
      const parts = videoData.url.split('/');
      return parts[parts.length - 1];
    }
    
    // Default fallback
    return 'demo-video.mp4';
  }
  
  // Helper method to download files
  static async downloadFile(url, filename) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      const downloadUrl = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      a.click();
      
      URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Download failed:', error);
      throw error;
    }
  }
  
  // Utility methods
  static formatTime(time) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }
}

export default ExportService;
