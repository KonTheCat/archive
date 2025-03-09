import React, { useState, useEffect } from "react";
import {
  Typography,
  Box,
  Button,
  Container,
  Paper,
  Grid,
  CircularProgress,
  Snackbar,
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
} from "@mui/material";
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import { useParams, Link, useNavigate } from "react-router-dom";
import { pagesApi } from "../services/api";
import { Page } from "../types/index";

const PageDetail: React.FC = () => {
  const { sourceId, pageId } = useParams<{
    sourceId: string;
    pageId: string;
  }>();
  const navigate = useNavigate();

  const [page, setPage] = useState<Page | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editPage, setEditPage] = useState({
    title: "",
    date: "",
    notes: "",
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success" as "success" | "error",
  });

  useEffect(() => {
    if (sourceId && pageId) {
      fetchPage(sourceId, pageId);
    }
  }, [sourceId, pageId]);

  const fetchPage = async (sourceId: string, pageId: string) => {
    try {
      setLoading(true);
      const response = await pagesApi.getPage(sourceId, pageId);
      if (response.success) {
        setPage(response.data);
        setEditPage({
          title: response.data.title || "",
          date: response.data.date || "",
          notes: response.data.notes || "",
        });
      } else {
        setError(response.message || "Failed to fetch page");
      }
    } catch (err) {
      setError("An error occurred while fetching the page");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenEditDialog = () => {
    setOpenEditDialog(true);
  };

  const handleCloseEditDialog = () => {
    setOpenEditDialog(false);
    if (page) {
      setEditPage({
        title: page.title || "",
        date: page.date || "",
        notes: page.notes || "",
      });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEditPage((prev) => ({ ...prev, [name]: value }));
  };

  const handleUpdatePage = async () => {
    if (!sourceId || !pageId || !page) return;

    try {
      const response = await pagesApi.updatePage(sourceId, pageId, {
        title: editPage.title || undefined,
        date: editPage.date || undefined,
        notes: editPage.notes,
      });

      if (response.success) {
        setPage(response.data);
        handleCloseEditDialog();
        setSnackbar({
          open: true,
          message: "Page updated successfully",
          severity: "success",
        });
      } else {
        setSnackbar({
          open: true,
          message: response.message || "Failed to update page",
          severity: "error",
        });
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: "An error occurred while updating the page",
        severity: "error",
      });
      console.error(err);
    }
  };

  const handleDeletePage = async () => {
    if (!sourceId || !pageId) return;

    if (
      window.confirm(
        "Are you sure you want to delete this page? This action cannot be undone."
      )
    ) {
      try {
        const response = await pagesApi.deletePage(sourceId, pageId);
        if (response.success) {
          setSnackbar({
            open: true,
            message: "Page deleted successfully",
            severity: "success",
          });
          navigate(`/sources/${sourceId}`);
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

  if (error || !page) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ my: 2 }}>
          {error || "Page not found"}
        </Alert>
        <Button
          component={Link}
          to={sourceId ? `/sources/${sourceId}` : "/sources"}
          startIcon={<ArrowBackIcon />}
          sx={{ mt: 2 }}
        >
          Back to Source
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Button
          component={Link}
          to={`/sources/${sourceId}`}
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 3 }}
        >
          Back to Source
        </Button>

        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            mb: 4,
          }}
        >
          <Typography variant="h4" component="h1" gutterBottom>
            Page Details
          </Typography>
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
              onClick={handleDeletePage}
            >
              Delete
            </Button>
          </Box>
        </Box>

        <Grid container spacing={4}>
          {/* Image Section */}
          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 2,
                display: "flex",
                flexDirection: "column",
                height: "100%",
              }}
            >
              <Typography variant="h6" gutterBottom>
                Image
              </Typography>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  flexGrow: 1,
                  overflow: "hidden",
                  borderRadius: 1,
                  bgcolor: "background.default",
                }}
              >
                <img
                  src={page.imageUrl}
                  alt="Page"
                  style={{
                    maxWidth: "100%",
                    maxHeight: "600px",
                    objectFit: "contain",
                  }}
                />
              </Box>
            </Paper>
          </Grid>

          {/* Details Section */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: "100%" }}>
              <Typography variant="h6" gutterBottom>
                Details
              </Typography>

              {page.title && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Title
                  </Typography>
                  <Typography variant="body1">{page.title}</Typography>
                </Box>
              )}

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Date
                </Typography>
                <Typography variant="body1">
                  {page.date
                    ? new Date(page.date).toLocaleDateString()
                    : "Not specified"}
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Created
                </Typography>
                <Typography variant="body1">
                  {new Date(page.createdAt).toLocaleString()}
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Last Updated
                </Typography>
                <Typography variant="body1">
                  {new Date(page.updatedAt).toLocaleString()}
                </Typography>
              </Box>

              {page.notes && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Notes
                  </Typography>
                  <Typography variant="body1">{page.notes}</Typography>
                </Box>
              )}

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Extracted Text
              </Typography>
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  maxHeight: "300px",
                  overflow: "auto",
                  bgcolor: "background.default",
                }}
              >
                {page.extractedText ? (
                  <Typography
                    variant="body1"
                    component="pre"
                    sx={{
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                      fontFamily: "inherit",
                    }}
                  >
                    {page.extractedText}
                  </Typography>
                ) : (
                  <Typography
                    variant="body1"
                    color="text.secondary"
                    fontStyle="italic"
                  >
                    No text extracted from this page
                  </Typography>
                )}
              </Paper>
            </Paper>
          </Grid>
        </Grid>
      </Box>

      {/* Edit Page Dialog */}
      <Dialog
        open={openEditDialog}
        onClose={handleCloseEditDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Page</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            name="title"
            label="Title"
            type="text"
            fullWidth
            variant="outlined"
            value={editPage.title}
            onChange={handleInputChange}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="date"
            label="Date"
            type="date"
            fullWidth
            variant="outlined"
            value={editPage.date ? editPage.date.split("T")[0] : ""}
            onChange={handleInputChange}
            InputLabelProps={{ shrink: true }}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="notes"
            label="Notes"
            type="text"
            fullWidth
            variant="outlined"
            value={editPage.notes}
            onChange={handleInputChange}
            multiline
            rows={4}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog}>Cancel</Button>
          <Button
            onClick={handleUpdatePage}
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

export default PageDetail;
