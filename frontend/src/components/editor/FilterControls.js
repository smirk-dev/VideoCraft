import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Slider,
  Switch,
  FormControlLabel,
  Grid,
  Chip,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button
} from '@mui/material';
import {
  Brightness6,
  Contrast,
  Palette,
  BlurOn,
  ExpandMore,
  Delete,
  Refresh
} from '@mui/icons-material';

const FilterControls = ({ filters, onFiltersChange }) => {
  const [activeFilters, setActiveFilters] = useState({
    brightness: 100,
    contrast: 100,
    saturation: 100,
    blur: 0,
    grayscale: 0,
    sepia: 0,
    hueRotate: 0
  });

  const filterDefinitions = [
    {
      key: 'brightness',
      label: 'Brightness',
      icon: <Brightness6 />,
      min: 0,
      max: 200,
      default: 100,
      unit: '%'
    },
    {
      key: 'contrast',
      label: 'Contrast',
      icon: <Contrast />,
      min: 0,
      max: 200,
      default: 100,
      unit: '%'
    },
    {
      key: 'saturation',
      label: 'Saturation',
      icon: <Palette />,
      min: 0,
      max: 200,
      default: 100,
      unit: '%'
    },
    {
      key: 'blur',
      label: 'Blur',
      icon: <BlurOn />,
      min: 0,
      max: 10,
      default: 0,
      unit: 'px'
    },
    {
      key: 'grayscale',
      label: 'Grayscale',
      icon: null,
      min: 0,
      max: 100,
      default: 0,
      unit: '%'
    },
    {
      key: 'sepia',
      label: 'Sepia',
      icon: null,
      min: 0,
      max: 100,
      default: 0,
      unit: '%'
    },
    {
      key: 'hue-rotate',
      label: 'Hue Rotate',
      stateKey: 'hueRotate',
      icon: null,
      min: 0,
      max: 360,
      default: 0,
      unit: '°'
    }
  ];

  const presetFilters = [
    {
      name: 'Vintage',
      filters: { brightness: 110, contrast: 120, saturation: 80, sepia: 30 }
    },
    {
      name: 'High Contrast',
      filters: { brightness: 105, contrast: 150, saturation: 110 }
    },
    {
      name: 'Soft',
      filters: { brightness: 105, contrast: 90, blur: 0.5 }
    },
    {
      name: 'Monochrome',
      filters: { grayscale: 100, contrast: 110 }
    },
    {
      name: 'Warm',
      filters: { brightness: 105, saturation: 120, hueRotate: 10 }
    },
    {
      name: 'Cool',
      filters: { brightness: 95, saturation: 110, hueRotate: 200 }
    }
  ];

  const handleFilterChange = (filterKey, value) => {
    const stateKey = filterDefinitions.find(f => f.key === filterKey)?.stateKey || filterKey;
    const newActiveFilters = { ...activeFilters, [stateKey]: value };
    setActiveFilters(newActiveFilters);

    // Convert to filter format expected by VideoPlayer
    const newFilters = [];
    
    Object.entries(newActiveFilters).forEach(([key, value]) => {
      const filterDef = filterDefinitions.find(f => (f.stateKey || f.key) === key);
      if (filterDef && value !== filterDef.default) {
        newFilters.push({
          id: key,
          type: filterDef.key,
          value: value
        });
      }
    });

    onFiltersChange(newFilters);
  };

  const applyPreset = (preset) => {
    const newActiveFilters = { ...activeFilters };
    
    // Reset to defaults first
    filterDefinitions.forEach(filter => {
      const stateKey = filter.stateKey || filter.key;
      newActiveFilters[stateKey] = filter.default;
    });

    // Apply preset values
    Object.entries(preset.filters).forEach(([key, value]) => {
      newActiveFilters[key] = value;
    });

    setActiveFilters(newActiveFilters);

    // Convert to filter format
    const newFilters = [];
    Object.entries(newActiveFilters).forEach(([key, value]) => {
      const filterDef = filterDefinitions.find(f => (f.stateKey || f.key) === key);
      if (filterDef && value !== filterDef.default) {
        newFilters.push({
          id: key,
          type: filterDef.key,
          value: value
        });
      }
    });

    onFiltersChange(newFilters);
  };

  const resetFilters = () => {
    const resetActiveFilters = {};
    filterDefinitions.forEach(filter => {
      const stateKey = filter.stateKey || filter.key;
      resetActiveFilters[stateKey] = filter.default;
    });
    
    setActiveFilters(resetActiveFilters);
    onFiltersChange([]);
  };

  const removeFilter = (filterId) => {
    const filterDef = filterDefinitions.find(f => (f.stateKey || f.key) === filterId);
    if (filterDef) {
      handleFilterChange(filterDef.key, filterDef.default);
    }
  };

  const getActiveFiltersList = () => {
    return filters.filter(f => {
      const filterDef = filterDefinitions.find(def => def.key === f.type);
      return filterDef && f.value !== filterDef.default;
    });
  };

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Filters</Typography>
        <Button
          startIcon={<Refresh />}
          onClick={resetFilters}
          size="small"
          variant="outlined"
        >
          Reset
        </Button>
      </Box>

      {/* Active Filters */}
      {getActiveFiltersList().length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>Active Filters:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {getActiveFiltersList().map((filter) => {
              const filterDef = filterDefinitions.find(f => f.key === filter.type);
              return (
                <Chip
                  key={filter.id}
                  label={`${filterDef?.label}: ${filter.value}${filterDef?.unit || ''}`}
                  onDelete={() => removeFilter(filter.id)}
                  deleteIcon={<Delete />}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              );
            })}
          </Box>
        </Box>
      )}

      {/* Preset Filters */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="subtitle1">Preset Filters</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={1}>
            {presetFilters.map((preset) => (
              <Grid item xs={6} sm={4} key={preset.name}>
                <Button
                  variant="outlined"
                  fullWidth
                  size="small"
                  onClick={() => applyPreset(preset)}
                  sx={{ textTransform: 'none' }}
                >
                  {preset.name}
                </Button>
              </Grid>
            ))}
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Individual Filter Controls */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="subtitle1">Custom Filters</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            {filterDefinitions.map((filter) => {
              const stateKey = filter.stateKey || filter.key;
              const currentValue = activeFilters[stateKey] || filter.default;
              
              return (
                <Grid item xs={12} sm={6} key={filter.key}>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      {filter.icon}
                      <Typography variant="body2" sx={{ ml: filter.icon ? 1 : 0, mr: 'auto' }}>
                        {filter.label}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {currentValue}{filter.unit}
                      </Typography>
                    </Box>
                    <Slider
                      value={currentValue}
                      onChange={(_, value) => handleFilterChange(filter.key, value)}
                      min={filter.min}
                      max={filter.max}
                      step={filter.key === 'blur' ? 0.1 : 1}
                      size="small"
                      sx={{
                        '& .MuiSlider-track': {
                          backgroundColor: currentValue !== filter.default ? '#2196f3' : '#ccc'
                        },
                        '& .MuiSlider-thumb': {
                          backgroundColor: currentValue !== filter.default ? '#2196f3' : '#ccc'
                        }
                      }}
                    />
                  </Box>
                </Grid>
              );
            })}
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Filter Tips */}
      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        💡 Use presets for quick styling or customize individual filters. Changes apply in real-time.
      </Typography>
    </Paper>
  );
};

export default FilterControls;
