import React, { useState, useEffect } from "react";
import {
  Typography,
  Box,
  Button,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Snackbar,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";
import {
  Add as AddIcon,
  Folder as FolderIcon,
  Visibility as VisibilityIcon,
} from "@mui/icons-material";
import { Link } from "react-router-dom";
import { sourcesApi } from "../services/api";
import { Source } from "../types/index";

const Sources: React.FC = () => {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [newSource, setNewSource] = useState({ name: "", description: "" });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success" as "success" | "error",
  });

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      setLoading(true);
      const response = await sourcesApi.getSources();
      if (response.success) {
        setSources(response.data);
      } else {
        setError(response.message || "Failed to fetch sources");
      }
    } catch (err) {
      setError("An error occurred while fetching sources");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setNewSource({ name: "", description: "" });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewSource((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreateSource = async () => {
    try {
      if (!newSource.name.trim()) {
        setSnackbar({
          open: true,
          message: "Source name is required",
          severity: "error",
        });
        return;
      }

      const response = await sourcesApi.createSource({
        name: newSource.name,
        description: newSource.description,
        userId: "current-user", // This would be replaced with actual user ID in a real app
      });

      if (response.success) {
        setSources((prev) => [...prev, response.data]);
        handleCloseDialog();
        setSnackbar({
          open: true,
          message: "Source created successfully",
          severity: "success",
        });
      } else {
        setSnackbar({
          open: true,
          message: response.message || "Failed to create source",
          severity: "error",
        });
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: "An error occurred while creating the source",
        severity: "error",
      });
      console.error(err);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 4,
          }}
        >
          <Typography variant="h4" component="h1">
            Sources
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenDialog}
          >
            Add Source
          </Button>
        </Box>

        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", my: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        ) : sources.length === 0 ? (
          <Box sx={{ textAlign: "center", my: 4 }}>
            <FolderIcon sx={{ fontSize: 60, color: "text.secondary", mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No sources found
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              Create your first source to get started
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleOpenDialog}
            >
              Add Source
            </Button>
          </Box>
        ) : (
          <TableContainer component={Paper} sx={{ mt: 3 }}>
            <Table sx={{ minWidth: 650 }} aria-label="sources table">
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Last Updated</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sources.map((source) => (
                  <TableRow key={source.id} hover>
                    <TableCell component="th" scope="row">
                      <Typography variant="subtitle1">{source.name}</Typography>
                    </TableCell>
                    <TableCell>
                      {source.description ? (
                        <Typography variant="body2" color="text.secondary">
                          {source.description}
                        </Typography>
                      ) : (
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          fontStyle="italic"
                        >
                          No description
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {new Date(source.createdAt).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {new Date(source.updatedAt).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="center">
                      <Button
                        component={Link}
                        to={`/sources/${source.id}`}
                        size="small"
                        color="primary"
                        startIcon={<VisibilityIcon />}
                      >
                        View Pages
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>

      {/* Create Source Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Source</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="name"
            label="Source Name"
            type="text"
            fullWidth
            variant="outlined"
            value={newSource.name}
            onChange={handleInputChange}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="description"
            label="Description (Optional)"
            type="text"
            fullWidth
            variant="outlined"
            value={newSource.description}
            onChange={handleInputChange}
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleCreateSource}
            variant="contained"
            color="primary"
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Sources;
