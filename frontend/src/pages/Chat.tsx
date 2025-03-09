import React, { useState, useRef, useEffect } from "react";
import {
  Typography,
  Box,
  Container,
  TextField,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Divider,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from "@mui/material";
import {
  Send as SendIcon,
  MoreVert as MoreVertIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
} from "@mui/icons-material";

// Note: This is a placeholder for the RAG chat functionality
// The actual implementation would require backend API endpoints for chat

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<
    Array<{
      id: string;
      role: "user" | "assistant";
      content: string;
      timestamp: Date;
    }>
  >([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Welcome to the Archive Chat! I can help you find information in your personal archive. What would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [openClearDialog, setOpenClearDialog] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }

    if (!input.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      role: "user" as const,
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate API call delay
    setTimeout(() => {
      // This is where you would call your backend API for RAG
      // For now, we'll just simulate a response
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant" as const,
        content: `This is a simulated response to your query: "${input}". In a real implementation, this would use RAG to search through your archive and provide relevant information.`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleClearChat = () => {
    setOpenClearDialog(true);
    handleMenuClose();
  };

  const handleConfirmClear = () => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content:
          "Chat history cleared. How can I help you with your archive today?",
        timestamp: new Date(),
      },
    ]);
    setOpenClearDialog(false);
  };

  const handleCancelClear = () => {
    setOpenClearDialog(false);
  };

  const handleSaveChat = () => {
    // This would save the chat to the backend in a real implementation
    // For now, we'll just show an alert
    alert(
      "Chat saved! (This is a placeholder - actual implementation would save to backend)"
    );
    handleMenuClose();
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Typography variant="h4" component="h1">
            Archive Chat
          </Typography>
          <IconButton
            aria-label="chat options"
            aria-controls="chat-menu"
            aria-haspopup="true"
            onClick={handleMenuClick}
          >
            <MoreVertIcon />
          </IconButton>
          <Menu
            id="chat-menu"
            anchorEl={anchorEl}
            keepMounted
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleSaveChat}>
              <SaveIcon fontSize="small" sx={{ mr: 1 }} />
              Save Chat
            </MenuItem>
            <MenuItem onClick={handleClearChat}>
              <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
              Clear Chat
            </MenuItem>
          </Menu>
        </Box>

        <Typography variant="body1" color="text.secondary" paragraph>
          Ask questions about your personal archive using natural language.
        </Typography>

        <Paper
          sx={{
            height: "60vh",
            mb: 2,
            p: 2,
            overflow: "auto",
            backgroundColor: "background.paper",
          }}
        >
          <List>
            {messages.map((message, index) => (
              <React.Fragment key={message.id}>
                <ListItem
                  alignItems="flex-start"
                  sx={{
                    flexDirection:
                      message.role === "user" ? "row-reverse" : "row",
                  }}
                >
                  <ListItemText
                    primary={message.role === "user" ? "You" : "Assistant"}
                    secondary={
                      <Typography
                        component="span"
                        variant="body1"
                        sx={{
                          display: "inline",
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {message.content}
                      </Typography>
                    }
                    sx={{
                      backgroundColor:
                        message.role === "user"
                          ? "primary.dark"
                          : "background.default",
                      borderRadius: 2,
                      p: 2,
                      maxWidth: "80%",
                    }}
                    primaryTypographyProps={{
                      fontSize: 12,
                      color:
                        message.role === "user"
                          ? "primary.contrastText"
                          : "text.secondary",
                    }}
                    secondaryTypographyProps={{
                      color:
                        message.role === "user"
                          ? "primary.contrastText"
                          : "text.primary",
                    }}
                  />
                </ListItem>
                {index < messages.length - 1 && (
                  <Divider
                    variant="middle"
                    component="li"
                    sx={{ my: 1, opacity: 0.2 }}
                  />
                )}
              </React.Fragment>
            ))}
            {isLoading && (
              <ListItem>
                <Box sx={{ display: "flex", ml: 2 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2" sx={{ ml: 2 }}>
                    Thinking...
                  </Typography>
                </Box>
              </ListItem>
            )}
            <div ref={messagesEndRef} />
          </List>
        </Paper>

        <Paper
          component="form"
          onSubmit={handleSendMessage}
          sx={{ p: 2, backgroundColor: "background.paper" }}
        >
          <Box sx={{ display: "flex", alignItems: "flex-end" }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask a question about your archive..."
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
              variant="outlined"
              sx={{ mr: 2 }}
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={isLoading || !input.trim()}
              endIcon={<SendIcon />}
            >
              Send
            </Button>
          </Box>
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 1, display: "block" }}
          >
            Press Enter to send, Shift+Enter for a new line
          </Typography>
        </Paper>
      </Box>

      {/* Clear Chat Confirmation Dialog */}
      <Dialog
        open={openClearDialog}
        onClose={handleCancelClear}
        aria-labelledby="clear-dialog-title"
        aria-describedby="clear-dialog-description"
      >
        <DialogTitle id="clear-dialog-title">Clear Chat History</DialogTitle>
        <DialogContent>
          <DialogContentText id="clear-dialog-description">
            Are you sure you want to clear the chat history? This action cannot
            be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelClear}>Cancel</Button>
          <Button onClick={handleConfirmClear} color="error" autoFocus>
            Clear
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Chat;
