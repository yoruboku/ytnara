"""
Scheduler Module
Handles scheduling and timing of content uploads throughout the day
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import json
from pathlib import Path
import threading
from dataclasses import dataclass, asdict
from enum import Enum

# Create ContentItem class locally to avoid circular import
@dataclass
class ContentItem:
    """Represents a piece of content to be processed"""
    url: str
    title: str
    platform: str
    creator: str
    keywords: List[str]
    downloaded_path: Optional[str] = None
    edited_path: Optional[str] = None
    uploaded_platforms: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.uploaded_platforms is None:
            self.uploaded_platforms = []

class ScheduleStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class ScheduledTask:
    """Represents a scheduled upload task"""
    id: str
    content_item: ContentItem
    scheduled_time: datetime
    status: ScheduleStatus = ScheduleStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class ContentScheduler:
    """Content scheduling and automation system"""
    
    def __init__(self):
        self.scheduled_tasks: List[ScheduledTask] = []
        self.is_running = False
        self.scheduler_thread = None
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.schedule_file = self.data_dir / "schedule.json"
        
        # Load existing schedule
        self._load_schedule()
        
        # Callback functions
        self.upload_callback: Optional[Callable] = None
        self.progress_callback: Optional[Callable] = None
        
    def set_upload_callback(self, callback: Callable):
        """Set the callback function for processing uploads"""
        self.upload_callback = callback
    
    def set_progress_callback(self, callback: Callable):
        """Set the callback function for progress updates"""
        self.progress_callback = callback
    
    async def schedule_uploads(self, content_list: List, cycles: int, daily_frequency: int, interval_hours: float):
        """Schedule uploads throughout multiple days"""
        logging.info(f"Scheduling {cycles} cycles with {daily_frequency} uploads per day")
        
        # Calculate total content needed
        content_per_cycle = 4  # 4 videos per cycle (1 per account)
        total_content_needed = cycles * content_per_cycle
        
        # Ensure we have enough content
        if len(content_list) < total_content_needed:
            logging.warning(f"Not enough content for all cycles. Have {len(content_list)}, need {total_content_needed}")
            # Adjust cycles based on available content
            cycles = len(content_list) // content_per_cycle
            total_content_needed = cycles * content_per_cycle
        
        # Schedule content across days
        current_time = datetime.now()
        content_index = 0
        
        for day in range((cycles + daily_frequency - 1) // daily_frequency):  # Calculate number of days needed
            day_start = current_time + timedelta(days=day)
            
            # Schedule uploads for this day
            uploads_today = min(daily_frequency, cycles - (day * daily_frequency))
            
            for upload_slot in range(uploads_today):
                # Calculate time for this upload
                upload_time = day_start + timedelta(hours=upload_slot * interval_hours)
                
                # Get content for this cycle (4 videos)
                cycle_content = content_list[content_index:content_index + content_per_cycle]
                content_index += content_per_cycle
                
                if not cycle_content:
                    break
                
                # Schedule each video in the cycle
                for i, content_item in enumerate(cycle_content):
                    # Stagger uploads within the cycle (5 minute intervals)
                    staggered_time = upload_time + timedelta(minutes=i * 5)
                    
                    task = ScheduledTask(
                        id=f"task_{day}_{upload_slot}_{i}_{int(time.time())}",
                        content_item=content_item,
                        scheduled_time=staggered_time
                    )
                    
                    self.scheduled_tasks.append(task)
                    logging.info(f"Scheduled upload: {content_item.title} at {staggered_time}")
        
        # Save schedule
        self._save_schedule()
        
        # Start the scheduler
        await self.start_scheduler()
    
    async def start_scheduler(self):
        """Start the scheduling system"""
        if self.is_running:
            logging.warning("Scheduler is already running")
            return
        
        self.is_running = True
        logging.info("Starting content scheduler...")
        
        # Start scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Monitor scheduled tasks
        asyncio.create_task(self._monitor_tasks())
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        while self.is_running:
            try:
                # Check for pending tasks
                current_time = datetime.now()
                
                for task in self.scheduled_tasks:
                    if (task.status == ScheduleStatus.PENDING and 
                        task.scheduled_time <= current_time):
                        
                        # Mark as running
                        task.status = ScheduleStatus.RUNNING
                        
                        # Process the task
                        asyncio.create_task(self._process_task(task))
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                logging.error(f"Error in scheduler thread: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    async def _monitor_tasks(self):
        """Monitor task execution and provide progress updates"""
        while self.is_running:
            try:
                # Count task statuses
                status_counts = {
                    ScheduleStatus.PENDING: 0,
                    ScheduleStatus.RUNNING: 0,
                    ScheduleStatus.COMPLETED: 0,
                    ScheduleStatus.FAILED: 0
                }
                
                for task in self.scheduled_tasks:
                    status_counts[task.status] += 1
                
                # Call progress callback if set
                if self.progress_callback:
                    progress_info = {
                        "total_tasks": len(self.scheduled_tasks),
                        "pending": status_counts[ScheduleStatus.PENDING],
                        "running": status_counts[ScheduleStatus.RUNNING],
                        "completed": status_counts[ScheduleStatus.COMPLETED],
                        "failed": status_counts[ScheduleStatus.FAILED],
                        "next_task": self._get_next_task_info()
                    }
                    
                    self.progress_callback(progress_info)
                
                # Save schedule periodically
                self._save_schedule()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logging.error(f"Error monitoring tasks: {str(e)}")
                await asyncio.sleep(60)
    
    async def _process_task(self, task: ScheduledTask):
        """Process a scheduled task"""
        try:
            logging.info(f"Processing scheduled task: {task.content_item.title}")
            
            if self.upload_callback:
                # Call the upload function
                success = await self.upload_callback(task.content_item)
                
                if success:
                    task.status = ScheduleStatus.COMPLETED
                    logging.info(f"Task completed successfully: {task.content_item.title}")
                else:
                    # Handle retry logic
                    task.retry_count += 1
                    
                    if task.retry_count <= task.max_retries:
                        # Reschedule for retry (in 30 minutes)
                        task.scheduled_time = datetime.now() + timedelta(minutes=30)
                        task.status = ScheduleStatus.PENDING
                        logging.warning(f"Task failed, retrying in 30 minutes: {task.content_item.title} (attempt {task.retry_count}/{task.max_retries})")
                    else:
                        task.status = ScheduleStatus.FAILED
                        logging.error(f"Task failed permanently: {task.content_item.title}")
            else:
                logging.error("No upload callback set")
                task.status = ScheduleStatus.FAILED
                
        except Exception as e:
            logging.error(f"Error processing task: {str(e)}")
            task.status = ScheduleStatus.FAILED
    
    def _get_next_task_info(self) -> Optional[Dict]:
        """Get information about the next scheduled task"""
        pending_tasks = [t for t in self.scheduled_tasks if t.status == ScheduleStatus.PENDING]
        
        if not pending_tasks:
            return None
        
        # Sort by scheduled time
        next_task = min(pending_tasks, key=lambda t: t.scheduled_time)
        
        return {
            "title": next_task.content_item.title,
            "scheduled_time": next_task.scheduled_time.isoformat(),
            "time_until": str(next_task.scheduled_time - datetime.now())
        }
    
    def pause_scheduler(self):
        """Pause the scheduler"""
        self.is_running = False
        logging.info("Scheduler paused")
    
    def resume_scheduler(self):
        """Resume the scheduler"""
        if not self.is_running:
            asyncio.create_task(self.start_scheduler())
            logging.info("Scheduler resumed")
    
    def stop_scheduler(self):
        """Stop the scheduler completely"""
        self.is_running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logging.info("Scheduler stopped")
    
    def add_immediate_task(self, content_item) -> str:
        """Add a task to be executed immediately"""
        task = ScheduledTask(
            id=f"immediate_{int(time.time())}",
            content_item=content_item,
            scheduled_time=datetime.now()
        )
        
        self.scheduled_tasks.append(task)
        self._save_schedule()
        
        logging.info(f"Added immediate task: {content_item.title}")
        return task.id
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        for task in self.scheduled_tasks:
            if task.id == task_id and task.status == ScheduleStatus.PENDING:
                self.scheduled_tasks.remove(task)
                self._save_schedule()
                logging.info(f"Cancelled task: {task_id}")
                return True
        
        return False
    
    def reschedule_task(self, task_id: str, new_time: datetime) -> bool:
        """Reschedule a task to a new time"""
        for task in self.scheduled_tasks:
            if task.id == task_id and task.status == ScheduleStatus.PENDING:
                task.scheduled_time = new_time
                self._save_schedule()
                logging.info(f"Rescheduled task {task_id} to {new_time}")
                return True
        
        return False
    
    def get_schedule_summary(self) -> Dict:
        """Get a summary of the current schedule"""
        now = datetime.now()
        
        # Group tasks by day
        daily_schedule = {}
        
        for task in self.scheduled_tasks:
            if task.status in [ScheduleStatus.PENDING, ScheduleStatus.RUNNING]:
                day_key = task.scheduled_time.strftime("%Y-%m-%d")
                
                if day_key not in daily_schedule:
                    daily_schedule[day_key] = []
                
                daily_schedule[day_key].append({
                    "id": task.id,
                    "title": task.content_item.title,
                    "time": task.scheduled_time.strftime("%H:%M"),
                    "status": task.status.value
                })
        
        # Sort tasks within each day
        for day in daily_schedule:
            daily_schedule[day].sort(key=lambda t: t["time"])
        
        return {
            "total_tasks": len(self.scheduled_tasks),
            "pending": len([t for t in self.scheduled_tasks if t.status == ScheduleStatus.PENDING]),
            "completed": len([t for t in self.scheduled_tasks if t.status == ScheduleStatus.COMPLETED]),
            "failed": len([t for t in self.scheduled_tasks if t.status == ScheduleStatus.FAILED]),
            "daily_schedule": daily_schedule,
            "next_upload": self._get_next_task_info()
        }
    
    def _save_schedule(self):
        """Save schedule to file"""
        try:
            schedule_data = []
            
            for task in self.scheduled_tasks:
                task_data = {
                    "id": task.id,
                    "content_item": {
                        "url": task.content_item.url,
                        "title": task.content_item.title,
                        "platform": task.content_item.platform,
                        "creator": task.content_item.creator,
                        "keywords": task.content_item.keywords,
                        "downloaded_path": task.content_item.downloaded_path,
                        "edited_path": task.content_item.edited_path,
                        "uploaded_platforms": task.content_item.uploaded_platforms
                    },
                    "scheduled_time": task.scheduled_time.isoformat(),
                    "status": task.status.value,
                    "retry_count": task.retry_count,
                    "max_retries": task.max_retries,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
                
                schedule_data.append(task_data)
            
            with open(self.schedule_file, 'w') as f:
                json.dump(schedule_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving schedule: {str(e)}")
    
    def _load_schedule(self):
        """Load schedule from file"""
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r') as f:
                    schedule_data = json.load(f)
                
                for task_data in schedule_data:
                    content_item = ContentItem(
                        url=task_data["content_item"]["url"],
                        title=task_data["content_item"]["title"],
                        platform=task_data["content_item"]["platform"],
                        creator=task_data["content_item"]["creator"],
                        keywords=task_data["content_item"]["keywords"],
                        downloaded_path=task_data["content_item"].get("downloaded_path"),
                        edited_path=task_data["content_item"].get("edited_path"),
                        uploaded_platforms=task_data["content_item"].get("uploaded_platforms", [])
                    )
                    
                    task = ScheduledTask(
                        id=task_data["id"],
                        content_item=content_item,
                        scheduled_time=datetime.fromisoformat(task_data["scheduled_time"]),
                        status=ScheduleStatus(task_data["status"]),
                        retry_count=task_data.get("retry_count", 0),
                        max_retries=task_data.get("max_retries", 3),
                        created_at=datetime.fromisoformat(task_data["created_at"]) if task_data.get("created_at") else None
                    )
                    
                    self.scheduled_tasks.append(task)
                
                logging.info(f"Loaded {len(self.scheduled_tasks)} scheduled tasks")
                
        except Exception as e:
            logging.error(f"Error loading schedule: {str(e)}")
    
    def clear_completed_tasks(self):
        """Remove completed and failed tasks from schedule"""
        initial_count = len(self.scheduled_tasks)
        
        self.scheduled_tasks = [
            task for task in self.scheduled_tasks 
            if task.status not in [ScheduleStatus.COMPLETED, ScheduleStatus.FAILED]
        ]
        
        removed_count = initial_count - len(self.scheduled_tasks)
        
        if removed_count > 0:
            self._save_schedule()
            logging.info(f"Removed {removed_count} completed/failed tasks")
        
        return removed_count
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_scheduler()