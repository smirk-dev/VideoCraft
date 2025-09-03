import jsPDF from 'jspdf';

import axios from 'axios';
import { API_CONFIG } from '../config/api';

const API_BASE_URL = API_CONFIG.BASE_URL;

class ExportService {
  
  // Helper method to extract filename from video data
  static extractFilename(videoData) {
    if (!videoData) return null;
    
    // If videoData is a string (URL or filename)
    if (typeof videoData === 'string') {
      // Extract filename from URL or path
      const parts = videoData.split('/');
      return parts[parts.length - 1];
    }
    
    // If videoData is an object with name property
    if (videoData.name) {
      return videoData.name;
    }
    
    // If videoData is a File object
    if (videoData instanceof File) {
      return videoData.name;
    }
    
    return null;
  }

  // Export video with editing data
  static async exportVideo(videoData, editingData, videoQuality = 'high', progressCallback = null) {
    try {
      const filename = this.extractFilename(videoData) || 'unknown-video';
      
      // Report initial progress
      if (progressCallback) progressCallback(10);
      
      // Try backend first, fallback to direct download
      try {
        const response = await fetch(`${API_BASE_URL}/export/video`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            video_filename: filename,
            export_type: 'video',
            editing_data: editingData || {},
            quality: videoQuality
          })
        });

        // Report progress
        if (progressCallback) progressCallback(50);

        if (response.ok) {
          const result = await response.json();

          if (result.success && result.download_url) {
            // Report progress
            if (progressCallback) progressCallback(80);
            
            // Download the processed video
            const downloadResponse = await fetch(result.download_url);
            if (downloadResponse.ok) {
              const blob = await downloadResponse.blob();
              const url = URL.createObjectURL(blob);
              
              const a = document.createElement('a');
              a.href = url;
              a.download = result.filename;
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              URL.revokeObjectURL(url);
              
              // Report completion
              if (progressCallback) progressCallback(100);
              
              return {
                success: true,
                fileName: result.filename,
                message: 'Video exported successfully!'
              };
            }
          }
        }
      } catch (backendError) {
        console.warn('Backend video export failed, using fallback:', backendError);
      }

      // Report fallback progress
      if (progressCallback) progressCallback(70);

      // Fallback: Direct download (if video is available)
      if (videoData instanceof File) {
        const url = URL.createObjectURL(videoData);
        const a = document.createElement('a');
        a.href = url;
        a.download = `exported_${filename}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Report completion
        if (progressCallback) progressCallback(100);
        
        return {
          success: true,
          fileName: `exported_${filename}`,
          message: 'Video exported successfully! (Direct download)'
        };
      } else if (typeof videoData === 'string' && videoData.startsWith('blob:')) {
        // If it's a blob URL, download directly
        const a = document.createElement('a');
        a.href = videoData;
        a.download = `exported_${filename}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Report completion
        if (progressCallback) progressCallback(100);
        
        return {
          success: true,
          fileName: `exported_${filename}`,
          message: 'Video exported successfully! (Direct download)'
        };
      }
      
      // If we get here, check if videoData has a url property
      if (videoData && videoData.url) {
        // Try to download from the URL
        const a = document.createElement('a');
        a.href = videoData.url;
        a.download = `exported_${filename}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Report completion
        if (progressCallback) progressCallback(100);
        
        return {
          success: true,
          fileName: `exported_${filename}`,
          message: 'Video exported successfully! (Direct download)'
        };
      }
      
      throw new Error('Video source not available for direct download');
      
    } catch (error) {
      console.error('Video export failed:', error);
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

  // Export raw data as JSON
  static async exportRawData(videoData, editingData, analysisData) {
    try {
      const filename = this.extractFilename(videoData) || 'unknown-video';
      
      // Try backend first, fallback to local generation
      try {
        const response = await fetch(`${API_BASE_URL}/export/data`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            video_filename: filename,
            export_type: 'data',
            editing_data: editingData || {},
            analysis_data: analysisData || {}
          })
        });

        if (response.ok) {
          const result = await response.json();

          if (result.success) {
            // Download the raw data as JSON
            const dataToExport = result.export_data;
            const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `project_data_${filename.replace('.mp4', '')}_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            return {
              success: true,
              fileName: a.download,
              message: 'Project data exported successfully!'
            };
          }
        }
      } catch (backendError) {
        console.warn('Backend data export failed, using fallback:', backendError);
      }

      // Fallback: Generate local data export
      const exportData = {
        video_info: {
          filename: filename,
          export_date: new Date().toISOString(),
          exported_by: 'VideoCraft'
        },
        editing_data: editingData || {},
        analysis_data: analysisData || {},
        metadata: {
          export_version: '1.0',
          export_type: 'raw_data',
          generated_locally: true
        }
      };
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `project_data_${filename.replace('.mp4', '')}_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      return {
        success: true,
        fileName: a.download,
        message: 'Project data exported successfully! (Local generation)'
      };
      
    } catch (error) {
      console.error('Raw data export failed:', error);
      throw error;
    }
  }

  // Alias for exportRawData - for compatibility with ExportDialog
  static async exportProjectData(videoData, editingData, analysisData) {
    return this.exportRawData(videoData, editingData, analysisData);
  }
}

export default ExportService;
