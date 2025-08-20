import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormControl,
  FormLabel,
  Tabs,
  Tab,
  LinearProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  VideoFile,
  Description,
  DataObject,
  Download,
  Info,
  CheckCircle,
  Error,
  Movie,
  PictureAsPdf,
  Code,
  Analytics
} from '@mui/icons-material';
import ExportService from '../../services/exportService';

const ExportDialog = ({ 
  open, 
  onClose, 
  videoData = {}
}) => {
  // Extract data from videoData prop with defaults
  const {
    filename = 'video',
    url: videoUrl,
    metadata: projectData = {},
    editingData: videoEditingData = {},
    analysisData = null,
    timeline = {}
  } = videoData;
  
  // Use videoEditingData with fallbacks
  const editingData = {
    trimStart: 0,
    trimEnd: projectData.duration || 0,
    cuts: [],
    filters: [],
    ...videoEditingData
  };
  
  const videoName = filename;
  const [currentTab, setCurrentTab] = useState(0);
  const [videoQuality, setVideoQuality] = useState('720p');
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportResult, setExportResult] = useState(null);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
    setExportResult(null);
  };

  const handleVideoExport = async () => {
    setIsExporting(true);
    setExportProgress(0);
    setExportResult(null);

    try {
      // Pass the entire videoData object to the service
      const result = await ExportService.exportVideo(
        { filename, url: videoUrl, ...videoData }, // Pass full video data
        editingData,
        videoQuality,
        (progress) => setExportProgress(progress)
      );
      
      setExportResult(result);
    } catch (error) {
      setExportResult({
        success: false,
        error: error.message
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleReportExport = async () => {
    setIsExporting(true);
    setExportResult(null);

    try {
      const result = await ExportService.exportProjectReport(
        { filename, ...videoData, ...projectData, videoName },
        editingData
      );
      setExportResult(result);
    } catch (error) {
      setExportResult({
        success: false,
        error: error.message
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleDataExport = async () => {
    setIsExporting(true);
    setExportResult(null);

    try {
      const result = await ExportService.exportProjectData(
        { filename, ...videoData, ...projectData, videoName },
        editingData
      );
      setExportResult(result);
    } catch (error) {
      setExportResult({
        success: false,
        error: error.message
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleAnalysisExport = async () => {
    setIsExporting(true);
    setExportResult(null);

    try {
      const result = await ExportService.exportAnalysisReport(
        { filename, ...videoData, ...projectData },
        analysisData
      );
      setExportResult(result);
    } catch (error) {
      setExportResult({
        success: false,
        error: error.message
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleClose = () => {
    if (!isExporting) {
      setExportResult(null);
      setExportProgress(0);
      onClose();
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getEditingSummary = () => {
    const summary = [];
    const duration = projectData?.duration || 0;
    
    if (editingData.trimStart > 0 || editingData.trimEnd < duration) {
      summary.push(`Trimmed: ${formatTime(editingData.trimStart)} - ${formatTime(editingData.trimEnd || duration)}`);
    }
    
    if (editingData.cuts && editingData.cuts.length > 0) {
      summary.push(`${editingData.cuts.length} cut point(s)`);
    }
    
    const filters = editingData.filters || {};
    const modifiedFilters = Object.entries(filters).filter(([_, value]) => 
      value !== 100 && value !== 0
    );
    
    if (modifiedFilters.length > 0) {
      summary.push(`${modifiedFilters.length} filter(s) applied`);
    }
    
    return summary;
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      disableEscapeKeyDown={isExporting}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Download />
          Export Project
        </Box>
      </DialogTitle>

      <DialogContent>
        {/* Project Summary */}
        <Box sx={{ mb: 3, p: 2, backgroundColor: '#f8f9fa', borderRadius: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
            Project: {videoName}
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
            <Chip label={`Duration: ${formatTime(projectData?.duration || 0)}`} size="small" />
            {getEditingSummary().map((item, index) => (
              <Chip key={index} label={item} size="small" color="primary" />
            ))}
          </Box>
        </Box>

        {/* Export Options Tabs */}
        <Tabs value={currentTab} onChange={handleTabChange} variant="fullWidth">
          <Tab icon={<VideoFile />} label="Video Export" />
          <Tab icon={<Description />} label="Project Report" />
          {analysisData && <Tab icon={<Analytics />} label="Analysis Report" />}
          <Tab icon={<DataObject />} label="Project Data" />
        </Tabs>

        <Box sx={{ mt: 2 }}>
          {/* Video Export Tab */}
          {currentTab === 0 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>Export Edited Video</Typography>
              
              <FormControl component="fieldset" sx={{ mb: 3 }}>
                <FormLabel component="legend">Video Quality</FormLabel>
                <RadioGroup
                  value={videoQuality}
                  onChange={(e) => setVideoQuality(e.target.value)}
                  row
                >
                  <FormControlLabel value="480p" control={<Radio />} label="480p (Small)" />
                  <FormControlLabel value="720p" control={<Radio />} label="720p (HD)" />
                  <FormControlLabel value="1080p" control={<Radio />} label="1080p (Full HD)" />
                  <FormControlLabel value="original" control={<Radio />} label="Original Quality" />
                </RadioGroup>
              </FormControl>

              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  The exported video will include all your edits: trim points, cuts, and applied filters.
                  Processing time depends on video length and quality.
                </Typography>
              </Alert>

              {isExporting && currentTab === 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Processing video... {exportProgress}%
                  </Typography>
                  <LinearProgress variant="determinate" value={exportProgress} />
                </Box>
              )}
            </Box>
          )}

          {/* Project Report Tab */}
          {currentTab === 1 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>Export Project Report</Typography>
              
              <List>
                <ListItem>
                  <ListItemIcon><PictureAsPdf /></ListItemIcon>
                  <ListItemText 
                    primary="PDF Report" 
                    secondary="Comprehensive project summary with editing details and timeline visualization"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon><Info /></ListItemIcon>
                  <ListItemText 
                    primary="Includes:" 
                    secondary="Project info, editing summary, trim/cut details, filters applied, timeline overview"
                  />
                </ListItem>
              </List>

              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Perfect for sharing project details or keeping records of your editing work.
                </Typography>
              </Alert>
            </Box>
          )}

          {/* Analysis Report Tab */}
          {analysisData && currentTab === 2 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>Export Analysis Report</Typography>
              
              <List>
                <ListItem>
                  <ListItemIcon><Analytics /></ListItemIcon>
                  <ListItemText 
                    primary="AI Analysis Report" 
                    secondary="Comprehensive PDF report including emotion analysis, scene detection, and AI suggestions"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon><Info /></ListItemIcon>
                  <ListItemText 
                    primary="Includes:" 
                    secondary="Video metrics, emotion timeline, scene changes, audio analysis, and optimization suggestions"
                  />
                </ListItem>
              </List>

              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Professional analysis report perfect for sharing insights or documentation.
                </Typography>
              </Alert>
            </Box>
          )}

          {/* Project Data Tab */}
          {currentTab === (analysisData ? 3 : 2) && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>Export Project Data</Typography>
              
              <List>
                <ListItem>
                  <ListItemIcon><Code /></ListItemIcon>
                  <ListItemText 
                    primary="JSON Data Export" 
                    secondary="Machine-readable project data for backup or integration with other tools"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon><Info /></ListItemIcon>
                  <ListItemText 
                    primary="Contains:" 
                    secondary="All editing parameters, timestamps, filter settings, and project metadata"
                  />
                </ListItem>
              </List>

              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Use this to backup your project settings or import into other video editing tools.
                </Typography>
              </Alert>
            </Box>
          )}

          {/* Export Result */}
          {exportResult && (
            <Box sx={{ mt: 2 }}>
              <Alert 
                severity={exportResult.success ? "success" : "error"}
                icon={exportResult.success ? <CheckCircle /> : <Error />}
                action={
                  exportResult.success && exportResult.fileName && (
                    <Button color="inherit" size="small">
                      Downloaded: {exportResult.fileName}
                    </Button>
                  )
                }
              >
                <Typography variant="body2">
                  {exportResult.success 
                    ? exportResult.message
                    : `Export failed: ${exportResult.error}`
                  }
                  {exportResult.success && exportResult.editingApplied && (
                    <><br /><strong>✅ Editing parameters were applied to the export</strong></>
                  )}
                </Typography>
              </Alert>
            </Box>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={isExporting}>
          Close
        </Button>
        <Button
          variant="contained"
          onClick={
            currentTab === 0 ? handleVideoExport :
            currentTab === 1 ? handleReportExport :
            (analysisData && currentTab === 2) ? handleAnalysisExport :
            handleDataExport
          }
          disabled={isExporting}
          startIcon={
            currentTab === 0 ? <Movie /> :
            currentTab === 1 ? <PictureAsPdf /> :
            (analysisData && currentTab === 2) ? <Analytics /> :
            <DataObject />
          }
        >
          {isExporting ? 'Exporting...' : 
           currentTab === 0 ? 'Export Video' :
           currentTab === 1 ? 'Export Report' :
           (analysisData && currentTab === 2) ? 'Export Analysis' :
           'Export Data'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ExportDialog;
