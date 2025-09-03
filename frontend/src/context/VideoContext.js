import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { API_CONFIG } from '../config/api';

// Video action types
const VIDEO_ACTIONS = {
  SET_VIDEO: 'SET_VIDEO',
  CLEAR_VIDEO: 'CLEAR_VIDEO',
  SET_PROCESSING: 'SET_PROCESSING',
  SET_ERROR: 'SET_ERROR',
  UPDATE_METADATA: 'UPDATE_METADATA',
  SET_EDITING_DATA: 'SET_EDITING_DATA',
  SET_CURRENT_PROJECT: 'SET_CURRENT_PROJECT',
  CLEAR_CURRENT_PROJECT: 'CLEAR_CURRENT_PROJECT'
};

// Initial state
const initialState = {
  currentVideo: "test_video.mp4", // Default video for testing
  videoFile: null,
  videoUrl: null,
  videoMetadata: {
    duration: 120,
    width: 1920,
    height: 1080,
    size: 50000000,
    type: "video/mp4",
    name: "test_video.mp4"
  },
  isProcessing: false,
  error: null,
  editingData: {
    trimStart: 0,
    trimEnd: null,
    cuts: [],
    filters: []
  },
  currentProject: null  // Currently loaded project data
};

// Video reducer
const videoReducer = (state, action) => {
  switch (action.type) {
    case VIDEO_ACTIONS.SET_VIDEO:
      return {
        ...state,
        currentVideo: action.payload.video,
        videoFile: action.payload.file,
        videoUrl: action.payload.url,
        videoMetadata: action.payload.metadata,
        isProcessing: false,
        error: null
      };
    
    case VIDEO_ACTIONS.CLEAR_VIDEO:
      return {
        ...initialState
      };
    
    case VIDEO_ACTIONS.SET_PROCESSING:
      return {
        ...state,
        isProcessing: action.payload
      };
    
    case VIDEO_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isProcessing: false
      };
    
    case VIDEO_ACTIONS.UPDATE_METADATA:
      return {
        ...state,
        videoMetadata: {
          ...state.videoMetadata,
          ...action.payload
        }
      };
    
    case VIDEO_ACTIONS.SET_EDITING_DATA:
      return {
        ...state,
        editingData: {
          ...state.editingData,
          ...action.payload
        }
      };
    
    case VIDEO_ACTIONS.SET_CURRENT_PROJECT:
      return {
        ...state,
        currentProject: action.payload
      };
    
    case VIDEO_ACTIONS.CLEAR_CURRENT_PROJECT:
      return {
        ...state,
        currentProject: null
      };
    
    default:
      return state;
  }
};

// Create context
const VideoContext = createContext();

