import React, { useState } from "react";
import {
  Typography,
  Box,
  Container,
  TextField,
  Button,
  CircularProgress,
  Paper,
  FormControlLabel,
  Switch,
  FormControl,
  Select,
  MenuItem,
  SelectChangeEvent,
  LinearProgress,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
} from "@mui/material";
import { Search as SearchIcon } from "@mui/icons-material";
import { Link } from "react-router-dom";
import { searchApi } from "../services/api";
import { Source, Page } from "../types/index";

// Extended Page interface to include similarity score
interface PageWithSimilarity extends Page {
  similarity?: number;
}

const Search: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<{
    sources: Source[];
    pages: PageWithSimilarity[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Default to showing only pages (tab index 2)
  const [useVectorSearch, setUseVectorSearch] = useState(false);
  const [resultLimit, setResultLimit] = useState<number>(10);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!searchQuery.trim()) {
      return;
    }

    try {
      setIsSearching(true);
      setError(null);
      setSearchResults(null);

      const response = await searchApi.search(
        searchQuery,
        resultLimit,
        useVectorSearch
      );

      if (response.success) {
        // If using vector search, sort pages by similarity score
        if (
          useVectorSearch &&
          response.data.pages.length > 0 &&
          "similarity" in response.data.pages[0]
        ) {
          response.data.pages.sort((a, b) => {
            const aSimilarity = (a as PageWithSimilarity).similarity || 0;
            const bSimilarity = (b as PageWithSimilarity).similarity || 0;
            return aSimilarity - bSimilarity; // Lower distance means higher similarity
          });
        }

        setSearchResults(
          response.data as { sources: Source[]; pages: PageWithSimilarity[] }
        );
      } else {
        setError(response.message || "Search failed");
      }
    } catch (err) {
      setError("An error occurred while searching");
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleVectorSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUseVectorSearch(e.target.checked);
  };

  const handleResultLimitChange = (event: SelectChangeEvent<number>) => {
    setResultLimit(Number(event.target.value));
  };

  const highlightSearchTerms = (text: string) => {
    if (!searchQuery.trim()) return text;

    const regex = new RegExp(`(${searchQuery})`, "gi");
    return text.replace(
      regex,
      '<span style="background-color: rgba(144, 202, 249, 0.5); font-weight: bold;">$1</span>'
    );
  };

  // Calculate relevance percentage from similarity score
  // For cosine similarity, the score is between -1 and 1, where 1 is most similar
  // For our display, we want to convert this to a percentage where 100% is most similar
  const calculateRelevancePercentage = (similarity: number): number => {
    // For cosine similarity (which is what we're using in the backend)
    // The score from VectorDistance is actually the distance, so lower is better
    // Typically ranges from 0 to 2, where 0 is identical

    // Convert distance to a percentage where 0 distance = 100% relevance
    // and 2 distance = 0% relevance
    const percentage = Math.max(0, Math.min(100, (1 - similarity / 2) * 100));
    return Math.round(percentage);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Search Archive
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Search through your personal archive sources and pages.
        </Typography>

        <Paper
          component="form"
          onSubmit={handleSearch}
          sx={{ p: 3, mb: 4, backgroundColor: "background.paper" }}
        >
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Box sx={{ display: "flex", alignItems: "flex-end" }}>
              <TextField
                fullWidth
                label="Search"
                variant="outlined"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Enter search terms..."
                sx={{ mr: 2 }}
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={isSearching || !searchQuery.trim()}
                startIcon={
                  isSearching ? <CircularProgress size={20} /> : <SearchIcon />
                }
              >
                {isSearching ? "Searching..." : "Search"}
              </Button>
            </Box>

            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <FormControlLabel
                control={
                  <Switch
                    checked={useVectorSearch}
                    onChange={handleVectorSearchChange}
                    color="primary"
                  />
                }
                label="Use Vector Search"
              />

              <Box
                sx={{ display: "flex", alignItems: "center", width: "250px" }}
              >
                <Typography variant="body2" sx={{ mr: 2, minWidth: "120px" }}>
                  Results Limit:
                </Typography>
                <FormControl variant="outlined" size="small" fullWidth>
                  <Select
                    value={resultLimit}
                    onChange={handleResultLimitChange}
                  >
                    <MenuItem value={5}>5</MenuItem>
                    <MenuItem value={10}>10</MenuItem>
                    <MenuItem value={20}>20</MenuItem>
                    <MenuItem value={50}>50</MenuItem>
                    <MenuItem value={100}>100</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>
          </Box>
        </Paper>

        {error && (
          <Box sx={{ mb: 4 }}>
            <Typography color="error">{error}</Typography>
          </Box>
        )}

        {searchResults && (
          <Box>
            <Paper sx={{ width: "100%" }}>
              <Typography variant="h6" gutterBottom sx={{ px: 3, pt: 2 }}>
                Pages ({searchResults.pages.length})
              </Typography>

              {searchResults.pages.length === 0 ? (
                <Box sx={{ p: 3, textAlign: "center" }}>
                  <Typography variant="body1">
                    No pages found for "{searchQuery}"
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ p: 2 }}>
                  <Paper>
                    <Box sx={{ overflow: "auto" }}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Image</TableCell>
                            <TableCell>Date</TableCell>
                            {useVectorSearch && (
                              <TableCell align="center">Relevance</TableCell>
                            )}
                            <TableCell>Content</TableCell>
                            <TableCell align="center">Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {searchResults.pages.map((page) => (
                            <TableRow key={page.id}>
                              <TableCell sx={{ width: 100 }}>
                                {page.imageUrl && (
                                  <Box
                                    sx={{
                                      width: 80,
                                      height: 80,
                                      backgroundImage: `url(${page.imageUrl})`,
                                      backgroundSize: "cover",
                                      backgroundPosition: "center",
                                      borderRadius: 1,
                                    }}
                                  />
                                )}
                              </TableCell>
                              <TableCell>
                                {page.date
                                  ? new Date(page.date).toLocaleDateString()
                                  : "No date"}
                              </TableCell>
                              {useVectorSearch && (
                                <TableCell align="center" sx={{ width: 120 }}>
                                  {page.similarity !== undefined ? (
                                    <Box sx={{ width: 100, mx: "auto" }}>
                                      <Typography
                                        variant="body2"
                                        color="primary"
                                        fontWeight="bold"
                                        align="center"
                                      >
                                        {calculateRelevancePercentage(
                                          page.similarity
                                        )}
                                        %
                                      </Typography>
                                      <LinearProgress
                                        variant="determinate"
                                        value={calculateRelevancePercentage(
                                          page.similarity
                                        )}
                                        color="primary"
                                        sx={{ height: 6, borderRadius: 3 }}
                                      />
                                    </Box>
                                  ) : (
                                    "N/A"
                                  )}
                                </TableCell>
                              )}
                              <TableCell>
                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                  sx={{
                                    maxHeight: "80px",
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                    display: "-webkit-box",
                                    WebkitLineClamp: 3,
                                    WebkitBoxOrient: "vertical",
                                  }}
                                  dangerouslySetInnerHTML={{
                                    __html: highlightSearchTerms(
                                      page.extractedText || "No text extracted"
                                    ),
                                  }}
                                />
                              </TableCell>
                              <TableCell align="center">
                                <Button
                                  component={Link}
                                  to={`/sources/${page.sourceId}/pages/${page.id}`}
                                  size="small"
                                  color="primary"
                                >
                                  View Details
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </Box>
                  </Paper>
                </Box>
              )}
            </Paper>
          </Box>
        )}

        {!isSearching && !searchResults && !error && (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              py: 8,
            }}
          >
            <SearchIcon sx={{ fontSize: 60, color: "text.secondary", mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Enter a search term to find content in your archive
            </Typography>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default Search;
