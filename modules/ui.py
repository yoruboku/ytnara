"""
Terminal UI Module
Provides a stylish terminal interface with interactive prompts and progress tracking
"""

import os
import sys
import time
import threading
from typing import Optional, Dict, Any, List
from datetime import datetime
import colorama
from colorama import Fore, Back, Style
import pyfiglet
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.prompt import Prompt, Confirm, IntPrompt
import json
from pathlib import Path

# Initialize colorama for Windows compatibility
colorama.init()

class TerminalUI:
    """Stylish terminal user interface"""
    
    def __init__(self):
        self.console = Console()
        self.progress = None
        self.live_display = None
        self.stats = {
            "discovered": 0,
            "verified": 0,
            "downloaded": 0,
            "edited": 0,
            "uploaded": 0,
            "failed": 0
        }
        
    def show_banner(self):
        """Display the YT-Nara banner"""
        self.clear_screen()
        
        # Create ASCII art banner
        banner = pyfiglet.figlet_format("YT-NARA", font="slant")
        
        # Style the banner
        banner_text = Text(banner, style="bold cyan")
        
        # Add subtitle
        subtitle = Text(
            "Universal Content Automation Tool\n"
            "Discover • Download • Edit • Upload\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            style="bright_white",
            justify="center"
        )
        
        # Display banner
        self.console.print(Panel(
            banner_text + "\n" + subtitle,
            border_style="bright_cyan",
            padding=(1, 2)
        ))
        
        print()
    
    def get_topic_input(self) -> str:
        """Get topic input from user"""
        self.print_section_header("📝 Topic Configuration")
        
        topic = Prompt.ask(
            "[bold cyan]Enter your topic[/bold cyan] (e.g., 'one piece', 'suits', 'anime memes')",
            default="",
            show_default=False
        )
        
        while not topic.strip():
            self.print_error("Topic cannot be empty!")
            topic = Prompt.ask(
                "[bold cyan]Enter your topic[/bold cyan]",
                default="",
                show_default=False
            )
        
        self.print_success(f"Topic set: {topic}")
        return topic.strip()
    
    def get_cycles_input(self) -> int:
        """Get number of cycles from user"""
        self.print_section_header("🔄 Cycle Configuration")
        
        self.console.print("[dim]Each cycle processes 4 videos (1 per account)[/dim]")
        
        cycles = IntPrompt.ask(
            "[bold cyan]How many cycles to run?[/bold cyan]",
            default=3,
            show_default=True
        )
        
        while cycles <= 0:
            self.print_error("Number of cycles must be positive!")
            cycles = IntPrompt.ask(
                "[bold cyan]How many cycles to run?[/bold cyan]",
                default=3
            )
        
        self.print_success(f"Cycles set: {cycles}")
        return cycles
    
    def get_daily_frequency_input(self) -> Optional[int]:
        """Get daily frequency input from user"""
        self.print_section_header("📅 Schedule Configuration")
        
        use_scheduling = Confirm.ask(
            "[bold cyan]Do you want to schedule uploads throughout the day?[/bold cyan]",
            default=True
        )
        
        if not use_scheduling:
            self.print_info("All cycles will run immediately")
            return None
        
        frequency = IntPrompt.ask(
            "[bold cyan]How many times per day?[/bold cyan]",
            default=5,
            show_default=True
        )
        
        while frequency <= 0 or frequency > 24:
            self.print_error("Daily frequency must be between 1 and 24!")
            frequency = IntPrompt.ask(
                "[bold cyan]How many times per day?[/bold cyan]",
                default=5
            )
        
        self.print_success(f"Daily frequency set: {frequency} times per day")
        return frequency
    
    def show_confirmation(self, topic: str, cycles: int, daily_frequency: Optional[int]) -> bool:
        """Show configuration confirmation"""
        self.print_section_header("✅ Configuration Summary")
        
        # Create summary table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Setting", style="bold cyan")
        table.add_column("Value", style="bright_white")
        
        table.add_row("Topic:", topic)
        table.add_row("Cycles:", str(cycles))
        table.add_row("Videos per cycle:", "4")
        table.add_row("Total videos:", str(cycles * 4))
        
        if daily_frequency:
            table.add_row("Daily frequency:", f"{daily_frequency} times per day")
            days_needed = (cycles + daily_frequency - 1) // daily_frequency
            table.add_row("Duration:", f"~{days_needed} day(s)")
        else:
            table.add_row("Execution:", "Immediate (all cycles)")
        
        self.console.print(Panel(table, title="Configuration", border_style="green"))
        
        return Confirm.ask(
            "\n[bold green]Proceed with this configuration?[/bold green]",
            default=True
        )
    
    def print_step(self, message: str):
        """Print a step message"""
        self.console.print(f"[bold blue]⚡[/bold blue] {message}")
    
    def print_success(self, message: str):
        """Print a success message"""
        self.console.print(f"[bold green]✅[/bold green] {message}")
    
    def print_error(self, message: str):
        """Print an error message"""
        self.console.print(f"[bold red]❌[/bold red] {message}")
    
    def print_warning(self, message: str):
        """Print a warning message"""
        self.console.print(f"[bold yellow]⚠️[/bold yellow] {message}")
    
    def print_info(self, message: str):
        """Print an info message"""
        self.console.print(f"[bold cyan]ℹ️[/bold cyan] {message}")
    
    def print_section_header(self, title: str):
        """Print a section header"""
        print()
        self.console.print(Panel(
            Text(title, justify="center"),
            border_style="bright_blue",
            padding=(0, 1)
        ))
        print()
    
    def print_cycle_start(self, current_cycle: int, total_cycles: int):
        """Print cycle start message"""
        self.print_section_header(f"🚀 Starting Cycle {current_cycle}/{total_cycles}")
    
    def start_progress_tracking(self, total_items: int):
        """Start progress tracking"""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        )
        
        # Create tasks for different stages
        self.progress_tasks = {
            "discovery": self.progress.add_task("🔍 Discovering content...", total=1),
            "verification": self.progress.add_task("✅ Verifying content...", total=total_items),
            "download": self.progress.add_task("⬇️ Downloading videos...", total=total_items),
            "editing": self.progress.add_task("✂️ Editing videos...", total=total_items),
            "upload": self.progress.add_task("⬆️ Uploading videos...", total=total_items)
        }
        
        self.progress.start()
    
    def update_progress(self, stage: str, advance: int = 1, description: str = None):
        """Update progress for a specific stage"""
        if self.progress and stage in self.progress_tasks:
            if description:
                self.progress.update(self.progress_tasks[stage], description=description)
            self.progress.advance(self.progress_tasks[stage], advance)
    
    def complete_progress_stage(self, stage: str):
        """Mark a progress stage as complete"""
        if self.progress and stage in self.progress_tasks:
            task_id = self.progress_tasks[stage]
            task = self.progress.tasks[task_id]
            if not task.finished:
                self.progress.update(task_id, completed=task.total)
    
    def stop_progress_tracking(self):
        """Stop progress tracking"""
        if self.progress:
            self.progress.stop()
            self.progress = None
    
    def show_statistics_dashboard(self, stats: Dict[str, Any]):
        """Show real-time statistics dashboard"""
        # Create layout
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="stats", ratio=1),
            Layout(name="progress", ratio=1)
        )
        
        # Header
        header = Panel(
            Text("YT-Nara Dashboard", justify="center", style="bold cyan"),
            border_style="bright_cyan"
        )
        layout["header"].update(header)
        
        # Statistics table
        stats_table = Table(title="Statistics", box=None)
        stats_table.add_column("Metric", style="bold cyan")
        stats_table.add_column("Count", style="bright_white", justify="right")
        
        for key, value in stats.items():
            emoji = {
                "discovered": "🔍",
                "verified": "✅",
                "downloaded": "⬇️",
                "edited": "✂️",
                "uploaded": "⬆️",
                "failed": "❌"
            }.get(key, "📊")
            
            stats_table.add_row(f"{emoji} {key.title()}", str(value))
        
        layout["stats"].update(Panel(stats_table, border_style="green"))
        
        # Progress info
        if "next_task" in stats and stats["next_task"]:
            next_task = stats["next_task"]
            progress_text = f"Next: {next_task.get('title', 'Unknown')}\n"
            progress_text += f"Time: {next_task.get('time_until', 'Soon')}"
        else:
            progress_text = "No upcoming tasks"
        
        progress_panel = Panel(
            Text(progress_text, justify="center"),
            title="Next Upload",
            border_style="yellow"
        )
        layout["progress"].update(progress_panel)
        
        # Footer
        footer = Panel(
            Text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                 justify="center", style="dim"),
            border_style="bright_black"
        )
        layout["footer"].update(footer)
        
        return layout
    
    def start_live_dashboard(self, stats: Dict[str, Any]):
        """Start live updating dashboard"""
        if self.live_display:
            self.stop_live_dashboard()
        
        layout = self.show_statistics_dashboard(stats)
        self.live_display = Live(layout, console=self.console, refresh_per_second=1)
        self.live_display.start()
    
    def update_live_dashboard(self, stats: Dict[str, Any]):
        """Update live dashboard"""
        if self.live_display:
            layout = self.show_statistics_dashboard(stats)
            self.live_display.update(layout)
    
    def stop_live_dashboard(self):
        """Stop live dashboard"""
        if self.live_display:
            self.live_display.stop()
            self.live_display = None
    
    def show_upload_summary(self, results: Dict[str, bool]):
        """Show upload results summary"""
        self.print_section_header("📊 Upload Summary")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Platform", style="bold")
        table.add_column("Account", style="cyan")
        table.add_column("Status", justify="center")
        
        for platform_account, success in results.items():
            platform, account = platform_account.split('_', 1)
            
            if success:
                status = Text("✅ Success", style="bold green")
            else:
                status = Text("❌ Failed", style="bold red")
            
            table.add_row(platform.title(), account, status)
        
        self.console.print(table)
    
    def show_schedule_summary(self, schedule_info: Dict[str, Any]):
        """Show schedule summary"""
        self.print_section_header("📅 Schedule Overview")
        
        # Overall stats
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="bold cyan")
        stats_table.add_column("Value", style="bright_white", justify="right")
        
        stats_table.add_row("Total Tasks", str(schedule_info.get("total_tasks", 0)))
        stats_table.add_row("Pending", str(schedule_info.get("pending", 0)))
        stats_table.add_row("Completed", str(schedule_info.get("completed", 0)))
        stats_table.add_row("Failed", str(schedule_info.get("failed", 0)))
        
        self.console.print(Panel(stats_table, title="Statistics", border_style="blue"))
        
        # Next upload info
        if schedule_info.get("next_upload"):
            next_info = schedule_info["next_upload"]
            next_text = f"📹 {next_info['title']}\n"
            next_text += f"⏰ {next_info['scheduled_time']}\n"
            next_text += f"⏳ {next_info['time_until']}"
            
            self.console.print(Panel(
                Text(next_text, justify="center"),
                title="Next Upload",
                border_style="green"
            ))
        
        # Daily schedule
        daily_schedule = schedule_info.get("daily_schedule", {})
        if daily_schedule:
            self.console.print("\n[bold cyan]Daily Schedule:[/bold cyan]")
            
            for day, tasks in sorted(daily_schedule.items()):
                day_table = Table(title=f"📅 {day}", show_header=True, header_style="bold yellow")
                day_table.add_column("Time", style="cyan")
                day_table.add_column("Title", style="white")
                day_table.add_column("Status", justify="center")
                
                for task in tasks:
                    status_emoji = {
                        "pending": "⏳",
                        "running": "▶️",
                        "completed": "✅",
                        "failed": "❌"
                    }.get(task["status"], "❓")
                    
                    day_table.add_row(
                        task["time"],
                        task["title"][:50] + ("..." if len(task["title"]) > 50 else ""),
                        f"{status_emoji} {task['status'].title()}"
                    )
                
                self.console.print(day_table)
                print()
    
    def run_setup(self):
        """Run initial setup wizard"""
        self.show_banner()
        self.print_section_header("🛠️ Initial Setup")
        
        self.print_info("Setting up YT-Nara for first use...")
        
        # Create directories
        directories = ["downloads", "edited_videos", "data", "logs", "sessions", "temp"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            self.print_success(f"Created directory: {directory}")
        
        # Check dependencies
        self.print_step("Checking dependencies...")
        
        dependencies = [
            ("yt-dlp", "yt_dlp"),
            ("moviepy", "moviepy"),
            ("selenium", "selenium"),
            ("aiohttp", "aiohttp"),
            ("colorama", "colorama"),
            ("rich", "rich"),
            ("pyfiglet", "pyfiglet")
        ]
        
        missing_deps = []
        for dep_name, import_name in dependencies:
            try:
                __import__(import_name)
                self.print_success(f"✓ {dep_name}")
            except ImportError:
                self.print_error(f"✗ {dep_name} (missing)")
                missing_deps.append(dep_name)
        
        if missing_deps:
            self.print_warning(f"Missing dependencies: {', '.join(missing_deps)}")
            self.print_info("Please install missing dependencies with: pip install " + " ".join(missing_deps))
            return False
        
        # Setup account configuration
        self.print_step("Setting up account configuration...")
        
        accounts_config = {
            "youtube": [
                {"name": "account1", "logged_in": False},
                {"name": "account2", "logged_in": False}
            ],
            "instagram": [
                {"name": "account1", "logged_in": False},
                {"name": "account2", "logged_in": False}
            ]
        }
        
        config_path = Path("data/accounts.json")
        with open(config_path, 'w') as f:
            json.dump(accounts_config, f, indent=2)
        
        self.print_success("Account configuration created")
        
        # Setup complete
        self.print_section_header("🎉 Setup Complete!")
        self.print_success("YT-Nara is ready to use!")
        self.print_info("Run 'python yt_nara.py' to start the application")
        
        return True
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def wait_for_input(self, message: str = "Press Enter to continue..."):
        """Wait for user input"""
        input(f"\n{message}")
    
    def show_error_details(self, error: Exception, context: str = ""):
        """Show detailed error information"""
        self.print_section_header("❌ Error Details")
        
        error_info = f"Context: {context}\n" if context else ""
        error_info += f"Error Type: {type(error).__name__}\n"
        error_info += f"Error Message: {str(error)}"
        
        self.console.print(Panel(
            Text(error_info, style="red"),
            title="Error Information",
            border_style="red"
        ))
    
    def animate_loading(self, message: str, duration: float = 2.0):
        """Show animated loading message"""
        with self.console.status(f"[bold green]{message}...") as status:
            time.sleep(duration)
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_progress_tracking()
        self.stop_live_dashboard()