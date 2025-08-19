import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Button,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Fab,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
} from '@mui/material';
import {
  Add,
  MoreVert,
  PlayArrow,
  Edit,
  Delete,
  Share,
  Download,
  Folder,
  VideoLibrary,
  AccessTime,
  DateRange,
  FilterList,
  Search,
  Sort,
  Clear,
} from '@mui/icons-material';

const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [filteredProjects, setFilteredProjects] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    template: 'blank',
  });
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [sortBy, setSortBy] = useState('dateModified');
  const [filterBy, setFilterBy] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock project data
  const mockProjects = [
    {
      id: 1,
      name: 'Summer Vacation 2024',
      description: 'Family vacation highlights with background music',
      thumbnail: '/api/placeholder/320/180',
      dateCreated: '2024-07-15',
      dateModified: '2024-07-20',
      duration: '3:45',
      status: 'completed',
      fileSize: '250 MB',
      clips: 12,
    },
    {
      id: 2,
      name: 'Product Demo Video',
      description: 'Marketing video for new product launch',
      thumbnail: '/api/placeholder/320/180',
      dateCreated: '2024-07-10',
      dateModified: '2024-07-18',
      duration: '2:30',
      status: 'in-progress',
      fileSize: '180 MB',
      clips: 8,
    },
    {
      id: 3,
      name: 'Birthday Party Montage',
      description: 'Quick montage with automatic cuts and transitions',
      thumbnail: '/api/placeholder/320/180',
      dateCreated: '2024-06-25',
      dateModified: '2024-07-01',
      duration: '1:55',
      status: 'completed',
      fileSize: '120 MB',
      clips: 15,
    },
    {
      id: 4,
      name: 'Tutorial Series - Episode 1',
      description: 'Educational content with screen recording',
      thumbnail: '/api/placeholder/320/180',
      dateCreated: '2024-06-20',
      dateModified: '2024-06-22',
      duration: '12:30',
      status: 'draft',
      fileSize: '890 MB',
      clips: 25,
    },
  ];

  useEffect(() => {
    setProjects(mockProjects);
    setFilteredProjects(mockProjects);
  }, []);

  useEffect(() => {
    let filtered = [...projects];

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(project => 
        project.name.toLowerCase().includes(query) ||
        project.description.toLowerCase().includes(query) ||
        project.status.toLowerCase().includes(query)
      );
    }

    // Apply status filter
    if (filterBy !== 'all') {
      filtered = filtered.filter(project => project.status === filterBy);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'dateCreated':
          return new Date(b.dateCreated) - new Date(a.dateCreated);
        case 'dateModified':
          return new Date(b.dateModified) - new Date(a.dateModified);
        case 'duration':
          return b.duration.localeCompare(a.duration);
        default:
          return 0;
      }
    });

    setFilteredProjects(filtered);
  }, [projects, sortBy, filterBy, searchQuery]);

  const handleCreateProject = () => {
    const project = {
      ...newProject,
      id: Date.now(),
      dateCreated: new Date().toISOString().split('T')[0],
      dateModified: new Date().toISOString().split('T')[0],
      duration: '0:00',
      status: 'draft',
      fileSize: '0 MB',
      clips: 0,
      thumbnail: '/api/placeholder/320/180',
    };

    setProjects([project, ...projects]);
    setOpenDialog(false);
    setNewProject({ name: '', description: '', template: 'blank' });
  };

  const handleMenuOpen = (event, project) => {
    setAnchorEl(event.currentTarget);
    setSelectedProject(project);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedProject(null);
  };

  const handleDeleteProject = () => {
    setProjects(projects.filter(p => p.id !== selectedProject.id));
    handleMenuClose();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in-progress':
        return 'warning';
      case 'draft':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'background.default', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ py: 2 }}>
        {/* Header */}
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              📁 My Projects
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Manage your video editing projects
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            size="large"
            onClick={() => setOpenDialog(true)}
          >
            New Project
          </Button>
        </Box>

        {/* Filters and Sort */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                placeholder="Search projects..."
                variant="outlined"
                size="small"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={filterBy}
                  label="Filter by Status"
                  onChange={(e) => setFilterBy(e.target.value)}
                  startAdornment={<FilterList />}
                >
                  <MenuItem value="all">All Projects</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="in-progress">In Progress</MenuItem>
                  <MenuItem value="draft">Draft</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Sort by</InputLabel>
                <Select
                  value={sortBy}
                  label="Sort by"
                  onChange={(e) => setSortBy(e.target.value)}
                  startAdornment={<Sort />}
                >
                  <MenuItem value="dateModified">Last Modified</MenuItem>
                  <MenuItem value="dateCreated">Date Created</MenuItem>
                  <MenuItem value="name">Name</MenuItem>
                  <MenuItem value="duration">Duration</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={2}>
              <Typography variant="body2" color="text.secondary">
                {filteredProjects.length} project{filteredProjects.length !== 1 ? 's' : ''}
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        {/* Projects Grid */}
        {filteredProjects.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <VideoLibrary sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No projects found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              {filterBy === 'all' 
                ? "Create your first video project to get started"
                : `No projects match the current filter: ${filterBy}`
              }
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpenDialog(true)}
            >
              Create New Project
            </Button>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {filteredProjects.map((project) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={project.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <Box sx={{ position: 'relative' }}>
                    <CardMedia
                      component="div"
                      sx={{
                        height: 180,
                        bgcolor: 'grey.200',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <VideoLibrary sx={{ fontSize: 48, color: 'text.secondary' }} />
                    </CardMedia>
                    <IconButton
                      sx={{
                        position: 'absolute',
                        top: 8,
                        right: 8,
                        bgcolor: 'background.paper',
                        '&:hover': { bgcolor: 'background.paper' },
                      }}
                      onClick={(e) => handleMenuOpen(e, project)}
                    >
                      <MoreVert />
                    </IconButton>
                    <Chip
                      label={project.status}
                      color={getStatusColor(project.status)}
                      size="small"
                      sx={{
                        position: 'absolute',
                        bottom: 8,
                        left: 8,
                        textTransform: 'capitalize',
                      }}
                    />
                  </Box>
                  
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="h3" gutterBottom>
                      {project.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {project.description}
                    </Typography>
                    
                    <List dense>
                      <ListItem disablePadding>
                        <ListItemAvatar>
                          <Avatar sx={{ width: 24, height: 24 }}>
                            <AccessTime sx={{ fontSize: 14 }} />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText primary={project.duration} />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemAvatar>
                          <Avatar sx={{ width: 24, height: 24 }}>
                            <VideoLibrary sx={{ fontSize: 14 }} />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText primary={`${project.clips} clips`} />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemAvatar>
                          <Avatar sx={{ width: 24, height: 24 }}>
                            <DateRange sx={{ fontSize: 14 }} />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText primary={formatDate(project.dateModified)} />
                      </ListItem>
                    </List>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      startIcon={<PlayArrow />}
                      variant="contained"
                      fullWidth
                    >
                      Open Project
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Project Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleMenuClose}>
            <Edit sx={{ mr: 1 }} />
            Edit Project
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <Share sx={{ mr: 1 }} />
            Share
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <Download sx={{ mr: 1 }} />
            Export
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleDeleteProject} sx={{ color: 'error.main' }}>
            <Delete sx={{ mr: 1 }} />
            Delete
          </MenuItem>
        </Menu>

        {/* Create Project Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Project Name"
              fullWidth
              variant="outlined"
              value={newProject.name}
              onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Description"
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              value={newProject.description}
              onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth>
              <InputLabel>Template</InputLabel>
              <Select
                value={newProject.template}
                label="Template"
                onChange={(e) => setNewProject({ ...newProject, template: e.target.value })}
              >
                <MenuItem value="blank">Blank Project</MenuItem>
                <MenuItem value="social">Social Media (16:9)</MenuItem>
                <MenuItem value="story">Story (9:16)</MenuItem>
                <MenuItem value="square">Square (1:1)</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button 
              onClick={handleCreateProject} 
              variant="contained"
              disabled={!newProject.name.trim()}
            >
              Create Project
            </Button>
          </DialogActions>
        </Dialog>

        {/* Floating Action Button */}
        <Fab
          color="primary"
          aria-label="add"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={() => setOpenDialog(true)}
        >
          <Add />
        </Fab>
      </Container>
    </Box>
  );
};

export default ProjectsPage;
