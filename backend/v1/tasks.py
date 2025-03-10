import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Body

from backend.utils.logger import get_logger
from backend.v1.models import BackgroundTask, BackgroundTaskResponse, BackgroundTasksResponse

# Set up logger
logger = get_logger(__name__)

router = APIRouter()

# In-memory store for active tasks
# This is a simple dictionary that maps task IDs to task objects
# In a production environment, you might want to use a more robust solution
# like Redis or a database for task persistence across restarts
_tasks: Dict[str, BackgroundTask] = {}
_tasks_lock = threading.Lock()  # Lock for thread-safe operations on the tasks dictionary

def register_task(
    task_type: str,
    source_id: Optional[str] = None,
    page_id: Optional[str] = None,
    can_cancel: bool = True
) -> BackgroundTask:
    """
    Register a new background task and return its ID.
    
    Args:
        task_type: Type of the task (e.g., "text_extraction")
        source_id: Optional ID of the related source
        page_id: Optional ID of the related page
        can_cancel: Whether this task can be cancelled
        
    Returns:
        The created BackgroundTask object
    """
    task_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    task = BackgroundTask(
        id=task_id,
        taskType=task_type,
        status="pending",
        sourceId=source_id,
        pageId=page_id,
        scheduledAt=now,
        canCancel=can_cancel
    )
    
    with _tasks_lock:
        _tasks[task_id] = task
    
    logger.info(f"Registered task {task_id} of type {task_type}")
    return task

def update_task_status(task_id: str, status: str) -> Optional[BackgroundTask]:
    """
    Update the status of a task.
    
    Args:
        task_id: ID of the task to update
        status: New status ("in_progress", "completed", "failed", "cancelled")
        
    Returns:
        The updated task, or None if the task doesn't exist
    """
    with _tasks_lock:
        if task_id not in _tasks:
            logger.warning(f"Attempted to update non-existent task {task_id}")
            return None
        
        task = _tasks[task_id]
        task.status = status
        
        # Remove completed or failed tasks from the in-memory store
        if status in ["completed", "failed"]:
            _tasks.pop(task_id)
            logger.info(f"Removed {status} task {task_id} from task store")
        else:
            logger.info(f"Updated task {task_id} status to {status}")
        
        return task

def get_task(task_id: str) -> Optional[BackgroundTask]:
    """
    Get a task by ID.
    
    Args:
        task_id: ID of the task to retrieve
        
    Returns:
        The task, or None if it doesn't exist
    """
    with _tasks_lock:
        return _tasks.get(task_id)

def get_all_tasks() -> List[BackgroundTask]:
    """
    Get all active tasks.
    
    Returns:
        List of all active tasks
    """
    with _tasks_lock:
        return list(_tasks.values())

def cancel_task(task_id: str) -> Optional[BackgroundTask]:
    """
    Cancel a task if it's still pending.
    
    Args:
        task_id: ID of the task to cancel
        
    Returns:
        The cancelled task, or None if the task doesn't exist or can't be cancelled
    """
    with _tasks_lock:
        if task_id not in _tasks:
            logger.warning(f"Attempted to cancel non-existent task {task_id}")
            return None
        
        task = _tasks[task_id]
        
        if not task.canCancel:
            logger.warning(f"Attempted to cancel non-cancellable task {task_id}")
            return None
        
        if task.status != "pending":
            logger.warning(f"Attempted to cancel task {task_id} with status {task.status}")
            return None
        
        task.status = "cancelled"
        _tasks.pop(task_id)
        logger.info(f"Cancelled and removed task {task_id}")
        
        return task

def cancel_all_tasks() -> int:
    """
    Cancel all pending tasks that can be cancelled.
    
    Returns:
        Number of tasks cancelled
    """
    cancelled_count = 0
    
    with _tasks_lock:
        task_ids = list(_tasks.keys())
        
        for task_id in task_ids:
            task = _tasks[task_id]
            
            if task.canCancel and task.status == "pending":
                task.status = "cancelled"
                _tasks.pop(task_id)
                cancelled_count += 1
                logger.info(f"Cancelled and removed task {task_id}")
    
    return cancelled_count

# API Routes

@router.get("/tasks", response_model=BackgroundTasksResponse)
async def get_tasks():
    """Get all active background tasks."""
    try:
        tasks = get_all_tasks()
        return BackgroundTasksResponse(data=tasks)
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting tasks: {str(e)}")

@router.get("/tasks/{task_id}", response_model=BackgroundTaskResponse)
async def get_task_by_id(task_id: str):
    """Get a specific background task by ID."""
    try:
        task = get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        
        return BackgroundTaskResponse(data=task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting task: {str(e)}")

@router.delete("/tasks/{task_id}", response_model=BackgroundTaskResponse)
async def cancel_task_by_id(task_id: str):
    """Cancel a specific background task by ID."""
    try:
        task = cancel_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found or cannot be cancelled")
        
        return BackgroundTaskResponse(data=task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}")

@router.delete("/tasks", response_model=dict)
async def cancel_tasks(task_ids: List[str] = Body(default=None)):
    """
    Cancel multiple background tasks.
    
    If task_ids is provided, cancel those specific tasks.
    If task_ids is None or empty, cancel all cancellable tasks.
    """
    try:
        if task_ids:
            # Cancel specific tasks
            cancelled_tasks = []
            for task_id in task_ids:
                task = cancel_task(task_id)
                if task:
                    cancelled_tasks.append(task)
            
            return {
                "success": True,
                "message": f"Cancelled {len(cancelled_tasks)} tasks",
                "cancelled_count": len(cancelled_tasks)
            }
        else:
            # Cancel all cancellable tasks
            cancelled_count = cancel_all_tasks()
            
            return {
                "success": True,
                "message": f"Cancelled {cancelled_count} tasks",
                "cancelled_count": cancelled_count
            }
    except Exception as e:
        logger.error(f"Error cancelling tasks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error cancelling tasks: {str(e)}")
