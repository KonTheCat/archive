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
  CircularProgress,
  Divider,
  IconButton,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from "@mui/material";
import {
  Send as SendIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Info as InfoIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import { chatApi } from "../services/api";
import { Citation } from "../types";

// Citation list component
const CitationList: React.FC<{ citations: Citation[] }> = ({ citations }) => {
  const [expanded, setExpanded] = useState(false);

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  return (
    <Box sx={{ mt: 1 }}>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          cursor: "pointer",
          color: "text.secondary",
        }}
        onClick={handleToggle}
      >
        <InfoIcon fontSize="small" sx={{ mr: 0.5 }} />
        <Typography variant="caption">
          {expanded ? "Hide sources" : "Show sources"} ({citations.length})
        </Typography>
        {expanded ? (
          <ExpandLessIcon fontSize="small" />
        ) : (
          <ExpandMoreIcon fontSize="small" />
        )}
      </Box>

      <Collapse in={expanded}>
        <Box
          sx={{ mt: 1, pl: 2, borderLeft: "1px solid", borderColor: "divider" }}
        >
          {citations.map((citation, index) => (
            <Box key={index} sx={{ mb: 1 }}>
              <Typography variant="caption" sx={{ fontWeight: "bold" }}>
                {citation.source_name}{" "}
                {citation.page_title && `- ${citation.page_title}`}
              </Typography>
              <Typography variant="caption" component="div" sx={{ mt: 0.5 }}>
                {citation.text_snippet}
              </Typography>
            </Box>
          ))}
        </Box>
      </Collapse>
    </Box>
  );
};

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<
    Array<{
      id: string;
      role: "user" | "assistant";
      content: string;
      citations?: Citation[];
    }>
  >([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Welcome to the Archive Chat! I can help you find information in your personal archive. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [openClearDialog, setOpenClearDialog] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  // Handle clearing the chat
  const handleClearChat = () => {
    setOpenClearDialog(true);
  };

  const handleConfirmClear = () => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content:
          "Chat history cleared. How can I help you with your archive today?",
      },
    ]);
    setOpenClearDialog(false);
  };

  const handleCancelClear = () => {
    setOpenClearDialog(false);
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
    };

    // Add user message to the UI
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Call the chat API - always use RAG (vector search)
      const response = await chatApi.sendMessage(input, true);

      // Add assistant response to the UI
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: response.data.role,
        content: response.data.content,
        citations: response.data.citations,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);

      // Add error message
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant" as const,
        content:
          "Sorry, there was an error processing your request. Please try again.",
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
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
            aria-label="clear chat"
            onClick={handleClearChat}
            color="default"
            size="large"
          >
            <DeleteIcon />
          </IconButton>
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
                  <Box
                    sx={{
                      backgroundColor:
                        message.role === "user"
                          ? "primary.dark"
                          : "background.default",
                      borderRadius: 2,
                      p: 2,
                      maxWidth: "80%",
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{
                        color:
                          message.role === "user"
                            ? "primary.contrastText"
                            : "text.secondary",
                        display: "block",
                        mb: 0.5,
                      }}
                    >
                      {message.role === "user" ? "You" : "Assistant"}
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        color:
                          message.role === "user"
                            ? "primary.contrastText"
                            : "text.primary",
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {message.content}
                    </Typography>

                    {/* Show citations if available */}
                    {message.role === "assistant" &&
                      message.citations &&
                      message.citations.length > 0 && (
                        <CitationList citations={message.citations} />
                      )}
                  </Box>
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