// Video provider component
export const VideoProvider = ({ children }) => {
  const [state, dispatch] = useReducer(videoReducer, initialState);

  // Set new video
  const setVideo = useCallback((videoData) => {
    dispatch({
      type: VIDEO_ACTIONS.SET_VIDEO,
      payload: videoData
    });
  }, []);

  // Clear current video
  const clearVideo = useCallback(() => {
    dispatch({
      type: VIDEO_ACTIONS.CLEAR_VIDEO
    });
  }, []);

  // Set processing state
  const setProcessing = useCallback((isProcessing) => {
    dispatch({
      type: VIDEO_ACTIONS.SET_PROCESSING,
      payload: isProcessing
    });
  }, []);

  // Set error
  const setError = useCallback((error) => {
    dispatch({
      type: VIDEO_ACTIONS.SET_ERROR,
      payload: error
    });
  }, []);

  // Update video metadata
  const updateMetadata = useCallback((metadata) => {
    dispatch({
      type: VIDEO_ACTIONS.UPDATE_METADATA,
      payload: metadata
    });
  }, []);

  // Update editing data
  const updateEditingData = useCallback((editingData) => {
    dispatch({
      type: VIDEO_ACTIONS.SET_EDITING_DATA,
      payload: editingData
    });
  }, []);

  // Upload video with automatic metadata extraction
  const uploadVideo = useCallback(async (file) => {
    setProcessing(true);
    setError(null);

    try {
      // Create local URL for immediate preview
      const url = URL.createObjectURL(file);
      
      // Extract basic metadata
      const video = document.createElement('video');
      video.preload = 'metadata';
      
      const metadata = await new Promise((resolve, reject) => {
        video.onloadedmetadata = () => {
          resolve({
            duration: video.duration,
            width: video.videoWidth,
            height: video.videoHeight,
            size: file.size,
            type: file.type,
            name: file.name,
            lastModified: file.lastModified
          });
        };
        video.onerror = reject;
        video.src = url;
      });

      // Set video data
      setVideo({
        video: file.name,
        file: file,
        url: url,
        metadata: metadata
      });

      // Initialize editing data based on video duration
      updateEditingData({
        trimStart: 0,
        trimEnd: metadata.duration,
        cuts: [],
        filters: []
      });

      return { success: true, url, metadata };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    }
  }, [setVideo, setProcessing, setError, updateEditingData]);

  // Add trim points
  const addTrimPoint = useCallback((start, end) => {
    updateEditingData({
      trimStart: start,
      trimEnd: end
    });
  }, [updateEditingData]);

  // Add cut point
  const addCut = useCallback((timePoint) => {
    const currentCuts = state.editingData.cuts;
    const newCuts = [...currentCuts, timePoint].sort((a, b) => a - b);
    updateEditingData({
      cuts: newCuts
    });
  }, [state.editingData.cuts, updateEditingData]);

  // Remove cut point
  const removeCut = useCallback((timePoint) => {
    const currentCuts = state.editingData.cuts;
    const newCuts = currentCuts.filter(cut => Math.abs(cut - timePoint) > 0.1);
    updateEditingData({
      cuts: newCuts
    });
  }, [state.editingData.cuts, updateEditingData]);

  // Add filter
  const addFilter = useCallback((filter) => {
    const currentFilters = state.editingData.filters;
    const newFilters = [...currentFilters, filter];
    updateEditingData({
      filters: newFilters
    });
  }, [state.editingData.filters, updateEditingData]);

  // Remove filter
  const removeFilter = useCallback((filterId) => {
    const currentFilters = state.editingData.filters;
    const newFilters = currentFilters.filter(filter => filter.id !== filterId);
    updateEditingData({
      filters: newFilters
    });
  }, [state.editingData.filters, updateEditingData]);

  // Helper function to check if video is loaded
  const hasVideo = useCallback(() => {
    return state.currentVideo !== null; // Temporarily allow analysis with just filename
  }, [state.currentVideo]);

  // Get video duration for calculations
  const getVideoDuration = useCallback(() => {
    return state.videoMetadata?.duration || 0;
  }, [state.videoMetadata]);

  // Project management functions
  const saveProject = useCallback(async (projectName, description = '') => {
    setProcessing(true);
    setError(null);

    try {
      const API_BASE_URL = API_CONFIG.BASE_URL;
      
      // Calculate project duration based on editing data
      const calculateDuration = () => {
        if (!state.videoMetadata) return '0:00';
        const startTime = state.editingData.trimStart || 0;
        const endTime = state.editingData.trimEnd || state.videoMetadata.duration;
        const totalSeconds = Math.max(0, endTime - startTime);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = Math.floor(totalSeconds % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
      };

      // Calculate file size estimate
      const calculateFileSize = () => {
        if (!state.videoMetadata) return '0 MB';
        const originalSize = state.videoMetadata.size || 0;
        const startTime = state.editingData.trimStart || 0;
        const endTime = state.editingData.trimEnd || state.videoMetadata.duration;
        const duration = state.videoMetadata.duration || 1;
        const trimRatio = Math.max(0, (endTime - startTime) / duration);
        const estimatedSize = Math.round((originalSize * trimRatio) / (1024 * 1024));
        return `${estimatedSize} MB`;
      };

      const projectData = {
        id: state.currentProject?.id || null, // Will be generated by backend if null
        name: projectName.trim(),
        description: description.trim(),
        video_filename: state.currentVideo,
        video_metadata: state.videoMetadata,
        editing_data: state.editingData,
        status: 'draft',
        duration: calculateDuration(),
        file_size: calculateFileSize(),
        clips: state.editingData.cuts.length + 1, // Number of segments after cuts
        date_created: state.currentProject?.date_created || new Date().toISOString(),
      };

      const response = await fetch(`${API_BASE_URL}/api/projects/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(projectData)
      });

      const result = await response.json();

      if (result.success) {
        // Update current project state
        dispatch({
          type: VIDEO_ACTIONS.SET_CURRENT_PROJECT,
          payload: {
            ...projectData,
            id: result.project_id,
            date_modified: new Date().toISOString()
          }
        });

        setProcessing(false);
        return { success: true, project_id: result.project_id };
      } else {
        throw new Error(result.error || 'Failed to save project');
      }
    } catch (error) {
      setError(`Failed to save project: ${error.message}`);
      setProcessing(false);
      return { success: false, error: error.message };
    }
  }, [state, setProcessing, setError]);

  const loadProject = useCallback(async (projectId) => {
    setProcessing(true);
    setError(null);

    try {
      const API_BASE_URL = API_CONFIG.BASE_URL;
      
      const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
      const result = await response.json();

      if (result.success) {
        const project = result.project;
        
        // Set the project data
        dispatch({
          type: VIDEO_ACTIONS.SET_CURRENT_PROJECT,
          payload: project
        });

        // Set video data from project
        setVideo({
          video: project.video_filename,
          file: null, // File may not be available, just filename
          url: null,
          metadata: project.video_metadata
        });

        // Set editing data
        updateEditingData(project.editing_data);

        setProcessing(false);
        return { success: true, project };
      } else {
        throw new Error(result.error || 'Failed to load project');
      }
    } catch (error) {
      setError(`Failed to load project: ${error.message}`);
      setProcessing(false);
      return { success: false, error: error.message };
    }
  }, [setVideo, updateEditingData, setProcessing, setError]);

  const clearProject = useCallback(() => {
    dispatch({
      type: VIDEO_ACTIONS.CLEAR_CURRENT_PROJECT
    });
  }, []);

  const value = {
    // State
    ...state,
    
    // Actions
    setVideo,
    clearVideo,
    setProcessing,
    setError,
    updateMetadata,
    updateEditingData,
    uploadVideo,
    
    // Editing actions
    addTrimPoint,
    addCut,
    removeCut,
    addFilter,
    removeFilter,
    
    // Project management
    saveProject,
    loadProject,
    clearProject,
    
    // Helper functions
    hasVideo,
    getVideoDuration
  };

  return (
    <VideoContext.Provider value={value}>
      {children}
    </VideoContext.Provider>
  );
};

// Custom hook to use video context
export const useVideo = () => {
  const context = useContext(VideoContext);
  if (!context) {
    throw new Error('useVideo must be used within a VideoProvider');
  }
  return context;
};

export default VideoContext;
