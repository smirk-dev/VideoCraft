import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip
} from '@mui/material';
import {
  Save,
  Cancel,
  CheckCircle
} from '@mui/icons-material';

const SaveProjectDialog = ({ 
  open, 
  onClose, 
  onSave, 
  currentProject = null, 
  isProcessing = false,
  error = null 
}) => {
  const [projectName, setProjectName] = useState(currentProject?.name || '');
  const [description, setDescription] = useState(currentProject?.description || '');
  const [status, setStatus] = useState(currentProject?.status || 'draft');
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSave = async () => {
    if (!projectName.trim()) return;

    setSaveSuccess(false);
    const result = await onSave(projectName, description, status);
    
    if (result.success) {
      setSaveSuccess(true);
      // Auto-close after success message
      setTimeout(() => {
        setSaveSuccess(false);
        onClose();
      }, 1500);
    }
  };

  const handleClose = () => {
    setSaveSuccess(false);
    onClose();
  };

  const handleNameChange = (e) => {
    setProjectName(e.target.value);
  };

  const handleDescriptionChange = (e) => {
    setDescription(e.target.value);
  };

  const isUpdate = currentProject && currentProject.id;

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: { 
          borderRadius: 2,
          bgcolor: 'background.paper',
          color: 'text.primary'
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Save color="primary" />
          <Typography variant="h6">
            {isUpdate ? 'Update Project' : 'Save Project'}
          </Typography>
        </Box>
        {isUpdate && (
          <Chip 
            label="Updating existing project" 
            size="small" 
            color="info" 
            sx={{ mt: 1 }}
          />
        )}
      </DialogTitle>
      
      <DialogContent sx={{ pt: 2 }}>
        {saveSuccess ? (
          <Alert 
            severity="success" 
            sx={{ mb: 2 }}
            icon={<CheckCircle />}
          >
            <Typography variant="body1" fontWeight="medium">
              Project saved successfully!
            </Typography>
            <Typography variant="body2">
              Your project has been {isUpdate ? 'updated' : 'saved'} and is now available in the Projects section.
            </Typography>
          </Alert>
        ) : (
          <>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            <TextField
              autoFocus
              label="Project Name"
              fullWidth
              variant="outlined"
              value={projectName}
              onChange={handleNameChange}
              placeholder="Enter a name for your project"
              sx={{ 
                mb: 2,
                '& .MuiInputLabel-root': { color: 'text.primary' },
                '& .MuiOutlinedInput-input': { color: 'text.primary' }
              }}
              disabled={isProcessing}
              error={!projectName.trim() && projectName.length > 0}
              helperText={!projectName.trim() && projectName.length > 0 ? 'Project name is required' : ''}
            />
            
            <TextField
              label="Description (Optional)"
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              value={description}
              onChange={handleDescriptionChange}
              placeholder="Describe what this project contains..."
              sx={{ 
                mb: 2,
                '& .MuiInputLabel-root': { color: 'text.primary' },
                '& .MuiOutlinedInput-input': { color: 'text.primary' }
              }}
              disabled={isProcessing}
            />

            <FormControl fullWidth sx={{ 
              mb: 2,
              '& .MuiInputLabel-root': { color: 'text.primary' },
              '& .MuiSelect-select': { color: 'text.primary' }
            }}>
              <InputLabel>Project Status</InputLabel>
              <Select
                value={status}
                label="Project Status"
                onChange={(e) => setStatus(e.target.value)}
                disabled={isProcessing}
              >
                <MenuItem value="draft">Draft</MenuItem>
                <MenuItem value="in-progress">In Progress</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ 
              p: 2, 
              bgcolor: 'rgba(25, 118, 210, 0.08)', 
              borderRadius: 1, 
              border: '1px solid',
              borderColor: 'rgba(25, 118, 210, 0.2)'
            }}>
              <Typography variant="subtitle2" gutterBottom sx={{ 
                color: '#1976d2',
                fontWeight: 'bold'
              }}>
                💡 Save Tips:
              </Typography>
              <Typography variant="body2" sx={{ color: '#333333' }}>
                • Your project will be saved with all current edits and settings<br/>
                • You can load and continue editing anytime from the Projects page<br/>
                • Changes are saved locally and will persist between sessions
              </Typography>
            </Box>
          </>
        )}
      </DialogContent>
      
      {!saveSuccess && (
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button 
            onClick={handleClose}
            disabled={isProcessing}
            startIcon={<Cancel />}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSave}
            variant="contained"
            disabled={!projectName.trim() || isProcessing}
            startIcon={isProcessing ? <CircularProgress size={16} /> : <Save />}
          >
            {isProcessing ? 'Saving...' : (isUpdate ? 'Update Project' : 'Save Project')}
          </Button>
        </DialogActions>
      )}
    </Dialog>
  );
};

export default SaveProjectDialog;
