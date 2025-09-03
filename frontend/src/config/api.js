// API Configuration for VideoCraft Frontend
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8003',
  ENDPOINTS: {
    HEALTH: '/api/health',
    UPLOAD: '/api/upload',
    ANALYZE: '/api/analyze',
    ANALYZE_FILENAME: '/api/analyze/analyze-filename',
    RECOMMENDATIONS: '/api/recommendations',
    PROJECTS: '/api/projects'
  },
  // Default headers for all requests
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  },
  // File upload headers
  UPLOAD_HEADERS: {
    // Don't set Content-Type for file uploads (browser sets it automatically)
  }
};

// Helper function to build full URL
export const buildApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Export for backward compatibility
export const API_BASE_URL = API_CONFIG.BASE_URL;
