import React, { useState } from 'react';
import { Button } from '@mui/material';
import { GetApp } from '@mui/icons-material';
import ExportDialog from '../export/ExportDialog';

const ExportButton = ({ 
  videoData,
  variant = "outlined",
  size = "medium",
  fullWidth = false,
  children = "Export"
}) => {
  const [exportDialogOpen, setExportDialogOpen] = useState(false);

  const handleExportClick = () => {
    setExportDialogOpen(true);
  };

  const handleExportClose = () => {
    setExportDialogOpen(false);
  };

  // Don't render if no video data at all
  if (!videoData) {
    return null;
  }

  // Show button for any video data - let the dialog handle validation

  return (
    <>
      <Button
        startIcon={<GetApp />}
        variant={variant}
        size={size}
        fullWidth={fullWidth}
        onClick={handleExportClick}
        color="primary"
      >
        {children}
      </Button>
      
      <ExportDialog
        open={exportDialogOpen}
        onClose={handleExportClose}
        videoData={videoData}
      />
    </>
  );
};

export default ExportButton;
