import React, { createContext, useContext, useReducer, useCallback } from 'react';

// Video action types
const VIDEO_ACTIONS = {
  SET_VIDEO: 'SET_VIDEO',
  CLEAR_VIDEO: 'CLEAR_VIDEO',
  SET_PROCESSING: 'SET_PROCESSING',
  SET_ERROR: 'SET_ERROR',
  UPDATE_METADATA: 'UPDATE_METADATA',
  SET_EDITING_DATA: 'SET_EDITING_DATA'
};

// Initial state
const initialState = {
  currentVideo: null,
  videoFile: null,
  videoUrl: null,
  videoMetadata: null,
  isProcessing: false,
  error: null,
  editingData: {
    trimStart: 0,
    trimEnd: null,
    cuts: [],
    filters: []
  }
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
    return state.currentVideo !== null && state.videoFile !== null;
  }, [state.currentVideo, state.videoFile]);

  // Get video duration for calculations
  const getVideoDuration = useCallback(() => {
    return state.videoMetadata?.duration || 0;
  }, [state.videoMetadata]);

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
