import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Checkbox,
  FormControlLabel,
  Paper,
  TextField,
  Collapse,
  IconButton,
  Divider,
  List,
  ListItem,
  CircularProgress,
} from "@mui/material";
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Search as SearchIcon,
} from "@mui/icons-material";
import { sourcesApi } from "../services/api";
import { Source } from "../types/index";

interface SourceSelectorProps {
  selectedSourceIds: string[];
  onSourceSelectionChange: (sourceIds: string[]) => void;
}

const SourceSelector: React.FC<SourceSelectorProps> = ({
  selectedSourceIds,
  onSourceSelectionChange,
}) => {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [filterText, setFilterText] = useState("");

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      setLoading(true);
      const response = await sourcesApi.getSources();
      if (response.success) {
        // Sort sources by start date (sources without start date go to the end)
        const sortedSources = [...response.data].sort((a, b) => {
          // If both sources have start dates, compare them
          if (a.startDate && b.startDate) {
            return (
              new Date(a.startDate).getTime() - new Date(b.startDate).getTime()
            );
          }
          // If only a has a start date, it comes first
          if (a.startDate) return -1;
          // If only b has a start date, it comes first
          if (b.startDate) return 1;
          // If neither has a start date, maintain original order
          return 0;
        });

        setSources(sortedSources);
        // If no sources are selected yet, select all by default
        if (selectedSourceIds.length === 0) {
          onSourceSelectionChange(sortedSources.map((source) => source.id));
        }
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

  const handleToggleExpand = () => {
    setExpanded(!expanded);
  };

  const handleSelectAll = () => {
    onSourceSelectionChange(sources.map((source) => source.id));
  };

  const handleDeselectAll = () => {
    onSourceSelectionChange([]);
  };

  const handleSourceToggle = (sourceId: string) => {
    if (selectedSourceIds.includes(sourceId)) {
      onSourceSelectionChange(
        selectedSourceIds.filter((id) => id !== sourceId)
      );
    } else {
      onSourceSelectionChange([...selectedSourceIds, sourceId]);
    }
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilterText(e.target.value);
  };

  // Filter sources by name
  const filteredSources = sources.filter((source) =>
    source.name.toLowerCase().includes(filterText.toLowerCase())
  );

  // Format date for display
  const formatDate = (dateString?: string) => {
    if (!dateString) return "Not specified";
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Paper sx={{ mb: 2, p: 2, backgroundColor: "background.paper" }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          cursor: "pointer",
        }}
        onClick={handleToggleExpand}
      >
        <Typography variant="subtitle1">
          Sources ({selectedSourceIds.length}/{sources.length} Selected)
        </Typography>
        <IconButton size="small">
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      <Collapse in={expanded}>
        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: "flex", mb: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Filter by title..."
              value={filterText}
              onChange={handleFilterChange}
              InputProps={{
                startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />,
              }}
              sx={{ mb: 1 }}
            />
          </Box>

          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              mb: 1,
            }}
          >
            <FormControlLabel
              control={
                <Checkbox
                  checked={
                    selectedSourceIds.length === sources.length &&
                    sources.length > 0
                  }
                  indeterminate={
                    selectedSourceIds.length > 0 &&
                    selectedSourceIds.length < sources.length
                  }
                  onChange={
                    selectedSourceIds.length === sources.length
                      ? handleDeselectAll
                      : handleSelectAll
                  }
                />
              }
              label="Select All"
            />
          </Box>

          <Divider sx={{ my: 1 }} />

          {loading ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
              <CircularProgress size={24} />
            </Box>
          ) : error ? (
            <Typography color="error" variant="body2">
              {error}
            </Typography>
          ) : filteredSources.length === 0 ? (
            <Typography variant="body2" sx={{ py: 2, textAlign: "center" }}>
              No sources match the filter
            </Typography>
          ) : (
            <List dense disablePadding>
              {filteredSources.map((source) => (
                <ListItem key={source.id} disablePadding sx={{ py: 0.5 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={selectedSourceIds.includes(source.id)}
                        onChange={() => handleSourceToggle(source.id)}
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" component="span">
                          {source.name}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          component="span"
                          sx={{ ml: 1 }}
                        >
                          ({formatDate(source.startDate)} -{" "}
                          {formatDate(source.endDate)})
                        </Typography>
                      </Box>
                    }
                    sx={{ width: "100%" }}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default SourceSelector;
