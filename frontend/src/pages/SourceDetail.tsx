import React, { useState, useEffect, useRef } from "react";
import {
  Typography,
  Box,
  Button,
  Container,
  CircularProgress,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tabs,
  Tab,
  Divider,
  Paper,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import {
  Add as AddIcon,
  Image as ImageIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  ArrowBack as ArrowBackIcon,
  Visibility as VisibilityIcon,
} from "@mui/icons-material";
import { useParams, Link, useNavigate } from "react-router-dom";
import { sourcesApi, pagesApi } from "../services/api";
import { Source, Page } from "../types/index";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const SourceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const multipleFileInputRef = useRef<HTMLInputElement>(null);

  const [source, setSource] = useState<Source | null>(null);
  const [pages, setPages] = useState<Page[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success" as "success" | "error",
  });
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editSource, setEditSource] = useState({ name: "", description: "" });
  const [uploadLoading, setUploadLoading] = useState(false);

  useEffect(() => {
    if (id) {
      fetchSourceAndPages(id);
    }
  }, [id]);

  const fetchSourceAndPages = async (sourceId: string) => {
    try {
      setLoading(true);
      const sourceResponse = await sourcesApi.getSource(sourceId);
      const pagesResponse = await pagesApi.getPages(sourceId);

      if (sourceResponse.success && pagesResponse.success) {
        setSource(sourceResponse.data);
        setPages(pagesResponse.data);
        setEditSource({
          name: sourceResponse.data.name,
          description: sourceResponse.data.description || "",
        });
      } else {
        setError(
          sourceResponse.message ||
            pagesResponse.message ||
            "Failed to fetch data"
        );
      }
    } catch (err) {
      setError("An error occurred while fetching data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenEditDialog = () => {
    setOpenEditDialog(true);
  };

  const handleCloseEditDialog = () => {
    setOpenEditDialog(false);
    if (source) {
      setEditSource({
        name: source.name,
        description: source.description || "",
      });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEditSource((prev) => ({ ...prev, [name]: value }));
  };

  const handleUpdateSource = async () => {
    if (!id || !source) return;

    try {
      if (!editSource.name.trim()) {
        setSnackbar({
          open: true,
          message: "Source name is required",
          severity: "error",
        });
        return;
      }

      const response = await sourcesApi.updateSource(id, {
        name: editSource.name,
        description: editSource.description,
      });

      if (response.success) {
        setSource(response.data);
        handleCloseEditDialog();
        setSnackbar({
          open: true,
          message: "Source updated successfully",
          severity: "success",
        });
      } else {
        setSnackbar({
          open: true,
          message: response.message || "Failed to update source",
          severity: "error",
        });
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: "An error occurred while updating the source",
        severity: "error",
      });
      console.error(err);
    }
  };

  const handleDeleteSource = async () => {
    if (!id) return;

    if (
      window.confirm(
        "Are you sure you want to delete this source? This action cannot be undone."
      )
    ) {
      try {
        const response = await sourcesApi.deleteSource(id);
        if (response.success) {
          setSnackbar({
            open: true,
            message: "Source deleted successfully",
            severity: "success",
          });
          navigate("/sources");
        } else {
          setSnackbar({
            open: true,
            message: response.message || "Failed to delete source",
            severity: "error",
          });
        }
      } catch (err) {
        setSnackbar({
          open: true,
          message: "An error occurred while deleting the source",
          severity: "error",
        });
        console.error(err);
      }
    }
  };

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleMultipleUploadClick = () => {
    if (multipleFileInputRef.current) {
      multipleFileInputRef.current.click();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!id || !e.target.files || e.target.files.length === 0) return;

    try {
      setUploadLoading(true);
      const file = e.target.files[0];
      const formData = new FormData();
      formData.append("file", file);
      formData.append("fileName", file.name);

      const response = await pagesApi.createPage(id, formData);

      if (response.success) {
        setPages((prev) => [...prev, response.data]);
        setSnackbar({
          open: true,
          message: "Page uploaded successfully",
          severity: "success",
        });
      } else {
        setSnackbar({
          open: true,
          message: response.message || "Failed to upload page",
          severity: "error",
        });
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: "An error occurred while uploading the page",
        severity: "error",
      });
      console.error(err);
    } finally {
      setUploadLoading(false);
      // Reset the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleMultipleFileChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (!id || !e.target.files || e.target.files.length === 0) return;

    try {
      setUploadLoading(true);
      const files = Array.from(e.target.files);
      const formData = new FormData();

      files.forEach((file, index) => {
        formData.append(`files[${index}]`, file);
        formData.append(`fileNames[${index}]`, file.name);
      });

      const response = await pagesApi.uploadPages(id, formData);

      if (response.success) {
        setPages((prev) => [...prev, ...response.data]);
        setSnackbar({
          open: true,
          message: `${response.data.length} pages uploaded successfully`,
          severity: "success",
        });
      } else {
        setSnackbar({
          open: true,
          message: response.message || "Failed to upload pages",
          severity: "error",
        });
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: "An error occurred while uploading pages",
        severity: "error",
      });
      console.error(err);
    } finally {
      setUploadLoading(false);
      // Reset the file input
      if (multipleFileInputRef.current) {
        multipleFileInputRef.current.value = "";
      }
    }
  };

  const handleDeletePage = async (pageId: string) => {
    if (!id) return;

    if (
      window.confirm(
        "Are you sure you want to delete this page? This action cannot be undone."
      )
    ) {
      try {
        const response = await pagesApi.deletePage(id, pageId);
        if (response.success) {
          setPages((prev) => prev.filter((page) => page.id !== pageId));
          setSnackbar({
            open: true,
            message: "Page deleted successfully",
            severity: "success",
          });
        } else {
          setSnackbar({
            open: true,
            message: response.message || "Failed to delete page",
            severity: "error",
          });
        }
      } catch (err) {
        setSnackbar({
          open: true,
          message: "An error occurred while deleting the page",
          severity: "error",
        });
        console.error(err);
      }
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: "flex", justifyContent: "center", my: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !source) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ my: 2 }}>
          {error || "Source not found"}
        </Alert>
        <Button
          component={Link}
          to="/sources"
          startIcon={<ArrowBackIcon />}
          sx={{ mt: 2 }}
        >
          Back to Sources
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Button
            component={Link}
            to="/sources"
            startIcon={<ArrowBackIcon />}
            sx={{ mb: 2 }}
          >
            Back to Sources
          </Button>

          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
            }}
          >
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                {source.name}
              </Typography>
              {source.description && (
                <Typography variant="body1" color="text.secondary" paragraph>
                  {source.description}
                </Typography>
              )}
              <Typography variant="body2" color="text.secondary">
                Created: {new Date(source.createdAt).toLocaleDateString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last Updated: {new Date(source.updatedAt).toLocaleDateString()}
              </Typography>
            </Box>
            <Box>
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={handleOpenEditDialog}
                sx={{ mr: 1 }}
              >
                Edit
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={handleDeleteSource}
              >
                Delete
              </Button>
            </Box>
          </Box>
        </Box>

        <Divider sx={{ mb: 4 }} />

        <Box sx={{ width: "100%" }}>
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="source tabs"
            >
              <Tab label="Pages" id="tab-0" aria-controls="tabpanel-0" />
              <Tab label="Upload" id="tab-1" aria-controls="tabpanel-1" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            {pages.length === 0 ? (
              <Box sx={{ textAlign: "center", my: 4 }}>
                <ImageIcon
                  sx={{ fontSize: 60, color: "text.secondary", mb: 2 }}
                />
                <Typography variant="h6" color="text.secondary">
                  No pages found
                </Typography>
                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Upload pages to get started
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={() => setTabValue(1)}
                >
                  Upload Pages
                </Button>
              </Box>
            ) : (
              <TableContainer component={Paper} sx={{ mt: 3 }}>
                <Table sx={{ minWidth: 650 }} aria-label="pages table">
                  <TableHead>
                    <TableRow>
                      <TableCell>Title</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Summary</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pages.map((page) => (
                      <TableRow key={page.id} hover>
                        <TableCell component="th" scope="row">
                          {page.title || "Not specified"}
                        </TableCell>
                        <TableCell>
                          {page.date
                            ? new Date(page.date).toLocaleDateString()
                            : "Not specified"}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {page.notes || "No summary available"}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {new Date(page.createdAt).toLocaleDateString()}
                        </TableCell>
                        <TableCell align="center">
                          <Button
                            component={Link}
                            to={`/sources/${id}/pages/${page.id}`}
                            size="small"
                            color="primary"
                            startIcon={<VisibilityIcon />}
                            sx={{ mr: 1 }}
                          >
                            View
                          </Button>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeletePage(page.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Upload Pages
              </Typography>
              <Typography variant="body1" paragraph>
                Upload images of pages from your personal archive. The system
                will extract text from the images automatically.
              </Typography>

              <Box sx={{ mb: 4 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Upload a Single Page
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={handleUploadClick}
                  disabled={uploadLoading}
                >
                  {uploadLoading ? "Uploading..." : "Upload Page"}
                </Button>
                <input
                  type="file"
                  ref={fileInputRef}
                  style={{ display: "none" }}
                  accept="image/*"
                  onChange={handleFileChange}
                />
              </Box>

              <Divider sx={{ my: 3 }} />

              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Upload Multiple Pages
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={handleMultipleUploadClick}
                  disabled={uploadLoading}
                >
                  {uploadLoading ? "Uploading..." : "Upload Multiple Pages"}
                </Button>
                <input
                  type="file"
                  ref={multipleFileInputRef}
                  style={{ display: "none" }}
                  accept="image/*"
                  multiple
                  onChange={handleMultipleFileChange}
                />
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mt: 1 }}
                >
                  You can select multiple image files at once
                </Typography>
              </Box>
            </Paper>
          </TabPanel>
        </Box>
      </Box>

      {/* Edit Source Dialog */}
      <Dialog
        open={openEditDialog}
        onClose={handleCloseEditDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Source</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="name"
            label="Source Name"
            type="text"
            fullWidth
            variant="outlined"
            value={editSource.name}
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
            value={editSource.description}
            onChange={handleInputChange}
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog}>Cancel</Button>
          <Button
            onClick={handleUpdateSource}
            variant="contained"
            color="primary"
          >
            Save Changes
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

export default SourceDetail;
