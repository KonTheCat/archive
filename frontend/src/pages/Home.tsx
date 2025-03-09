import React from "react";
import { Typography, Box, Button, Container, Grid, Paper } from "@mui/material";
import { Link } from "react-router-dom";
import {
  Collections as CollectionsIcon,
  Search as SearchIcon,
  Chat as ChatIcon,
} from "@mui/icons-material";

const Home: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Personal Archive
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Store, organize, and search through your personal archive sources such
          as journals, documents, and more.
        </Typography>

        <Grid container spacing={4} sx={{ mt: 4 }}>
          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 3,
                display: "flex",
                flexDirection: "column",
                height: 240,
                backgroundColor: "background.paper",
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <CollectionsIcon
                  fontSize="large"
                  color="primary"
                  sx={{ mr: 1 }}
                />
                <Typography variant="h5" component="h2">
                  Sources
                </Typography>
              </Box>
              <Typography variant="body1" paragraph sx={{ flexGrow: 1 }}>
                Create and manage your archive sources. Upload pages with images
                and extract text.
              </Typography>
              <Button
                component={Link}
                to="/sources"
                variant="contained"
                color="primary"
                fullWidth
              >
                View Sources
              </Button>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 3,
                display: "flex",
                flexDirection: "column",
                height: 240,
                backgroundColor: "background.paper",
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <SearchIcon fontSize="large" color="primary" sx={{ mr: 1 }} />
                <Typography variant="h5" component="h2">
                  Search
                </Typography>
              </Box>
              <Typography variant="body1" paragraph sx={{ flexGrow: 1 }}>
                Search through your archive content to find specific information
                across all sources.
              </Typography>
              <Button
                component={Link}
                to="/search"
                variant="contained"
                color="primary"
                fullWidth
              >
                Search Content
              </Button>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 3,
                display: "flex",
                flexDirection: "column",
                height: 240,
                backgroundColor: "background.paper",
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <ChatIcon fontSize="large" color="primary" sx={{ mr: 1 }} />
                <Typography variant="h5" component="h2">
                  Chat
                </Typography>
              </Box>
              <Typography variant="body1" paragraph sx={{ flexGrow: 1 }}>
                Interact with your archive content through a chat interface
                using RAG technology.
              </Typography>
              <Button
                component={Link}
                to="/chat"
                variant="contained"
                color="primary"
                fullWidth
              >
                Start Chatting
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Home;
