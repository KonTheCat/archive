import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Button,
  Chip,
  IconButton,
  Link,
  Tooltip,
  CircularProgress,
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import CancelIcon from "@mui/icons-material/Cancel";
import { Link as RouterLink } from "react-router-dom";
import { tasksApi } from "../services/api";
import { BackgroundTask } from "../types";
import { format } from "date-fns";

const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<BackgroundTask[]>([]);
  const [selectedTasks, setSelectedTasks] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch tasks from the API
  const fetchTasks = useCallback(async () => {
    try {
      setRefreshing(true);
      const response = await tasksApi.getTasks();
      setTasks(response.data);
    } catch (error) {
      console.error("Error fetching tasks:", error);
    } finally {
      setRefreshing(false);
    }
  }, []);

  // Load tasks on component mount
  useEffect(() => {
    fetchTasks();

    // Set up auto-refresh every 5 seconds
    const intervalId = setInterval(() => {
      fetchTasks();
    }, 5000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [fetchTasks]);

  // Handle checkbox selection
  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const cancellableTasks = tasks
        .filter((task) => task.canCancel && task.status === "pending")
        .map((task) => task.id);
      setSelectedTasks(cancellableTasks);
    } else {
      setSelectedTasks([]);
    }
  };

  const handleSelectTask = (taskId: string, checked: boolean) => {
    if (checked) {
      setSelectedTasks([...selectedTasks, taskId]);
    } else {
      setSelectedTasks(selectedTasks.filter((id) => id !== taskId));
    }
  };

  // Cancel tasks
  const handleCancelTask = async (taskId: string) => {
    try {
      setLoading(true);
      await tasksApi.cancelTask(taskId);
      // Refresh the task list
      fetchTasks();
    } catch (error) {
      console.error(`Error cancelling task ${taskId}:`, error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSelected = async () => {
    if (selectedTasks.length === 0) return;

    try {
      setLoading(true);
      await tasksApi.cancelTasks(selectedTasks);
      setSelectedTasks([]);
      // Refresh the task list
      fetchTasks();
    } catch (error) {
      console.error("Error cancelling selected tasks:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAll = async () => {
    try {
      setLoading(true);
      await tasksApi.cancelAllTasks();
      setSelectedTasks([]);
      // Refresh the task list
      fetchTasks();
    } catch (error) {
      console.error("Error cancelling all tasks:", error);
    } finally {
      setLoading(false);
    }
  };

  // Format the scheduled time
  const formatTime = (isoString: string) => {
    try {
      return format(new Date(isoString), "h:mm:ss a");
    } catch (error) {
      return isoString;
    }
  };

  // Get status chip color
  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "default";
      case "in_progress":
        return "primary";
      case "completed":
        return "success";
      case "failed":
        return "error";
      case "cancelled":
        return "warning";
      default:
        return "default";
    }
  };

  // Check if all cancellable pending tasks are selected
  const allCancellableSelected =
    tasks.filter((task) => task.canCancel && task.status === "pending")
      .length === selectedTasks.length;

  // Count of cancellable pending tasks
  const cancellablePendingCount = tasks.filter(
    (task) => task.canCancel && task.status === "pending"
  ).length;

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h4" component="h1">
          Background Tasks
        </Typography>
        <Tooltip title="Refresh tasks">
          <IconButton onClick={fetchTasks} disabled={refreshing}>
            {refreshing ? <CircularProgress size={24} /> : <RefreshIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Button
          variant="outlined"
          color="primary"
          onClick={handleCancelSelected}
          disabled={selectedTasks.length === 0 || loading}
          sx={{ mr: 1 }}
        >
          Cancel Selected ({selectedTasks.length})
        </Button>
        <Button
          variant="outlined"
          color="error"
          onClick={handleCancelAll}
          disabled={cancellablePendingCount === 0 || loading}
        >
          Cancel All ({cancellablePendingCount})
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={
                    selectedTasks.length > 0 &&
                    selectedTasks.length < cancellablePendingCount
                  }
                  checked={
                    cancellablePendingCount > 0 && allCancellableSelected
                  }
                  onChange={handleSelectAll}
                  disabled={cancellablePendingCount === 0}
                />
              </TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Source/Page</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tasks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No background tasks found
                </TableCell>
              </TableRow>
            ) : (
              tasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedTasks.includes(task.id)}
                      onChange={(e) =>
                        handleSelectTask(task.id, e.target.checked)
                      }
                      disabled={!task.canCancel || task.status !== "pending"}
                    />
                  </TableCell>
                  <TableCell>{task.taskType}</TableCell>
                  <TableCell>
                    {task.sourceId && (
                      <>
                        <Link
                          component={RouterLink}
                          to={`/sources/${task.sourceId}`}
                        >
                          Source
                        </Link>
                        {task.pageId && (
                          <>
                            {" / "}
                            <Link
                              component={RouterLink}
                              to={`/sources/${task.sourceId}/pages/${task.pageId}`}
                            >
                              Page
                            </Link>
                          </>
                        )}
                      </>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={task.status}
                      color={getStatusColor(task.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{formatTime(task.scheduledAt)}</TableCell>
                  <TableCell>
                    {task.canCancel && task.status === "pending" && (
                      <Tooltip title="Cancel task">
                        <IconButton
                          size="small"
                          onClick={() => handleCancelTask(task.id)}
                          disabled={loading}
                        >
                          <CancelIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Tasks;
